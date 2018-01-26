import pandas as pd
import numpy as np
from keras.models import load_model
import jieba
import datetime
import re
import json


class DimFinder(object):

    def __init__(self):

        def str_dp(str1, sym):
            return list(str(str1).strip().lower().split(sym))

        begin = datetime.datetime.now()
        self.model = load_model('C:/Users/Administrator/Desktop/model1/model_180122.h5')
        jieba.load_userdict("C:/Users/Administrator/Desktop/aaa.txt")

        file = open('C:/Users/Administrator/Desktop/word2id.json', 'r')
        for line in file.readlines():
            self.word2id = json.loads(line)
        self.max_len = 30

        wd = pd.read_excel("C:/Users/Administrator/Desktop/维度20180118.xlsx", sheetname="Sheet1")
        self.wd_index = wd['d_id']
        self.wd_col_1 = wd['4rank']
        wd_col_2 = wd['desc']
        wd_col_3 = wd['description']

        self.wd_col_2 = pd.Series(wd_col_2).apply(str_dp, sym=" ")
        self.wd_col_3 = pd.Series(wd_col_3).apply(str_dp, sym=";")

        self.dim_type = wd['dim_type']
        self.dim_father = wd['dim_father']
        self.weight = wd['weight']

        no_re_wd_words = []
        for line in self.wd_col_2:
            for w in line:
                no_re_wd_words.append(w)

        for line in self.wd_col_3:
            for w in line:
                if w != "nan":
                    no_re_wd_words.append(w)

        self.no_re_wd_words = set(no_re_wd_words)

        self.wd_sim_word = pd.read_excel("C:/Users/Administrator/Desktop/维度20180118.xlsx", sheetname="Sheet2")

        self.dict_sim_word = {}

        for i in range(len(self.wd_sim_word)):
            value_list = []
            value_list.append(str(self.wd_sim_word['key'][i]).lower().strip())
            for j in str(self.wd_sim_word['value'][i]).split(" "):
                if str(j) != "nan":
                    value_list.append(str(j).lower().strip())
            self.dict_sim_word[str(self.wd_sim_word['key'][i]).lower().strip()] = value_list

        self.dict_all_keys = [k for k, v in self.dict_sim_word.items()]
        # for k, v in self.dict_sim_word.items():
        #     print(str(k) + "\t" + str(v))

        step1 = datetime.datetime.now()
        print("拉取维度数据用时：" + str(step1 - begin))

    def find_dim(self, comment_list):

        def doc2num(s):
            s = [self.word2id.get(i, 0) for i in s[:self.max_len]]
            return s + [0] * (self.max_len - len(s))

        def str_dp2(str1):
            return jieba.lcut(str(str1).lower().strip())

        def append_mo_gai(l, d):
            if len(l) == 0:
                l.append(d)
                return l
            s = [i['dim_desc'] for i in l]
            s1 = d['dim_desc']
            res = []
            for i in range(len(s) - 1, -1, -1):
                if str(s1).__contains__(str(s[i])) and len(s1) > len(s[i]):
                    res.append(i)

            if len(res) > 0:
                for i in res:
                    l.remove(l[i])
                l.append(d)
                return l

            for i in range(len(s) - 1, -1, -1):
                if str(s[i]).__contains__(str(s1)) and len(s[i]) > len(s1):
                    return l

            l.append(d)
            return l

        def lstm_predict(sentence):
            X = doc2num(sentence)
            X = np.vstack([np.array(list(X))])
            y = self.model.predict(X)
            lstm_predict_result = []
            for i in range(len(y)):
                uniques, ids = np.unique(y[i], return_index=True)
                for j in range(len(uniques)):
                    if uniques[j] > 0.4:
                        lstm_predict_result.append(ids[j]+128)
            return lstm_predict_result

        begin = datetime.datetime.now()

        content_cut = [str_dp2(line) for line in comment_list]
        print(len(content_cut))
        print(content_cut)

        result = []
        for i in range(len(content_cut)):
            sentence_result = []
            if len(set(content_cut[i]) & self.no_re_wd_words) == 0:
                res = {}
                res['content'] = comment_list[i]
                res['content_cut'] = content_cut[i]
                res['dim'] = ""
                res['dim_desc'] = ""
                res['dim_index'] = ""
                res['dim_father'] = ""
                res['dim_type'] = ""
                res['weight'] = ""
                append_mo_gai(sentence_result, res)
                result.append(sentence_result)
                continue
            for j in range(len(self.wd_col_2)):
                a_round = set(content_cut[i]) & set(self.wd_col_3[j])
                if len(a_round) > 0:
                    res = {}
                    res['content'] = comment_list[i]
                    res['content_cut'] = content_cut[i]
                    res['dim'] = self.wd_col_1[j]
                    res['dim_desc'] = str(a_round)[2:len(a_round)-3]
                    res['dim_index'] = self.wd_index[j]
                    res['dim_father'] = self.dim_father[j]
                    res['dim_type'] = self.dim_type[j]
                    res['weight'] = self.weight[j]
                    append_mo_gai(sentence_result, res)
                    continue

                res_str = ""
                count = 0
                for k in range(len(self.wd_col_2[j])):
                    if self.wd_col_2[j][k] in self.dict_all_keys:
                        if len(set(self.dict_sim_word[self.wd_col_2[j][k]]) & set(content_cut[i])) != 0:
                            count += 1
                            mid_str = str(set(self.dict_sim_word[self.wd_col_2[j][k]]) & set(content_cut[i]))
                            res_str += mid_str[2: len(mid_str) - 2] + ","

                if count == len(self.wd_col_2[j]):
                    res = {}
                    res['content'] = comment_list[i]
                    res['content_cut'] = content_cut[i]
                    res['dim'] = self.wd_col_1[j]
                    res['dim_desc'] = res_str[0: len(res_str) - 1]
                    res['dim_index'] = self.wd_index[j]
                    res['dim_father'] = self.dim_father[j]
                    res['dim_type'] = self.dim_type[j]
                    res['weight'] = self.weight[j]
                    append_mo_gai(sentence_result, res)
            if len(sentence_result) == 0:
                res = {}
                res['content'] = comment_list[i]
                res['content_cut'] = content_cut[i]
                res['dim'] = ""
                res['dim_desc'] = ""
                res['dim_index'] = ""
                res['dim_father'] = ""
                res['dim_type'] = ""
                res['weight'] = ""
                sentence_result.append(res)

            rule_index = [i['dim_index'] for i in sentence_result]
            lstm_index = lstm_predict(content_cut[i])
            nn_more_than_rule = [i for i in lstm_index if i not in rule_index]
            # print(nn_more_than_rule)
            if len(nn_more_than_rule) != 0:
                for n in nn_more_than_rule:
                    if n != 128:
                        res = {}
                        res['content'] = comment_list[i]
                        res['content_cut'] = content_cut[i]
                        res['dim'] = self.wd_col_1[n - 129]
                        res['dim_desc'] = ""
                        res['dim_index'] = n
                        res['dim_father'] = self.dim_father[n - 129]
                        res['dim_type'] = self.dim_type[n - 129]
                        res['weight'] = self.weight[n - 129]
                        sentence_result.append(res)
            result.append(sentence_result)

        stop = datetime.datetime.now()
        print("匹配维度用时：" + str(stop - begin))
        return result

aaa = DimFinder()


def cut_short_sentences(every_str):
    sentence_list = []
    for s in re.split('。|！|？|；| |>|【|】| |;|：|，|,', every_str):
        if len(s) != 0:
            sentence_list.append(s)
    return sentence_list

text = ['座椅的通风不行', '这个车座椅按钮的做工真不错', '空调的制冷效果非常的好']
bbb = aaa.find_dim(text)
print(bbb)
