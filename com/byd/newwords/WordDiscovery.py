# -*- coding: utf-8 -*-
import re
import math
import xlrd
import time


class WordDiscovery(object):
    def __init__(self):
        self.N = 6
        self.threshold_le = 0.7
        self.threshold_re = 0.7
        self.threshold_tf = 20
        self.threshold_mi = 30
        self.stopwords = "的很了么呢是嘛个都也比还这于不与才上用就好在和对挺去后没说"
        self.words = {}
        self.word_lf = {}
        self.word_rf = {}
        self.total_words = 0
        self.new_words = []
        self.dic = set()

    # 设置词语最大长度，默认是5
    def set_n(self, n):
        self.N = n

    # 设置词语的左邻信息熵、右邻信息熵、频数、内聚度的阈值
    def set_threshold(self, le, re, tf, mi):
        self.threshold_le = le
        self.threshold_re = re
        self.threshold_tf = tf
        self.threshold_mi = mi

    # 设置停用词
    def set_stopwords(self, words):
        self.stopwords = words

    # 设置词典
    def set_dic_from_file(self, file):
        f = open(file, "r", encoding='utf-8')
        lines = f.readlines()  # 读取全部内容
        f.close()
        self.dic.clear()
        for line in lines:
            if len(line) > 0:
                word = line.split('\t')[0]
                self.dic.add(word)
                # print(self.dic)
                # print(len(self.dic))

    def set_dic_from_list(self, dic_list):
        self.dic.clear()
        for word in dic_list:
            if len(word) > 0:
                self.dic.add(word)

    def add_word(self, word):
        self.dic.add(word)

    # 加入 text 中的所有词语
    def add_text(self, text):
        phrases = re.split("[^\u4E00-\u9FA50-9A-Za-z]+|[" + self.stopwords + "]", text)
        for phrase in phrases:
            if len(phrase) == 0:
                continue
            # print(phrase, " ", len(phrase))
            l = len(phrase)
            for i in range(l):
                for wl in range(1, self.N + 2):
                    if i + wl > l:
                        break
                    str = phrase[i:i + wl]
                    if str in self.words:
                        self.words[str] += 1
                    else:
                        self.words[str] = 1
                        # print(str)
            self.total_words += l

    def get_mi(self, word, tf):
        if len(word) <= 1:
            return 0  # 1e7
        l = len(word)
        total = self.total_words
        # tf = self.words[word]
        if total <= l:
            return 1e7
        if tf == 0:
            return 0
        res = 1e7
        p = tf / total
        for i in range(1, l):
            left = word[:i]
            right = word[i:]
            # print(left, " ", right)
            prob_l = self.words[left] / total
            prob_r = self.words[right] / total
            if prob_l == 0 or prob_r == 0:
                continue
            prob = p / prob_l / prob_r
            res = min(res, prob)
        return res

    # 清空所有词语
    def clear_text(self):
        self.total_words = 0
        self.words.clear()

    # 计算当前的所有新词
    def run(self):
        # 首先计算所有可能新词的左邻字和右邻字频数列表
        self.word_lf.clear()
        self.word_rf.clear()
        for word in self.words:
            count = self.words[word]
            if len(word) > 1:
                wl = word[1:]
                if wl not in self.dic:
                    if wl in self.word_lf:
                        self.word_lf[wl].append(count)
                    else:
                        self.word_lf[wl] = [count]
                wr = word[:-1]
                if wr not in self.dic:
                    if wr in self.word_rf:
                        self.word_rf[wr].append(count)
                    else:
                        self.word_rf[wr] = [count]
        # print(self.word_lf)
        # print(self.word_rf)
        self.new_words.clear()
        for word in self.words:
            if len(word) <= self.N:
                tf = self.words[word]
                if (word in self.dic) or (tf < self.threshold_tf):
                    continue
                # print(word, " ", tf)
                # 内聚度
                mi = self.get_mi(word, tf)
                if mi < self.threshold_mi:
                    continue
                # print(word, " ", tf, " ", mi)
                le = 0
                if word in self.word_lf:
                    for num in self.word_lf[word]:
                        le += -num / tf * math.log(num / tf)
                if le < self.threshold_le:
                    continue
                re = 0
                if word in self.word_rf:
                    for num in self.word_rf[word]:
                        re += -num / tf * math.log(num / tf)
                if re < self.threshold_re:
                    continue
                ret = {}
                ret['word'] = word
                ret['tf'] = tf
                ret['le'] = le
                ret['re'] = re
                ret['mi'] = mi
                self.new_words.append(ret)
                # self.new_words.append({word, tf, le, re, mi})
                print(word, " ", tf, " ", le, " ", re, " ", mi)
        return self.new_words
        # print(self.new_words)


def test(file, limit):
    t0 = time.time()
    data = xlrd.open_workbook(file)
    table = data.sheets()[0]
    nrows = min(table.nrows, limit)
    a = WordDiscovery()
    a.set_dic("docs/dic.dic")
    # a.add_word("微信")
    for i in range(1, nrows):
        # print(table.row_values(i)[3])
        # a.clear_text()
        a.add_text(table.row_values(i)[2])
    print(a.run())
    print(time.time() - t0)


# 统一计算前 10000 条文本
# test("docs/201711月.xlsx", 10000)
'''
a = WordDiscovery()
#doc = "食品电商小米拖拉机每年最忙的5-17吃货节又要到了。说到吃货节你想到了什么"
#doc = "中国一拖技术中心两个项目获洛阳市小米拖拉机科技进步奖www.d1cm.com2013/07/17 10:00来源：第一工程机械网 近日，洛阳市政府表彰2013年度科技进步奖项目，技术中心的“东方红-LX954/LX1000轮式拖拉机”项目获得洛阳市2013年度科技小米智能轮椅进步一等奖，“东方红—LX700H-LX900H系列高地隙拖拉机”项目获得洛阳市小米智能轮椅2013年度科技进步二等奖。 “东方红-LX954/LX1000轮式拖拉机”项目是默默白条技术中心小米智能轮椅通过自主创新开发的95马力～100马力轮式拖拉机产品。该项目于2012年11月12日通过河南省科技厅组织的科技成果鉴定，整机技术、发动机、传动系等部件技术小米拖拉机达到了国内领先水平。截至2012年12月，共销售29412台，新增产值默默白条26.88亿元，为中国一拖带来巨大的经济效益和默默白条社会效益。 “东方红—LX700H-LX900H系列高地隙拖拉机”是技术中心为了默默白条适用于棉花、甘蔗、玉米的田间作业而开发的市场急需产品，整机性能达到国内同类机型领先水平，目前已经批量生产。(本文来自一拖) (责任编辑：Eason) 关键词: 中国一拖 技术中心 科技进步奖 延伸阅读: 中国一拖与保利集团在京签订战略合作框架协议 国机小米拖拉机集团小米智能轮椅副董事长陈志一行到中国默默白条一拖调研 中国一拖成功拓展履带拖拉机应用新领域 中国一拖：“小智慧”小米拖拉机解决企业“大难题” 中国小米智能轮椅一拖工会2013工作会 满足小米拖拉机职工服务需求 分享到： [大 中 小] 收藏 向本网编辑提供资讯线索 热线：010-64866846 E-mail:news@d1cm.com"
doc = "小明硕士毕业于中国科学院计算所，后在日本京都大学深造，平时喜欢玩猎魔人3还有GTA5等游戏。猎魔人又称为巫师，是一款波兰的游戏。我也很喜欢猎魔人这个游戏。"
a.set_threshold(0.1, 0.1, 1, 10)
a.set_dic("docs/dic.dic")
a.add_text(doc)
print (a.run())
# print (a.get_mi("食品电"))
'''
