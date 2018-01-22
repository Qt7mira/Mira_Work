import xlrd
import jieba

jieba.load_userdict('scene.txt')

class SceneFinder(object):
    def __init__(self):
        def readFile(path, sheet_name):
            all_data = []
            file = xlrd.open_workbook(path)
            wk = file.sheet_by_name(sheet_name)
            nrows = wk.nrows
            for i in range(1, nrows):
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
                    sen[word] = val
            return sen, key_set

        self.all_sen = readFile('scene2Mysql-V2.xls', 'Sheet1')
        self.sen, self.key_set = convertDict(self.all_sen)

    def start(self, data, comeFrom):
        result = []
        status = 0
        for sentence in data:
            sceneResult = []
            data = str(sentence).strip().lower()

            if str(comeFrom) == 'autohome_koubei':
                if data.__contains__('buy_reason'):
                    status = 1
                if data.startswith('c_'):
                    status = 0
            words = list(jieba.cut(data, HMM=False))
            uion = set(words) & self.key_set
            if len(uion) == 1:
                w1 = uion.pop()
                val = {}
                val['scene'] = self.sen[w1]['type']
                val['scene_demo'] = self.sen[w1]['demo']
                sceneResult.append(val)
            elif status == 1:
                val = {}
                val['scene'] = '购车场景'
                val['scene_demo'] = ''
                sceneResult.append(val)
            else:
                val = {}
                val['scene'] = '用车场景'
                val['scene_demo'] = ''
                sceneResult.append(val)
            result.append(sceneResult)
        return result

