__author__ = 'Administrator'
# coding=utf-8
import sys

import pickup
import maxent


feature_file = "data/feature.txt"
pickup.generate_feature_file(sys.argv[1], feature_file)
# classify(sys.argv[1],sys.argv[2],sys.argv[3])
maxent = maxent.Maxent()
maxent.Maxent()
maxent.train(feature_file)
maxent.test(sys.argv[2], sys.argv[3], sys.argv[4])