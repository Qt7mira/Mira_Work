from __future__ import division
import numpy as np
import pandas as pd
import jieba
import keras
from keras.models import model_from_json
import keras.models


pos = pd.read_excel('data/pos.xls', header=None)
pos['label'] = 1
neg = pd.read_excel('data/neg.xls', header=None)
neg['label'] = 0
all_ = pos.append(neg, ignore_index=True)
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
print('gou jian wan cheng')


def doc2num(s, maxlen):
    s = [i for i in s if i in word_set]
    s = s[:maxlen] + ['']*max(0, maxlen-len(s))
    return list(abc[s])


def predict_one(s):  # 单个句子的预测函数
    s = np.array(doc2num(list(jieba.cut(s)), maxlen))
    s = s.reshape((1, s.shape[0]))
    return model.predict_classes(s, verbose=0)[0][0]


json_string = '{"keras_version": "2.0.5", "class_name": "Sequential", "backend": "tensorflow", "config": [{"class_name": "Embedding", "config": {"activity_regularizer": null, "dtype": "int32", "trainable": true, "embeddings_constraint": null, "output_dim": 256, "embeddings_initializer": {"class_name": "RandomUniform", "config": {"minval": -0.05, "maxval": 0.05, "seed": null}}, "embeddings_regularizer": null, "input_dim": 6111, "batch_input_shape": [null, 50], "mask_zero": false, "name": "embedding_1", "input_length": 50}}, {"class_name": "LSTM", "config": {"activity_regularizer": null, "trainable": true, "recurrent_regularizer": null, "units": 128, "use_bias": true, "bias_constraint": null, "recurrent_activation": "hard_sigmoid", "kernel_constraint": null, "recurrent_dropout": 0.0, "unit_forget_bias": true, "activation": "tanh", "recurrent_initializer": {"class_name": "Orthogonal", "config": {"seed": null, "gain": 1.0}}, "dropout": 0.0, "stateful": false, "go_backwards": false, "bias_regularizer": null, "implementation": 0, "unroll": false, "kernel_regularizer": null, "return_state": false, "kernel_initializer": {"class_name": "VarianceScaling", "config": {"scale": 1.0, "seed": null, "mode": "fan_avg", "distribution": "uniform"}}, "bias_initializer": {"class_name": "Zeros", "config": {}}, "return_sequences": false, "recurrent_constraint": null, "name": "lstm_1"}}, {"class_name": "Dropout", "config": {"rate": 0.5, "name": "dropout_1", "trainable": true}}, {"class_name": "Dense", "config": {"activation": "linear", "trainable": true, "activity_regularizer": null, "units": 1, "bias_regularizer": null, "use_bias": true, "kernel_regularizer": null, "kernel_initializer": {"class_name": "VarianceScaling", "config": {"scale": 1.0, "seed": null, "mode": "fan_avg", "distribution": "uniform"}}, "kernel_constraint": null, "bias_constraint": null, "name": "dense_1", "bias_initializer": {"class_name": "Zeros", "config": {}}}}, {"class_name": "Activation", "config": {"activation": "sigmoid", "name": "activation_1", "trainable": true}}]}'
model = model_from_json(json_string)
# from keras.models import Sequential
# model = Sequential()
model.load_weights('my_model_weights.h5')

idx = np.arange(len(all_))
np.random.shuffle(idx)
doc = all_.loc[idx][500:1500]

# doc['words'] = doc[0].apply(lambda s: list(jieba.cut(s)))
# doc['doc2num'] = doc['words'].apply(lambda s: doc2num(s, maxlen))

predict = []
for line in pos[0]:
    pred = predict_one(line)
    predict.append(pred)

y = []
for i in pos['label']:
    y.append(i)

print(y)
print(predict)


def calc(list1, list2):
    num1 = len(y)
    list3 = []
    for i in range(0, num1):
        if list1[i] == list2[i]:
            list3.append(1)
    return len(list3)/num1


# print(keras.metrics.binary_accuracy(y, predict))
print(calc(y, predict))
