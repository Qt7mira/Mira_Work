import jieba
import pandas as pd
import numpy as np
from com.byd.newwords.WordDiscovery import WordDiscovery

data = pd.read_excel("C:/Users/Administrator/Desktop/autohome_bbs_2017-08-01.xlsx")
comment = np.array(data['thread_context']).tolist()

comment_str = ""
old_words_list = []
for i in comment:
    old_words_list.extend(jieba.lcut(str(i).lower()))
    comment_str += str(i).lower()

already_words_list = np.array(pd.read_excel("C:/Users/Administrator/Desktop/already.xlsx")['words']).tolist()
for line in already_words_list:
    for w in str(line).replace(" ", "").lower().strip().split('/'):
        old_words_list.append(w)

old_words_set = list(set(old_words_list))

nwf = WordDiscovery()
nwf.set_n(6)
nwf.set_threshold(0.5, 0.5, 10, 30)
nwf.set_dic_from_list(old_words_set)
nwf.add_text(comment_str)
nwf.run()



