from pymongo import MongoClient
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
import datetime
import jieba
import sys
import gc

begin = datetime.datetime.now()
conn = MongoClient('mongodb://root:hm20130707_soften@101.251.237.244', 27017)

db_new = conn.linshi
db_ad = conn.linshi
new_set = db_new.bbb
ad_set = db_ad.deldata

count_vec = joblib.load("tf_idf_model.m")
clf = joblib.load("bayes_model.m")

try:
    for skip_num in range(2, 7):
        per_begin = datetime.datetime.now()
        x = []
        y = []
        for i in new_set.find({}, {'title': '1', 'txt': 1, '_id': 0}).skip(skip_num * 10000).limit(10000):
            tit_con = ""
            for key, value in i.items():
                if value is None:
                    tit_con += ""
                else:
                    tit_con += value
            x.append(str(list(jieba.cut(tit_con))))
            y.append(0)
        step_0 = datetime.datetime.now()
        print("第" + str(skip_num - 2) + "轮读取新闻数据总耗时：" + str(step_0 - per_begin))

        for i in ad_set.find({}, {'title': '1', 'txt': 1, '_id': 0}).skip(skip_num * 10000).limit(10000):
            tit_con = ""
            for key, value in i.items():
                if value is None:
                    tit_con += ""
                else:
                    tit_con += value
            x.append(str(list(jieba.cut(tit_con))))
            y.append(1)
        step_1 = datetime.datetime.now()
        print("第" + str(skip_num - 2) + "轮读取广告数据总耗时：" + str(step_1 - step_0))

        x = pd.Series(x)
        y = pd.Series(y)
        print(len(x))

        x = count_vec.transform(x.values.astype('U'))
        step_2 = datetime.datetime.now()
        print("第" + str(skip_num - 2) + "轮数据变换总耗时：" + str(step_2 - step_1))

        clf = MultinomialNB().partial_fit(x, y)

        del x, y
        gc.collect()

        step_3 = datetime.datetime.now()
        print("第" + str(skip_num - 2) + "轮训练模型总耗时：" + str(step_3 - per_begin))
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(str(e) + "   " + str(exc_tb.tb_lineno))
joblib.dump(clf, "bayes_model_final.m")
step_final = datetime.datetime.now()
print("总耗时：" + str(step_final - begin))
