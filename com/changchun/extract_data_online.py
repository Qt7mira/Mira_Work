import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.ioloop
import json
import sys
import os
import re
import signal
import pymysql
import datetime
import logging
import logging.handlers
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
import tornado.options


class App(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/extract_data", ExtractData),
        ]
        settings = dict()
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    logger = logging.getLogger()
    tornado.options.parse_command_line()
    fm = tornado.log.LogFormatter(
        fmt='[%(asctime)s][%(levelname)s][%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logger.handlers[0].setFormatter(fm)
    logging.info("临时模型Extract Data已启动成功。")
    executor = ThreadPoolExecutor(1)

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')


class ExtractData(BaseHandler):
    @run_on_executor
    def post(self):
        try:
            def print_time_consuming():
                step_final = datetime.datetime.now()
                logging.info("模块总耗时：" + str(step_final - begin))

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
                    company['公司名称'] + "','" + company['企业法人'] + "','" + company['企业类型'] + "','" + company[
                        '所在地'] + "','" +
                    company['成立时间'] + "','" + company['注册资金'] + "','" + company['员工人数'] + "','" + company[
                        '主营行业'] + "','" + company[
                        '主营产品'] + "')")
                conn.commit()
                cur.close()
                conn.close()

            def drop_tab(string):
                dr = re.compile(r'<[^>]+>', re.S)
                return dr.sub('', string)

            begin = datetime.datetime.now()
            doc = json.loads(self.get_argument("doc", None))
            title = doc['title']
            txt = doc['txt']
            company = {}

            column_name = ['公司名称', '所在地', '企业类型', '成立时间', '员工人数', '主营行业', '主营产品', '注册资金', '企业法人']
            for i in column_name:
                company[i] = 'Null'

            company['公司名称'] = ck_null(title).replace('简介，地址', '')

            if txt.find('企业类型') == -1:
                ret = "{'type': 'false'}"
                self.write(json.dumps(ret))
            elif txt.__contains__('详细资料'):
                keys = (re.findall(r'<label>(.*?)：</label>', txt))
                values = (re.findall(r'</label>(.*?)</li>', txt))
                for i in range(len(keys)):
                    company[str(keys[i]).strip()] = drop_tab(str(values[i])).strip()
            else:
                longtext = (txt.split('##br##')[2].split('公司介绍')[0]).strip()
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
            ret = "{'type': 'success'}"
            self.write(json.dumps(ret))
            print_time_consuming()

        except Exception as e:
            ret = "{'type': 'error', 'error_msg': '%s'}" % e
            self.write(json.dumps(ret))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(str(e) + "   " + str(exc_tb.tb_lineno))
            print_time_consuming()
            return


def stop_service():
    tornado.ioloop.IOLoop.instance().stop()
    logging.info('---------exit-----------')
    os._exit(0)


def handler(signal_num, frame):
    logging.info("\nYou Pressed Ctrl-C.")
    stop_service()


if __name__ == "__main__":
    app = App()
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.listen(18888)
    signal.signal(signal.SIGINT, handler)
    tornado.ioloop.IOLoop.instance().start()
