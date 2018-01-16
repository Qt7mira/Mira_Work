from elasticsearch import Elasticsearch
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.streaming import StreamingContext
import datetime
from AlgStart import AlgStart

alg = AlgStart()

def write2es(rdd):
    print(str(rdd))
    id = str(rdd).split("@@@@")[0]
    website = str(rdd).split("@@@@")[1]
    context = str(rdd).split("@@@@")[2]
    es = Elasticsearch('101.89.68.208:9200')
    print("-------------------------------------------")
    result = alg.start(website, context)
    es.index(index="test_index_2", doc_type="article", id=id,
             body={"result": result})

start = datetime.datetime.now()
spark_conf = SparkConf()
spark_conf.set('spark.cores.max', 8)
spark_conf.set("spark.executorEnv.PYTHONHASHSEED", "123")
spark_conf.set("spark.streaming.kafka.maxRatePerPartition", 4)

sc = SparkContext(appName='spark_online_test', conf=spark_conf)
ssc = StreamingContext(sc, 2)

step1 = datetime.datetime.now()
brokers = "101.201.153.51:9092"
topic = 'mira_test'

kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
lines = kvs.map(lambda x: x[1])
counts = lines.foreachRDD(lambda rdd: rdd.foreach(write2es) if rdd.count != 0 else "")

ssc.start()
ssc.awaitTermination()
stop = datetime.datetime.now()
print("读存用时：" + str(stop-step1))
print("查数用时：" + str(stop-start))
sc.stop()

