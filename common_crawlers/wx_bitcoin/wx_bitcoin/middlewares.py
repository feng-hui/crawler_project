# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import base64
import random
from scrapy.conf import settings
import logging
from urllib.parse import urljoin
from wx_bitcoin.common.ydm import YunDaMa
import requests
logger = logging.getLogger(__name__)


class WxBitcoinSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WxBitcoinDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class WxRedirectMiddleWare(object):

    base_url = "http://weixin.sogou.com/antispider/"

    # YDM 相关配置信息
    username = 'kapri12039'
    password = 'kapri12039!'
    ydm = YunDaMa(username, password)
    post_url = "http://weixin.sogou.com/antispider/thank.php"

    def process_response(self, request, response, spider):
        res_url = response.url
        code_img_url = response.xpath('//img[@id="seccodeImage"]/@src').extract_first("")
        if code_img_url:
            code_img_url = urljoin(self.base_url, code_img_url)
            img_content = self.get_source(code_img_url)
            captcha = self.ydm.get_captcha(img_content)
        else:
            return None

    @staticmethod
    def get_source(url):
        result = requests.get(url).content
        return result.decode(encoding='utf-8')


class ProxyMiddleWare(object):
    """阿布云的代理ip配置"""

    # 代理服务器
    proxyServer = "http://http-dyn.abuyun.com:9020"

    # 代理隧道验证信息
    proxyUser = "H930601LM27C00CD"
    proxyPass = "F35796ABA21C361B"

    proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")

    def __init__(self):
        super(ProxyMiddleWare, self).__init__()

    def process_request(self, request, spider):
        request.meta['proxy'] = self.proxyServer
        request.headers["Proxy-Authorization"] = self.proxyAuth


class UserAgentMiddleWare(object):

    user_agent_list = settings['USER_AGENT_LIST']

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = ua

