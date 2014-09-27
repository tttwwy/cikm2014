__author__ = 'Administrator'
# coding=utf-8
import sys

for line in sys.stdin:
    try:
        line = line.strip("\n")
        if line:
            label, query, title = line.split("\t")
            print "{0}\t{1]".format(label,0)
    except Exception,e:
        pass









