import pandas as pd
import numpy as np
import jieba
import datetime
import re


def str_dp(str1, sym):
    return list(str(str1).strip().lower().split(sym))


def str_dp2(str1):
    return jieba.lcut(str(str1).lower().strip())


def cut_short_sentences(data_list):
    sentence_list = []
    for data in data_list:
        if len(data) > 30:
            for s in re.split('。|！|？|；| |>|【|】| |；|：', data):
                if len(s) != 0:
                    sentence_list.append(s)
        else:
            sentence_list.append(data)
    return sentence_list


begin = datetime.datetime.now()
jieba.load_userdict("C:/Users/Administrator/Desktop/aaa.txt")

wd = pd.read_excel("C:/Users/Administrator/Desktop/维度20180109.xlsx", sheetname="Sheet1")
wd_index = wd['d_id']
wd_col_1 = wd['4rank']
wd_col_2 = wd['desc']
wd_col_3 = wd['description']

wd_col_2 = pd.Series(wd_col_2).apply(str_dp, sym=" ")
wd_col_3 = pd.Series(wd_col_3).apply(str_dp, sym=";")

# print(wd_col_2[0:10])
# print(wd_col_3[0:10])

no_re_wd_words = []
for line in wd_col_2:
    for w in line:
        no_re_wd_words.append(w)

for line in wd_col_3:
    for w in line:
        if w != "nan":
            no_re_wd_words.append(w)

no_re_wd_words = set(no_re_wd_words)
# no_re_wd_words.remove("nan")
# print("nan" in no_re_wd_words)

content = np.array(pd.read_excel("C:/Users/Administrator/Desktop/autohome_bbs_2017-08-07.xlsx")['G']).tolist()
content_dp = cut_short_sentences(content)
content_cut = pd.Series(content_dp).apply(str_dp2)
print(len(content_cut))

wd_sim_word = pd.read_excel("C:/Users/Administrator/Desktop/维度20180109.xlsx", sheetname="Sheet2")
# print(wd_sim_word[0:10])

dict_sim_word = {}
for i in range(len(wd_sim_word)):
    value_list = []
    value_list.append(str(wd_sim_word['key'][i]).lower().strip())
    for j in str(wd_sim_word['value'][i]).split(" "):
        if str(j) != "nan":
            value_list.append(str(j).lower().strip())
    dict_sim_word[str(wd_sim_word['key'][i]).lower().strip()] = value_list

# for k, v in dict_sim_word.items():
#     print(str(k) + "\t" + str(v))

step1 = datetime.datetime.now()
print("读取+处理数据用时：" + str(step1 - begin))

result = []
for i in range(len(content_cut)):
    res = {}
    res['desc'] = content_dp[i]
    res['desc_cut'] = content_cut[i]
    res['wd'] = "null"
    if len(set(content_cut[i]) & no_re_wd_words) == 0:
        result.append(res)
        continue
    for j in range(len(wd_col_2)):
        a_round = set(content_cut[i]) & set(wd_col_3[j])
        if len(a_round) > 0:
            res['wd'] = wd_col_1[j]
            res['wd_description'] = str(a_round)
            res['wd_index'] = wd_index[j]
            break

        res_str = ""
        for k in range(len(wd_col_2[j])):
            diff1 = len(res_str)
            count = len(set(dict_sim_word[wd_col_2[j][k]]) & set(content_cut[i]))
            if count == 0:
                break
            res_str += str(set(dict_sim_word[wd_col_2[j][k]]) & set(content_cut[i]))
            diff2 = len(res_str)
            if diff2 <= diff1:
                break

            res['wd'] = wd_col_1[j]
            res['wd_desc'] = res_str
            res['wd_index'] = wd_index[j]
            break

    if i % 10 == 0:
        print(i)
    result.append(res)

step2 = datetime.datetime.now()
print("匹配维度用时：" + str(step2 - step1))

result_df = pd.DataFrame(result)
# print(result_df)
result_df.to_excel("C:/Users/Administrator/Desktop/result_0109.xlsx")
stop = datetime.datetime.now()
print("写入excel用时" + str(stop - step2))
print("总共用时" + str(stop - begin))
