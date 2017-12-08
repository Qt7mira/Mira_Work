min_long = 125
max_long = 125.6
min_lat = 43.7
max_lat = 44.1

import pymysql
import random

conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='api_fast_2')
cur = conn.cursor()
cur.close()
conn.close()
count = 0
for i in range(600):
    for j in range(400):

        longitude = round(min_long + i * 0.001, 3)
        latitude = round(min_lat + j * 0.001, 3)
        person_num = round(random.random() * 30 + 5, 2)
        car_num = round(random.random() * 10 + 5, 2)

        if longitude > 125.306 and longitude < 125.338 and latitude > 43.884 and latitude < 43.914:
            person_num *= 10
            car_num *= 10
        # print(longitude, latitude, person_num, car_num)
        # conn.ping(reconnect=True)

        # cur.execute(
        #     "INSERT INTO a_cc_data (longitude, latitude, person_num, car_num) VALUES ('" +
        #     str(longitude) + "','" + str(latitude) + "','" + str(person_num) + "','" + str(car_num) + "')")
        # conn.commit()
        count += 1
        if count % 10000 == 0:
            print(count)

# cur.close()
# conn.close()
