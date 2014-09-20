# coding=utf-8
__author__ = 'Administrator'
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

# with open("data/sougou.txt","r") as f:
#     with open("data/sougounew.txt","w") as f_write:
#         for line in f:
#             line = line.strip().decode('utf-8')
#             word_list = list(line)
#             str = " ".join(word_list)
#             f_write.write(str + "\n")

def separate_file(file_name,result_name):
    with open(file_name, "r") as file_read:
        with open(result_name,"w") as file_write:
            for line in file_read:
                line = line.strip("\n")
                if line:
                    label, query, title = line.split("\t")
                    file_write.write(query + "\n")
                    if len(title) > 2:
                        file_write.write(title + "\n")