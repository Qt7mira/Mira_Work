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
    data_desc_copy = []
    data_it_code = []
    max_len = 200

    jieba.load_userdict("data/tb_dictionary.txt")

    def read_file_data2list(path):
        list = []
        file = open(path, 'r', encoding='utf8')
        for line in file.readlines():
            list.append(line.replace('\n', ''))
        return list


    stops = read_file_data2list('data/stops.txt')
    re_words = read_file_data2list('data/re.txt')

    file = open('data/word2id_lenovo.json', 'r')
    for line in file.readlines():
        word2id = json.loads(line)

    def doc2num(s):
        s = [w for w in s if w not in stops]
        s = [w for w in s if w not in re_words]
        s = [word2id.get(i, 0) for i in s[:max_len]]
        return s + [0] * (max_len - len(s))


    def rank2num(rank):
        if rank == "L":
            return 1
        elif rank == "M":
            return 2
        else:
            return 3

    conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='lenovo_ml_test',
                           charset='utf8')
    cur = conn.cursor()
    cur.execute('select a.itcode, b.rank, a.description from ml_incident a join bz b ON a.itcode = b.itcode')
    results = cur.fetchall()
    for row in results:
        data_it_code.append(row[0])
        data_rank.append(rank2num(row[1]))
        data_desc.append(jieba.lcut(str(row[2]).lower()))
        data_desc_copy.append(row[2])
    cur.close()

    print("数据读取完毕")
    step_0 = datetime.datetime.now()
    print("读取数据总耗时：" + str(step_0 - begin))

    data_dp = pd.Series(data_desc)
    data_dp['id'] = data_dp.apply(doc2num)
    x = np.vstack([np.array(list(data_dp['id']))])
    y = np.array(data_rank)

    # print(x)
    # print(y)
    # for i in range(5):
    #     print(x[i])

    # x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)
    step_1 = datetime.datetime.now()
    print("数据变换总耗时：" + str(step_1 - step_0))

    # clf = MultinomialNB(alpha=0.5).fit(x_train, y_train)
    clf = MultinomialNB(alpha=1.0).fit(x, y)
    doc_class_predicted = clf.predict(x)

    # prob = clf.predict_proba(x)
    # prob_1 = clf.predict_proba(x)[:, 0]
    # prob_2 = clf.predict_proba(x)[:, 1]
    # prob_3 = clf.predict_proba(x)[:, 2]
    # for i in range(len(prob)):
    #     print(prob[i])

    print("---------------------------------------------------------------")
    print(np.mean(doc_class_predicted == y))
    print("---------------------------------------------------------------")

    for i in range(len(y)):
        if doc_class_predicted[i] != y[i]:
            # print(data_it_code[i]+"\t"+str(y[i])+"\t"+str(doc_class_predicted[i])+"\t\t"+str(prob_1[i])+"\t"+str(prob_2[i])+"\t"+str(prob_3[i]))
            print(data_it_code[i])
    # print("-----------------------------------------------------------")
    # for i in range(len(doc_class_predicted)):
    #     print(doc_class_predicted[i])

    # 准确率与召回率
    # precision, recall, thresholds = precision_recall_curve(y_test, clf.predict(x_test))
    # answer = clf.predict_proba(x_test)[:, 1]
    # report = answer > 0.5
    # print(classification_report(y_test, report, target_names=['ad', 'new']))

    # joblib.dump(clf, "bayes_model.m")

    step_final = datetime.datetime.now()
    print("训练模型总耗时：" + str(step_final - step_1))
    print("总耗时：" + str(step_final - begin))
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(str(e) + "   " + str(exc_tb.tb_lineno))
