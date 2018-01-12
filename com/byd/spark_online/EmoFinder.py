# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:26:24 2018

return fake emotion words and its info

@author: William
"""

import pandas as pd
import jieba


class emotionGrabb():
    def __init__(self, pathOfsqlTable, sheetname='Sheet1'):
        """
            read sqlTable with specific sheetname
        """

        #        jieba.load_userdict('../texts/dictionaries/carSelfDict.txt')
        self.file = pd.read_excel(pathOfsqlTable, sheetname=sheetname, header=0)
        self.word2info = {}
        self.num2word = {}
        self.emotionWords = set()
        self.buildDict()

    def buildDict(self):

        """
            initialize word2info and num2word
        """
        tmp = {}
        for index in range(len(self.file)):
            self.word2info[str(self.file['emotion_word'][index])] = \
                [self.file['e_id'][index], self.file['  d_id'][index], \
                 self.file['  worth'][index], self.file['  isfault'][index], \
                 self.file['p_id'][index]]

            self.num2word[self.file['e_id'][index]] = str(self.file['emotion_word'][index])

        self.emotionWords = list(self.word2info.keys())

    def getEmotionWords(self, sentence):

        """
            using intersection to catch emotionWords
            sentene: str
        """
        words = set(jieba.cut(sentence, cut_all=False, HMM=False))

        catchedEmotions = words.intersection(set(self.emotionWords))

        return catchedEmotions

    def getEmotionWordsInfo(self, sentence):

        """
            Grab catch words' infos
            input: catched emotion words
            return: list of dict
                    dict with values: [e_id, d_id, worth, isfault, 'descriptionBelong']
        """
        emotionWordsCatched = self.getEmotionWords(sentence)

        listOfDict = []
        for emotionWord in emotionWordsCatched:

            tmp = {}
            if self.word2info[emotionWord][4] != 0:

                description = self.num2word[self.word2info[emotionWord][4]]

            else:
                description = ''

            tmp[emotionWord] = [self.word2info[emotionWord][0], self.word2info[emotionWord][1], \
                                self.word2info[emotionWord][2], self.word2info[emotionWord][3], \
                                description]

            listOfDict.append(tmp)

        return listOfDict

    def getEmotionWordsInfos(self, sentences):

        listOflistOfDicts = []
        for sentence in sentences:
            listOflistOfDicts.append(self.getEmotionWordsInfo(sentence))

        return listOflistOfDicts

# if __name__ == '__main__':
#     pathOfsqlTable = '../data/emo2Mysql-V3.xls'
#
#     sample_sentence = ['刚出保后暖风水箱不热，仪表故障，油表偏差，现在发动机有吱吱和哒哒的异响。',\
#                        '再者说纳智捷毕竟市场占有量很少,哒哒故障，',\
#                        '很多人都不了解车子的相关性能以及性价比。']
#
#     tograb = emotionGrabb(pathOfsqlTable, sheetname='Sheet1')
#
#     emotionWordsCatched = tograb.getEmotionWordsInfos(sample_sentence)
#
#     print(emotionWordsCatched)
