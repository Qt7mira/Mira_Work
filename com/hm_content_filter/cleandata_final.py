import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.ioloop
import jieba
import json
import sys
import os
import base64
import re
import math
import signal
import datetime
import logging
import logging.handlers
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
import tornado.options

stop_words = []


class App(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/cleandata", CleanData),
        ]
        settings = dict()
        with open('data/stop_words.txt', 'r', encoding='utf-8') as f:
            for line in f:
                stop_words.append(line.strip())
        stop_words.append(' ')
        stop_words.append('\n')
        jieba.load_userdict('data/dic_test.txt')
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


class CleanData(BaseHandler):
    @run_on_executor
    def post(self):
        try:
            def read_data_from_json(type_value):
                words_set = []
                for line in json_data['subwords']:
                    if line['type'] == type_value:
                        phrase = str(line['name']).lower()
                        word_sub_set = []
                        if phrase.__contains__('\"'):
                            s = re.findall('\"(.+?)\"', phrase)
                            if len(s) == 1:
                                s_real = str(s)[2: len(str(s)) - 2]
                                s_real1 = s_real.replace(' ', '')
                                word_sub_set.append(s_real1)
                            elif len(s) > 1:
                                for i in s:
                                    s_real = i[1:len(i) - 1]
                                    s_real1 = s_real.replace(' ', '')
                                    word_sub_set.append(s_real1)

                            s2 = phrase.replace('"' + s_real + '"', '').strip()

                            if len(s2) != 0:
                                for w in s2.split(','):
                                    for w1 in w.split(' '):
                                        word_sub_set.append(w1)
                        else:
                            for w in phrase.split(' '):
                                word_sub_set.append(w)
                        if word_sub_set not in words_set:
                            words_set.append(word_sub_set)
                return words_set

            def doc_cut(title, content):
                docs1 = []
                title = ''.join(title.split()).lower()
                content = ''.join(content.split()).lower()
                a = list(jieba.cut(title))
                b = list(jieba.cut(content))
                for w_t in a:
                    docs1.append(str(w_t))
                for w_c in b:
                    docs1.append(str(w_c))
                return docs1

            def print_time_consuming():
                step_final = datetime.datetime.now()
                logging.info("计算模块总耗时：" + str(step_final - begin))

            begin = datetime.datetime.now()
            json_data = json.loads(base64.urlsafe_b64decode(self.get_argument("json_data", None)).decode())

            title = json_data["title"]
            content = json_data['txt']

            logging.info("接收到的文章标题为：" + title)
            docs_core = read_data_from_json('1')
            if len(docs_core) == 0:
                ret = {"type": "error", "error_msg": "传入的核心词为空"}
                self.write(json.dumps(ret))
                print_time_consuming()
                return
            docs_include = read_data_from_json('2')
            docs_not_include = read_data_from_json('3')

            # logging.info("配置项 --> 核心词:" + str(len(docs_core)) + " 包含词:" + str(len(docs_include)) + " 排除词:" + str(len(docs_not_include)))

            docs1 = doc_cut(title, content)
            docs2 = [word for word in docs1 if word not in stop_words]
            if len(docs2) == 0:
                ret = {"type": "result", "result": "false", "msg": "经处理后，文章标题与内容词量为0"}
                self.write(json.dumps(ret))
                print_time_consuming()
                return

            num0 = 0
            for i in range(0, len(docs_core)):
                s = set(docs2) & (set(docs_core[i]))
                if len(s) == len(set(docs_core[i])):
                    num0 += 1
                    break

            if num0 == 0:
                ret = {"type": "result", "result": "false", "msg": "不符合核心词标准"}
                self.write(json.dumps(ret))
                print_time_consuming()
                return
            else:
                inc_num = len(docs_include)
                if inc_num != 0:
                    num1 = 0
                    for i in range(0, len(docs_include)):
                        s = set(docs2) & (set(docs_include[i]))
                        if len(s) == len(set(docs_include[i])):
                            num1 += 1
                            break

                    if num1 == 0:
                        ret = {"type": "result", "result": "false", "msg": "不符合包含词标准"}
                        self.write(json.dumps(ret))
                        print_time_consuming()
                        return

                not_inc_num = len(docs_not_include)
                if not_inc_num != 0:
                    not_inc_no_re = []
                    for j in range(0, len(docs_not_include)):
                        for word in docs_not_include[j]:
                            if word not in not_inc_no_re:
                                not_inc_no_re.append(word)

                    doc_not_inc_num = [i for i in docs2 if i in not_inc_no_re]

                    words_num = len(docs2)
                    not_inc = len(doc_not_inc_num)
                    if words_num <= 100 and not_inc == 0:
                        ret = {"type": "result", "result": "true"}
                        self.write(json.dumps(ret))
                        print_time_consuming()
                    else:
                        not_inc_pc = math.log(not_inc + 2) / math.log(words_num + 2)

                        if not_inc_pc > 0.15:
                            ret = {"type": "result", "result": "false", "msg": "不符合排除词标准"}
                            self.write(json.dumps(ret))
                            print_time_consuming()
                        else:
                            ret = {"type": "result", "result": "true"}
                            self.write(json.dumps(ret))
                            print_time_consuming()
                elif not_inc_num == 0:
                    ret = {"type": "result", "result": "true", "msg": "未配置排除词，结果准确率下降"}
                    self.write(json.dumps(ret))
                    print_time_consuming()

        except Exception as e:
            ret = '{"type": "error", "error_msg": "%s"}' % e
            self.write(json.dumps(ret))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logging.error(str(e) + "   " + str(exc_tb.tb_lineno))
            return


def stopService():
    tornado.ioloop.IOLoop.instance().stop()
    logging.info('---------exit-----------')
    os._exit(0)


def handler(signal_num, frame):
    logging.info("\nYou Pressed Ctrl-C.")
    stopService()


if __name__ == "__main__":
    app = App()
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    server.listen(17778)
    signal.signal(signal.SIGINT, handler)
    tornado.ioloop.IOLoop.instance().start()
