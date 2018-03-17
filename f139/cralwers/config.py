# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/2/28 17:19'
# @email = 'fengh@asto-inc.com'
import logging
import time

# # 1、日志格式
LOG_FORMAT = '%(asctime)s %(name)s [%(module)s] %(levelname)s: %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logging.getLogger(__name__).setLevel(logging.INFO)


# 基本配置类
class F139Config(object):

    # 文章标题的时间格式
    now_month1 = time.localtime().tm_mon
    now_day1 = time.localtime().tm_mday
    now_month = '{}'.format('0' + str(now_month1) if now_month1 < 10 else str(now_month1))
    now_day = '{}'.format('0' + str(now_day1) if now_day1 < 10 else str(now_day1))
    prefix_of_title = '{}月{}日'.format(now_month, now_day)

    # 富宝账号与密码等配置文件
    account = {
        'username': 'Judyhe',
        'password': '123456'
    }

    # headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/64.0.3282.186 Safari/537.36'
    }


# 日志设置类
class Logger(object):

    log_format = '%(asctime)s %(name)s [%(module)s] %(levelname)s: %(message)s'

    def __init__(self, name="Default"):
        self.logger = logging.getLogger(name)
        self.init_logger()

    def init_logger(self):
        self.logger.propagate = False
        handler = logging.StreamHandler()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(self.log_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        # self.logger.removeHandler(handler)

f139_config = F139Config()
f139_logger = Logger('F139Cralwers')
