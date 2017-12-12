import jieba
import pymysql

all_incident = {}
count_1 = 0
count_2 = 0

conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='lenovo_ml_test')
cur = conn.cursor()
cur.execute(
    "SELECT SUBSTRING_INDEX(LOWER(internetemail),'@lenovo.com',1) itcode, t.description from ml_data_all_incident_1 t where SUBSTRING_INDEX(LOWER(t.internetemail),'@lenovo.com',1) in (SELECT DISTINCT LOWER(itcode) FROM bz)")
results = cur.fetchall()
for row in results:
    itcode = row[0]
    desc = str(row[1]).replace("'", ' ')
    if itcode in all_incident:
        all_incident[itcode] += desc
    else:
        all_incident[itcode] = desc
    count_1 += 1
    if count_1 % 100 == 0:
        print(count_1)
cur.close()

print(len(all_incident))

conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='lenovo_ml_test', charset='utf8')
cur = conn.cursor()
for (k, v) in all_incident.items():
    sql = "insert into ml_incident(itcode, descripition) VALUES ('" + str(k) + "','" + str(v) + "')"
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
        print(sql)
    count_2 += 1
    if count_2 % 100 == 0:
        print(count_2)
cur.close()
