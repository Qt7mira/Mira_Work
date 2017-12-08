import pymysql
import numpy as np
import pandas as pd
from sklearn import tree
from sklearn.externals import joblib


def score2num(score):
    if score is None:
        return 0
    else:
        return int(score)


def dom2num(dom):
    if str(dom).__contains__('长春') or str(dom) is None:
        return 0
    elif str(dom).__contains__('吉林'):
        return 1
    elif str(dom).__contains__('辽宁') or str(dom).__contains__('黑龙江') or str(dom).__contains__('东北'):
        return 2
    else:
        return 3

conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='api_fast_mira_1')
cur = conn.cursor()
cur.execute("SELECT t.dom, t.conratio, t.score FROM a_profile_v3 t ")

results = cur.fetchall()
X = []
Y = []

for row in results:
    record = {}
    record['dom'] = dom2num(row[0])
    record['conratio'] = float(row[1])
    record['score'] = score2num(row[2])
    X.append(record)
    if record['conratio'] >= 1:
        Y.append(0)
    else:
        Y.append(1)

cur.close()
conn.close()

X = np.array(pd.DataFrame(X))
Y = np.array(pd.DataFrame(Y))
# print(X)
# print(Y)
print(X.shape)
print(Y.shape)

clf = tree.DecisionTreeClassifier(criterion='entropy')
print(clf)
clf.fit(X, Y)

# with open("tree.dot", 'w') as f:
#     f = tree.export_graphviz(clf, out_file=f)

joblib.dump(clf, "test_model.m")

print(clf.feature_importances_)


