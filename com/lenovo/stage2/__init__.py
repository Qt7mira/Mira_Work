import pymysql
import jieba
from collections import Counter


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


def save_data2file(path, list):
    file_object = open(path, 'w', encoding='utf-8')
    for k, v in Counter(list).items():
        file_object.write(str(k) + "\t" + str(v))
        file_object.write('\n')
    file_object.close()


list_L = read_from_mysql("incident_L")
list_M = read_from_mysql("incident_M")
list_H = read_from_mysql("incident_H")

save_data2file("'incident_L.txt'", list_L)
save_data2file("'incident_M.txt'", list_M)
save_data2file("'incident_H.txt'", list_H)
