__author__ = 'Administrator'
# coding=utf-8
import collections
import math
import cPickle
class Ngram():

    window = 4
    edge_window = 1
    frq = collections.defaultdict(int)
    frq_left = collections.defaultdict(lambda :collections.defaultdict(int))
    frq_right = collections.defaultdict(lambda :collections.defaultdict(int))

    def count(self,sentence):
        for length in range(self.window):
            for index,word in enumerate(sentence):
                cur_word = sentence[index:index + length + 1]
                self.frq[cur_word] += 1
                left_word = sentence[index - self.edge_window:index]
                right_word = sentence[index + 1:index + self.edge_window + 1]
                if left_word:
                    self.frq_left[cur_word][left_word] += 1
                if right_word:
                    self.frq_right[cur_word][right_word] += 1

    def cal_inner(self,word):
        try:
            max_inner = max([self.frq[left] * self.frq[right] for left,right in self.splits(word)])
            return float(self.frq[word])/max_inner
        except:
            return 0

    def cal_edge(self,word):
        try:
            frq = self.frq[word]
            left_ent = sum([-math.log10(float(value)/frq) for key,value in self.frq_left[word].items()])
            right_ent = sum([-math.log10(float(value)/frq) for key,value in self.frq_right[word].items()])
            return min(left_ent,right_ent)
        except Exception,ex:
            return 0

    def splits(self,text):
        return [(text[:i+1], text[i+1:]) for i in range(min(len(text), self.window))]

    def read(self,file_name):
        with open(file_name,'r') as f:
            for index,line in enumerate(f):
                line = line.strip("\n").decode('utf-8')
                if line:
                    print index
                    if index == 1000:
                        break
                    self.count(line)

    def find(self):
        for word,value in self.frq.items():
            # print word,value
            result = []
            if value > 0 and self.cal_edge(word) >=    0 and self.cal_inner(word) > 0:
                result.append((word,value))
                print word,value

            result = sorted(result,key=lambda x:x[1],reverse=True)
            for word,value in result:
                print word,value

ngram = Ngram()
ngram.read("C:\Users\Administrator\Desktop\sougou.txt")
with open('model.txt','w') as f:
    cPickle.dump(ngram,f)

with open('model.txt','r') as f:
    ngram = cPickle.load(f)
ngram.find()