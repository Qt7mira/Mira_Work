import pymysql
import re
doc = ""
file = open('data/data_1.txt', 'r', encoding='utf-8')
for line in file.readlines():
    doc += line


def ck_null(value):
    if str(value).strip() is None or str(value).strip() == '':
        return 'Null'
    else:
        return value


def save_company_2mysql(company):
    conn = pymysql.connect(host='60.205.171.171', user='root', password='123456', database='api_fast_2')
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO a_extracted_data (entname, frdb, enttype, dom, esdate, regcap, employee_num, opscope, ops) VALUES ('" +
        company['公司名称'] + "','" + company['企业法人'] + "','" + company['企业类型'] + "','" + company['所在地'] + "','" +
        company['成立时间'] + "','" + company['注册资金'] + "','" + company['员工人数'] + "','" + company['主营行业'] + "','" + company[
            '主营产品'] + "')")
    conn.commit()
    cur.close()
    conn.close()


def drop_tab(string):
    dr = re.compile(r'<[^>]+>', re.S)
    return dr.sub('', string)

company = {}
column_name = ['公司名称', '所在地', '企业类型', '成立时间', '员工人数', '主营行业', '主营产品', '注册资金']
for i in column_name:
    company[i] = 'Null'
company['公司名称'] = ck_null(re.findall(r'"(.*?)"', doc)[5])
if doc.find('企业类型') == -1:
    print('a')
elif doc.__contains__('详细资料'):
    longtext = (re.findall(r'<label>(.*?)：</label>', doc))
    longtext_2 = (re.findall(r'</label>(.*?)</li>', doc))
    print(longtext)
    for i in longtext_2:
        print(drop_tab(i))
    # print(longtext_2)
else:
    longtext = (re.findall(r'"(.*?)"', doc)[9].split('##br##')[2].split('公司介绍')[0]).strip()
    longtext_dp = longtext.replace('所在地', '@所在地') \
        .replace('企业类型', '@企业类型') \
        .replace('成立时间', '@成立时间') \
        .replace('员工人数', '@员工人数') \
        .replace('主营行业', '@主营行业') \
        .replace('主营产品', '@主营产品') \
        .replace('注册资金', '@注册资金')

    for line in longtext_dp.split('@'):
        company[line.split('：')[0]] = ck_null(line.split('：')[1])
    print(company)
    save_company_2mysql(company)






