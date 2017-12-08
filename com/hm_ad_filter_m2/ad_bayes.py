from pymongo import MongoClient
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import classification_report
from sklearn.externals import joblib
import datetime
import jieba
import sys

begin = datetime.datetime.now()
conn = MongoClient('mongodb://root:hm20130707_soften@101.251.237.244', 27017)

db_new = conn.linshi
db_ad = conn.linshi
new_set = db_new.bbb
ad_set = db_ad.deldata

try:
    x = []
    y = []
    for i in new_set.find({}, {'title': '1', 'txt': 1, '_id': 0}).limit(10):
        tit_con = ""
        for key, value in i.items():
            if value is None:
                tit_con += ""
            else:
                tit_con += value
        x.append(str(list(jieba.cut(tit_con))))
        y.append(1)
    print("新闻数据读取完毕")
    step_0 = datetime.datetime.now()
    print("读取新闻数据总耗时：" + str(step_0 - begin))

    count = 0
    try:
        for i in ad_set.find({}, {'title': '1', 'txt': 1, '_id': 0}).limit(10):
            tit_con = ""
            count += 1
            for key, value in i.items():
                if value is None:
                    tit_con += ""
                else:
                    tit_con += value
            x.append(str(list(jieba.cut(tit_con))))
            y.append(0)
    except Exception as e:
        print(e)
        print(count)

    print("广告数据读取完毕")
    step_1 = datetime.datetime.now()
    print("读取广告数据总耗时：" + str(step_1 - step_0))

    x = pd.Series(x)
    y = pd.Series(y)
    print(len(x))

    # BOOL型特征下的向量空间模型，注意，测试样本调用的是transform接口
    count_vec = TfidfVectorizer(binary=False, decode_error='ignore', encoding='utf-8', stop_words='english', max_features=1000000, ngram_range=(1, 3), min_df=1)

    # K = 10
    # for i in range(K):
    #     size = len(x)/K
    #     x = count_vec.fit_transform(x[i*size: (i+1)*size])
    #     eval(x)

    # 加载数据集，切分数据集80%训练，20%测试
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

    # xxx = x_train[0:10]
    # print(xxx)
    # print(y_train[0:10])

    x_train = count_vec.fit_transform(x_train.values.astype('U'))
    x_test = count_vec.transform(x_test.values.astype('U'))
    print(x_train.shape)
    print(x_test.shape)

    step_2 = datetime.datetime.now()
    print("数据变换总耗时：" + str(step_2 - step_1))

    # 调用MultinomialNB分类器
    # clf = MultinomialNB(alpha=0.5).fit(x_train, y_train)
    clf = MultinomialNB().fit(x_train, y_train)
    doc_class_predicted = clf.predict(x_test)

    # print(doc_class_predicted)
    # print(y)
    print(np.mean(doc_class_predicted == y_test))

    # 准确率与召回率
    precision, recall, thresholds = precision_recall_curve(y_test, clf.predict(x_test))
    answer = clf.predict_proba(x_test)[:, 1]
    report = answer > 0.5
    print(classification_report(y_test, report, target_names=['ad', 'new']))

    # print(clf.predict_proba(count_vec.transform(xxx.values.astype('U'))))
    # print(clf.predict(count_vec.transform(xxx.values.astype('U'))))

    joblib.dump(clf, "bayes_model.m")
    joblib.dump(count, "tf_idf_model.m")

    step_final = datetime.datetime.now()
    print("训练模型总耗时：" + str(step_final - step_2))
    print("总耗时：" + str(step_final - begin))
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(str(e) + "   " + str(exc_tb.tb_lineno))
