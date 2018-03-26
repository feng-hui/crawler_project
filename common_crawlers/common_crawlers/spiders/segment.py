# -*- coding: utf-8 -*-
import scrapy
import logging
from pydispatch import dispatcher
from scrapy import signals
logger = logging.getLogger(__name__)


class SegmentSpider(scrapy.Spider):
    name = 'segment'
    allowed_domains = ['segment.com']
    start_urls = [
        'https://segmentfault.com/t/python2',
        'https://segmentfault.com/t/python4'
    ]
    # scrapy只处理200~300的response，其他的均忽略
    # 设置可以参考http://scrapy-chs.readthedocs.io/zh_CN/stable/topics/spider-middleware.html
    handle_httpstatus_list = [404]  # 让scrapy处理返回404状态码的请求

    def __init__(self):
        self.failed_urls = []
        super(SegmentSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self):
        """在scrapy发出spider_closed信号的时候触发该函数"""
        self.crawler.stats.set_value("failed_urls", ','.join(self.failed_urls))

    def parse(self, response):
        """测试收集器stats的使用"""
        if response.status == 404:
            self.failed_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")
        title = response.xpath('//title/text()').extract()[0]
        logger.info("正在抓取的页面的标题是：{0}".format(title))
