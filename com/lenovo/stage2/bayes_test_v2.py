import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB, BernoulliNB, GaussianNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import classification_report
from sklearn.externals import joblib
import datetime
import jieba
import sys
import json

begin = datetime.datetime.now()

try:
    max_len = 500
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

    def doc_dp(s):
        s = [w for w in s if w not in stops]
        s = [w for w in s if w not in re_words]
        return str(s)

    def rank2num(rank):
        if rank == "L":
            return 1
        elif rank == "M":
            return 2
        else:
            return 3

    def some_dp(s):
        return str(s).lower()


    data = pd.read_excel("data/lenovo_dp_data.xlsx")
    data_rank = pd.Series(data['rank']).apply(rank2num)
    data_desc_copy = pd.Series(data['description']).apply(some_dp)
    data_desc = pd.Series(data_desc_copy).apply(jieba.lcut)
    data_it_code = pd.Series(data['itcode'])

    print("数据读取完毕")
    step_0 = datetime.datetime.now()
    print("读取数据总耗时：" + str(step_0 - begin))

    # data_dp = pd.Series(data_desc)
    # data_dp['id'] = data_dp.apply(doc2num)
    # x = np.vstack([np.array(list(data_dp['id']))])

    count_vec = TfidfVectorizer(binary=False, decode_error='ignore', encoding='utf-8', stop_words='english',
                                max_features=30000, ngram_range=(1, 3), min_df=1)

    x = pd.Series(pd.Series(data_desc).apply(doc_dp))
    x = count_vec.fit_transform(x)
    print(x[0:10])
    y = np.array(data_rank)

    # print(x)
    # print(y)

    # x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)
    step_1 = datetime.datetime.now()
    print("数据变换总耗时：" + str(step_1 - step_0))

    # clf = MultinomialNB(alpha=0.5).fit(x_train, y_train)
    clf = MultinomialNB().fit(x, y)
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

    # for i in range(len(y)):
    #     if doc_class_predicted[i] != y[i]:
    #         # print(data_it_code[i]+"\t"+str(y[i])+"\t"+str(doc_class_predicted[i])+"\t\t"+str(prob_1[i])+"\t"+str(prob_2[i])+"\t"+str(prob_3[i]))
    #         print(data_it_code[i])
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
