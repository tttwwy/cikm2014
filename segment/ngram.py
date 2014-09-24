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

class NGram():

    def dd(self):
        return collections.defaultdict(int)
    def __init__(self):
        self.window = 5
        self.edge_window = 1
        self.frq = collections.defaultdict(int)
        self.frq_left = collections.defaultdict(self.dd)
        self.frq_right = collections.defaultdict(self.dd)
        self.frq_total = collections.defaultdict(int)

        self.inner = collections.defaultdict(int)
        self.ent = collections.defaultdict(int)
        self.dicts = collections.defaultdict(int)

    def save(self,model_name,encoding='utf-8'):
        with open(model_name,'w') as f:
            for key,value in self.frq.items():
                f.write("{0}\t{1}\t{2}\t{3}\n".format(key,value,self.inner[key],self.ent[key]))


    def load(self,model_name,encoding='utf-8'):
        with open(model_name,'r') as f:
            self.frq = collections.defaultdict(int)
            self.inner = collections.defaultdict(int)
            self.ent = collections.defaultdict(int)

            for line in f:
                key,value,inner,ent = line.decode(encoding).strip().split("\t")
                self.frq[key] = value
                self.inner[key] = inner
                self.ent[key] = ent

    def count(self,sentence):
        for length in range(self.window):
            len_sentence = len(sentence)
            for index in range(len_sentence):
                if index + length + 1 <= len_sentence:
                    cur_word = sentence[index:index + length + 1]
                    self.frq[cur_word] += 1
                    self.frq_total[len(cur_word)] += 1
                    left_word = sentence[index - self.edge_window:index]
                    right_word = sentence[index + length + 1:index + length + self.edge_window + 1]

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

    def train(self,file_name,frq_min=10):
        with open(file_name,'r') as f:
            for index,line in enumerate(f):
                line = line.strip("\n").decode('utf-8')
                if line:
                    self.count(line)

        for word,value in self.frq.items():
            if value >= frq_min:
                self.inner[word] = self.cal_inner(word)
                self.ent[word] = self.cal_ent(word)


    def generate_dicts(self,file_name,frq_min=10,inner_min=1,ent_min=1.9,encoding='utf-8'):
        with open(file_name,'w') as f:
            for word,value in self.frq.items():
                if value >= frq_min:
                    inner = self.inner[word]
                    ent = self.ent[word]
                    if inner >= inner_min and ent >=  ent_min:
                        self.dicts[word] = value
                        f.write("{0}\t{1}\n".format(word,value))





class Segment():
    def __init__(self):
        self.dicts = collections.defaultdict(int)
        self.window = 5

    def read_dict(self,dict_name,encoding = 'utf-8'):
        with open(dict_name,'r') as f:
            for line in f:
                line = line.strip().decode(encoding)
                if line:
                    word,value = line.split("\t")
                    self.dicts[word] = value


    def rmm_segment(self,sentence):
        sentence = sentence.decode('utf-8')

        # for right in range(len(sentence),0,-1):
        words = []
        right = len(sentence)
        temp = ""
        while right > 0:
            matched = False
            for left in range(0 if right - self.window < 0 else right - self.window,right-1,1):
                word = sentence[left:right]
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
        #
        result = " ".join(words)
        # for word in words:
        #     print word
        return result


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
    # ngram.train("C:\Users\Administrator\Desktop\sougou.txt")

    # 根据指定参数，生成词典,frq_min为最小词频,inner_min为词语内部结合紧密程度，一般应当大于1，ent_min为左右两侧自由程度，至少应当大于1
    # ngram.generate_dicts("dict.txt",frq_min=6,inner_min=1,ent_min=1.2,encoding='utf-8')
    #
    #
    segment = Segment()

    # 读取词典
    segment.read_dict("dict.txt")
    # generate_gram2("C:\Users\Administrator\Desktop\sougou.txt","gram2.txt")
    myseg = DNASegment()
    myseg.initial_dict("dict.txt","gram2.txt")
    with open('C:\Users\Administrator\Desktop\sougou.txt') as f:
        with open("result.txt",'w') as f_write:
            for line in f:
                line = line.strip()
                if line:
                    rmm = segment.rmm_segment(line)
                    seg = myseg.mp_seg(line)
                    f_write.write("{0}\n{1}\n{2}\n".format(line,rmm,seg))

    sequence = "学业水平测试历史知识点"
    print  myseg.mp_seg(sequence)

    print segment.rmm_segment(sequence)
