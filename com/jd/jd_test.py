import xlrd
import gensim
from gensim.models import word2vec
from sklearn.cluster import KMeans
import sklearn.decomposition
import jieba
import numpy as np
# from multiprocessing import Pool
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
import re
import networkx as nx
import datetime
import os
import shutil
import scipy
import scipy.cluster.hierarchy as sch
import matplotlib.pylab as plt
import xlwt

datafile = xlrd.open_workbook('C:/Users/Administrator/Desktop/舆情监控项目第二轮测试用例v1.0.xlsx')
# out_xl = xlrd.open_workbook("舆情第二轮测试-博彦多彩数据.xls")
# out_xl = copy(out_xl)
out_xl = xlwt.Workbook(encoding='utf-8')
'''
try:
    sheet_index = out_xl.sheet_index('二、功能3 事件聚合结果')
    table_out = out_xl.get_sheet(sheet_index)
except:
    table_out = out_xl.add_sheet('二、功能3 事件聚合结果',cell_overwrite_ok=True)
'''
table_out = out_xl.add_sheet('二、功能3 事件聚合结果', cell_overwrite_ok=True)
T = 1
summary_size = 3
LOAD_MODEL = 1
DIM_SIZE = 32
model_file = 'model_file'
table = datafile.sheet_by_name('功能3 事件聚合 结果')
nrows = table.nrows
# jieba.load_userdict('user_word_dict.txt')
# nrows = 3

stop_words = []


def cut(line):
    ret = ''
    arr = jieba.cut(line)
    for item in arr:
        if item and item not in stop_words:
            ret += item
            ret += '|'
    return ret


def cut_sentence(sentence):
    delimiters = frozenset(u'。！？； >【】')
    buf = []
    for ch in sentence:
        buf.append(ch)
        if delimiters.__contains__(ch):
            yield ''.join(buf)
            buf = []
    if buf:
        yield ''.join(buf)


def cut_sentence_short(sentence):
    delimiters = frozenset(u'。！？； >【】，；')
    buf = []
    for ch in sentence:
        buf.append(ch)
        if delimiters.__contains__(ch):
            yield ''.join(buf)
            buf = []
    if buf:
        yield ''.join(buf)


def load_data():
    data_list = []
    data_id_dict = {}
    data_content_dict = {}
    for row in range(1, nrows):
        # if row>10:break
        data = {}
        data['id'] = table.cell(row, 0).value
        content = ''
        # for item in table.cell(row,1).value.replace('\n','').replace('>',' ').replace('【',' ').replace('】',' ').split(' '):
        for item in cut_sentence(table.cell(row, 1).value.replace('\n', '')):
            if len(item) > 7:
                content += item
        data['content'] = content
        # data['content'] = table.cell(row,1).value.replace('\n','').replace('  ','')
        head = data['content'][:100]
        if head in data_content_dict:
            doc_id = data_content_dict[head]
            data_id_dict[doc_id].append(data['id'])
            continue
        data_content_dict[head] = data['id']
        data_id_dict[data['id']] = [data['id']]
        data_list.append(data)
    return data_list, data_id_dict


def cut_text(data):
    data['text'] = cut(data['company']) + cut(data['title']) + cut(data['content'])
    return data


def list_for_summary(data_list):
    sentence_set = set()
    for data in data_list:
        for s in cut_sentence(data['content']):
            if s not in sentence_set:
                sentence_set.add(s)
                yield s


def list_for_summary_short(data_list):
    sentence_set = set()
    for data in data_list:
        for s in re.split('。|！|？|；| |>|【|】|，|；', data['content']):
            if s not in sentence_set:
                sentence_set.add(s)
                yield s


def get_vec_by_word(docs):
    vec_list = []
    for s in docs:
        vec = np.zeros(DIM_SIZE)
        for word in jieba.cut(s):
            try:
                vec += model[word]
            except:
                # print(word)
                continue
        vec_list.append(vec)
    return np.array(vec_list)


def get_vec_by_doc(data_list):
    tfidf_model = TfidfVectorizer(tokenizer=jieba.cut, min_df=10, stop_words=stop_words)
    docs = [data['content'] for data in data_list]
    tfidf_matrix = tfidf_model.fit_transform(docs)
    ret = tfidf_matrix.todense()
    return ret


def get_sentences():
    for data in data_list:
        for w in jieba.cut(data['content']):
            yield w


def doc_cluster(vec_list):
    # 层次聚类
    '''
    disMat = sch.distance.pdist(vec_list,'euclidean') 
    Z=sch.linkage(disMat,method='single')
    cluster= sch.fcluster(Z, t=T,depth = 2,criterion = 'inconsistent')-1
    '''  # kmeans聚类
    print('len(vec_list)', len(vec_list))
    clf = KMeans(n_clusters=15)
    clf.fit(vec_list)
    cluster = clf.labels_

    K = max(cluster) + 1
    print('cluster:', K)
    classified_data = [[] for _ in range(K)]

    l = 0
    for ids in cluster:
        ids = ids - 1
        classified_data[ids].append(data_list[l])
        l = l + 1
    return classified_data, K




def get_hf_words(docs):
    word_dict = {}
    for doc in docs:
        for word in jieba.cut(doc):
            if word in stop_words or word.isdigit(): continue
            if word not in word_dict:
                word_dict[word] = 1
            else:
                word_dict[word] += 1
    word_list = [[value, key] for key, value in word_dict.items()]
    word_list.sort(reverse=True)
    word_list = word_list[:10]

    evet_name = ''
    for w in word_list:
        evet_name += w[1]
        evet_name += ' '
    return evet_name, word_list


def get_event_name(docs_short, word_list):
    event_vec = [0] * len(docs_short)
    i = 0
    for doc in docs_short:
        if (len(doc) < 10):
            event_vec[i] = 0
            i += 1
            continue
        doc = list(jieba.cut(doc))
        w_n = 0
        for f, w in word_list[:5]:
            if w in doc:
                w_n += 1
                event_vec[i] += f
        event_vec[i] = float(event_vec[i]) / (float(len(doc)) + 1 - w_n)
        i += 1
    index = event_vec.index(max(event_vec))
    evet_name = docs_short[index]
    print(index)
    print(word_list[:5], event_vec[index])
    print(docs_short[index])
    return index


def get_summary(docs, word_list):
    summary_vec = [0] * len(docs)
    i = 0
    for doc in docs:
        if (len(doc) < 50):
            summary_vec[i] = 0
            i += 1
            continue
        doc = list(jieba.cut(doc))
        w_n = 0
        for f, w in word_list:
            if w in doc:
                w_n += 1
                summary_vec[i] += f
        # summary_vec[i] = float(summary_vec[i])/(float(len(doc))+1-w_n)
        i += 1

    index = summary_vec.index(max(summary_vec))
    summary_all = docs[index]
    print(index)
    print(word_list, summary_vec[index])
    print(docs[index])
    return index


begin = datetime.datetime.now()
with open('stop_words.txt', 'r', encoding='utf-8') as f:
    for line in f:
        stop_words.append(line.strip())
stop_words.append(' ')
stop_words.append('\n')

print('reading data....')
data_list, data_id_dict = load_data()

row_out = 1
table_out.write(0, 0, '文章编号')
table_out.write(0, 1, '事件名称')
table_out.write(0, 2, '文章摘要')

print('getting vector....')
vec_list = get_vec_by_doc(data_list)
print('runing PCA....')
print(vec_list.shape)

pca = sklearn.decomposition.PCA(32, copy=False)
vec_list = pca.fit_transform(vec_list)

print('getting cluster....')
''' 打印数据分布图
pca = sklearn.decomposition.PCA(2,copy = False)
vec_list2 = pca.fit_transform(vec_list)
plt.plot(vec_list2[:,0], vec_list2[:,1], 'or')
plt.show()
'''
classified_data, K = doc_cluster(vec_list)

print('saving files....')
for ids in range(0, K):
    docs = list(list_for_summary(classified_data[ids]))
    docs_short = list(list_for_summary_short(classified_data[ids]))

    str_words, word_list = get_hf_words(docs)
    index = get_event_name(docs_short, word_list)
    evet_name = docs_short[index]
    index = get_summary(docs, word_list)
    summary = docs[index]

    data_id_list = []
    for data in classified_data[ids]:
        data_id_list.extend(data_id_dict[data['id']])
    data_id_list.sort()
    table_out.write(row_out, 0, str(data_id_list).replace('[', '').replace(']', '').replace("'", ''))
    table_out.write(row_out, 1, evet_name)
    table_out.write(row_out, 2, summary)
    row_out += 1

out_xl.save('舆情第二轮测试-博彦多彩数据.xls')
print('over....')
print('take ', datetime.datetime.now() - begin)
