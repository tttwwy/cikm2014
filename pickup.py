__author__ = 'Administrator'
# coding=utf-8
# label = ("VIDEO", "NOVEL", "GAME", "TRAVEL", "VIDEO", "LOTTERY", "OTHER")
import sys


def read_train(file_name_read):
    with open(file_name_read, "r") as file_read:
        session = []
        for line in file_read:
            line = line.strip()
            if line:
                label, query, title = line.split("\t")
                labels = label.split(" | ")
                for index,label in enumerate(labels):
                    labels[index] = label[6:]
                query = query.split(" ")
                title = title.split(" ")
                session.append([labels,query,title])
            else:
                yield session
                session = []
        yield session


def generate_feature(base_file,feature_file):
    with open(feature_file,"w") as f:
        for session in read_train(base_file):
            features = []
            for index,(labels,query,title) in enumerate(session):
                if "UNKNOWN" not in labels and "TEST" not in labels:
                    for word in query:
                        features.append(word)
                    for index in enumerate(query):
                        features.append("".join(query[index:index+2]))
                    for word in title:
                        features.append(word)
                    for index in enumerate(title):
                        features.append("".join(title[index:index+2]))

                    for label in labels:
                        f.write("{0} {1}\n".format(label," ".join(features)))



generate_feature(sys.argv[1],sys.argv[2])

