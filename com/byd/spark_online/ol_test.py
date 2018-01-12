from elasticsearch import Elasticsearch
from pyspark import SparkConf
from pyspark import SparkContext
import datetime

start = datetime.datetime.now()
# spark_conf = SparkConf()
# spark_conf.set('spark.cores.max', 8)
# spark_conf.set("spark.executorEnv.PYTHONHASHSEED", "123")
#
# sc = SparkContext(appName='spark_online_test', conf=spark_conf)
es = Elasticsearch('101.89.68.208:9200')

step1 = datetime.datetime.now()
print("查数用时：" + str(step1-start))
page = es.search(index="byd", scroll='2m', size=5000, body={"query": {"match_all": {}}})

sid = page['_scroll_id']
scroll_size = page['hits']['total']
print(scroll_size)

while scroll_size > 0:
    print("Scrolling...")
    page = es.scroll(scroll_id=sid, scroll='2m')
    sid = page['_scroll_id']
    scroll_size = len(page['hits']['hits'])
    for hit in page['hits']['hits']:
        id = hit["_id"]
        website = hit["_source"]["website"]
        context = hit["_source"]["thread_context"]
        es.index(index="test_index", doc_type="article", id=id,
                 body={"result": {"thread_context": context, "length": len(context)}})

stop = datetime.datetime.now()
print("读存用时：" + str(stop-step1))
print("查数用时：" + str(stop-start))
# sc.stop()

