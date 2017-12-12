import pymysql
import jieba
from collections import Counter

list_L = []
list_M = []
list_H = []
conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='lenovo_ml_test')
cur = conn.cursor()
cur.execute("SELECT t.description from incident_L t ")
results = cur.fetchall()
for row in results:
    list_L.extend(jieba.lcut(str(row).lower()))
cur.close()

cur = conn.cursor()
cur.execute("SELECT t.description from incident_M t ")
results = cur.fetchall()
for row in results:
    list_M.extend(jieba.lcut(str(row).lower()))
cur.close()

cur = conn.cursor()
cur.execute("SELECT t.description from incident_H t ")
results = cur.fetchall()
for row in results:
    list_H.extend(jieba.lcut(str(row).lower()))
cur.close()
conn.close()

file_object = open('incident_L.txt', 'w', encoding='utf-8')
for k, v in Counter(list_L).items():
    file_object.write(str(k) + "\t" + str(v))
    file_object.write('\n')
file_object.close()

file_object = open('incident_M.txt', 'w', encoding='utf-8')
for k, v in Counter(list_M).items():
    file_object.write(str(k) + "\t" + str(v))
    file_object.write('\n')
file_object.close()

file_object = open('incident_H.txt', 'w', encoding='utf-8')
for k, v in Counter(list_H).items():
    file_object.write(str(k) + "\t" + str(v))
    file_object.write('\n')
file_object.close()
