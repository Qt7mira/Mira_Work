import traceback
import re

# from com.byd.spark_online.CarFinder import CarFinder
# from com.byd.spark_online.DimFinder import DimFinder
# from com.byd.spark_online.EmoFinder import emotionGrabb
# from com.byd.spark_online.SenFinder import SenFinder
from CarFinder import CarFinder
from DimFinder import DimFinder
from EmoFinder import emotionGrabb
from SenFinder import SenFinder

class AlgStart(object):

    def __init__(self):
        self.cf = CarFinder()
        self.df = DimFinder()
        pathOfsqlTable = '../data/emo2Mysql-V3.xls'
        self.tograb = emotionGrabb(pathOfsqlTable, sheetname='Sheet1')
        self.sf = SenFinder()

    def start(self, website, thread_context):

        result = []

        def cut_short_sentences(every_str):
            sentence_list = []
            for s in re.split('。|！|？|；| |>|【|】| |;|：|，|,', every_str):
                if len(s) != 0:
                    sentence_list.append(s)
            return sentence_list


        content = thread_context
        defaultCarName = website
        sentences = cut_short_sentences(content)
        # for sentence in sentences:
        try:
            finallName = self.cf.start(allContent=sentences, defaultCarNames=defaultCarName)
            finalDim = self.df.find_dim(sentences)
            emotionWordsCatched = self.tograb.getEmotionWordsInfos(sentences)

            for i in range(0, len(sentences)):
                val = {}
                # val['article'] = content
                # val['from'] = defaultCarName
                val['sentence'] = sentences[i]

                val['car'] = finallName[i][0]['finallName']
                val['car_desc'] = finallName[i][0]['originalName']
                val['dim'] = finalDim[i]['dim']
                if finalDim[i]['dim'] != 'null':
                    val['dim_desc'] = finalDim[i]['dim_desc']
                else:
                    val['dim_desc'] = 'null'

                val['emo'] = 'null'
                val['emo_worth'] = 'null'
                if len(emotionWordsCatched[i]) != 0:
                    t1 = []
                    t2 = []
                    for key in emotionWordsCatched[i][0].keys():
                        t1.append(key)
                        t2.append(emotionWordsCatched[i][0][key][2])
                    val['emo'] = t1
                    val['emo_worth'] = t2

                sen = self.sf.start(sentences[i], val)
                if len(sen) >= 1:
                    val['sen_type'] = sen[0]
                    val['sen_key'] = sen[1]
                else:
                    val['sen_type'] = '-'
                    val['sen_key'] = '-'

                val['car'] = str(val['car'])
                val['car_desc'] = str(val['car_desc'])
                val['sen_type'] = str(val['sen_type'])
                val['sen_key'] = str(val['sen_key'])
                val['emo'] = str(val['emo'])
                val['emo_worth'] = str(val['emo_worth'])
                # print(val)
                result.append(val)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            print(content)
        return result


# if __name__ == "__main__":
#     begin = datetime.datetime.now()
#     print('begin')
#     # filename1 = "autohome_bbs_2017-08-30.xlsx"
#     result = []
#     fileList = []
#     # GetFileList(dir='data/', fileList=fileList)
#     fileList = ["autohome_bbs_2017-08-30.xlsx"]
#     for filename in fileList:
#         print(filename)
#         start(filename, 500, result)
#     # print(result)
#     result2 = pd.DataFrame(result)
#     result2.to_excel('result_bbs_2.xlsx')
#     stop = datetime.datetime.now()
#     print(str(stop - begin))
#     print('end')
