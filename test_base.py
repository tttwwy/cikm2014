from unittest import TestCase
import base
__author__ = 'Administrator'




class TestBase(TestCase):
    def test_generate_full_test_file(self):
        test = base.Base()
        test.generate_full_test_file("data/1.txt","data/2.txt","data/result.txt")
