import gensim
import logging
import datetime

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
begin = datetime.datetime.now()


class Sentences:
    def __iter__(self):
        with open('model/w2v_test.txt', 'r', encoding='utf-8') as f:
            for line in f:
                yield list(line.lower().strip().split(" "))

word2vec = gensim.models.word2vec.Word2Vec(Sentences(), size=256, window=10, min_count=10, sg=0, hs=1, iter=10, workers=25)

word2vec.save('model/word2vec_test_2.model')

end = datetime.datetime.now()
print("共耗时：" + str(end - begin))

# print(word2vec.most_similar('比亚迪'))
# print(word2vec.most_similar('疝气大灯'))


