__author__ = 'Administrator'
# coding=utf-8
import sys
import collections
import time
import logging
from segment import wordsegment

if sys.platform == "win32":
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logging.basicConfig(level=log_level,
                    format='%(asctime)s %(message)s',
                    datefmt='%m-%d %H:%M:%S', )


class Base():
    lables = ("ZIPCODE", "NOVEL", "GAME", "TRAVEL", "VIDEO", "LOTTERY", "OTHER",
              "GAME|LOTTERY",
              "GAME|NOVEL",
              "GAME|TRAVEL",
              "GAME|VIDEO",
              "NOVEL|VIDEO",
              "VIDEO|LOTTERY",
              "VIDEO|TRAVEL",
              "ZIPCODE|TRAVEL")
    segment = wordsegment.WordSegment()
    # segment.read_dict("segment/data/dict.txt")

    def run_time(func):
        def new_func(*args, **args2):
            start = time.clock()
            logging.info("{0}:start".format(func.__name__))
            back = func(*args, **args2)
            end = time.clock()
            logging.info("{0}:end".format(func.__name__))
            logging.info("running time {0}".format(end - start))
            return back

        return new_func


    # noinspection PyArgumentList
    @run_time
    def word_segment(self, sentence):
        return Base.segment.rmm_segment(sentence, 200, 2.6, 2.8)

    @run_time
    def train_dict(self, *args):
        Base.segment.train(*args)

    @run_time
    def save_dict(self, *args):
        Base.segment.save(*args)

    @run_time
    def load_dict(self, *args):
        Base.segment.load(*args)

    @run_time
    def train(self, feature_file, *args):
        pass

    def save(self, model_name):
        pass

    def load(self, model_name):
        pass

    def model_predict(self, label, feature):
        pass

    def read_train_file(self, file_name):
        with open(file_name, "r") as file_read:
            session = []
            for line_num, line in enumerate(file_read):
                if line and line != "\n":
                    label, query, title = line.strip("\n").split("\t")
                    labels = label.split(" | ")
                    for index, label in enumerate(labels):
                        labels[index] = label[6:]

                    query = query.split(" ")

                    title = title.split(" ")
                    if "-" in title:
                        title = []
                    if (labels, query, title) not in session:
                        session.append((labels, query, title))
                else:
                    if session:
                        yield session
                    session = []


    # @run_time
    # def classify(self,file_name,train_name,test_name):
    # with open(file_name, "r") as file_read:
    # with open(train_name,"w") as file_train:
    # with open(test_name,"w") as file_test:
    # session = []
    # type = 0
    # for index,line in enumerate(file_read):
    # print index
    # if line != "\n" and line:
    # if line.find("TEST") >= 0:
    # type = 1
    # session.append(line)
    # else:
    # if type == 1:
    # file_write = file_test
    # else:
    # file_write = file_train
    # for line in session:
    # file_write.write(line)
    # if session:
    # file_write.write("\n")
    # type = 0
    # session = []
    @run_time
    def generate_full_train_file(self, train_file, save_file):
        dict = {}
        logging.info("read train file start")
        index = 0
        for session in self.read_train_file(train_file):
            logging.info(index)
            index += 1
            for labels, query, title in session:
                query_str = " ".join(query)
                if query_str in dict:
                    if session not in dict[query_str]:
                        dict[query_str].append(session)
                else:
                    dict[query_str] = [session]
        logging.info("read train file end")
        logging.info("saving file start")
        index = 0
        with open(save_file, 'w') as f_write:
            for query_str in dict.keys():
                logging.info("save:{1}".format(index))
                index += 1
                str = "{0}\t{1}\t{2}\n".format("CLASS=SUBMIT",query_str, "-")

                for session in dict[query_str]:
                    for labels, query, title in session:
                        label_str = "|".join(["CLASS=" + x for x in labels])
                        str += "{0}\t{1}\t{2}\n".format(label_str, " ".join(query), " ".join(title))
                    str += "\n"
                f_write.write(str)
        logging.info("saving file end")


    @run_time
    def generate_full_test_file(self, test_file, test_submit_file, result):
        dict = {}
        index = 0
        logging.info("reading test start")
        for session in self.read_train_file(test_file):
            logging.info(index)
            index += 1
            for labels, query, title in session:
                if "TEST" in labels:
                    query_str = "".join(query)
                    if query_str in dict:
                        if session not in dict[query_str]:
                        # if session != dict[query_str][-1]:
                            dict[query_str].append(session)
                    else:
                        dict[query_str] = [session]
        logging.info("reading test end")

        logging.info("saving test start")

        with open(test_submit_file, "r") as f:
            index = 0
            with open(result, "w") as f_write:
                for line in f:
                    logging.debug("reading test:{0}".format(index))

                    query_list = line.strip().split(" ")
                    query_str = "".join(query_list)
                    sessions = dict[query_str]

                    str = "{0}\t{1}\t{2}\n".format("CLASS=SUBMIT", " ".join(query_list), "-")
                    for session in sessions:
                        for labels, query, title in session:
                            label_str = "|".join(["CLASS=" + x for x in labels])
                            str += "{0}\t{1}\t{2}\n".format(label_str, " ".join(query), " ".join(title))
                        str += "\n"
                    f_write.write(str)
                    index += 1
                    logging.info("save:{1}".format(index))

    @run_time
    def generate_feature_file(self, base_file, feature_file):
        with open(feature_file, "w") as f:
            for session in self.read_train_file(base_file):
                for index, (labels, query, title) in enumerate(session):
                    if "UNKNOWN" not in labels and "TEST" not in labels:
                        features = self.generate_feature(session, index)
                        label_str = "|".join(labels)
                        if label_str not in Base.labels:
                            label_str = "|".join(reversed(labels))
                        f.write("{0} {1}\n".format(label_str, " ".join(features)))

    @run_time
    def read_test(self, file_name):
        with open(file_name, "r") as f:
            test_query_list = []
            sessions = []
            session = []
            for line in f:
                if line != "":
                    if line != "\n":
                        labels, query, title = line.strip("\n").split("\t")
                        labels = labels.split(" | ")
                        for index, label in enumerate(labels):
                            labels[index] = label[6:]
                        query_list = query.split(" ")
                        title = title.split(" ")
                        if "SUBMIT" in labels:
                            if test_query_list:
                                yield test_query_list, sessions
                            test_query_list = query_list
                            sessions = []
                            session = []
                        else:
                            session.append([labels, query_list, title])
                    else:
                        sessions.append(session)
                        session = []
            yield test_query_list, sessions


    @run_time
    def save_predict_file(self, test_file_name, result_file_name):
        with open(result_file_name, 'w') as f:
            for index, (query, sessions) in enumerate(self.read_test(test_file_name)):
                logging.info("{0}:{1}".format(index, query))
                predict_result = self.sessions_predict(query, sessions)
                predict_str = " | ".join(["CLASS=" + x for x in predict_result])
                logging.debug("{0}:{1}".format(index, predict_str))
                f.write("{0}\t{1}\n".format(" ".join(query), predict_str))

    def model_predict(self, label, feature):
        pass

    def generate_feature(self, session, i):
        features = []
        labels, query, title = session[i]
        query_segment = self.word_segment(query)
        title_segment = self.word_segment(title)

        for word in query_segment:
            features.append(word)
        for index in range(len(query_segment)):
            features.append("".join(query_segment[index:index + 2]))

        for word in title_segment:
            features.append("title" + word)
        for index in range(len(title_segment)):
            features.append("title" + "".join(title_segment[index:index + 2]))

        for word in query:
            features.append(word)
        for index in range(len(query)):
            features.append("".join(query[index:index + 2]))

        for word in title:
            features.append("title" + word)
        for index in range(len(title)):
            features.append("title" + "".join(title[index:index + 2]))
        return list(set(features))

    def feature_predict(self, feature):
        result_list = [(label.split("|"), self.model_predict(label, feature)) for label in Base.lables]
        sort_list = sorted(result_list, key=lambda x: x[1], reverse=True)
        return sort_list[0]

    def session_predict(self, query_list, session):
        predict_result = []
        for index, (labels, query, title) in enumerate(session):
            if query == query_list:
                features = self.generate_feature(session, index)
                predict_result = self.feature_predict(features)
            if "UNKNOWN" not in labels and "TEST" not in labels:
                predict_result = (labels, 1.0)

        return predict_result

    def sessions_predict(self, query_list, sessions):
        logging.debug("test:{0}\nsessions:{1}\n".format(query_list, sessions))

        predict_results = []
        for session in sessions:
            predict_results.append(self.session_predict(query_list, session))

        logging.debug("predict:{0}\nsessions:{1}\n".format(query_list, predict_results))

        result = sorted(predict_results, key=lambda x: x[1], reverse=True)
        predict_result = result[0][0]

        return predict_result


if __name__ == '__main__':
    pass
    # generate_feature_file("data/test.txt", "features.txt")
    # generate_full_test_file("data/test.txt","data/submit.txt","data/result.txt")
    # for session in read_test("data/result.txt"):
    # print session



