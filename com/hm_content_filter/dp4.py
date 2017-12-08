import pandas as pd
import numpy as np
import datetime
import re

begin = datetime.datetime.now()
df = pd.read_csv('data/subwords.csv', usecols=[4, 5, 8])
df_1 = df['name'][(df.status == 1) & (df.type < 4)]
df_2 = (np.array(df_1)).tolist()
step1 = datetime.datetime.now()
print("数据读取耗时："+str(step1-begin))

df_3 = []
df_sp = []
for word in df_2:
    word_1 = str(word).replace('\\', '"').replace('"""', '"')
    if word_1.__contains__('"'):
        s = re.findall('"(.+?)"', word_1)
        if len(s) == 1:
            s_real = str(s)[2: len(str(s)) - 2]
            df_sp.append(s_real.replace(' ', ''))
        if len(s) > 1:
            for i in s:
                s_real = i[1:len(i)-1]
                df_sp.append(s_real.replace(' ', ''))

        s2 = word_1.replace('"' + s_real + '"', '').strip()
        if len(s2) != 0:
            for w in s2.split(','):
                for w1 in w.split(' '):
                    df_3.append(w1.strip())

        # if word_1.__contains__('中国芝麻香'):
        #     print(str(s))
        #     print(s_real)
        #     print(s2)
    else:
        if len(word_1) != 0:
            for w in word_1.split(','):
                for w1 in w.split(' '):
                    df_3.append(w1)

    # for w in str(word).split(','):
    #     word_1 = str(w).replace('\\', '"').replace('"""', '"')
    #     if word_1.__contains__('"'):
    #         s = re.findall('"(.+?)"', word_1)
    #         s_final = str(s)[2:len(s) - 3]
    #         if s_final not in df_sp:
    #             df_sp.append(s_final)
    #         i1 = word_1.index('"')
    #         if i1 == 0:
    #             i2 = word_1[i1 + 1:len(word_1)].index('"')
    #             a1 = word_1[0:i1].strip()
    #             a2 = word_1[i2 + 2:len(word_1)].strip()
    #             a_final = a1 + a2
    #         else:
    #             a_final = word_1[0:i1].strip()
    #         if a_final not in df_sp:
    #             df_sp.append(a_final)
    #     else:
    #         for w in word_1.split(','):
    #             for w1 in w.split(' '):
    #                 if w not in df_3:
    #                     df_3.append(w)


print(len(df_3))
print(len(df_sp))
df_3_set = set(df_3)
df_sp_set = set(df_sp)
print(len(df_3_set))
print(len(df_sp_set))

step4 = datetime.datetime.now()
print("数据处理耗时："+str(step4-step1))

file_object = open('data/dic_test.txt', 'w', encoding='utf-8')
for word in df_3_set:
    if len(word) > 2:
        file_object.write(word+" 1000")
        file_object.write('\n')
for word in df_sp_set:
    file_object.write(word + " 1000")
    file_object.write('\n')
file_object.close()

step5 = datetime.datetime.now()
print("总共耗时："+str(step5-begin))
