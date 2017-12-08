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

begin = datetime.datetime.now()
conn = MongoClient('mongodb://root:hm20130707_soften@101.251.237.244', 27017)

db_new = conn.linshi
db_ad = conn.linshi
new_set = db_new.bbb
ad_set = db_ad.deldata


x = []
y = []
for i in new_set.find({}, {'title': '1', 'txt': 1, '_id': 0}).limit(1):
    tit_con = ""
    for key, value in i.items():
        tit_con += value + ""
    x.append(tit_con)
    y.append(1)
print("新闻数据读取完毕")
step_0 = datetime.datetime.now()
print("读取新闻数据总耗时：" + str(step_0 - begin))


print("TF-IDF模型加载中。。。")
count_vec = joblib.load("model/tfidf_model.m")
print("TF-IDF模型加载完成。")

print("Bayes模型加载中。。。")
clf = joblib.load("model/bayes_model.m")
print("Bayes模型加载完成。")

x = pd.Series(x)
y = pd.Series(y)

x_train = count_vec.transform(x.values.astype('U'))
print(x_train.shape)
print(clf.predict(x_train))
