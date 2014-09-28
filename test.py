__author__ = 'Administrator'
import MySQLdb
db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root", db="cikm", port=3306)
cursor = db.cursor()

def get(type,word):
    types = {"frq":1,"left":2,"right":3}
    key1 = types[type]
    key2 = word[0]
    sql = "select value from kv where key1 = {0} and key2 = '{1}'".format(key1,key2)
    print sql
    cursor.execute(sql)
    data = cursor.fetchall()
    return data



def update(type,*word):
    types = {"frq":1,"left":2,"right":3}
    print word
    key1 = types[type]
    key2 = word[0]
    key3 = ""
    if len(word) == 2:
        key3 = word[1]

    sql = "insert into kv (key1,key2,key3,value)values ({0},'{1}','{2}',1) on DUPLICATE key update value = value + 1".format(key1,key2,key3)
    print sql
    cursor.execute(sql)



update("left","a","b")
print get("left",".*")