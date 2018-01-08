import pandas as pd
import numpy as np
import jieba
import datetime


def str_dp(str1):
    return list(str(str1).strip().split(' '))


def str_dp2(str1):
    return jieba.lcut(str(str1).strip())

begin = datetime.datetime.now()
jieba.load_userdict("C:/Users/Administrator/Desktop/aaa.txt")

wd = pd.read_excel("C:/Users/Administrator/Desktop/汽车维度整理20180105.xlsx", sheetname="Sheet2")
wd_col_1 = wd['4rank']
wd_col_2 = wd['desc']

content = pd.read_excel("C:/Users/Administrator/Desktop/autohome_bbs_2017-08-07.xlsx")['G']

print(content[0:10])
print(wd_col_2[0:10])
content_cut = pd.Series(content).apply(str_dp2)
wd_col_2 = pd.Series(wd_col_2).apply(str_dp)
print(len(content_cut))
print(content_cut[0])
print(wd_col_2[0])

step1 = datetime.datetime.now()
print("读取+处理数据用时：" + str(step1-begin))

no_re_wd_words = []
for line in wd_col_2:
    for w in line:
        no_re_wd_words.append(w)
no_re_wd_words = set(no_re_wd_words)

result = []
for i in range(len(content_cut)):
    res = {}
    res['desc'] = content[i]
    res['desc_cut'] = content_cut[i]
    res['wd'] = "null"
    res['wd_desc'] = "null"
    res['wd_index'] = "null"
    if len(set(content_cut[i]) & no_re_wd_words) == 0:
        continue
    for j in range(len(wd_col_2)):
        aaa = set(content_cut[i]) & set(wd_col_2[j])
        if len(aaa) == len(set(wd_col_2[j])):
            res['wd'] = wd_col_1[j]
            res['wd_desc'] = wd_col_2[j]
            res['wd_index'] = j
            break
    if i % 100 == 0:
        print(i)
    result.append(res)

result_df = pd.DataFrame(result)
result_df.to_excel("C:/Users/Administrator/Desktop/result_2.xlsx")
stop = datetime.datetime.now()
print("匹配维度用时" + str(stop-step1))
print("总共用时" + str(stop-begin))
