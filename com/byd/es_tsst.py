from elasticsearch import Elasticsearch
es = Elasticsearch('101.201.252.151:9200')
tt = es.get(index="radiott", doc_type="artiststt", id="AWBzSSGGQYJQovPXN9FN")
print(tt)