__author__ = 'Administrator'
# coding=utf-8
import sys

cur_word = ""
num = 0
for line in sys.stdin:
    line = line.strip("\n")
    if line:
        if cur_word == "":
            cur_word = line
        if cur_word == line:
            num = num + 1
        else:
            print "{0} {1}".format(cur_word, num)
            num = 1
            cur_word = line












