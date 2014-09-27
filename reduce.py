__author__ = 'Administrator'
# coding=utf-8
import sys

for line in sys.stdin:
    line = line.strip("\n")
    cur_word = ""
    count = 0
    if line:
        if line == cur_word or cur_word == "":
            count += 1
        else:
            print "{0}\t{1}".format(cur_word, count)
            cur_word = line
            count = 1











