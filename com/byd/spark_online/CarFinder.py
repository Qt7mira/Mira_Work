import jieba
import xlrd
import datetime

jieba.load_userdict("../data/myDict.txt")

class CarFinder(object):
    def __init__(self):
        def readExcel(filename):
            data = xlrd.open_workbook(filename)
            table = data.sheet_by_name("Sheet1")
            nrows = table.nrows
            allCars = []
            nickName = []
            linkID = []
            allCarsName = []
            allCarsID = []
            for i in range(1, nrows):
                allCarsID.append(str(table.row_values(i)[0]).strip())
                allCarsName.append(str(table.row_values(i)[1]).strip())
                allCars.append(str(table.row_values(i)[3]).strip())
                linkID.append(str(table.row_values(i)[4]).strip())
                nickName.append(str(table.row_values(i)[6]).strip())
            return allCars, nickName, linkID, allCarsName, allCarsID

        # 构建字典
        def carsClass(allCars, nickName, linkID):
            oneCarDict = {}
            twoCarDict = {}
            threeCarDict = {}
            for i in range(len(allCars)):
                carNames = allCars[i].split("_")
                if len(carNames) == 3:
                    keyName = str(carNames[1]).lower().replace(" ", "")
                    oneCarDict[keyName] = linkID[i]
                    if len(nickName[i]) > 0:
                        nickNames = nickName[i].split(";")
                        for oneNick in nickNames:
                            oneCarDict[oneNick] = "*" + linkID[i]
                elif len(carNames) == 4:
                    keyName = str(carNames[2]).lower().replace(" ", "")
                    twoCarDict[keyName] = linkID[i]
                    if len(nickName[i]) > 0:
                        nickNames = nickName[i].split(";")
                        for oneNick in nickNames:
                            twoCarDict[oneNick] = "*" + linkID[i]
                elif len(carNames) == 5:
                    keyName = str(carNames[3]).lower().replace(" ", "")
                    threeCarDict[keyName] = linkID[i]
                    if len(nickName[i]) > 0:
                        nickNames = nickName[i].split(";")
                        for oneNick in nickNames:
                            threeCarDict[oneNick] = "*" + linkID[i]
            return oneCarDict, twoCarDict, threeCarDict
        filename = "../data/car2Mysql-V4.xlsx"
        self.allCars, self.nickName, self.linkID, self.allCarsName, self.allCarsID = readExcel(filename)
        self.oneCarDict, self.twoCarDict, self.threeCarDict = carsClass(self.allCars, self.nickName, self.linkID)


    def carsRelation(self, allContent):
        oneCarKey = list(self.oneCarDict.keys())
        twoCarKey = list(self.twoCarDict.keys())
        threeCarKey = list(self.threeCarDict.keys())
        sentencePatterns = ["比", "相对于", "对比", "优于", "不比", "没有", "比不上",
                            "离着", "宁可", "和", "跟", "同"]

        allID = []
        finallOriginalName = []

        for i in range(len(allContent)):
            oneIDs = []
            originalName = []
            oneContent = str(allContent[i]).lower().replace(" ", "")
            cutContentWords = jieba.lcut(oneContent, cut_all=True)
            if set(cutContentWords) & set(threeCarKey):
                carNames = list(set(cutContentWords) & set(threeCarKey))
                originalName.append(",".join(carNames))
                for oneName in carNames:
                    oneID = self.threeCarDict[oneName]
                    if len(oneID.split("*")) > 1:
                        oneIDs.append(oneID.split("*")[1])
                    else:
                        oneIDs.append(oneID)
                        # print("###########3", oneName, oneID)
            if set(cutContentWords) & set(twoCarKey):
                carNames = list(set(cutContentWords) & set(twoCarKey))
                originalName.append(",".join(carNames))
                for oneName in carNames:
                    oneID = self.twoCarDict[oneName]
                    if len(oneID.split("*")) > 1:
                        oneIDs.append(oneID.split("*")[1])
                    else:
                        oneIDs.append(oneID)
                        # print("###########2", oneName, oneID)
            if set(cutContentWords) & set(oneCarKey):
                carNames = list(set(cutContentWords) & set(oneCarKey))
                originalName.append(",".join(carNames))
                for oneName in carNames:
                    oneID = self.oneCarDict[oneName]
                    if len(oneID.split("*")) > 1:
                        oneIDs.append(oneID.split("*")[1])
                    else:
                        oneIDs.append(oneID)
                        # print("###########2", oneName, oneID)
            if set(cutContentWords) & set(sentencePatterns) and len(oneIDs) == 1:
                if i == 0:
                    pass
                else:
                    beforeID = allID[0:i]
                    j = len(beforeID) - 1
                    while(len(beforeID[j]) == 0):
                        j -= 1
                        if j < 0:
                            # defNameID = getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                            # finallID.append(defNameID)
                            break
                    if j > -1:
                        # finallID.append(beforeID[j])
                        # print("beforeID[j]: ", beforeID[j])
                        # print(oneIDs[0])
                        if oneIDs[0] not in beforeID[j]:
                            oneIDs.append(beforeID[j][0])
                        else:
                            for i in beforeID[j]:
                                if oneIDs[0] != i:
                                    oneIDs.append(i)
                                    break
            allID.append(oneIDs)
            finallOriginalName.append(originalName)
        return allID, finallOriginalName,oneCarKey, twoCarKey, threeCarKey



    def getDefaultName(self, defaultCarNames, oneCarKey, twoCarKey, threeCarKey):
        oneIDs = []
        if len(defaultCarNames.split("/")) > 1:
            defaultCarNames = defaultCarNames.split("/")[0]
        defaultCarNames = str(defaultCarNames).lower().replace(" ", "")
        # print("默认名： ", defaultCarNames)
        if defaultCarNames in threeCarKey:
            finallID = self.threeCarDict[defaultCarNames]
            finallID = finallID.split("*")
            if len(finallID) > 1:
                oneIDs.append(finallID[1])
            else:
                oneIDs.append(finallID[0])
                # print("默认名属于3 ", finallID)
        elif defaultCarNames in twoCarKey:
            finallID = self.twoCarDict[defaultCarNames]
            finallID = finallID.split("*")
            if len(finallID) > 1:
                oneIDs.append(finallID[1])
            else:
                oneIDs.append(finallID[0])
                # print("默认名属于2 ", finallID)
        elif defaultCarNames in oneCarKey:
            finallID = self.oneCarDict[defaultCarNames]
            finallID = finallID.split("*")
            if len(finallID) > 1:
                oneIDs.append(finallID[1])
            else:
                oneIDs.append(finallID[0])
                # print("默认名属于1 ", finallID)
        else:
            oneIDs.append(defaultCarNames)
        return oneIDs


    def delDefaultName(self, allID, oneCarKey, twoCarKey, threeCarKey, defaultCarNames):
        finallID = []
        for i in range(len(allID)):
            if len(allID[i]) == 0:
                if i == 0:
                    defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                    finallID.append(defNameID)
                else:
                    beforeID = allID[0:i]
                    j = len(beforeID) - 1
                    while (len(beforeID[j]) == 0):
                        j -= 1
                        if j < 0:
                            defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                            finallID.append(defNameID)
                            break
                    if j > -1:
                        finallID.append(beforeID[j])
            else:
                finallID.append(allID[i])
        # print("finallID: ", finallID)
        return finallID


    def finallCarsName(self, finallID):
        allCarsDict = {}
        finallName = []
        for i in range(len(self.allCarsName)):
            allCarsDict[(int(float(self.allCarsID[i])))] = self.allCarsName[i]
        for oneID in finallID:
            names = []
            for id in oneID:
                id = id.split("_")
                if len(id) == 3:
                    names.append(allCarsDict[int(id[1])])
                elif len(id) == 4:
                    names.append(allCarsDict[int(id[2])])
                elif len(id) == 5:
                    names.append(allCarsDict[int(id[3])])
            finallName.append(names)
        # print(finallName)
        return finallName

    def combineResult(self, finalOriginalName, finallName):
        result = []
        for i in range(len(finalOriginalName)):
            onelist = []
            oneDict = {}
            oneDict["originalName"] = finalOriginalName[i]
            oneDict["finallName"] = finallName[i]
            onelist.append(oneDict)
            result.append(onelist)
        return result

    def start(self, allContent, defaultCarNames):
        allID, finalOriginalName, oneCarKey, twoCarKey, threeCarKey = self.carsRelation(allContent)
        # print(allID)
        finallID = self.delDefaultName(allID, oneCarKey, twoCarKey, threeCarKey, defaultCarNames)
        finallName = self.finallCarsName(finallID)
        result = self.combineResult(finalOriginalName, finallName)
        return result



# if __name__ == "__main__":
#     begin = datetime.datetime.now()
#
#     Content = ["大众还大众","比亚迪宋都是我的", "大黄蜂还唐是挺不错的", "相对于唐的车还可以", "都是我的奔驰", "其实都可以", "唐比宋", "我的"]
#     defaultCarNames = "大黄蜂"
#     cf = CarFinder()
#
#     finallName = cf.start(allContent=Content, defaultCarNames=defaultCarNames)
#
#
#     print(finallName)
#     stop = datetime.datetime.now()
#     print(str(stop - begin))
