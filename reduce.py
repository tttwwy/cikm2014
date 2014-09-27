__author__ = 'Administrator'
# coding=utf-8
import sys

cur_word = ""
num = 0
for line in sys.stdin:
    try:
        line = line.strip("\n")
        if line:
            word,value = line.split("\t")
            if cur_word == "":
                cur_word = word
            if cur_word == word:
                num = num + 1
            else:
                print "{0} {1}".format(cur_word, num)
                num = 1
                cur_word = word
    except Exception,e:
        pass












