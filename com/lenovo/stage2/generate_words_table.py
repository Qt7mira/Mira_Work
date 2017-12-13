"""
生成一个简单的全词表
"""
import pandas as pd
import jieba
import pymysql
import json

all_incident = []
all_incident_data = {}
jieba.load_userdict("data/tb_dictionary.txt")

conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='lenovo_ml_test')
cur = conn.cursor()
cur.execute("SELECT t.description from ml_incident t ")
results = cur.fetchall()
for row in results:
    all_incident.extend(jieba.lcut(str(row).lower()))
cur.close()

# for i in range(len(all_incident)):
#     print(all_incident[i])

all_incident_data['words'] = pd.Series(all_incident)

words = {}
for l in all_incident_data['words']:
    if l in words:
        words[l] += 1
    else:
        words[l] = 1


min_count = 1  # 词频低于min_count的舍弃

# for k, v in words.items():
#     print(k + "  " + str(v))

words = {i: j for i, j in words.items() if j >= min_count}
id2word = {i + 1: j for i, j in enumerate(words)}  # id映射到词，未登录词全部用0表示
word2id = {j: i for i, j in id2word.items()}  # 词映射到id

print(len(word2id))

# for d, x in word2id.items():
#     print("key:"+d+",value:"+str(x))

with open('data/word2id_lenovo.json', 'a', encoding='utf8') as outfile:
    json.dump(word2id, outfile)
    outfile.write('\n')
