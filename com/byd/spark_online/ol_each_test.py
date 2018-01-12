from elasticsearch import Elasticsearch
from pyspark import SparkConf
from pyspark import SparkContext
import datetime
from com.byd.spark_online.AlgStart import AlgStart

start = datetime.datetime.now()
# spark_conf = SparkConf()
# spark_conf.set('spark.cores.max', 8)
# spark_conf.set("spark.executorEnv.PYTHONHASHSEED", "123")
#
# sc = SparkContext(appName='spark_online_test', conf=spark_conf)
es = Elasticsearch('101.89.68.208:9200')

step1 = datetime.datetime.now()
page = es.search(index="byd", size=10, body={"query": {"match_all": {}}})

alg = AlgStart()


def dict_2_es_data(result):
    return '{"sentence": "' + str(result['sentence']) + '","series": "' + str(
        result['car']) + '","car_nickname": "' + str(
        result[
            'car_desc']) + '","fourth_dim": "' + str(result['dim']) + '","dim_des": "' + str(
        result['dim_desc']) + '","emotion_word": "' + \
           str(result['emo']) + '","emotion_worth": "' + str(result['emo_worth']) + '","sen_type": "' + \
           str(result['sen_type']) + '","sen_type": "' + str(result['sen_key']) + '"}'

for hit in page['hits']['hits']:
    id = hit["_id"]
    website = hit["_source"]["website"]
    context = hit["_source"]["thread_context"]
    result = alg.start(website, context)
    print(result)

    body = ""
    for i in range(len(result)):
        body += dict_2_es_data(result[i]) + ","

    body = "[" + body[0:len(body) - 1] + "]"

    es.index(index="test_index", doc_type="article", id=id,
             body={"result": result})

stop = datetime.datetime.now()
print("读存用时：" + str(stop - step1))
print("查数用时：" + str(stop - start))
# sc.stop()
