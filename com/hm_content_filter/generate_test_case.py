import pandas as pd
import pymysql

dbconn = pymysql.connect(
    host="101.251.225.162 ",
    database="usys",
    user="soften",
    password="soften2017",
    port=3306,
    charset='utf8'
)

# sql语句
sqlcmd = "SELECT NAME,count(*) as num FROM subwords_used WHERE type = 3 GROUP BY NAME order by num desc;"

# 利用pandas 模块导入mysql数据
df1 = pd.read_sql(sqlcmd, dbconn)
