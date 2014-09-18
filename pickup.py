__author__ = 'Administrator'
#coding=utf-8
label = ("VIDEO","NOVEL","GAME","TRAVEL","VIDEO","LOTTERY","OTHER")
def pickup(file_name_read,file_name_save):
    with open(file_name_read,"r") as file_read:
        with open(file_name_save,"r") as file_write:
            for line in file_read:
                line = line.strip()
                session
                if line:
                    label,query,title = line.split("\t")
                    labels = label.split(" | ")
                    for label in labels:
                        label = label[6:]
                    query = query.split(" ")
                    title = title.split(" ")
                    if "UNKNOWN" not in labels and "TEST" not in labels:
                        for label in labels:
                            file_write.write("{0} {1}".format(label,))

