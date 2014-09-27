__author__ = 'Administrator'
# coding=utf-8
import collections
import math
# import dill as pickle
import pickle
import sys
import logging
import os
import base
reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='segment.log',
                    filemode='w')


class WordSegment():
    def dd(self):
        return collections.defaultdict(int)

    def __init__(self, encoding=''):
        self.encoding = encoding
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
        self.word_len = 7


    def save(self, model_name):
        with open(model_name, 'w') as f:
            for index,(key, value) in enumerate(self.frq.items()):
                logging.info("save:{0}".format(index))
                f.write("{0}\t{1}\t{2}\t{3}\n".format(key, value, self.cal_inner(key), self.cal_ent(key)))


    def load(self, model_name):
        with open(model_name, 'r') as f:
            self.frq = collections.defaultdict(int)
            self.inner = collections.defaultdict(int)
            self.ent = collections.defaultdict(int)
            self.frq_total = collections.defaultdict(int)
            self.inner_total = collections.defaultdict(int)
            self.ent_total = collections.defaultdict(int)
            for line in f:
                # print line
                key, value, inner, ent = line.decode(self.encoding).strip().split("\t")
                value = float(value)
                inner = float(inner)
                ent = float(ent)
                self.frq[key] = value
                self.inner[key] = inner
                self.ent[key] = ent
                self.frq_total[len(key)] += value
                self.inner_total[len(key)] += inner
                self.ent_total[len(key)] += ent


    def count(self, sentence):

        for length in range(self.window):
            len_sentence = len(sentence)
            for index in range(len_sentence):
                if index + length + 1 <= len_sentence:
                    cur_word = "".join(sentence[index:index + length + 1])
                    if cur_word:
                        self.frq[cur_word] += 1

                        left_word = "".join(sentence[index - self.edge_window:index])
                        right_word = "".join(sentence[index + length + 1:index + length + self.edge_window + 1])

                        if left_word:
                            self.frq_left[cur_word][left_word] += 1

                        if right_word:
                            self.frq_right[cur_word][right_word] += 1

    def cal_inner(self, word):
        try:
            if self.get_word_len(word) == 1:
                return 100
            max_inner = max(
                [float(self.frq[left] * self.frq[right]) / (self.frq_total[self.get_word_len(right)] * self.frq_total[self.get_word_len(left)]) for
                 left, right in self.splits(word)])
            return float(self.frq[word]) / (max_inner * self.frq_total[self.get_word_len(word)])
        except Exception, ex:
            return 0


    def cal_ent(self, word):
        try:
            left_frq = sum(self.frq_left[word].values())
            right_frq = sum(self.frq_right[word].values())
            left_ent = [-float(value) / left_frq * math.log(float(value) / left_frq, 2) for key, value in
                        self.frq_left[word].items()]
            left_ent = sum(left_ent)
            right_ent = [-float(value) / right_frq * math.log(float(value) / right_frq, 2) for key, value in
                         self.frq_right[word].items()]
            right_ent = sum(right_ent)
            return min(left_ent, right_ent)
        except Exception, ex:
            return (-1)

    def splits(self, text):
        text_list =  [(text[:(i + 1)*self.word_len], text[(i + 1)*self.word_len:]) for i in range(min(self.get_word_len(text), self.window) - 1)]
        # print text_list
        return text_list

    def old_train(self,train_file_name):
        model = base.Base()
        logging.info("train start")

        for index,session in enumerate(model.read_train_file(train_file_name)):
            for label,query,title in session:
                logging.info("read train:{0}".format(index))
                self.count(query)
                if title:
                    self.count(title)

        logging.info("train start")



    def train(self, file_name, file_write_name, frq_min=5):
        with open(file_write_name, 'w') as f_write:
            with open(file_name, 'r') as f:
                for index, line in enumerate(f):
                    logging.info(index)
                    line = line.strip("\n").split()
                    if len(line) == 1:
                        line = list(line[0])
                    frq, frq_left, frq_right = self.count(line)

                    for word in frq.keys():
                        frq_str = " ".join([word, str(frq[word])])
                        left_str = "\t".join([" ".join([x, str(y)]) for x, y in frq_left[word].items()])
                        right_str = "\t".join([" ".join([x, str(y)]) for x, y in frq_left[word].items()])

                        f_write.write("{0}\t\t{1}\t\t{2}\n".format(frq_str, left_str, right_str))

    def get_word_len(self,word):
        return len(word)/self.word_len

    def reduce(self, file_name, model_name):
        self.frq_total = collections.defaultdict(int)
        self.frq = collections.defaultdict(int)
        self.frq_left = collections.defaultdict(lambda: collections.defaultdict(int))
        self.frq_right = collections.defaultdict(lambda: collections.defaultdict(int))
        logging.info("cal total start")

        with open(file_name, 'r') as file_read:
            for index,line in enumerate(file_read):
                line = line.strip("\n")
                logging.info(index)
                if line:
                    frq_str, left_str, right_str = line.split("\t\t")
                    word, frq_value = frq_str.split(" ")
                    frq_value = int(frq_value)
                    self.frq_total[self.get_word_len(word)] += frq_value
                    self.frq[word] += frq_value
        
        logging.info("cal total end")
        logging.info("cal model start")
        with open(file_name, 'r') as file_read:
            with open(model_name, 'w') as file_write:
                cur_word = ""
                for index,line in enumerate(file_read):
                        line = line.strip("\n")
                        logging.info(line)
                        if line:
                            frq_str, left_str, right_str = line.split("\t\t")
                            word, frq_value = frq_str.split(" ")
                            frq_value = int(frq_value)
                            if cur_word == "":
                                cur_word = word
                            if word != cur_word:
                                frq_value = self.frq[cur_word]
                                ent = self.cal_ent(cur_word)
                                inner = self.cal_inner(cur_word)
                                file_write.write("{0}\t{1}\t{2}\t{3}\n".format(cur_word, frq_value, inner, ent))

                                self.frq_left = collections.defaultdict(lambda: collections.defaultdict(int))
                                self.frq_right = collections.defaultdict(lambda: collections.defaultdict(int))
                                cur_word = word
                        try:

                            for line in left_str.split("\t"):
                                left_word, value = line.split(" ")
                                value = int(value)
                                self.frq_left[word][left_word] += value

                            for line in right_str.split("\t"):
                                right_word, value = line.split(" ")
                                value = int(value)
                                self.frq_right[word][right_word] += value
                        except Exception,e:
                            logging.info(sys.exc_info() )
                            logging.info(e)

        logging.info("cal model end")






                            # with open(file_write_name,'r') as f:
                            #
                            #
                            # for word,value in self.frq.items():
                            # # print word,value
                            # if value >= frq_min:
                            #         inner = self.cal_inner(word)
                            #         ent = self.cal_ent(word)
                            #         self.inner[word] = inner
                            #         self.ent[word] = ent
                            #         self.inner_total[len(word)] += inner
                            #         self.ent_total[len(word)] += ent


    def generate_dicts(self, frq_min=5, inner_min=0.6, ent_min=1):
        for word, value in self.frq.items():
            if value >= frq_min:
                # print word,value
                inner = self.inner[word]
                ent = self.ent[word]
                if inner >= inner_min and ent >= ent_min:
                    self.dicts[word] = value
                    self.inner_total[word] += inner
                    self.ent_total[word] += ent

    def save_dict(self, dict_name):
        with open(dict_name, 'w') as f:
            for word, value in self.dicts.items():
                f.write("{0}\t{1}\n".format(word, value))


    def read_dict(self, dict_name):
        self.dicts = collections.defaultdict(int)
        with open(dict_name, 'r') as f:
            for line in f:
                word, value = line.strip().split()
                if self.encoding:
                    word = word.decode(self.encoding)
                self.dicts[word] = value

    def get_prob(self, word, k, a, b, c):

        frq = float(self.frq[word]) * k
        inner = float(self.inner[word])
        ent = float(self.ent[word])
        # print word,frq,inner,ent,
        if frq <= a or ent <= b or inner <= c:
            all_freq = sum([x for x in self.frq_total.values()])
            prob = -math.log(a * 10. / (all_freq * 10 ** len(word)))
        else:
            frq /= self.frq_total[len(word)]
            # inner /= self.frq_total[len(word)]
            # ent /= self.frq_total[len(word)]
            # prob = -math.log(a * frq + b * inner + c * ent)
            prob = -math.log(frq)

        # print prob
        return prob

    def mp(self, sentence, k, a, b, c):
        words = []
        wait_words = []
        left_index = collections.defaultdict(list)
        len_sentence = len(sentence)
        index = 0
        best_end_index = -1
        for left in range(len(sentence)):
            for right in range(left + 1, min(left + self.window + 1, len_sentence + 1)):
                word_now = "".join(sentence[left:right])
                cost_now = self.get_prob(word_now, k, a, b, c)
                cost_total_now = -1
                best_left_now = -1
                for i in left_index[left]:
                    # print i
                    # print wait_words
                    word, cost, cost_total, best_left = wait_words[i]
                    if cost_total < cost_total_now or cost_total_now == -1:
                        cost_total_now = cost_total
                        best_left_now = i

                if cost_total_now == -1:
                    cost_total_now = cost_now
                else:
                    cost_total_now += cost_now

                left_index[right].append(index)

                wait_words.append([word_now, cost_now, cost_total_now, best_left_now])
                # print index,left,right,word_now,cost_now,cost_total_now,best_left_now
                if right == len_sentence:
                    if best_end_index == -1 or cost_total_now < wait_words[best_end_index][2]:
                        best_end_index = index
                index += 1
        # print best_end_index
        while best_end_index != -1:
            word, cost, total_cost, best_left = wait_words[best_end_index]
            words.insert(0, word)
            best_end_index = best_left
        return words

    def rmm_segment(self, sentence, a=25, b=2.6, c=2.8):
        # if encoding:
        # sentence = sentence.decode(encoding)
        # for right in range(len(sentence),0,-1):
        words = []
        right = len(sentence)
        temp = ""
        while right > 0:
            matched = False
            for left in range(0 if right - self.window < 0 else right - self.window, right - 1, 1):
                word = "".join(sentence[left:right])
                # print left,right,word,self.dicts[word]
                frq = float(self.frq[word])
                inner = float(self.inner[word])
                ent = float(self.ent[word])

                if frq >= a and inner >= b and ent >= c:
                    if len(temp) > 0:
                        words.insert(0, temp)
                        temp = ""
                    words.insert(0, word)
                    right = left
                    matched = True
                    break

            if not matched:
                temp = sentence[right - 1] + temp
                right -= 1

        if len(temp) > 0:
            words.insert(0, temp)
        # print words
        return words


def generate_gram2(file_read, file_write, encoding='utf-8'):
    gram1 = collections.defaultdict(int)
    gram2 = collections.defaultdict(lambda: collections.defaultdict(int))
    segment.read_dict("dict.txt")

    with open(file_read, 'r') as f_read:
        for line in f_read:
            line = line.strip().decode(encoding)
            if line:
                segment_list = segment.rmm_segment(line)
                for index in range(0, len(segment_list) - 1):
                    if index == 0:
                        word1 = "<S>"
                    else:
                        word1 = segment_list[index - 1]
                    word2 = segment_list[index]
                    gram1[word1] += 1
                    gram2[word1][word2] += 1

    with open(file_write, 'w') as f:
        for word in gram2.keys():
            for word2 in gram2[word].keys():
                f.write("{0} {1}\t{2}\n".format(word, word2, gram2[word][word2]))


if __name__ == '__main__':
    # ngram = NGram()
    # ngram.train("data/msr_train.txt")

    # 根据指定参数，生成词典,frq_min为最小词频,inner_min为词语内部结合紧密程度，一般应当大于1，ent_min为左右两侧自由程度，至少应当大于1
    # ngram.generate_dicts("dict.txt",frq_min=6,inner_min=1,ent_min=1.9,encoding='utf-8')

    segment = WordSegment()
    segment.old_train("../data/1.txt")
    segment.save("model.txt")
    # logging.info("train start")
    # segment.train("/home/wangzhe/cikm2014/data/uniq_train.txt", "/home/wangzhe/cikm2014/data/uniq_train_new.txt")
    # logging.info("train end")
    # os.system("sort -t " " -k 1,1 /home/wangzhe/cikm2014/data/uniq_train_new.txt > /home/wangzhe/cikm2014/data/uniq_train_sort.txt")
    # segment.reduce("/home/wangzhe/cikm2014/data/train/count.txt", "/home/wangzhe/cikm2014/data/train/dict_model.txt")

    # segment.save("data/model.txt")
    # logging.info("load start")
    # segment.load("data/model.txt")
    # logging.info("load end")
    # segment.generate_dicts(frq_min=5,inner_min=0.7,ent_min=1)
    # segment.save_dict("data/dict.txt")

    # 读取词典
    # segment.read_dict("data/dict.txt")
    # generate_gram2("C:\Users\Administrator\Desktop\sougou.txt","gram2.txt")
    # for key,value in segment.dicts.items():
    # print key,value
    # with open("data/msr.txt") as f:
    # lines = f.readlines()
    #     for a in range(5,100,10):
    #         for b in range(2,30,2):
    #             b = b*1.0/10
    #             for c in range(2,30,2):
    #                 try:
    #                     c = c * 1.0/10
    #
    #                     right = 0
    #                     false = 0
    #                     logging.info("{0} {1} {2}".format(a,b,c))
    #                     for line in lines:
    #                         line = line.strip()
    #                         if line:
    #                             line = line.decode('utf-8')
    #                             standard = line.split(" ")
    #                             test = list("".join(standard))
    #                             test = segment.rmm_segment(test,a,b,c)
    #                             all = set(standard) & set(test)
    #                             right += len(all)
    #                             false += len(standard)
    #                     prc = right * 1.0 / (right + false) * 100
    #                     logging.info("{0} {1} {2}".format(right,false,prc))
    #
    #                 except Exception:
    #                     pass

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
