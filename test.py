__author__ = 'Administrator'


class A():
    a = "dd"

    def __init__(self):
        print self.a


class B(A):
    pass


a = B()