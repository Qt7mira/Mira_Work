import json
import re
import xlrd
import jieba

jieba.load_userdict('user_dict.txt')


class SenFinder(object):
    def __init__(self):
        def readFile(path, sheet_name, row=float('inf')):
            all_data = []
            file = xlrd.open_workbook(path)
            wk = file.sheet_by_name(sheet_name)
            nrows = wk.nrows
            for i in range(1, min(nrows, row)):
                row = wk.row_values(i)
                all_data.append(row)
            return all_data

        def convertDict(all_sen):
            sen = {}
            key_set = set()
            for data in all_sen:
                word = str(data[2]).strip()
                if len(word) > 0:
                    key_set.add(word)
                    val = {}
                    val['id'] = data[0]
                    val['demo'] = data[1]
                    val['key_word'] = data[2]
                    val['type'] = data[3]
                    val['emotional_class'] = data[4]
                    val['worth'] = data[5]
                    sen[word] = val
            return sen, key_set

        self.all_sen = readFile('sen2Mysql-V4.xls', 'sentence_pattern')
        self.sen, self.key_set = convertDict(self.all_sen)
        self.ambiguityWords = ["比唐", "比宋", "和唐", "和宋", "秦和", "秦比", "和元", "比元"]

    def start(self, data, val):
        res = {}
        senResult = []
        data = str(data).lower()

        words = list(jieba.cut(data, cut_all=False, HMM=False))


        cutContentWords =[]
        copyWords = []
        bufWords = []

        for words in words:
            for oneambiguity in self.ambiguityWords:
                if oneambiguity in words:
                    copyWords.append(words)
                    for mm in words:
                        bufWords.append(mm)
                else:
                    bufWords.append(words)

        copyWordsSet = set(copyWords)
        for oneWords in bufWords:
            if (oneWords not in cutContentWords) and (oneWords not in copyWordsSet):
                cutContentWords.append(oneWords)
        words = cutContentWords
        # print(words)

        uion = set(words) & self.key_set
        w1 = ''
        if len(uion) >= 1:
            w1 = uion.pop()
            senResult = self.sen[w1]
            loc = words.index(w1)  # if len(cars) >0:
            # print(loc)
            if self.sen[w1]['type'] == '正反对比':
                # num1 = words.index(w1)
                # print(num1)
                emo_class = self.sen[w1]['emotional_class']
                # print(emo_class)
                if len(val) >= 2:
                    mid = {}
                    num = float('inf')
                    for d in val:
                        c = str(d).split(',')[0]
                        # print(c)
                        if c in words:
                            num1 = words.index(str(c).lower())
                            mid2 = {}
                            mid2['label'] = c
                            mid2['original'] = d
                            mid[num1] = mid2
                            if num1 < loc:
                                if emo_class == 1:
                                    res[d] = 1
                                    val.remove(d)
                                    res[str(val[0])] = -1
                                elif emo_class == -1:
                                    res[d] = -1
                                    val.remove(d)
                                    res[str(val[0])] = 1
                            else:
                                if emo_class == 1:
                                    res[d] = -1
                                    val.remove(d)
                                    res[str(val[0])] = 1
                                elif emo_class == -1:
                                    res[d] = 1
                                    val.remove(d)
                                    res[str(val[0])] = -1

        return res, senResult

