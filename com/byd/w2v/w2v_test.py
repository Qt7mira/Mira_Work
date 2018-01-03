from gensim.models import Word2Vec
from com.mira_utils.TxtOperate import TxtOperate
import gc

new_list = []
txt_operate = TxtOperate()
old_list = txt_operate.read_file_2_list("C:/Users/Administrator/Desktop/weidu.txt")

model = Word2Vec.load('model/word2vec_test_2.model')
vocab = list([k for k, v in model.wv.vocab.items()])

for i in old_list:
    if i in vocab:
        for k, v in model.most_similar(i, topn=30):
            if v > 0.2:
                new_list.append(k)

new_list = list(set([w for w in new_list if w not in old_list]))
txt_operate.save_list_2_file("C:/Users/Administrator/Desktop/wd_res.txt", new_list)
del model
gc.collect()



