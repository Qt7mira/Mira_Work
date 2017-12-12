import pymysql
import jieba

list_L = []
list_M = []
list_H = []
jieba.load_userdict("data/tb_dictionary.txt")
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

list_L = set(list_L)
list_M = set(list_M)
list_H = set(list_H)

re = set([w for w in list_L if w in list_M and w in list_H])

file_object = open('data/re.txt', 'w', encoding='utf-8')
for w in re:
    file_object.write(str(w))
    file_object.write('\n')
file_object.close()
