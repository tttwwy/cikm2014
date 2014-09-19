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
        self.labels = ("VIDEO", "NOVEL", "GAME", "TRAVEL", "VIDEO", "LOTTERY", "OTHER")

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
        result_list = [(label, self.m.eval(feature, label)) for label in self.labels]
        sort_list = sorted(result_list, key=lambda x: x[1], reverse=True)
        if sort_list[0][1] - sort_list[1][1] <= 0.3:
            return sort_list[0][0], sort_list[1][0]
        else:
            return sort_list[0][0]

    def read_test_data(self,file_name):
        # 将测试数据上下文读入内存
        for session in pickup.read_train(file_name):
            for labels, query, title in session:
                if "TEST" in labels:
                    query_str = "".join(query)
                    self.test_dict[query_str].append(session)


    def save_test_data(self,file_name):
        logging.info("saving test data begin")
        with open(file_name,'w') as f:
            marshal.dump(self.test_dict,f)
        logging.info("saving test data end")


    def load_test_data(self,file_name):
        logging.info("loading test data begin")

        with open(file_name,'r') as f:
            self.test_dict = marshal.load(f)
        logging.info("loading test data end")


    def test(self, test_data, test_submit, result):

        logging.info("submit test begin")

        def session_predict(session, query_list):
            for index, (label, query, title) in session:
                if query == query_list:
                    features = pickup.generate_feature(session, index)
                    predict_result = self.predict(features)
                    return predict_result

        with open(test_submit, "r") as f_submit:
            with open(result, "w") as f_result:
                for line in f_submit:
                    query_list = line.strip().split(" ")
                    query_str = "".join(query_list)
                    sessions = self.test_dict[query_str]

                    predict_results = []
                    for session in sessions:
                        predict_results.append(session_predict(session, query_list))

                    predict_result = predict_results[0]
                    predict_result = " | ".join(["CLASS=" + x for x in predict_result])
                    f_result.write("{0} {1}".format(query_str, predict_result))



        logging.info("submit test end")

