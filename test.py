__author__ = 'Administrator'
import sqlite3
class A():
    a = "dd"
    def __init__(self):
        print self.a

class B(A):
    pass

a = B()