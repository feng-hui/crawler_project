# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
import logging
logger = logging.getLogger(__name__)
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["jobbole.com"]
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def __init__(self):
        self.browser = webdriver.Chrome()
        super(JobboleSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self):
        logger.info("jobbole 爬虫已经结束，接下来会关闭打开的浏览器……")
        self.browser.quit()

    def parse(self, response):
        title = response.xpath('//title/text()').extract()[0]
        logger.info('正在访问的页面的标题是： {0}'.format(title))
