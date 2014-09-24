# coding=utf-8
import collections
import maxent.pymaxent as pymaxent
import maxent.cmaxent as cmaxent
import base



class Maxent(base.Base):
    def __init__(self):

        self.m = cmaxent.MaxentModel()
        self.test_dict = collections.defaultdict(list)

    def train(self, feature_file,*argv):
        self.m.begin_add_event()
        with open(feature_file, "r") as f:
            for line in f:
                line = line.strip().split()
                context = line[1:]
                label = line[0]
                self.m.add_event(context, label)


        self.m.end_add_event()
        # self.m.train(150, 'lbfgs', 2.0, 1E-05)
        self.m.train(*argv)

    def save(self,model_name):
        self.m.save(model_name)

    def load(self,model_name):
        self.m.load(model_name)

    def model_predict(self,label,feature):
        return self.m.eval(feature,label)


