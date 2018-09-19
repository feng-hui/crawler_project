# -*- coding: utf-8 -*-
import scrapy


class CarelinkSpider(scrapy.Spider):
    name = 'carelink'
    allowed_domains = ['carelink.cn']
    start_urls = ['http://carelink.cn/']

    def parse(self, response):
        pass
