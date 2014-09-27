__author__ = 'Administrator'
# coding=utf-8
import sys

for line in sys.stdin:
    line = line.strip("\n")
    if line:
        label, query, title = line.split("\t")
        print label









