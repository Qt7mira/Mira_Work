import os
import pandas as pd
import jieba
import datetime
import gc


def path_walk(path):
    p_list = []
    for root, dirs, files in os.walk(path):
        for fn in files:
            p_list.append(root + "/" + fn)
    return p_list


def str_dp(cell):
    return jieba.lcut(str(cell).replace(" ", "").strip())


begin = datetime.datetime.now()
jieba.load_userdict("C:/Users/Administrator/Desktop/already.txt")
path_list = path_walk("H:/1226 BYD汽车数据(7490335)")

for i in range(len(path_list)):
    print(path_list[i])
    data = pd.Series(pd.read_excel(path_list[i], header=None)[6]).apply(str_dp)
    file_object = open('C:/Users/Administrator/Desktop/w2v.txt', 'a', encoding='utf-8')
    for j in range(len(data)):
        line = ""
        for word in data[j]:
            line += word + " "
        file_object.write(line)
        file_object.write('\n')
    file_object.close()
    del data
    gc.collect()

end = datetime.datetime.now()
print("共耗时：" + str(end - begin))
