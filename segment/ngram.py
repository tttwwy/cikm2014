__author__ = 'Administrator'
# coding=utf-8
import collections
import math
# import dill as pickle
import pickle
import sys
import logging
reload(sys)
sys.setdefaultencoding("utf-8")
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

    def save(self,model_name):

        with open(model_name + "1",'w') as f:
            pickle.dump(self.frq,f)
        with open(model_name + "2",'w') as f:
            pickle.dump(self.frq_left,f)
        with open(model_name + "3",'w') as f:
            pickle.dump(self.frq_right,f)

    def load(self,model_name):
        with open(model_name + "1",'r') as f:
            self.frq = pickle.load(f)
        with open(model_name + "2",'r') as f:
            self.frq_left = pickle.load(f)
        with open(model_name + "3",'r') as f:
            self.frq_right = pickle.load(f)

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
                    # print sentence,cur_word,left_word,right_word

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


    def cal_edge(self,word):
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

    def train(self,file_name):
        with open(file_name,'r') as f:
            for index,line in enumerate(f):
                line = line.strip("\n").decode('utf-8')
                if line:
                    self.count(line)

    def get_dicts(self,file_name,frq_min=10,inner_min=1,ent_min=1.9):
        for word,value in self.frq.items():
            if value > frq_min:
                inner = self.cal_inner(word)
                ent = self.cal_edge(word)
                if inner >= inner_min and ent >=  ent_min:
                    logging.info("{0} {1} {2} {3} {4}".format(word,value,inner,left_edge,right_edge))
if __name__ == '__main__':

    ngram = NGram()
    print ngram.splits("ab")
    ngram.train("C:\Users\Administrator\Desktop\\sougou.txt")

    ngram.get_dicts()