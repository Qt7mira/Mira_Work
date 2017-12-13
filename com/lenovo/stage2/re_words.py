"""
找到三个分类中相同的词，存储为重复词表 re_words
"""
import pymysql
import jieba

jieba.load_userdict("data/tb_dictionary.txt")


def read_from_mysql(table_name):
    list = []
    conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='lenovo_ml_test')
    cur = conn.cursor()
    cur.execute("SELECT t.description from " + table_name + " t ")
    results = cur.fetchall()
    for row in results:
        list.extend(jieba.lcut(str(row).lower()))
    cur.close()
    conn.close()
    return list


list_L = set(read_from_mysql("incident_L"))
list_M = set(read_from_mysql("incident_M"))
list_H = set(read_from_mysql("incident_H"))

re = set([w for w in list_L if w in list_M and w in list_H])

file_object = open('data/re.txt', 'w', encoding='utf-8')
for w in re:
    file_object.write(str(w))
    file_object.write('\n')
file_object.close()
