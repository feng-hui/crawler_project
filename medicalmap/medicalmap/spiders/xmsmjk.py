# -*- coding: utf-8 -*-
import scrapy


class XmsmjkSpider(scrapy.Spider):
    name = 'xmsmjk'
    allowed_domains = ['xmsmjk.com']
    start_urls = ['http://xmsmjk.com/']

    def parse(self, response):
        pass
