import gensim
import logging
import datetime

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
begin = datetime.datetime.now()


class Sentences:
    def __iter__(self):
        with open('w2v.txt', 'r', encoding='utf-8') as f:
            for line in f:
                yield line.lower().strip()

word2vec = gensim.models.word2vec.Word2Vec(Sentences(), size=256, window=10, min_count=5, sg=1, hs=1, iter=10, workers=25)
word2vec.save('word2vec_test.m')

end = datetime.datetime.now()
print("共耗时：" + str(end - begin))

print(word2vec.most_similar('比亚迪'))
print(word2vec.most_similar('疝气大灯'))
