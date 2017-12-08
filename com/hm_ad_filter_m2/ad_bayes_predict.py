import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.ioloop
import json
import sys
import os
import signal
import datetime
import logging
import logging.handlers
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
import tornado.options
from sklearn.externals import joblib
import pandas as pd

stop_words = []
count_vec = joblib.load("model/tfidf_model.m")
clf = joblib.load("model/bayes_model.m")


class App(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/v1.0/ad_bayes_predict", Ad_Bayes_Predict),
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
    logging.info("广告识别模型M2_Bayes已启动成功。")
    executor = ThreadPoolExecutor(1)

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')


class Ad_Bayes_Predict(BaseHandler):
    @run_on_executor
    def post(self):
        try:
            def print_time_consuming():
                step_final = datetime.datetime.now()
                logging.info("计算模块总耗时：" + str(step_final - begin))

            begin = datetime.datetime.now()

            title = self.get_argument("title", None)
            content = self.get_argument("txt", None)
            logging.info("接收到的文章标题为：" + title)

            if len(str(title)) == 0 and len(str(content)) == 0:
                ret = "{'type': 'result', 'result': '0'}"
                self.write(json.dumps(ret))
                print_time_consuming()
                return

            tit_con = str(title) + str(content)
            x = pd.Series(tit_con)
            x = count_vec.transform(x.values.astype('U'))
            # logging.info(clf.predict_proba(x)[:, 1])
            result = clf.predict(x)
            ret = "{'type': 'result', 'result': '%s'}" % result[0]
            logging.info(result)
            # result = clf.predict_proba(x)[:, 1]
            # if result >= 0.2:
            #     ret = "{'type': 'result', 'result': '1'}"
            # else:
            #     ret = "{'type': 'result', 'result': '0'}"
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
    server.listen(17779)
    signal.signal(signal.SIGINT, handler)
    tornado.ioloop.IOLoop.instance().start()
