__author__ = 'Administrator'
# coding=utf-8
# label = ("VIDEO", "NOVEL", "GAME", "TRAVEL", "VIDEO", "LOTTERY", "OTHER")
import sys


def read_train(file_name_read):
    with open(file_name_read, "r") as file_read:
        session = []
        for index,line in enumerate(file_read):
            print index
            if line and line != "\n":
                # print line
                label, query, title = line.split("\t")
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
    return features


def generate_feature_file(base_file, feature_file):
    with open(feature_file, "w") as f:
        for session in read_train(base_file):
            for index, (labels, query, title) in enumerate(session):
                if "UNKNOWN" not in labels and "TEST" not in labels:
                    features = generate_feature(session, index)
                    for label in labels:
                        f.write("{0} {1}\n".format(label, " ".join(features)))


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


if sys.platform == "win32":
    generate_feature("test.txt", "features.txt")
    classify("test.txt","train.txt","test_file.txt")
else:
    generate_feature(sys.argv[1], sys.argv[2])
    classify(sys.argv[1],sys.argv[2],sys.argv[3])



