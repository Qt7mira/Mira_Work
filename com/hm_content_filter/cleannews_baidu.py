# coding=utf-8
import xlrd
import xlwt
import datetime
import jieba
from tqdm import tqdm
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

datafile1 = xlrd.open_workbook('data/问题数据.xlsx')
table1 = datafile1.sheet_by_name('Sheet5')
num_rows1 = table1.nrows

datafile2 = xlrd.open_workbook('data/陕西电力关键词.xlsx')
table2 = datafile2.sheet_by_name('Sheet2')
num_rows2 = table2.nrows

out_xl = xlwt.Workbook(encoding='utf-8')
table_out = out_xl.add_sheet('分析结果', cell_overwrite_ok=True)

stop_words = []
result = []


def load_docs_data(table, num_rows):
    docs_list = []
    for row in range(1, num_rows):
        doc = {}
        doc['id'] = row
        doc['content'] = table.cell(row, 13).value.replace('\n', '')
        docs_list.append(doc)
    return docs_list


def load_words_data(table, num_rows):
    data_list = []
    for row in range(1, num_rows):
        data = {}
        data['id'] = row+1
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
                    words_group.append(word)
            perline.append(words_group)
        docs1.append(perline)
    return docs1


begin = datetime.datetime.now()

with open('data/stop_words.txt', 'r', encoding='utf-8') as f:
    for line in f:
        stop_words.append(line.strip())
stop_words.append(' ')
stop_words.append('\n')

jieba.load_userdict('data/dic.txt')

data_list_news = load_docs_data(table1, num_rows1)
data_list_words = load_words_data(table2, num_rows2)

docs = [data['content'] for data in data_list_news]
docs_core = doc_process([data['core'] for data in data_list_words])
docs_include = doc_process([data['include'] for data in data_list_words])
docs_not_include = doc_process([data['not_include'] for data in data_list_words])
print("数据读取完成")
step1 = datetime.datetime.now()
print("数据读取耗时："+str(step1-begin))

print("开始切词")
docs1 = cut(docs)
step2 = datetime.datetime.now()
print("结束切词")
print("数据切词耗时："+str(step2-step1))

print("开始去除停词")
docs2 = [[word for word in document if word not in stop_words] for document in docs1]
step3 = datetime.datetime.now()
print("结束去除停词")
print("数据去停词耗时："+str(step3-step2))

print("开始分析数据")
result = []
for num in range(0, len(docs2)):
    res = []
    res_r1 = []
    for i in range(0, len(docs_core)):
        for j in range(0, len(docs_core[i])):
            s = set(docs2[num]) ^ (set(docs_core[i][j]))
            if len(s) == abs(len(set(docs2[num])) - len(set(docs_core[i][j]))):
                if i not in res_r1:
                    res_r1.append(i)

    res_r2 = []
    for i in range(0, len(res_r1)):
        res_r2_n = []
        for j in range(0, len(docs_include[res_r1[i]])):
            s = set(docs2[num]) ^ (set(docs_include[res_r1[i]][j]))
            if len(s) == abs(len(set(docs2[num])) - len(set(docs_include[res_r1[i]][j]))):
                res_r2_n.append(j)
        res_r2.append(res_r2_n)

    nul_v = []
    for i in range(0, len(res_r2)):
        if len(res_r2[i]) == 0:
            nul_v.append(i)

    for i in range(0, len(nul_v)):
        del (res_r1[nul_v[i] - i])
        del (res_r2[nul_v[i] - i])

    res_r3 = []
    for i in range(0, len(res_r1)):
        res_r3_n = []
        for j in range(0, len(docs_not_include[res_r1[i]])):
            s = set(docs2[num]) ^ (set(docs_not_include[res_r1[i]][j]))
            if len(s) == abs(len(set(docs2[num])) - len(set(docs_not_include[res_r1[i]][j]))):
                res_r3_n.append(j)
        res_r3.append(res_r3_n)

    # if num == 0:
    #     print('******')
    #     print(res_r1)
    #     print(res_r2)
    #     print(res_r3)

    for i in range(0, len(res_r1)):
        res = {}
        res['index'] = num
        res['category'] = res_r1[i]
        res['words_num'] = len(set(docs2[num]))
        inc_no_re = []
        not_inc_no_re = []
        try:
            for j in range(0, len(res_r2[i])):
                # if num == 0:
                #     print(res_r1[i])
                #     print(res_r2[i][j])
                #     print(docs_include[res_r1[i]][res_r2[i][j]])
                for word in docs_include[res_r1[i]][res_r2[i][j]]:
                    if word not in inc_no_re:
                        inc_no_re.append(word)
            for j in range(0, len(res_r3[i])):
                for word in docs_not_include[res_r1[i]][res_r3[i][j]]:
                    if word not in not_inc_no_re:
                        not_inc_no_re.append(word)
            doc_inc_num = [i for i in docs2[num] if i in inc_no_re]
            doc_not_inc_num = [i for i in docs2[num] if i in not_inc_no_re]
            # print(inc_no_re)
            # print(not_inc_no_re)
            # print(doc_inc_num)
            res['inc'] = len(doc_inc_num)
            res['inc_dic'] = len(inc_no_re)
            res['not_inc_dic'] = len(not_inc_no_re)
            # if res['inc'] == 0:
            #     print('***********')
            #     print(inc_no_re)
            #     print(docs2[num])
            #     print('***********')
            res['inc_pc'] = res['inc'] / res['words_num']
            res['not_inc'] = len(doc_not_inc_num)
            res['not_inc_pc'] = res['not_inc'] / res['words_num']
            result.append(res)
        except ZeroDivisionError as e:
            print(str(e)+': '+str(num))

step4 = datetime.datetime.now()
print("结束分析数据")
print(len(result))
print("数据分析耗时："+str(step4-step3))
print("总共耗时："+str(step4-begin))
# for i in result:
#     print(i)


def set_style(name, weight, bold=False):
    style = xlwt.XFStyle()  # 初始化样式
    font = xlwt.Font()
    font.name = name
    font.bold = bold
    font._weight = weight
    style.font = font
    return style

# result2 = []
# for i in range(0, len(result)):
#     if result[i]['inc_dic'] == 0:
#         if result[i]['not_inc_pc'] == 0:
#             result2.append(result[i])
#     else:
#         if result[i]['inc_pc'] * 3 - result[i]['not_inc_pc'] > 0.05:
#             result2.append(result[i])
#
# print(len(result2))


row0 = ['文章序号', '文章词量', '分类', '词库中包含词总个数', '文章中包含词个数', '文章中包含词百分占比', '词库中排除词总个数', '排除词', '排除词百分比']
for i in range(len(row0)):
    table_out.write(0, i, row0[i])
row_out = 1
# for i in range(0, len(result2)):
#     table_out.write(row_out, 0, result2[i]['index'])
#     table_out.write(row_out, 1, result2[i]['words_num'])
#     table_out.write(row_out, 2, result2[i]['category'])
#     table_out.write(row_out, 3, result2[i]['inc_dic'])
#     table_out.write(row_out, 4, result2[i]['inc'])
#     table_out.write(row_out, 5, result2[i]['inc_pc'])
#     table_out.write(row_out, 6, result2[i]['not_inc'])
#     table_out.write(row_out, 7, result2[i]['not_inc_pc'])
for i in range(0, len(result)):
    table_out.write(row_out, 0, result[i]['index'])
    table_out.write(row_out, 1, result[i]['words_num'])
    table_out.write(row_out, 2, result[i]['category'])
    table_out.write(row_out, 3, result[i]['inc_dic'])
    table_out.write(row_out, 4, result[i]['inc'])
    table_out.write(row_out, 5, result[i]['inc_pc'])
    table_out.write(row_out, 6, result[i]['not_inc_dic'])
    table_out.write(row_out, 7, result[i]['not_inc'])
    table_out.write(row_out, 8, result[i]['not_inc_pc'])
    row_out += 1
out_xl.save('cleandata_baidu_3.xls')
