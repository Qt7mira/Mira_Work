# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:26:24 2018

return fake emotion words and its info

@author: William
"""

import pandas as pd 
import jieba

class emotionGrabb():
    
    def __init__(self, sheetname='Sheet1'):
        """
            read sqlTable with specific sheetname
        """
        
        jieba.load_userdict('carSelfDict.txt')
        self.file = pd.read_excel('emo2Mysql-V3.xls', sheetname=sheetname, header=0)
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
                description = emotionWord
            
            emotion = '负面' if self.word2info[emotionWord][2] < 0 else '正面'
            isFault = 1 if self.word2info[emotionWord][3]==1 else 0
            
            tmp = {'emotion':emotion, 'emotion_desc': emotionWord, 'emo_worth': self.word2info[emotionWord][2], \
                   'isFault': isFault, 'emo_word': description, 'emo_id':self.word2info[emotionWord][0]}
                
            listOfDict.append(tmp)
                
        return listOfDict
    
    
    def getEmotionWordsInfos(self, sentences):

        listOflistOfDicts = []
        for sentence in sentences:
            listOflistOfDicts.append(self.getEmotionWordsInfo(sentence))

        return listOflistOfDicts
