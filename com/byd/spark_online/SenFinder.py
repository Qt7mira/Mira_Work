import re
import xlrd
import jieba

jieba.load_userdict('../data/user_dict.txt')


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
                key_words = str(data[2]).split('/')
                for word in key_words:
                    word = word.strip()
                    if len(word) > 0:
                        key_set.add(word.split('+')[0].strip())
                        val = {}
                        val['id'] = int(data[0])
                        val['demo'] = data[1]
                        val['key_word'] = data[2]
                        val['type'] = data[3]
                        val['emotional_class'] = data[4]
                        val['worth'] = data[5]
                        sen[word.split('+')[0].strip()] = val
            return sen, key_set

        self.all_sen = readFile('../data/sen2Mysql-V2.xls', 'sentence_pattern')
        self.sen, self.key_set = convertDict(self.all_sen)

    def start(self, data, val):
        all_data = {}
        # print(data)
        result = []
        fin = []
        if len(val['car']) > 0 and val['dim'] != 'null' and val['emo'] != 'null':
            data = str(data).lower()
            words = list(jieba.cut(data, cut_all=True))
            uion = set(words) & self.key_set
            w1 = ''
            if len(uion) == 1:
                w1 = uion.pop()
                cars = val['car']
                # print(cars)
                dims = []
                dims.append(val['dim'])
                emos = val['emo']
                loc = words.index(w1)  # if len(cars) >0:
                if self.sen[w1]['type'] == '正反对比':
                    # num1 = words.index(w1)
                    # print(num1)
                    emo_class = self.sen[w1]['emotional_class']
                    # print(emo_class)
                    if len(cars) >= 2 and emos != 'null' and len(dims) != 'null':
                        num = float('inf')
                        for car in cars:
                            if car in words:
                                num1 = words.index(str(car).lower())
                                if num1 < num:
                                    num = num1
                        loc1 = num - loc
                        if loc1 < 0:
                            if emo_class == 1:
                                result.append(words[num] + '+' + dims[0] + '+' + emos[0])
                                cars.remove(words[num])
                                # print(cars)
                                result.append(str(cars[0]) + '+' + dims[0] + '+' + '不' + emos[0])
                            elif emo_class == -1:
                                result.append(words[num] + '+' + dims[0] + '+' + '不' + emos[0])
                                cars.remove(words[num])
                                # print(cars)
                                result.append(str(cars[0]) + '+' + dims[0] + '+' + emos[0])
                        else:
                            if emo_class == -1:
                                result.append(words[num] + '+' + dims[0] + '+' + emos[0])
                                cars.remove(words[num])
                                # print(cars)
                                result.append(str(cars[0]) + '+' + dims[0] + '+' + '不' + emos[0])
                            elif emo_class == 1:
                                result.append(words[num] + '+' + dims[0] + '+' + '不' + emos[0])
                                cars.remove(words[num])
                                # print(cars)
                                result.append(str(cars[0]) + '+' + dims[0] + '+' + emos[0])
                    elif len(dims) >= 2 and emos != 'null' and len(cars) != 0:
                        num = float('inf')
                        for dim in dims:
                            num1 = words.index(str(dim).lower())
                            if num1 < num:
                                num = num1
                        loc2 = num - loc
                        if loc2 < 0:
                            if emo_class == 1:
                                result.append(cars[0] + '+' + words[num] + '+' + emos[0])
                                dims.remove(words[num])
                                # print(cars)
                                result.append(str(cars[0]) + '+' + str(dims[0]) + '+' + '不' + emos[0])
                            elif emo_class == -1:
                                result.append(cars[0] + '+' + words[num] + '+' + '不' + emos[0])
                                dims.remove(words[num])
                                # print(cars)
                                result.append(str(cars[0]) + '+' + str(dims[0]) + '+' + emos[0])
                        else:
                            if emo_class == -1:
                                result.append(cars[0] + '+' + words[num] + '+' + emos[0])
                                dims.remove(words[num])
                                # print(cars)
                                result.append(str(cars[0]) + '+' + str(dims[0]) + '+' + '不' + emos[0])
                            elif emo_class == 1:
                                result.append(cars[0] + '+' + words[num] + '+' + '不' + emos[0])
                                dims.remove(words[num])
                                # print(cars)
                                result.append(str(cars[0]) + '+' + str(dims[0]) + '+' + emos[0])
                else:
                    result.append(str(cars[0]) + '+' + str(dims[0]) + '+' + emos[0])
            fin.append(result)
            fin.append(w1)

        return fin

# if __name__ == '__main__':
#     aa = SenFinder()
#     print(aa.start('离着唐差远了', {'dim': '整体评价', 'car': ['宋', '唐'], 'emo': ['差']}))
#     print(aa.start('假设这个车真的很便宜', {'dim': '性能', 'car': ['这个车'], 'emo': ['便宜']}))
