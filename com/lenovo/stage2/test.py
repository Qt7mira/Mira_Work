from pymongo import MongoClient
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import classification_report
from sklearn.externals import joblib
import datetime
import jieba
import sys
import pymysql
import json

begin = datetime.datetime.now()

try:
    data_rank = []
    data_desc = []
    data_it_code = []
    stops = []
    max_len = 200

    file = open('data/stops.txt', 'r', encoding='utf8')
    for line in file.readlines():
        stops.append(line.replace('\n', ''))

    file = open('data/word2id_lenovo.json', 'r')
    for line in file.readlines():
        word2id = json.loads(line)

    def doc2num(s):
        s = [w for w in s if w not in stops]
        s = [word2id.get(i, 0) for i in s[:max_len]]
        return s + [0] * (max_len - len(s))


    def rank2num(rank):
        if rank == "L":
            return 1
        elif rank == "M":
            return 2
        else:
            return 3

    print(word2id)

    conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='lenovo_ml_test',
                           charset='utf8')
    cur = conn.cursor()
    cur.execute('select a.itcode, b.rank, a.description from ml_incident a join bz b ON a.itcode = b.itcode limit 10')
    results = cur.fetchall()
    for row in results:
        data_it_code.append(row[0])
        data_rank.append(rank2num(row[1]))
        data_desc.append(jieba.lcut(str(row[2]).lower()))
    cur.close()

    print("数据读取完毕")
    step_0 = datetime.datetime.now()
    print("读取数据总耗时：" + str(step_0 - begin))

    data_dp = pd.Series(data_desc)
    data_dp['id'] = data_dp.apply(doc2num)
    x = np.vstack([np.array(list(data_dp['id']))])
    y = np.array(data_rank)

    for i in range(5):
        print(data_desc[i])
        print(x[i])

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(str(e) + "   " + str(exc_tb.tb_lineno))
