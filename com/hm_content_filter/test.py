import jieba
import json

# stop_words = []
# with open('data/stop_words.txt', 'r', encoding='utf-8') as f:
#     for line in f:
#         stop_words.append(line.strip())
# stop_words.append(' ')
# stop_words.append('\n')
#
#
# doc = '国网宝鸡供电公司：“零距离”真情服务赢赞誉政企在线 三秦都市报 - 三秦网  2017-05-16 15:2438.6K'
# jieba.load_userdict('data/dic.txt')
#
# l = list(jieba.cut(doc))
# l = [word for word in l if word not in stop_words]
# print(l)
#
# a = [[0]]
# print(a[0][0])

# a = [1, 2, 3, [4, 5]]
# b = [3, 4]
# print(set(a))
# print(len(set(a) & set(b)))
# print((set(a) & set(b)))

# try:
#     a = 6 / 0
# except Exception as e:
#     ret = '{"type": "error", "error_msg": "%s"}' % e
#     print(ret)

# a = "\"Android lll\""
# if a.__contains__("\""):
#     b = a[1:len(a)-1]
# print(b)
# print(a.replace('\\', '"'))

# import re
# ddd = []
# a = str('bailongma "哪个 牌子"')
# s = re.findall('"(.+?)"', a)
# s_real = str(s)[2: len(str(s))-2]
# print(s_real)
# s2 = a.replace('"'+s_real+'"', '')
# print(s2)
# ddd.append(s_real)
# ddd.append(s2)
# ddd.append(s2)
# ddd.append(s_real)
#
# d = set(ddd)
#
# print('dddddddddd')
# for i in d:
#     print(i)


s = '{"title": "带你深度剖析雅思写作范文"}'
# print(type(s))
# a = bytes(s.encode())
# print(type(a.decode()))
# print(a.decode())
# b = json.loads(a.decode())
# print(type(b))
# print(b)

b = json.loads(s)

print(b)
# ddd.append(str(s)[2:len(s)-3])
# i1 = a.index('"')
# if i1 == 0:
#     i2 = a[i1 + 1:len(a)].index('"')
#     a1 = a[0:i1].strip()
#     a2 = a[i2 + 2:len(a)].strip()
#     a_final = a1 + a2
# else:
#     a_final = a[0:i1].strip()
# ddd.append(a_final)
#
# print(len(ddd))
# for i in ddd:
#     print(i)
#     print('ffasfa')
# import numpy as np
#
# all_ = np.arange(100)
# idx = np.arange(100)
# np.random.shuffle(idx)
# print(idx)
# all_ = all_.loc[idx]
import jieba

str = "我和住在农村的亨利一起在羊路边,遇到了放学MBG-CCI的杰克,听他讲了七千二百四十八个强盗的故事。下载速度16MB/s"
# jieba.load_userdict("data/dic_test.txt")
# jieba.add_word("ylo", freq=10000)
jieba.load_userdict("data/dic_test111.txt")
a = list(jieba.cut(str))
print(a)

