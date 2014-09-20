__author__ = 'Administrator'
# coding=utf-8
# label = ("VIDEO", "NOVEL", "GAME", "TRAVEL", "VIDEO", "LOTTERY", "OTHER")
import sys
import collections
import time
import logging
if sys.platform == "win32":
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logging.basicConfig(level=log_level,
                    format='%(asctime)s %(message)s',
                    datefmt='%m-%d %H:%M:%S',)


def run_time(func):
    def newFunc(*args, **args2):
        start = time.clock()
        logging.info("{0}:start".format(func.__name__))
        back = func(*args, **args2)
        end = time.clock()
        logging.info("{0}:end".format(func.__name__))
        logging.info("running time {0}".format(end-start))
        return back
    return newFunc


def read_train(file_name):
    with open(file_name, "r") as file_read:
        session = []
        for index,line in enumerate(file_read):
            # print index
            if line and line != "\n":
                # print line
                label, query, title = line.strip("\n").split("\t")
                # print query
                labels = label.split(" | ")
                for index, label in enumerate(labels):
                    labels[index] = label[6:]

                query = query.split(" ")

                title = title.split(" ")
                if "-" in title:
                    title = []
                session.append([labels, query, title])
            else:
                if session:
                    yield session
                session = []


def generate_feature(session, i):
    features = []
    labels, query, title = session[i]
    for word in query:
        features.append(word)
    for index in range(len(query)):
        features.append("".join(query[index:index + 2]))
    for word in title:
        features.append(word)
    for index in range(len(title)):
        features.append("".join(title[index:index + 2]))
    # print features
    return features

@run_time
def generate_feature_file(base_file, feature_file):
    with open(feature_file, "w") as f:
        for session in read_train(base_file):
            for index, (labels, query, title) in enumerate(session):
                if "UNKNOWN" not in labels and "TEST" not in labels:
                    features = generate_feature(session, index)
                    for label in labels:
                        f.write("{0} {1}\n".format(label, " ".join(features)))

@run_time
def classify(file_name,train_name,test_name):
    with open(file_name, "r") as file_read:
        with open(train_name,"w") as file_train:
            with open(test_name,"w") as file_test:
                session = []
                type = 0
                for index,line in enumerate(file_read):
                    print index
                    if line != "\n" and line:
                        if line.find("TEST") >= 0:
                            type = 1
                        session.append(line)
                    else:
                        if type == 1:
                            file_write = file_test
                        else:
                            file_write = file_train
                        for line in session:
                            file_write.write(line)
                        if session:
                            file_write.write("\n")
                        type = 0
                        session = []

@run_time
def generate_full_test_file(test_file,test_submit_file,result):
    dict = {}
    logging.info("reading test start")
    for session in read_train(test_file):
        for labels, query, title in session:
            if "TEST" in labels:
                query_str = "".join(query)
                if dict.has_key(query_str):
                    if session != dict[query_str][-1]:
                        dict[query_str].append(session)
                else:
                    dict[query_str] = [session]
    logging.info("reading test end")

    logging.info("saving test start")


    with open(test_submit_file,"r") as f:
        index = 0
        with open(result,"w") as f_write:
            for line in f:
                logging.info("reading test:{0}".format(index))

                query_list = line.strip().split(" ")
                query_str = "".join(query_list)
                sessions = dict[query_str]

                str = "{0}\t{1}\t{2}\n".format("CLASS=SUBMIT"," ".join(query_list),"-")
                for session in sessions:
                    for labels,query,title in session:
                        # print "labels:",labels
                        label_str = "|".join(["CLASS="+ x  for x in labels])
                        # print label_str
                        str += "{0}\t{1}\t{2}\n".format(label_str," ".join(query)," ".join(title) )
                    str += "\n"
                f_write.write(str)
                index += 1

@run_time
def read_test(file_name):
    with open(file_name,"r") as f:
        test_query_list = []
        sessions = []
        session = []
        for line in f:

            if line:
                if line != "\n":
                    labels,query,title = line.strip("\n").split("\t")
                    labels = labels.split(" | ")
                    for index,label in enumerate(labels):
                        labels[index] = label[6:]
                    query_list = query.split(" ")
                    title = title.split(" ")
                    if "SUBMIT" in labels:
                        if test_query_list:
                            yield test_query_list,sessions
                            test_query_list = []
                            sessions = []
                            session = []
                        else:
                            test_query_list = query_list
                            sessions = []
                            session = []
                    else:
                        session.append([labels,query_list,title])
                else:
                    sessions.append(session)
                    session = []
            else:
                yield test_query_list,sessions



            # query_list,sessions = marshal.loads(line)
            # yield query_list,sessions


@run_time
def test_file(newtest_name,result_name,model):
    with open(result_name,'w') as f:
        for index,(query,sessions) in enumerate(read_test(newtest_name)):
            logging.debug("{0}:{1}".format(index,query))
            predict_result = model.test(query,sessions)
            predict_str = " | ".join(["CLASS=" + x for x in predict_result])
            logging.debug("{0}:{1}".format(index,predict_str))

            f.write("{0} {1}\n".format(" ".join(query), predict_str))

if sys.platform == "win32":
    # generate_feature_file("data/test.txt", "features.txt")
    generate_full_test_file("data/test.txt","data/submit.txt","data/result.txt")
    for session in read_test("data/result.txt"):
        print session
    # classify("test.txt","train.txt","test_file.txt")
# else:
#     generate_feature(sys.argv[1], sys.argv[2])
#     classify(sys.argv[1],sys.argv[2],sys.argv[3])



