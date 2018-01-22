import json
import datetime
import os
import traceback
import pandas as pd
import re
import xlrd
import jieba
import logging
from CarFinder import CarFinder
from DimFinder import DimFinder
from EmoFinder import emotionGrabb
from SenFinder import SenFinder
from sceneFinder import SceneFinder

logging.basicConfig(filename='log_bbs.log', filemode='w', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

jieba.load_userdict('data/user_dict.txt')


class AlgStart(object):
    def __init__(self):
        self.cf = CarFinder()
        self.df = DimFinder()
        self.tograb = emotionGrabb()
        self.sf = SenFinder()
        self.scf = SceneFinder()

    def start(self, website, bbs_name, thread_context):

        def cut_short_sentences(every_str):
            sentence_list = []
            rub = ['buy_reason', 'c_comfort', 'c_control', 'c_interior', 'c_look', 'c_oil', 'c_power', 'c_space',
                   'c_satisfied',
                   'c_unsatisfied', 'c_cost']
            for s in re.split('。|！|？|；| |>|【|】| |;|：|，|,|\[|\]|\?', every_str):
                if len(s) != 0 and s not in rub:
                    sentence_list.append(s)
            return sentence_list

        def getCar(val, item):
            # 获取车型的相关信息
            finallIDs = str(item['finallID']).split('_')
            if len(finallIDs) == 3:
                val['brand'] = finallIDs[1]
                val['series'] = ''
                val['model_num'] = ''
                val['car_nickname'] = item['originalName']
            elif len(finallIDs) == 4:
                val['brand'] = finallIDs[1]
                val['series'] = finallIDs[2]
                val['model_num'] = ''
                val['car_nickname'] = item['originalName']
            elif len(finallIDs) == 5:
                val['brand'] = finallIDs[1]
                val['series'] = finallIDs[2]
                val['model_num'] = finallIDs[3]
                val['car_nickname'] = item['originalName']
            return val

        def getDim(val, item):
            # 获取维度的相关信息
            finallDims = str(item['dim_father']).split('_')
            val['first_dim'] = finallDims[1]
            val['second_dim'] = finallDims[2]
            val['third_dim'] = finallDims[3]
            val['fourth_dim'] = finallDims[4]
            val['dim_desc'] = item['dim_desc']
            val['dim_type'] = item['dim_type']
            val['dim_index'] = item['dim_index']
            return val

        def getEmo(val, item={}, label=True):
            if label:
                val['worth'] = item['emo_worth']
                val['emo_word'] = item['emo_word']
                val['emo_id'] = item['emo_id']
                val['isFault'] = item['isFault']
                val['emotion_desc'] = item['emotion_desc']
                val['emotion'] = item['emotion']
            else:
                val['worth'] = 0
                val['emo_word'] = ''
                val['emo_id'] = ''
                val['isFault'] = 0
                val['emotion_desc'] = ''
                val['emotion'] = '中立'
            return val

        def getSen(val, item):
            if item:
                val['sen_type'] = item['type']
                val['sen_demo'] = item['demo']
                val['sen_keyword'] = item['key_word']
                val['sen_worth'] = item['worth']
            else:
                # 无句式，则为一般句式
                val['sen_type'] = '一般句式'
                val['sen_demo'] = ''
                val['sen_keyword'] = ''
                val['sen_worth'] = ''
            return val

        def getScene(val, item):
            val['scene_demo'] = item['scene_demo']
            val['scene'] = item['scene']
            return val

        result = []
        content = str(thread_context).strip()
        defaultCarName = str(bbs_name).strip()
        comeForm = str(website).strip()
        sentences = cut_short_sentences(content)
        try:
            finallName = self.cf.start(allContent=sentences, defaultCarNames=defaultCarName)
            # print(finallName)

            finalDim = self.df.find_dim(sentences)
            # print(finalDim)

            emotionWordsCatched = self.tograb.getEmotionWordsInfos(sentences)
            # print(emotionWordsCatched)

            finalScene = self.scf.start(sentences, comeFrom=comeForm)
            # print(finalScene)

            senId = 1
            for i in range(0, len(sentences)):
                carFinal = finallName[i]
                dimFinal = finalDim[i]
                emoFinal = emotionWordsCatched[i]
                sceneFinal = finalScene[i]


                if dimFinal[0]['dim'] != '':
                    # 一个车型，一个维度,不限定多少个情感词
                    if len(dimFinal) == 1 and len(carFinal) == 1:
                        car_lebel, senResult = self.sf.start(sentences[i], [])
                        if emoFinal:
                            # print('一个车型，一个维度,存在情感词')
                            # 存在情感词
                            for e_item in emoFinal:
                                val = {}
                                val['id'] = senId
                                val['article'] = content
                                val['sectence'] = sentences[i]
                                val['bbs_name'] = defaultCarName
                                val = getCar(val, carFinal[0])
                                val = getDim(val, dimFinal[0])
                                val = getEmo(val, item=e_item)
                                val = getSen(val, item=senResult)
                                val = getScene(val, sceneFinal[0])
                                result.append(val)
                        else:
                            # print('一个车型，一个维度,不存在情感词')
                            # 不存在情感词，默认中立
                            val = {}
                            val['id'] = senId
                            val['article'] = content
                            val['sectence'] = sentences[i]
                            val['bbs_name'] = defaultCarName
                            val = getCar(val, carFinal[0])
                            val = getDim(val, dimFinal[0])
                            val = getEmo(val=val, label=False)
                            val = getSen(val, senResult)
                            val = getScene(val, sceneFinal[0])
                            result.append(val)

                    # 一个车型，多个维度，不限定多少个情感词
                    elif len(dimFinal) > 1 and len(carFinal) == 1:
                        # 判断句式
                        mid1 = []
                        for item in dimFinal:
                            mid1.append(item['dim_desc'])
                        dim_lebel, senResult = self.sf.start(sentences[i], mid1)

                        # 一个车型，多个维度，多个情感词
                        if len(emoFinal) >= 2:
                            val = {}
                            val['id'] = senId
                            val['sectence'] = sentences[i]
                            val['article'] = content
                            val['bbs_name'] = defaultCarName
                            car = []
                            for item in carFinal:
                                car.append(item['finallName'])
                            val['brand'] = car
                            val['series'] = ''
                            val['model_num'] = ''
                            val['car_nickname'] = ''

                            dim = []
                            val['first_dim'] = ''
                            val['second_dim'] = ''
                            val['third_dim'] = ''
                            val['dim_type'] = ''
                            val['dim_index'] = ''
                            for item in dimFinal:
                                dim.append(item['dim'])
                            val['fourth_dim'] = dim

                            dim_desc = []
                            for item in dimFinal:
                                dim_desc.append(item['dim_desc'])
                            val['dim_desc'] = dim_desc

                            if emoFinal:
                                emo = []
                                w_emo = []
                                for item in emoFinal:
                                    emo.append(item['emotion_desc'])
                                    w_emo.append(item['emotion'])
                                val['emo_word'] = emo
                                val['emotion'] = w_emo

                            else:
                                val['emo_word'] = ''
                                val['emotion'] = ''
                            val['worth'] = ''
                            val['emo_id'] = ''
                            val['isFault'] = ''
                            val['emotion_desc'] = ''

                            scene = []
                            w_scene = []
                            for item in sceneFinal:
                                scene.append(item['scene'])
                                w_scene.append(item['scene_demo'])
                            val['scene'] = scene
                            val['scene_demo'] = w_scene
                            result.append(val)

                        elif len(emoFinal) == 1:
                            # print('一个车型，多个维度,一个情感词')
                            # 存在情感词
                            if dim_lebel:
                                for d_item in dimFinal:
                                    val = {}
                                    val['id'] = senId
                                    val['article'] = content
                                    val['sectence'] = sentences[i]
                                    val['bbs_name'] = defaultCarName
                                    worth = dim_lebel.get(d_item['dim_desc'])
                                    val = getCar(val, carFinal[0])
                                    val = getDim(val, d_item)
                                    if worth == 1:
                                        val = getEmo(val, emoFinal[0])
                                    elif worth == -1:
                                        val = getEmo(val, emoFinal[0])
                                        emo = str(val['emo_word'])
                                        val['emo_word'] = '[相反]' + emo
                                        emotion = str(val['emotion'])
                                        val['emotion'] = '[相反]' + emotion
                                    val = getSen(val, senResult)
                                    val = getScene(val, sceneFinal[0])
                                    result.append(val)
                            elif senResult:
                                for item in dimFinal:
                                    val = {}
                                    val['id'] = senId
                                    val['article'] = content
                                    val['sectence'] = sentences[i]
                                    val['bbs_name'] = defaultCarName
                                    val = getCar(val, carFinal[0])
                                    val = getDim(val, item)
                                    val = getEmo(val, emoFinal[0])
                                    val = getSen(val, senResult)
                                    val = getScene(val, sceneFinal[0])
                                    result.append(val)
                            else:
                                for item in dimFinal:
                                    val = {}
                                    val['id'] = senId
                                    val['article'] = content
                                    val['sectence'] = sentences[i]
                                    val['bbs_name'] = defaultCarName
                                    val = getCar(val, carFinal[0])
                                    val = getDim(val, item)
                                    val = getEmo(val, emoFinal[0])
                                    val = getSen(val, senResult)
                                    val = getScene(val, sceneFinal[0])
                                    result.append(val)
                        else:
                            for d_item in dimFinal:
                                # 不存在情感词，默认中立
                                val = {}
                                val['id'] = senId
                                val['article'] = content
                                val['sectence'] = sentences[i]
                                val['bbs_name'] = defaultCarName
                                val = getCar(val, carFinal[0])
                                val = getDim(val, d_item)
                                val = getEmo(val=val, label=False)
                                val = getSen(val, senResult)
                                val = getScene(val, sceneFinal[0])
                                result.append(val)

                    # 多个车型，一个维度，不限定多少个情感词
                    elif len(carFinal) > 1 and len(dimFinal) == 1:
                        mid1 = []
                        for item in carFinal:
                            mid1.append(item['finallName'])
                        # print(mid1)
                        car_lebel, senResult = self.sf.start(sentences[i], mid1)
                        if len(emoFinal) == 1:
                            # print('多个车型，一个维度,一个情感词')
                            if car_lebel:
                                for item in carFinal:
                                    val = {}
                                    val['id'] = senId
                                    val['article'] = content
                                    val['sectence'] = sentences[i]
                                    val['bbs_name'] = defaultCarName
                                    worth = car_lebel.get(item['finallName'])
                                    val = getCar(val, item)
                                    val = getDim(val, dimFinal[0])

                                    if worth == 1:
                                        val = getEmo(val, emoFinal[0])
                                    elif worth == -1:
                                        val = getEmo(val, emoFinal[0])
                                        emo = str(val['emo_word'])
                                        val['emo_word'] = '[相反]' + emo
                                        emotion = str(val['emotion'])
                                        val['emotion'] = '[相反]' + emotion

                                    val = getSen(val, senResult)
                                    val = getScene(val, sceneFinal[0])
                                    result.append(val)
                            elif senResult:
                                for item in carFinal:
                                    val = {}
                                    val['id'] = senId
                                    val['article'] = content
                                    val['sectence'] = sentences[i]
                                    val['bbs_name'] = defaultCarName
                                    val = getCar(val, item)
                                    val = getDim(val, dimFinal[0])
                                    val = getEmo(val, emoFinal[0])
                                    val = getSen(val, senResult)
                                    val = getScene(val, sceneFinal[0])
                                    result.append(val)
                            else:
                                for item in carFinal:
                                    val = {}
                                    val['id'] = senId
                                    val['article'] = content
                                    val['sectence'] = sentences[i]
                                    val['bbs_name'] = defaultCarName
                                    val = getCar(val, item=item)
                                    val = getDim(val, item=dimFinal[0])
                                    val = getEmo(val, item=emoFinal[0])
                                    val = getSen(val, senResult)
                                    val = getScene(val, item=sceneFinal[0])
                                    result.append(val)
                        elif len(emoFinal) > 1:
                            # print('多个车型，一个维度,多个情感词')
                            if car_lebel:
                                for item in carFinal:
                                    # print(item)
                                    worth = car_lebel.get(item['finallName'])
                                    # print(worth)
                                    if worth == 1:
                                        for e_item in emoFinal:
                                            val = {}
                                            val['id'] = senId
                                            val['article'] = content
                                            val['sectence'] = sentences[i]
                                            val['bbs_name'] = defaultCarName
                                            val = getCar(val, item)
                                            val = getDim(val, dimFinal[0])
                                            val = getEmo(val, e_item)
                                            val = getSen(val, senResult)
                                            val = getScene(val, sceneFinal[0])
                                            result.append(val)
                                    elif worth == -1:
                                        for e_item in emoFinal:
                                            val = {}
                                            val['id'] = senId
                                            val['article'] = content
                                            val['sectence'] = sentences[i]
                                            val['bbs_name'] = defaultCarName
                                            val = getCar(val, item)
                                            val = getDim(val, dimFinal[0])
                                            val = getEmo(val, e_item)
                                            emo = str(val['emo_word'])
                                            val['emo_word'] = '[相反]' + emo
                                            emotion = str(val['emotion'])
                                            val['emotion'] = '[相反]' + emotion
                                            val = getSen(val, senResult)
                                            val = getScene(val, sceneFinal[0])
                                            result.append(val)
                            elif senResult:
                                for item in carFinal:
                                    for e_item in emoFinal:
                                        val = {}
                                        val['id'] = senId
                                        val['article'] = content
                                        val['sectence'] = sentences[i]
                                        val['bbs_name'] = defaultCarName
                                        val = getCar(val, item)
                                        val = getDim(val, dimFinal[0])
                                        val = getEmo(val, e_item)
                                        val = getSen(val, senResult)
                                        val = getScene(val, sceneFinal[0])
                                        result.append(val)
                            else:
                                for item in carFinal:
                                    for e_item in emoFinal:
                                        val = {}
                                        val['id'] = senId
                                        val['article'] = content
                                        val['sectence'] = sentences[i]
                                        val['bbs_name'] = defaultCarName
                                        val = getCar(val, item)
                                        val = getDim(val, dimFinal[0])
                                        val = getEmo(val, e_item)
                                        val = getSen(val, senResult)
                                        val = getScene(val, sceneFinal[0])
                                        result.append(val)
                        else:
                            # print('多个车型，一个维度,无情感词')
                            for item in carFinal:
                                val = {}
                                val['id'] = senId
                                val['article'] = content
                                val['sectence'] = sentences[i]
                                val['bbs_name'] = defaultCarName
                                val = getCar(val, item)
                                val = getDim(val, dimFinal[0])
                                val = getEmo(val, label=False)
                                val = getSen(val, senResult)
                                val = getScene(val, sceneFinal[0])
                                result.append(val)

                    # 多个车型，多个维度，不限定多少个情感词
                    elif len(carFinal) > 1 and len(dimFinal) > 1:
                        val = {}
                        val['id'] = senId
                        val['sectence'] = sentences[i]
                        val['article'] = content
                        val['bbs_name'] = defaultCarName
                        car = []
                        for item in carFinal:
                            car.append(item['finallName'])
                        val['brand'] = car
                        val['series'] = ''
                        val['model_num'] = ''
                        val['car_nickname'] = ''

                        dim = []
                        val['first_dim'] = ''
                        val['second_dim'] = ''
                        val['third_dim'] = ''
                        val['dim_type'] = ''
                        val['dim_index'] = ''
                        for item in dimFinal:
                            dim.append(item['dim'])
                        val['fourth_dim'] = dim

                        dim_desc = []
                        for item in dimFinal:
                            dim_desc.append(item['dim_desc'])
                        val['dim_desc'] = dim_desc

                        if emoFinal:
                            emo = []
                            w_emo = []
                            for item in emoFinal:
                                emo.append(item['emotion_desc'])
                                w_emo.append(item['emotion'])
                            val['emo_word'] = emo
                            val['emotion'] = w_emo

                        else:
                            val['emo_word'] = ''
                            val['emotion'] = ''
                        val['worth'] = ''
                        val['emo_id'] = ''
                        val['isFault'] = ''
                        val['emotion_desc'] = ''

                        scene = []
                        w_scene = []
                        for item in sceneFinal:
                            scene.append(item['scene'])
                            w_scene.append(item['scene_demo'])
                        val['scene'] = scene
                        val['scene_demo'] = w_scene
                        # print(val)
                        result.append(val)
                else:
                    val = {}
                    val['id'] = senId
                    val['sectence'] = sentences[i]
                    val['article'] = content
                    val['bbs_name'] = defaultCarName
                    car = []
                    for item in carFinal:
                        car.append(item['finallName'])
                    val['brand'] = car
                    val['series'] = ''
                    val['model_num'] = ''
                    val['car_nickname'] = ''

                    dim = []
                    val['first_dim'] = ''
                    val['second_dim'] = ''
                    val['third_dim'] = ''
                    val['dim_type'] = ''
                    val['dim_index'] = ''
                    for item in dimFinal:
                        dim.append(item['dim'])
                    val['fourth_dim'] = dim

                    dim_desc = []
                    for item in dimFinal:
                        dim_desc.append(item['dim_desc'])
                    val['dim_desc'] = dim_desc

                    if emoFinal:
                        emo = []
                        w_emo = []
                        for item in emoFinal:
                            emo.append(item['emotion_desc'])
                            w_emo.append(item['emotion'])
                        val['emo_word'] = emo
                        val['emotion'] = w_emo

                    else:
                        val['emo_word'] = ''
                        val['emotion'] = ''
                    val['worth'] = ''
                    val['emo_id'] = ''
                    val['isFault'] = ''
                    val['emotion_desc'] = ''

                    scene = []
                    w_scene = []
                    for item in sceneFinal:
                        scene.append(item['scene'])
                        w_scene.append(item['scene_demo'])
                    val['scene'] = scene
                    val['scene_demo'] = w_scene
                    result.append(val)
                senId += 1

        except Exception as e:
            logging.info('***************************')
            logging.info(traceback.format_exc())
            logging.info(thread_context)
            logging.info('%%%%%%%%%%%%%%%%%%%%%%%%%%%')

        return result
