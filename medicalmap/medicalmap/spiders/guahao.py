# -*- coding: utf-8 -*-
import scrapy


class GuahaoSpider(scrapy.Spider):
    name = 'guahao'
    allowed_domains = ['guahao.gov.cn']
    start_urls = ['http://guahao.gov.cn/']

    def parse(self, response):
        pass
