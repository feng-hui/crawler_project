# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/3/6 16:13'
# @email = 'fengh@asto-inc.com'
import requests
import logging
from lxml import etree
from ..config import f139_config
from ..login import F139Login


class F139Price(object):

    job_name = '富宝废有色报价抓取——每天执行时间11:10,重庆废铝13:00'
    login_url = "http://member.f139.com/center/index.do"
    test_url = login_url
    data_url = "http://data.f139.com/list.do?vid=137"
    title = "富宝废有色报价抓取"

    def __init__(self, session: requests.Session):
        self.session = session

    def login(self):
        """登录并更新cookies"""
        try:
            f139_cookies = F139Login(f139_config.account['username'], f139_config.account['password'])
            self.session.cookies.update(f139_cookies)
        except KeyError:
            logging.info("获取用户名、密码错误,请检查配置文件")
        except Exception as e:
            logging.info("登录过程中发生错误,错误的原因是: {}".format(e))

    def is_login(self):
        """判断是否登录"""
        r = self.session.get(self.test_url, headers=f139_config.headers, allow_redirects=False)
        location = r.headers.get('location', 'nothing')
        status_code = r.status_code
        if status_code == 302 or 'passport.139.com' in location:
            return False
        elif status_code == 200:
            return True
        else:
            return False

    def get_html(self, url):
        """获取url对应的html内容,适用于css或正则等方法"""
        html = self.session.get(url, headers=f139_config.headers)
        return html

    def get_selector(self, url):
        """获取url对应的selector,适用于xpath方法"""
        html = self.get_html(url).text
        selector = etree.HTML(html)
        return selector

    def run(self):
        """登录之后运行爬虫"""
        pass

