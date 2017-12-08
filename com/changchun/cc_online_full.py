from __future__ import division
import pymysql
import numpy as np
import pandas as pd
from sklearn.externals import joblib


def score2num(score):
    if score is None:
        return 0
    else:
        return score


def dom2num(dom):
    if str(dom).__contains__('长春'):
        return 0
    elif str(dom).__contains__('吉林'):
        return 1
    elif str(dom).__contains__('辽宁') or str(dom).__contains__('黑龙江') or str(dom).__contains__('东北'):
        return 2
    else:
        return 3


def scan_project_ing():
    conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='api_fast_2')
    cur = conn.cursor()
    cur.execute("SELECT t.id, t.industry, t.money from b_b_project t")

    results = cur.fetchall()
    project = []

    for row in results:
        record = {}
        record['id'] = row[0]
        record['industry'] = row[1]
        record['money'] = float(row[2])
        project.append(record)

    cur.close()
    conn.close()
    return project


def find_company(industry, money):
    conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='api_fast_2')
    cur = conn.cursor()
    cur.execute(
        "SELECT t.entname, t.dom, t.regcap, t.score FROM a_profile_v1 t WHERE t.entstatus = '在营（开业）企业' AND t.regcap >= " + str(
            money) + " AND t.opscope LIKE '%" + industry + "%'")

    results = cur.fetchall()
    if len(results) == 0:
        return None
    company_name = []
    data_X = []

    for row in results:
        record = {}
        company_name.append(row[0])
        record['dom'] = dom2num(row[1])
        record['regcap'] = money / float(row[2])
        record['score'] = score2num(row[3])
        data_X.append(record)

    cur.close()
    conn.close()

    X = np.array(pd.DataFrame(data_X))

    clf = joblib.load('test_model.m')
    res = clf.predict_proba(X)[:, 1]

    res1 = pd.DataFrame(res)
    res1.columns = [['abc']]
    company_name = pd.DataFrame(company_name)
    company_name.columns = [['c_name']]

    aaa = pd.concat([pd.concat([company_name, pd.DataFrame(data_X)], axis=1), res1], axis=1)

    bbb = aaa.sort_values(by=['abc', 'regcap', 'score'], ascending=[0, 1, 0])
    # print(bbb)
    return bbb


def save_company_list2mysql(id, list):
    conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='api_fast_2')
    cur = conn.cursor()

    for name in list:
        cur.execute("INSERT INTO a_recommend_result (id,entname) VALUES ('" + str(id) + "','" + name + "')")
        conn.commit()

    cur.close()
    conn.close()


def truncate_table():
    conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='api_fast_2')
    cur = conn.cursor()

    cur.execute("truncate table a_recommend_result")
    conn.commit()
    cur.close()
    conn.close()


all_project = scan_project_ing()
truncate_table()
for i in range(len(all_project)):
    # print(all_project[i]['id'])
    result = find_company(all_project[i]['industry'], all_project[i]['money'])
    if result is not None:
        save_company_list2mysql(all_project[i]['id'], result['c_name'])

