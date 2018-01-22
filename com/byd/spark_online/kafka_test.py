from pykafka import KafkaClient
from elasticsearch import Elasticsearch

client = KafkaClient(hosts="colordata-005:9092")
es = Elasticsearch('101.89.68.208:9200')
topic = client.topics[b'mira_test']
print(topic.name)

page = es.search(index="byd", scroll='2m', size=100, body={"query": {"match_all": {}}})
sid = page['_scroll_id']
scroll_size = page['hits']['total']
print(scroll_size)

with topic.get_sync_producer() as producer:
    while scroll_size > 0:
        print("Scrolling...")
        page = es.scroll(scroll_id=sid, scroll='2m')
        sid = page['_scroll_id']
        scroll_size = len(page['hits']['hits'])
        for hit in page['hits']['hits']:
            id = hit["_id"]
            website = hit["_source"]["website"]
            context = hit["_source"]["thread_context"]
            bbs_name = hit["_source"]["bbs_name"]
            str_send = str(id) + "@@@@" + str(website) + "@@@@" + str(bbs_name).strip() + "@@@@" + str(context).strip()
            producer.produce(bytes(str_send, 'utf-8'))

