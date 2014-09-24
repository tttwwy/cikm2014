__author__ = 'Administrator'
# coding=utf-8
import collections
import math
# import dill as pickle
import pickle
import sys
import logging

reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig(level=logging.INFO,
                    format='%(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='ngram.log',
                    filemode='w')

class WordSegment():

    def dd(self):
        return collections.defaultdict(int)
    def __init__(self,encoding=''):
        self.encoding=encoding
        self.window = 5
        self.edge_window = 1
        self.frq = collections.defaultdict(int)
        self.frq_left = collections.defaultdict(self.dd)
        self.frq_right = collections.defaultdict(self.dd)
        self.frq_total = collections.defaultdict(int)

        self.inner = collections.defaultdict(int)
        self.inner_total = collections.defaultdict(int)
        self.ent = collections.defaultdict(int)
        self.ent_total = collections.defaultdict(int)
        self.dicts = collections.defaultdict(int)



    def save(self,model_name):
        with open(model_name,'w') as f:
            for key,value in self.frq.items():
                f.write("{0}\t{1}\t{2}\t{3}\n".format(key,value,self.inner[key],self.ent[key]))


    def load(self,model_name):
        with open(model_name,'r') as f:
            self.frq = collections.defaultdict(int)
            self.inner = collections.defaultdict(int)
            self.ent = collections.defaultdict(int)
            self.frq_total = collections.defaultdict(int)
            self.inner_total  = collections.defaultdict(int)
            self.ent_total = collections.defaultdict(int)
            for line in f:
                # print line
                key,value,inner,ent = line.decode(self.encoding).strip().split("\t")
                value = float(value)
                inner = float(inner)
                ent = float(ent)
                self.frq[key] = value
                self.inner[key] = inner
                self.ent[key] = ent
                self.frq_total[len(key)] += value
                self.inner_total[len(key)] += inner
                self.ent_total[len(key)] += ent


    def count(self,sentence):
        for length in range(self.window):
            len_sentence = len(sentence)
            for index in range(len_sentence):
                if index + length + 1 <= len_sentence:
                    cur_word = "".join(sentence[index:index + length + 1])

                    self.frq[cur_word] += 1
                    self.frq_total[len(cur_word)] += 1

                    left_word = "".join(sentence[index - self.edge_window:index])
                    right_word = "".join(sentence[index + length + 1:index + length + self.edge_window + 1])

                    if left_word:
                        self.frq_left[cur_word][left_word] += 1

                    if right_word:
                        self.frq_right[cur_word][right_word] += 1

    def cal_inner(self,word):
        try:
            if len(word) == 1:
                return 100
            max_inner = max([float(self.frq[left]  * self.frq[right])/ (self.frq_total[len(right)]*self.frq_total[len(left)]) for left,right in self.splits(word)])
            return float(self.frq[word]) / (max_inner * self.frq_total[len(word)])
        except Exception,ex:
            return 0


    def cal_ent(self,word):
        try:
            left_frq = sum(self.frq_left[word].values())
            right_frq = sum(self.frq_right[word].values())
            left_ent = [-float(value)/left_frq * math.log(float(value)/left_frq,2) for key,value in self.frq_left[word].items()]
            left_ent = sum(left_ent)
            right_ent = [-float(value)/right_frq*math.log(float(value)/right_frq,2) for key,value in self.frq_right[word].items()]
            right_ent = sum(right_ent)
            return min(left_ent,right_ent)
        except Exception,ex:
            return (-1)

    def splits(self,text):
        return [(text[:i+1], text[i+1:]) for i in range(min(len(text), self.window) -1 )]

    def train(self,file_name,frq_min=5):
        with open(file_name,'r') as f:
            for index,line in enumerate(f):
                line = line.strip("\n")
                if self.encoding:
                    line = line.decode(self.encoding)
                line = line.split()
                if len(line) == 1:
                    line = list(line[0])
                self.count(line)

        for word,value in self.frq.items():
            # print word,value
            if value >= frq_min:
                inner = self.cal_inner(word)
                ent = self.cal_ent(word)
                self.inner[word] = inner
                self.ent[word] = ent
                self.inner_total[len(word)] += inner
                self.ent_total[len(word)] += ent


    def generate_dicts(self,frq_min=5,inner_min=0.6,ent_min=1):
        for word,value in self.frq.items():
            if value >= frq_min:
                # print word,value
                inner = self.inner[word]
                ent = self.ent[word]
                if inner >= inner_min and ent >=  ent_min:
                    self.dicts[word] = value
                    self.inner_total[word]  += inner
                    self.ent_total[word]  += ent

    def save_dict(self,dict_name):
        with open(dict_name,'w') as f:
            for word,value in self.dicts.items():
                f.write("{0}\t{1}\n".format(word,value))


    def read_dict(self,dict_name):
        self.dicts = collections.defaultdict(int)
        with open(dict_name,'r') as f:
            for line in f:
                word,value = line.strip().split()
                if self.encoding:
                    word = word.decode(self.encoding)
                self.dicts[word] = value

    def get_prob(self,word,k,a,b,c):

        frq = float(self.frq[word])*k
        inner = float(self.inner[word])
        ent = float(self.ent[word])
        # print word,frq,inner,ent,
        if frq <= 0 or ent <= 0.5 or inner <= 1:
            all_freq = sum([x for x in self.frq_total.values()])
            prob = -math.log(a*10./(all_freq*10**len(word)))
        else:
            frq /= self.frq_total[len(word)]
            inner /= self.frq_total[len(word)]
            ent /= self.frq_total[len(word)]
            prob = -math.log(a * frq + b * inner + c * ent)
        # print prob
        return prob

    def mp(self,sentence,k,a,b,c):
        words = []
        wait_words = []
        left_index = collections.defaultdict(list)
        len_sentence = len(sentence)
        index = 0
        best_end_index = -1
        for left in range(len(sentence)):
            for right in range(left+1,min(left + self.window+1,len_sentence+1)):
                word_now = "".join(sentence[left:right])
                cost_now = self.get_prob(word_now,k,a,b,c)
                cost_total_now = -1
                best_left_now = -1
                for i in left_index[left]:
                    # print i
                    # print wait_words
                    word,cost,cost_total,best_left = wait_words[i]
                    if cost_total < cost_total_now or cost_total_now == -1:
                        cost_total_now = cost_total
                        best_left_now = i

                if cost_total_now == -1:
                    cost_total_now = cost_now
                else:
                    cost_total_now += cost_now

                left_index[right].append(index)

                wait_words.append([word_now,cost_now,cost_total_now,best_left_now])
                # print index,left,right,word_now,cost_now,cost_total_now,best_left_now
                if right == len_sentence:
                    if best_end_index == -1 or cost_total_now < wait_words[best_end_index][2]:
                        best_end_index = index
                index += 1
        # print best_end_index
        while best_end_index != -1:
            word,cost,total_cost,best_left = wait_words[best_end_index]
            words.insert(0,word)
            best_end_index = best_left
        return words

    def rmm_segment(self,sentence,encoding=''):
        # if encoding:
        #     sentence = sentence.decode(encoding)
        # for right in range(len(sentence),0,-1):
        words = []
        right = len(sentence)
        temp = ""
        while right > 0:
            matched = False
            for left in range(0 if right - self.window < 0 else right - self.window,right-1,1):
                word = "".join(sentence[left:right])
                # print left,right,word,self.dicts[word]

                if self.dicts[word] > 0:
                    if len(temp) > 0:
                        words.insert(0,temp)
                        temp = ""
                    words.insert(0,word)
                    right = left
                    matched = True
                    break

            if not matched:
                temp = sentence[right-1] + temp
                right -= 1

        if len(temp) > 0:
            words.insert(0,temp)
        # print words
        return words








def generate_gram2(file_read,file_write,encoding='utf-8'):
    gram1 = collections.defaultdict(int)
    gram2 = collections.defaultdict(lambda :collections.defaultdict(int))
    segment.read_dict("dict.txt")

    with open(file_read,'r') as f_read:
        for line in f_read:
            line = line.strip().decode(encoding)
            if line:
                segment_list = segment.rmm_segment(line)
                for index in range(0,len(segment_list)-1):
                    if index == 0:
                        word1 = "<S>"
                    else:
                        word1 = segment_list[index-1]
                    word2 = segment_list[index]
                    gram1[word1] += 1
                    gram2[word1][word2] += 1

    with open(file_write,'w') as f:
        for word in gram2.keys():
            for word2 in gram2[word].keys():
                f.write("{0} {1}\t{2}\n".format(word,word2,gram2[word][word2]))





if __name__ == '__main__':

    # ngram = NGram()
    # ngram.train("data/msr_train.txt")

    # 根据指定参数，生成词典,frq_min为最小词频,inner_min为词语内部结合紧密程度，一般应当大于1，ent_min为左右两侧自由程度，至少应当大于1
    # ngram.generate_dicts("dict.txt",frq_min=6,inner_min=1,ent_min=1.9,encoding='utf-8')

    segment = WordSegment('utf-8')
    # segment.train("data/msr_train.txt")
    # segment.save("data/model.txt")
    segment.load("data/model.txt")
    # segment.generate_dicts(frq_min=5,inner_min=0.7,ent_min=1)
    # segment.save_dict("data/dict.txt")

    # 读取词典
    # segment.read_dict("data/dict.txt")
    # generate_gram2("C:\Users\Administrator\Desktop\sougou.txt","gram2.txt")
    # for key,value in segment.dicts.items():
    #     print key,value
    with open("data/msr.txt") as f:
        lines = f.readlines()
        for k in range(1,5,0.05):
            for a in range(0.1,0.7,0.05):
                for b in range(0.1,min(0.8,1 - a -0.1),0.05):
                    try:
                        c = 1 - a - b
                        right = 0
                        false = 0
                        for line in lines:
                            line = line.strip()
                            if line:
                                line = line.decode('utf-8')
                                standard = line.split(" ")
                                test = list("".join(standard))
                                test = segment.mp(test,k,a,b,c)
                                all = set(standard) & set(test)
                                right += len(all)
                                false += len(standard)
                        print k,a,b,c,right,false,float(right)/right+false
                    except Exception:
                        pass

    # segment.rmm_segment(sentence)
    # with open("C:\Users\Administrator\Desktop\sougou.txt",'r') as f:
    #     for line in f:
    #         line = line.strip()
    #         if line:
    #             sentence = list(line.decode('utf-8'))
    #             print " ".join(segment.mp(sentence))
    #             print " ".join(segment.rmm_segment(sentence))

    # for item in sequence:
    #     print item
