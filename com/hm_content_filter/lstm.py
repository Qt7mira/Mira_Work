# -*- coding:utf-8 -*-

import numpy as np
import pandas as pd
import jieba

pos = pd.read_excel('data/pos.xls', header=None)
pos['label'] = 1
neg = pd.read_excel('data/neg.xls', header=None)
neg['label'] = 0
all_ = pos[1000:3000].append(neg, ignore_index=True)
all_['words'] = all_[0].apply(lambda s: list(jieba.cut(s))) #调用结巴分词

maxlen = 50  # 截断词数
min_count = 5  # 出现次数少于该值的词扔掉。这是最简单的降维方法

content = []
for i in all_['words']:
    content.extend(i)


abc = pd.Series(content).value_counts()
abc = abc[abc >= min_count]
abc[:] = range(1, len(abc)+1)
abc[''] = 0  # 添加空字符串用来补全
word_set = set(abc.index)


def doc2num(s, maxlen):
    s = [i for i in s if i in word_set]
    s = s[:maxlen] + ['']*max(0, maxlen-len(s))
    return list(abc[s])

all_['doc2num'] = all_['words'].apply(lambda s: doc2num(s, maxlen))
print(all_['doc2num'][10])

#手动打乱数据
idx = np.arange(len(all_))
np.random.shuffle(idx)
all_ = all_.loc[idx]

# 按keras的输入要求来生成数据
x = np.array(list(all_['doc2num']))
y = np.array(list(all_['label']))
y = y.reshape((-1, 1))  # 调整标签形状


from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Embedding
from keras.layers import LSTM

#建立模型
model = Sequential()
model.add(Embedding(len(abc), 256, input_length=maxlen))
model.add(LSTM(128))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

batch_size = 128
train_num = 3000

model.fit(x[:train_num], y[:train_num], batch_size=batch_size, nb_epoch=20)
score = model.evaluate(x[train_num:], y[train_num:], batch_size=batch_size)


def predict_one(s):  # 单个句子的预测函数
    s = np.array(doc2num(list(jieba.cut(s)), maxlen))
    s = s.reshape((1, s.shape[0]))
    return model.predict_classes(s, verbose=0)[0][0]

print('**********valid score************')
print(score)
print('**********save model************')
json_string = model.to_json()
print(json_string)
model.save_weights('my_model_weights_1.h5')