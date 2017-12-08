from __future__ import division
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, ShuffleSplit


lenovo_data = pd.read_csv("C:/Users/Administrator/Desktop/qz2_f10.csv")

# lenovo_data['is_train'] = np.random.uniform(0, 1, len(lenovo_data)) <= .75
# train, test = lenovo_data[lenovo_data['is_train'] == True], lenovo_data[lenovo_data['is_train'] == False]
#
# features = lenovo_data.columns[1:14]
# y, _ = pd.factorize(train['target'])
#
# clf = RandomForestClassifier(n_jobs=2)
# clf.fit(train[features], y)
#
# preds = lenovo_data.target[clf.predict(test[features])]
# print(preds[0:len(preds)])

print(lenovo_data['target'].value_counts())
print(type(lenovo_data['target']))
features = lenovo_data.columns[1:15]
X = np.array(lenovo_data[features])
print(type(X))
Y = lenovo_data['target']
print(X[0:5])
# print(Y[0:10])

from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

clf = RandomForestClassifier(n_estimators=100)
clf.fit(x_train, y_train)

print("cross_val_score得分：")
acy = cross_val_score(clf, x_train, y_train)
print(acy.mean())

print("每个特征的影响力:")
print(clf.feature_importances_)

print("test验证结果")
answer = clf.predict(x_test)
# print(x_test)
print(answer)
print(y_test)
print(np.mean(answer == y_test))


print("开始聚类")
from sklearn.cluster import KMeans

clf_k = KMeans(n_clusters=3)
s = clf_k.fit(X)
print(s)
print(clf_k.cluster_centers_)

# 每个样本所属的簇
label = []
print(clf_k.labels_)
i = 1
while i <= len(clf_k.labels_):
    # print(i, clf_k.labels_[i - 1])
    label.append(clf_k.labels_[i - 1])
    i = i + 1

# 用来评估簇的个数是否合适，距离越小说明簇分的越好，选取临界点的簇个数  958.137281791
print("评估簇的个数:")
print(pd.Series(clf_k.labels_).value_counts())
print(clf_k.inertia_)
print(np.mean(clf_k.labels_ == Y-1))

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

pca = PCA(n_components=3)  # 输出两维
newData = pca.fit_transform(X)  # 载入N维
print(newData)
print(type(newData))

Y_1 = np.ones(Y.shape)

plt.figure(figsize=(8, 8), dpi=80)
plt.subplot(211)
plt.plot(newData, Y_1, 'or')
# plt.show()


from mpl_toolkits.mplot3d import Axes3D

x, y, z = newData[:, 0], newData[:, 1], newData[:, 2]
ax = plt.subplot(212, projection='3d')

ax.scatter(x[:100], y[:100], z[:100], c='b')
ax.scatter(x[100:400], y[100:400], z[100:400], c='r')
ax.scatter(x[400:], y[400:], z[400:], c='g')

ax.set_zlabel('Z')
ax.set_ylabel('Y')
ax.set_xlabel('X')
plt.show()

# from sklearn.metrics import precision_recall_curve
# from sklearn.metrics import classification_report
# print("准确率与召回率")
# precision, recall, thresholds = precision_recall_curve(y_train, clf.predict(x_train))
# answer = clf.predict_proba(X)[:, 1]
# print(classification_report(Y, answer, target_names=['thin', 'fat']))


# scores = []
# for i in range(X.shape[1]):
#     score = cross_val_score(clf, X[:, i:i + 1],
#                             Y,
#                             scoring="r2",
#                             cv=ShuffleSplit(len(X), 3, .3))
#     scores.append((round(np.mean(score), 3), i))
# print(sorted(scores, reverse=True))


