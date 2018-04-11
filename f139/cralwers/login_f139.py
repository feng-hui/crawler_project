# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/3/30 10:51'
# @email = 'fengh@asto-inc.com'
import requests
import logging
from lxml import etree
LOG_FORMAT = '%(asctime)s %(name)s [%(module)s] %(levelname)s: %(message)s'
logging.basicConfig(format=LOG_FORMAT, level='INFO')


class F139Login2(object):
    """单独的富宝登录模块，可搭配使用，整合一下项目即可"""

    login_url = "http://passport.f139.com/doLogin.do"
    login_page = "http://passport.f139.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Referer': 'http://passport.f139.com/login.do?url=http://member.f139.com/center/index.do',
        'Host': 'passport.f139.com',
        'Origin': 'http://passport.f139.com'
    }
    data_url = "http://news.f139.com/list.do?channelID=79&categoryID=6"

    def __init__(self):
        super(F139Login2, self).__init__()
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self.timeout = 10

    def get_html(self, url):
        """获取url对应的html内容,适用于css或正则等方法,utf-8编码"""
        html = requests.get(url, headers=self.headers, timeout=self.timeout).text
        return html

    def get_selector(self, url):
        """获取url对应的selector,适用于xpath方法"""
        html = self.get_html(url)
        selector = etree.HTML(html)
        return selector

    def get_token(self):
        """获取登录需要的token"""
        self.logger.info('>>>>>>正在获取需要登录的token……')
        selector = self.get_selector(self.login_page)
        token = selector.xpath('//input[@name="token"]/@value')[0]
        self.logger.info('>>>>>>获取的token为：{}'.format(token))
        return token

    def get_location_url(self):
        """登录跳转,禁止跳转,直接post登录获取cookies"""
        self.logger.info('>>>>>>正在模拟登录获取需要的cookies……')
        data = {
            'url':  'http://member.f139.com/center/index.do',
            'token': self.get_token(),
            'userName': 'judyhe',
            'passWord': '123456'
        }
        html = self.session.post(self.login_url, data=data, headers=self.headers2, allow_redirects=False)
        status_code = html.status_code
        if status_code == 302:
            location_url = html.headers.get('location')
            # print(self.session.cookies)
            # print(location_url)
            return location_url
        else:
            return ""

    def get_cookies(self):
        """登录获取cookies"""
        self.logger.info('>>>>>>正在模拟登录获取需要的cookies……')
        data = {
            'url': 'http://member.f139.com/center/index.do',
            'token': self.get_token(),
            'userName': 'judyhe',
            'passWord': '123456'
        }
        html = self.session.post(self.login_url, data=data, headers=self.headers2, allow_redirects=False)
        status_code = html.status_code
        if status_code == 302:
            return self.session.cookies
        else:
            return ""

    def is_login(self):
        """判断是否登录"""
        html = self.session.get(self.data_url, headers=self.headers, allow_redirects=False)
        status_code = html.status_code
        if status_code != 200:
            self.logger.info('>>>>>>模拟登录失败……')
            return False
        else:
            # print(html.text)
            self.logger.info('>>>>>>模拟登录成功……')
            return True

    def crawl_data(self):
        """获取数据中"""
        self.logger.info('>>>>>>>抓取数据中,即将返回页面标题……')
        html = self.session.get(self.data_url, headers=self.headers).text
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')
        if title:
            title = title[0]
        else:
            title = ""
        self.logger.info('>>>>>>>获取到的标题为：{0}'.format(title if title else '未获取到标题'))
        return title


if __name__ == "__main__":
    f139_login = F139Login2()
    try:
        redirect_url = f139_login.get_location_url()
        if redirect_url:
            # f139_login.get_login_info(redirect_url)
            if f139_login.is_login():
                f139_login.crawl_data()
    except Exception as e:
        f139_login.logger.error('>>>>>>抓取过程中出错了,出错的原因是：{}'.format(e))
