# -*- coding=UTF-8 -*-
from pymongo import MongoClient
import datetime
import requests
import json

begin = datetime.datetime.now()
conn = MongoClient('mongodb://root:112358s@182.92.196.59 ', 27017)
db = conn.usearch
collection = db.v4_articles_171023

i = 0
guanggao = 0.0
zhengchang = 0.0
errorNum = 0
total = 5000
num = 0
content_null = 0
url = r'http://60.205.168.205:17779/v1.0/ad_bayes_predict'
sign = 0

file_object = open('C:/Users/Administrator/Desktop/predict_as_ad_999.txt', 'w', encoding='utf-8')
for item in collection.find().limit(total):
    sign = sign + 1
    try:
        data = {'txt': item['content'], 'title': item['title']}
    except Exception as e:
        data = {'txt': '', 'title': item['title']}
        content_null = content_null + 1
        print("第" + str(sign) + '行没有content')

    a = requests.post(url, data=data)
    print(a.text)
    c = json.loads(a.text)
    d = eval(c)
    num = num + 1
    if d["type"] == 'result':
        if float(d["result"]) == 0:
            zhengchang += 1
        if float(d["result"]) == 1:
            file_object.write(item['title'])
            file_object.write('\n')
            guanggao += 1
    if d["type"] == 'error':
        print(data)
        errorNum = errorNum + 1
    print('没有内容的数量' + str(content_null))
    print('检查文章' + str(num) + '篇')
    print("广告率" + str(float(guanggao / num)))
    print("正常率" + str(float(zhengchang / num)))
    print('错误数' + str(errorNum))
file_object.close()