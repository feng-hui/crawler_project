# -*- coding: utf-8 -*-
import scrapy


class PxfybjySpider(scrapy.Spider):
    name = 'pxfybjy'
    allowed_domains = ['pxfybjy.cn']
    start_urls = ['http://pxfybjy.cn/']

    def parse(self, response):
        pass
