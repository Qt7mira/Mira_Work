import jieba
import xlrd
import datetime

jieba.load_userdict("myDict.txt")

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
        filename = "car2Mysql-V4.xlsx"
        self.allCars, self.nickName, self.linkID, self.allCarsName, self.allCarsID = readExcel(filename)
        self.oneCarDict, self.twoCarDict, self.threeCarDict = carsClass(self.allCars, self.nickName, self.linkID)


    # 车辆识别
    def carsRelation(self, allContent, defaultCarNames):
        dealAllID = []
        oneCarKey = list(self.oneCarDict.keys())
        twoCarKey = list(self.twoCarDict.keys())
        threeCarKey = list(self.threeCarDict.keys())
        sentencePatterns = ["比", "相对于", "对比", "优于", "不比", "没有", "比不上",
                            "离着", "宁可", "和", "跟", "同"]
        ambiguityWords = ["比唐", "比宋", "和唐", "和宋", "秦和", "秦比", "和元", "比元"]
        pronouns = ["它", "她", "他",]

        allID = []
        finallOriginalName = []

        for i in range(len(allContent)):
            # print("-------------------", i)
            # print("原始数据： ", allContent[i])
            oneIDs = []
            originalName = []
            cutContentWords = []
            bufWords = []
            copyWords = []
            oneContent = str(allContent[i]).lower().replace(" ", "")
            cutWords = jieba.lcut(oneContent, cut_all=False)
            # print("初始切词： ", cutWords)
            for words in cutWords:
                for oneambiguity in ambiguityWords:
                    if oneambiguity in words:
                        copyWords.append(words)
                        for mm in words:
                            bufWords.append(mm)
                    else:
                        bufWords.append(words)
            copyWordsSet = set(copyWords)
            # print("重复词： ", copyWordsSet)
            for oneWords in bufWords:
                if (oneWords not in cutContentWords) and (oneWords not in copyWordsSet):
                    cutContentWords.append(oneWords)
            # print("最终切词： ", cutContentWords)
            if set(cutContentWords) & set(threeCarKey):
                carNames = list(set(cutContentWords) & set(threeCarKey))
                originalName = originalName + carNames
                for oneName in carNames:
                    oneID = self.threeCarDict[oneName]
                    if len(oneID.split("*")) > 1:
                        oneIDs.append(oneID.split("*")[1])
                    else:
                        oneIDs.append(oneID)
                # print("###########3", oneIDs)

            if set(cutContentWords) & set(twoCarKey):

                carNames = list(set(cutContentWords) & set(twoCarKey))
                originalName = originalName + carNames
                for oneName in carNames:
                    oneID = self.twoCarDict[oneName]
                    if len(oneID.split("*")) > 1:
                        oneIDs.append(oneID.split("*")[1])
                    else:
                        oneIDs.append(oneID)
                # print("###########2", oneIDs)

            if set(cutContentWords) & set(oneCarKey):
                carNames = list(set(cutContentWords) & set(oneCarKey))
                originalName = originalName + carNames
                for oneName in carNames:
                    oneID = self.oneCarDict[oneName]
                    if len(oneID.split("*")) > 1:
                        oneIDs.append(oneID.split("*")[1])
                    else:
                        oneIDs.append(oneID)
                # print("###########1", oneIDs)
            # print(oneIDs)
            if (set(cutContentWords) & set(sentencePatterns)) and (len(oneIDs) > 0):
                # print("@@@@@@@@@@@@@@@@")
                # print(set(cutContentWords) & set(sentencePatterns))
                webNums = 0
                carNamesLocation = []
                sentencePattern = list(set(cutContentWords) & set(sentencePatterns))
                # print("含有的句式词： ", sentencePattern)
                oneSentencePattern = sentencePattern[0]
                if "比" in sentencePattern and "和" in sentencePattern:
                    oneSentencePattern = "比"
                if "比" in sentencePattern and "跟" in sentencePattern:
                    oneSentencePattern = "比"

                # print(oneSentencePattern)
                nums = cutContentWords.index(str(oneSentencePattern))
                # print("句式词的位置：  ", nums)
                if nums == 0:
                    if i == 0:
                        defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                        oneIDs.append("".join(defNameID))
                    else:
                        beforeID = allID[0:i]
                        # print("beforeID: ", beforeID)
                        j = len(beforeID) - 1
                        while len(set(beforeID[j]) - set(oneIDs)) == 0:
                            j -= 1
                            if j < 0:
                                defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                                oneIDs.append("".join(defNameID))
                                break
                        if j > -1:
                            diffCarNames = list(set(beforeID[j]) - set(oneIDs))[0]
                            oneIDs.append(diffCarNames)
                        # oneIDs.append("".join(diffCarNames))

                else:
                    for oneCarNames in originalName:
                        carNamesLocation.append(cutContentWords.index(oneCarNames))
                    #print("car Name Location:", carNamesLocation)
                    for oneCarLocation in carNamesLocation:
                        if nums > oneCarLocation:
                            webNums += 1
                        else:
                            webNums -= 1
                    #print("webNums: ", webNums)
                    if abs(webNums) == len(carNamesLocation) and (len(set(cutContentWords[nums:]) & set(pronouns)) > 0 or len(set(cutContentWords[:nums]) & set(pronouns)) > 0):
                        if i == 0:
                            defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                            oneIDs.append("".join(defNameID))
                        else:
                            beforeID = allID[0:i]
                            j = len(beforeID) - 1
                            while len(set(beforeID[j]) - set(oneIDs)) == 0:
                                # while (len(beforeID[j]) == 0) and len(set(beforeID[j]) - set(oneIDs)) == 0:
                                j -= 1
                                if j < 0:
                                    defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                                    oneIDs.append("".join(defNameID))
                                    break
                            if j > -1:
                                diffCarNames = list(set(beforeID[j]) - set(oneIDs))[0]
                                oneIDs.append(diffCarNames)
            # print("原始车名： ", originalName)
            # print("原始车ID： ", oneIDs)
            # print(len(oneIDs))
            for idnum in range(len(oneIDs)):
                # if idnum < len(oneIDs)-1:
                for nextnum in range(len(oneIDs)-1, idnum, -1):
                    # print("nexNum: ", nextnum)
                    # print(len(oneIDs))
                    num = 0
                    beforeList = oneIDs[idnum].split("_")
                    nextList = oneIDs[nextnum].split("_")
                    if len(beforeList) > len(nextList):
                        for oneid in nextList:
                            if oneid in beforeList:
                                num += 1
                        if num == len(nextList):
                            oneIDs.remove(oneIDs[nextnum])
                            if nextnum < len(originalName):
                                del originalName[nextnum]

                    elif len(beforeList) < len(nextList):
                        for oneid in beforeList:
                            if oneid in nextList:
                                num += 1
                        if num == len(beforeList):
                            oneIDs.remove(oneIDs[idnum])
                            if nextnum < len(originalName):
                                del originalName[nextnum]

            allID.append(oneIDs)
            # print("修改后oneIDs: ", oneIDs)
            finallOriginalName.append(originalName)
            # print("修改后车名： ", finallOriginalName)

        return allID, finallOriginalName, oneCarKey, twoCarKey, threeCarKey

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
        num = 0
        for i in range(len(allID)):
            if len(allID[i]) == 0:
                num += 1
                if num == 3:
                    defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                    finallID.append(defNameID)

                else:
                    if i == 0:
                        defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                        finallID.append(defNameID)
                    else:
                        beforeID = finallID[0:i]
                        j = len(beforeID) - 1
                        while(len(beforeID[j]) == 0):
                            j -= 1
                            if j < 0:
                                defNameID = self.getDefaultName(defaultCarNames, oneCarKey, twoCarKey, threeCarKey)
                                finallID.append(defNameID)
                                break
                        if j > -1:
                            finallID.append(beforeID[j][0].split())
            else:
                num = 0
                finallID.append(allID[i])

        return finallID

    def finallCarsName(self, allCarsName, allCarsID, finallID):
        allCarsDict = {}
        finallName = []
        for i in range(len(allCarsName)):
            allCarsDict[(int(float(allCarsID[i])))] = allCarsName[i]
        # print("allCarsDict: ", allCarsDict)
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
                else:
                    names.append(id[0])
            finallName.append(names)
        return finallName

    def combineResult(self, finalOriginalName, finallName, finallID, allCars, linkID):
        result = []
        carsDict = {}
        for i in range(len(finallName)):
            length = len(finallName[i])
            if len(finalOriginalName[i]) != length:
                finalOriginalName[i].append("")
        # print("!!!!!!!!!", finalOriginalName)
        for one in range(len(allCars)):
            carsDict[linkID[one]] = allCars[one]
        # print(carsDict)
        for j in range(len(finallName)):
            bufList = []
            length = len(finallName[j])
            for i in range(length):
                bufDict = {}
                bufDict["originalName"] = finalOriginalName[j][i]
                bufDict["finallName"] = finallName[j][i]
                if finallID[j][i] in carsDict:
                    bufDict["finallID"] = carsDict[finallID[j][i]]
                else:
                    bufDict["finallID"] = "#"
                bufList.append(bufDict)
            result.append(bufList)
        return result


    def start(self, allContent, defaultCarNames):
        allID, finalOriginalName, oneCarKey, twoCarKey, threeCarKey = self.carsRelation(allContent, defaultCarNames)
        finallID = self.delDefaultName(allID, oneCarKey, twoCarKey, threeCarKey, defaultCarNames)
        finallName = self.finallCarsName(self.allCarsName, self.allCarsID, finallID)
        result = self.combineResult(finalOriginalName, finallName, finallID, self.allCars, self.linkID)
        return result