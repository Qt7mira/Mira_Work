import pandas as pd
import numpy as np

lenovo_data = pd.read_csv("C:/Users/Administrator/Desktop/qz2_f10.csv")

print(lenovo_data['target'].value_counts())
print(type(lenovo_data['target']))
features = lenovo_data.columns[1:15]
X = np.array(lenovo_data[features])
Y = lenovo_data['target']

from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

print("开始聚类")
from sklearn.cluster import KMeans

clf_k = KMeans(n_clusters=12)
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
# print(np.mean(clf_k.labels_ == Y-1))
