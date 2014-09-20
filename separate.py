# coding=utf-8
__author__ = 'Administrator'
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

with open("data/sougou.txt","r") as f:
    with open("data/sougounew.txt","w") as f_write:
        for line in f:
            line = line.strip().decode('utf-8')
            word_list = list(line)
            str = " ".join(word_list)
            f_write.write(str + "\n")

