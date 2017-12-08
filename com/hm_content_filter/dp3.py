import pandas as pd
import numpy as np
import datetime

begin = datetime.datetime.now()

df = pd.read_csv('data/subwords.csv', usecols=[4, 5, 8])
df_1 = df['name'][(df.status == 1) & (df.type < 4)]
df_2 = (np.array(df_1)).tolist()

step1 = datetime.datetime.now()
print("数据读取耗时："+str(step1-begin))

dic_sp = []
dic_remove_dup = []

for line in df_2:
    for phrase in str(line).split(','):
        if phrase.__contains__("\\"):
            word_1 = str(phrase).replace('\\', '"')
            if word_1.__contains__('"'):
                str_sp = word_1[1:len(word_1) - 3]
                if str_sp not in dic_sp:
                    dic_sp.append(str_sp)

        else:
            for word in str(phrase).split(' '):
                if len(word) != 0:
                    if word not in dic_remove_dup:
                        dic_remove_dup.append(word.strip())

print(len(dic_remove_dup))
print(len(dic_sp))
step2 = datetime.datetime.now()
print("数据处理耗时："+str(step2-step1))

file_object = open('data/dic_test.txt', 'w', encoding='utf-8')
for word in dic_remove_dup:
    if len(word) > 2:
        file_object.write(word+" 1000")
        file_object.write('\n')
for word in dic_sp:
    file_object.write(word + "@@n 1000")
    file_object.write('\n')
file_object.close()
print('done')

step4 = datetime.datetime.now()
print("数据存储耗时："+str(step4-step2))
print("总共耗时："+str(step4-begin))
