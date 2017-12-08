from pymongo import MongoClient

conn = MongoClient('mongodb://root:hm20130707_soften@101.251.237.244', 27017)

db = conn.linshi
my_set = db.bbb

file_object = open('C:/Users/Administrator/Desktop/news_data.json', 'w', encoding='utf-8')
count = 0
for i in my_set.find({}, {'_id': 0}):
    print(i)
    for key, value in i.items():
        print("\"%s\":\"%s\"" % (key, value))
    file_object.write(str(i).replace("'", '"'))
    file_object.write('\n')
    count += 1
    if count % 1000 == 0:
        print(count / 1000)

