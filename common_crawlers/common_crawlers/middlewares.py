# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
import time
import logging
import random
from fake_useragent import UserAgent
logger = logging.getLogger(__name__)


class CommonCrawlersSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class JsMiddleWare(object):

    def process_request(self, request, spider):
        if spider.name == "jobbole":
            spider.browser.get(request.url)
            time.sleep(3)  # 加载结束
            logger.info("正在访问的页面链接为：{0}".format(request.url))
            return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source,
                                encoding='utf-8', request=request)


class RandomUserAgentMiddleWare(object):
    """随机切换user-agent，需要自己维护"""

    def __init__(self, crawler):
        super(RandomUserAgentMiddleWare, self).__init__()
        self.user_agent_list = crawler.settings.get('USER_AGENT_LIST', [])

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.user_agent_list))


class RandomUserAgentMiddleWare2(object):
    """
    利用fake-useragent来获取对应的user-agent
    安装方法: pip install fake-useragent，使用方法可参考github上的说明或者如下所写的方法都可以
    缺陷：第一次使用会比较慢，会有一个加载的过程
    """

    def __init__(self, crawler):
        super(RandomUserAgentMiddleWare2, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):

        def get_ua():
            """随机获取设置号的ua"""
            return getattr(self.ua, self.ua_type)

        random_agent = get_ua()

        request.headers.setdefault('User-Agent', random_agent)
