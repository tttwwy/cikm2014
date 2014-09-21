__author__ = 'Administrator'
# coding=utf-8
import collections

class NGram():

    def __init__(self):
        self.window = 4
        self.edge_window = 1
        self.frq = collections.defaultdict(int)
        self.frq_left = collections.defaultdict(collections.defaultdict(int))
        self.frq_right = collections.defaultdict(collections.defaultdict(int))

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

