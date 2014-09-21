# coding=utf-8
import collections
# import maxent.pymaxent as pymaxent
#
# import maxent.cmaxent as cmaxent
import pickup
import logging
import cPickle
# import marshal
import nltk

class Maxent():
    def __init__(self):
        nltk.config_megam('/home/wangzhe/tool/ml/MEGAM/megam-64.opt')

    @pickup.run_time
    def train(self, feature_file):
        features = []
        with open(feature_file, "r") as f:
            for line in f:
                line = line.strip().split()
                context = line[1:]
                context_dict = {}
                for index,item in enumerate(context):
                    context_dict[item] = 1
                label = line[0]
                features.append((context_dict,label))
        self.m = nltk.maxent.MaxentClassifier.train(features,algorithm='MEGAM',trace=0,gaussian_prior_sigma=4.0)

    def save(self,model_name):
        with open(model_name,'w') as f:
            cPickle.dump(self.m,f)

    def load(self,model_name):
        with open(model_name,'r') as f:
            self.m = cPickle.load(f)

    def predict(self, feature):
        label = self.m.classify(feature)
        pro = self.m.prob_classify(feature).prob(label)
        return ((label,),pro)



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

        result = sorted(predict_results,lambda x:x[1],reverse=True)
        predict_result = result[0][0]


        # dict = self.test_dict = collections.defaultdict(int)
        # for predict_result in predict_results:
        #     dict["|".join(predict_result[0])] += 1
        # dict = sorted(dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        # predict_result = dict[0][0].split("|")
        # logging.info("sorted:{0}\nsessions:{1}\n".format(query_list, dict))

        # logging.debug("predict_result:{0}".format(predict_result))

        return predict_result
