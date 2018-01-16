from pykafka import KafkaClient
from elasticsearch import Elasticsearch

# client = KafkaClient(hosts="colordata-005:9092")
# client = KafkaClient(hosts="101.201.153.51:9092", zookeeper_hosts="60.205.169.205:2181")
client = KafkaClient(hosts="101.201.153.51:9092")
es = Elasticsearch('101.89.68.208:9200')
topic = client.topics[b'mira_test']
print(topic.name)

page = es.search(index="byd", scroll='2m', size=100, body={"query": {"match_all": {}}})
sid = page['_scroll_id']
scroll_size = page['hits']['total']
print(scroll_size)

# with topic.get_sync_producer() as producer:
#     while scroll_size > 0:
#         print("Scrolling...")
#         page = es.scroll(scroll_id=sid, scroll='2m')
#         sid = page['_scroll_id']
#         scroll_size = len(page['hits']['hits'])
#         for hit in page['hits']['hits']:
#             id = hit["_id"]
#             website = hit["_source"]["website"]
#             context = hit["_source"]["thread_context"]
#             str_send = str(id) + "\t" + str(website) + "\t" + str(context).strip()
#             print(str_send)
#             producer.produce(bytes(str_send, 'utf-8'))

consumer = topic.get_simple_consumer()
for message in consumer:
    if message is not None:
        print(str(message.offset), str(message.value, encoding='utf-8'))
