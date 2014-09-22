# coding=utf-8
import collections
import maxent.pymaxent as pymaxent

import maxent.cmaxent as cmaxent
import pickup
import logging
import cPickle
import marshal


class Maxent():
    def __init__(self):

        self.m = cmaxent.MaxentModel()
        self.test_dict = collections.defaultdict(list)
        self.labels = ("ZIPCODE", "NOVEL", "GAME", "TRAVEL", "VIDEO", "LOTTERY", "OTHER",
"GAME|NOVEL",
"GAME|TRAVEL",
"GAME|VIDEO",
"NOVEL|VIDEO",
"VIDEO|LOTTERY",
"VIDEO|TRAVEL",
"ZIPCODE|TRAVEL")

    @pickup.run_time
    def train(self, feature_file):
        self.m.begin_add_event()
        with open(feature_file, "r") as f:
            for line in f:
                line = line.strip().split()
                context = line[1:]
                label = line[0]
                self.m.add_event(context, label)

        self.m.end_add_event()
        self.m.train(150, 'lbfgs', 2.0, 1E-05)

    def save(self,model_name):
        self.m.save(model_name)

    def load(self,model_name):
        self.m.load(model_name)
        
    def predict(self, feature):

        result_list = [(label.split("|"), self.m.eval(feature, label)) for label in self.labels]
        sort_list = sorted(result_list, key=lambda x: x[1], reverse=True)
        # sort_list[0][0].split("|")
        return sort_list[0]

        # if sort_list[0][1] - sort_list[1][1] <= 0.15 and sort_list[0][0] + sort_list[1][0] in double:
        #     return ((sort_list[0][0], sort_list[1][0]), min(sort_list[0][1], sort_list[1][1]))
        # else:
        #     return sort_list[0]


    def session_predict(self, query_list, session):
        predict_result = []
        for index, (labels, query, title) in enumerate(session):
            if query == query_list:
                features = pickup.generate_feature(session, index)
                predict_result = self.predict(features)
            if "UNKNOWN" not in labels and "TEST" not in labels:
                predict_result = (labels, 1.0)

        return predict_result


    def test(self, query_list, sessions):
        logging.debug("test:{0}\nsessions:{1}\n".format(query_list, sessions))

        predict_results = []
        for session in sessions:
            predict_results.append(self.session_predict(query_list, session))

        logging.info("predict:{0}\nsessions:{1}\n".format(query_list, predict_results))

        result = sorted(predict_results,key=lambda x:x[1],reverse=True )
        predict_result = result[0][0]


        # dict = self.test_dict = collections.defaultdict(int)
        # for predict_result in predict_results:
        #     dict["|".join(predict_result[0])] += 1
        # dict = sorted(dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        # predict_result = dict[0][0].split("|")
        # logging.info("sorted:{0}\nsessions:{1}\n".format(query_list, dict))
        #
        # logging.debug("predict_result:{0}".format(predict_result))

        return predict_result
