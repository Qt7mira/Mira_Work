import pandas as pd
import numpy as np
import jieba
import datetime
import re


class DimFinder(object):

    def __init__(self):

        def str_dp(str1, sym):
            return list(str(str1).strip().lower().split(sym))

        begin = datetime.datetime.now()
        jieba.load_userdict("C:/Users/Administrator/Desktop/aaa.txt")
        wd = pd.read_excel("C:/Users/Administrator/Desktop/维度20180109.xlsx", sheetname="Sheet1")
        self.wd_index = wd['d_id']
        self.wd_col_1 = wd['4rank']
        wd_col_2 = wd['desc']
        wd_col_3 = wd['description']

        self.wd_col_2 = pd.Series(wd_col_2).apply(str_dp, sym=" ")
        self.wd_col_3 = pd.Series(wd_col_3).apply(str_dp, sym=";")

        no_re_wd_words = []
        for line in self.wd_col_2:
            for w in line:
                no_re_wd_words.append(w)

        for line in self.wd_col_3:
            for w in line:
                if w != "nan":
                    no_re_wd_words.append(w)

        self.no_re_wd_words = set(no_re_wd_words)

        self.wd_sim_word = pd.read_excel("C:/Users/Administrator/Desktop/维度20180109.xlsx", sheetname="Sheet2")

        self.dict_sim_word = {}
        for i in range(len(self.wd_sim_word)):
            value_list = []
            value_list.append(str(self.wd_sim_word['key'][i]).lower().strip())
            for j in str(self.wd_sim_word['value'][i]).split(" "):
                if str(j) != "nan":
                    value_list.append(str(j).lower().strip())
            self.dict_sim_word[str(self.wd_sim_word['key'][i]).lower().strip()] = value_list

        # for k, v in self.dict_sim_word.items():
        #     print(str(k) + "\t" + str(v))

        step1 = datetime.datetime.now()
        print("拉取维度数据用时：" + str(step1 - begin))

    def find_dim(self, every_comment):

        def cut_short_sentences(every_str):
            sentence_list = []
            for s in re.split('。|！|？|；| |>|【|】| |;|：|，|,', every_str):
                if len(s) != 0:
                    sentence_list.append(s)
            return sentence_list

        def str_dp2(str1):
            return jieba.lcut(str(str1).lower().strip())

        begin = datetime.datetime.now()

        content_dp = cut_short_sentences(every_comment)
        content_cut = pd.Series(content_dp).apply(str_dp2)
        print(len(content_cut))

        result = []
        for i in range(len(content_cut)):
            res = {}
            res['desc'] = content_dp[i]
            res['desc_cut'] = content_cut[i]
            res['wd'] = "null"
            if len(set(content_cut[i]) & self.no_re_wd_words) == 0:
                result.append(res)
                continue
            for j in range(len(self.wd_col_2)):
                a_round = set(content_cut[i]) & set(self.wd_col_3[j])
                if len(a_round) > 0:
                    res['wd'] = self.wd_col_1[j]
                    res['wd_description'] = str(a_round)
                    res['wd_index'] = self.wd_index[j]
                    break

                res_str = ""
                count = 0
                for k in range(len(self.wd_col_2[j])):
                    if len(set(self.dict_sim_word[self.wd_col_2[j][k]]) & set(content_cut[i])) != 0:
                        count += 1
                        res_str += str(set(self.dict_sim_word[self.wd_col_2[j][k]]) & set(content_cut[i]))

                if count == len(self.wd_col_2[j]):
                    res['wd'] = self.wd_col_1[j]
                    res['wd_desc'] = res_str
                    res['wd_index'] = self.wd_index[j]
                    break
            result.append(res)

        stop = datetime.datetime.now()
        print("匹配维度用时：" + str(stop - begin))
        result_df = pd.DataFrame(result)
        return result

aaa = DimFinder()
content = np.array(pd.read_excel("C:/Users/Administrator/Desktop/autohome_bbs_2017-08-07.xlsx")['G'][0:2]).tolist()
for i in content:
    bbb = aaa.find_dim(i)
    print(bbb)

