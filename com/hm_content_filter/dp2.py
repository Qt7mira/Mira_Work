import xlrd
import jieba
from tqdm import tqdm
import logging
import datetime

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

datafile = xlrd.open_workbook('data/陕西电力关键词.xlsx')
table = datafile.sheet_by_name('Sheet1')
num_rows = table.nrows
stop_words = []


def load_data():
    data_list = []
    for row in range(1, num_rows):
        data = {}
        data['id'] = row
        data['core'] = table.cell(row, 5).value.replace('\n', '')
        data['include'] = table.cell(row, 6).value.replace('\n', '')
        data['not_include'] = table.cell(row, 7).value.replace('\n', '')
        data_list.append(data)
    return data_list


def cut(docs):
    docs1 = []
    with tqdm(total=len(docs)) as pbar:
        for doc in docs:
            a = list(jieba.cut(doc))
            docs1.append(a)
            for i in range(1):
                pbar.update(1)
    return docs1


def doc_process(docs):
    docs1 = []
    for line in docs:
        perline = []
        for phrase in line.split(','):
            words_group = []
            for word in phrase.split(' '):
                if len(word) != 0:
                    li = list(jieba.cut(word))
                    for wo in li:
                        words_group.append(wo)
        docs1.append(perline)
    return docs1


begin = datetime.datetime.now()
data_list = load_data()
print("数据读取完成")
step1 = datetime.datetime.now()
print("数据读取耗时："+str(step1-begin))

with open('data/stop_words.txt', 'r', encoding='utf-8') as f:
    for line in f:
        stop_words.append(line.strip())
stop_words.append(' ')
stop_words.append('\n')

docs_core = doc_process([data['core'] for data in data_list])
docs_include = doc_process([data['include'] for data in data_list])
docs_not_include = doc_process([data['not_include'] for data in data_list])

# print(docs_core[6])
# # for i in range(0, len(docs_core)):
# #     print(docs_core[i])
# print(docs_include[6])
# print(docs_not_include[6])

str = '张智民认为在陕西要慎重地实现宝鸡供电公司的运行，不要让电网大盘暴跌，电力市场要健康，电杆要直，电价要稳定，地方电力也不能放松。'
l = list(jieba.cut(str))
l = [word for word in l if word not in stop_words]
print(l)

res = []
res_r1 = []
for i in range(0, len(docs_core)):
    for j in range(0, len(docs_core[i])):
        s = set(l) ^ (set(docs_core[i][j]))
        if len(s) == abs(len(set(l)) - len(set(docs_core[i][j]))):
            res_r1.append(i)

res_r2 = []
for i in range(0, len(res_r1)):
    res_r2_n = []
    for j in range(0, len(docs_include[res_r1[i]])):
        s = set(l) ^ (set(docs_include[res_r1[i]][j]))
        if len(s) == abs(len(set(l)) - len(set(docs_include[res_r1[i]][j]))):
            res_r2_n.append(j)
    res_r2.append(res_r2_n)

nul_v = []
for i in range(0, len(res_r2)):
    if len(res_r2[i]) == 0:
        nul_v.append(i)

for i in range(0, len(nul_v)):
    del (res_r1[nul_v[i]-i])
    del (res_r2[nul_v[i]-i])

res_r3 = []
for i in range(0, len(res_r1)):
    res_r3_n = []
    for j in range(0, len(docs_not_include[res_r1[i]])):
        s = set(l) ^ (set(docs_not_include[res_r1[i]][j]))
        if len(s) == abs(len(set(l)) - len(set(docs_not_include[res_r1[i]][j]))):
            res_r3_n.append(j)
    res_r3.append(res_r3_n)

# print(res_r1)
# print(res_r2)
# print(res_r3)


result = []
for i in range(0, len(res_r1)):
    res = {}
    res['index'] = 1
    res['category'] = res_r1[i]
    res['words_num'] = len(set(l))
    inc_no_re = []
    not_inc_no_re = []
    for j in range(0, len(docs_include[res['category']])):
        for word in docs_include[res['category']][j]:
            if word not in inc_no_re:
                inc_no_re.append(word)
    for j in range(0, len(docs_not_include[res['category']])):
        for word in docs_not_include[res['category']][j]:
            if word not in not_inc_no_re:
                not_inc_no_re.append(word)
    doc_inc_num = [i for i in l if i in inc_no_re]
    doc_not_inc_num = [i for i in l if i in not_inc_no_re]
    # print(inc_no_re)
    # print(not_inc_no_re)
    # print(doc_inc_num)
    res['inc'] = len(doc_inc_num)
    res['inc_pc'] = res['inc'] / res['words_num']
    res['not_inc'] = len(doc_not_inc_num)
    res['not_inc_pc'] = res['not_inc'] / res['words_num']
    result.append(res)
print('done')

for i in result:
    print(i)
