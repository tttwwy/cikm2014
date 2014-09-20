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
        self.labels = ("ZIPCODE","NOVEL", "GAME", "TRAVEL", "VIDEO", "LOTTERY", "OTHER")

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
        self.m.train(150, 'lbfgs', 4, 1E-05)
        self.m.save("data/model.txt")

    def predict(self, feature):
        double = ("GAMELOTTERY",
                    "GAMENOVEL",
                    "GAMETRAVEL",
                    "GAMEVIDEO",
                    "NOVELGAME",
                    "NOVELVIDEO",
                    "VIDEOGAME",
                    "VIDEOLOTTERY",
                    "VIDEONOVEL",
                    "VIDEOTRAVEL",
                    "ZIPCODETRAVEL",
                    "LOTTERYGAME",
                    "NOVELGAME",
                    "TRAVELGAME",
                    "VIDEOGAME",
                    "GAMENOVEL",
                    "VIDEONOVEL",
                    "GAMEVIDEO",
                    "LOTTERYVIDEO",
                    "NOVELVIDEO",
                    "TRAVELVIDEO",
                    "TRAVELZIPCODE",)
        result_list = [((label,), self.m.eval(feature, label)) for label in self.labels]
        sort_list = sorted(result_list, key=lambda x: x[1], reverse=True)
        if sort_list[0][1] - sort_list[1][1] <= 0.15 and sort_list[0][0] + sort_list[1][0] in double:
            return ((sort_list[0][0],sort_list[1][0]), max(sort_list[0][1],sort_list[1][1]))
        else:
            return sort_list[0]


    def session_predict(self,query_list,session):
        predict_result = []
        for index, (label, query, title) in enumerate(session):
            if query == query_list:
                features = pickup.generate_feature(session, index)
                predict_result = self.predict(features)
            if label != "UNKNOWN" and label != "TEST":
               predict_result = (label,1.0)

        return predict_result


    def test(self,query_list,sessions):
        logging.debug("test:{0}\nsessions:{1}\n".format(query_list,sessions))

        predict_results = []
        for session in sessions:
            predict_results.append(self.session_predict(query_list,session))

        sorted(predict_results,key=lambda x:x[1],reverse=True)
        predict_result = predict_results[0][0]
        logging.debug("predict_result:{0}".format(predict_result))

        return predict_result
