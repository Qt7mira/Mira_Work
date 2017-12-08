import sys
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.ioloop
import jieba
import json
import os
import signal
import logging
import logging.handlers
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
import tornado.options

stop_words = []
ads = []


class App(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/v1/adidentify", AdIdentify),
        ]
        settings = dict()
        with open('data/stop_words.txt', 'r', encoding='utf-8') as f:
            for line in f:
                stop_words.append(line.strip())
        stop_words.append(' ')
        stop_words.append('\n')
        with open('data/ads.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if len(line) != 0:
                    ads.append(line.strip())
        jieba.load_userdict('data/dic.txt')
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    logger = logging.getLogger()
    tornado.options.parse_command_line()
    fm = tornado.log.LogFormatter(
        fmt='[%(asctime)s][%(levelname)s][%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logger.handlers[0].setFormatter(fm)
    logging.info("内容识别模型已启动。")
    executor = ThreadPoolExecutor(1)

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')


class AdIdentify(BaseHandler):
    @run_on_executor
    def post(self):
        try:
            # title = (base64.urlsafe_b64decode(str(self.get_argument("title", None)).replace(' ', '+'))).decode()
            # doc = (base64.urlsafe_b64decode(str(self.get_argument("content", None)).replace(' ', '+'))).decode()
            title = str(self.get_argument("title", None))
            doc = str(self.get_argument("content", None))

            title_cut = list(jieba.cut(title))
            title_dp = [word.lower() for word in title_cut if word not in stop_words]
            if len(title_dp) == 0:
                ret = {"type": "error", "error_msg": "文章标题经处理后，词量为0。"}
                self.write(json.dumps(ret))
                return
            print(title_cut)

            doc_cut = list(jieba.cut(doc))
            doc_dp = [word.lower() for word in doc_cut if word not in stop_words]
            if len(doc_dp) == 0:
                ret = {"type": "error", "error_msg": "文章正文经处理后，词量为0。"}
                self.write(json.dumps(ret))
                return
            print(doc_cut)

            ad_title = [i for i in title_dp if i in ads]
            ad_doc = [i for i in doc_dp if i in ads]
            print(ad_title)
            print(ad_doc)
            x = round(len(ad_title) / len(title_dp), 3)
            y = round(len(ad_doc) / len(doc_dp), 3)
            res = 40 * x + 60 * y
            if res > 2:  # 是广告
                ret = {"type": "result", "result": "true"}
                self.write(json.dumps(ret))
            else:  # 不是广告
                ret = {"type": "result", "result": "false"}
                self.write(json.dumps(ret))
        except Exception as e:
            ret = '{"type": "error", "error_msg": "%s"}' % e
            self.write(json.dumps(ret))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(str(e) + "   " + str(exc_tb.tb_lineno))
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
    server.listen(17777)
    signal.signal(signal.SIGINT, handler)
    tornado.ioloop.IOLoop.instance().start()
