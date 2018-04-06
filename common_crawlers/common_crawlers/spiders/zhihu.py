# -*- coding: utf-8 -*-
import time
import scrapy
from scrapy.http import Request, FormRequest


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    login_url = "https://www.zhihu.com/signup"
    test_url = "https://www.zhihu.com/inbox"
    host_url = "https://www.zhihu.com/"
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    grant_type = 'password'
    timestamp = str(int(time.time() * 1000))
    source = 'com.zhihu.web'
    signature = ''
    username = '+8618610379194'
    password = 'tuyue7208562'
    captcha = ''
    lang = 'cn'
    ref_source = 'homepage'
    utm_source = ''
    headers = {
        'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
        'origin': 'https://www.zhihu.com',
        'refer': 'https://www.zhihu.com/signup?next=%2F',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    }

    def get_signature(self):
        """获取签名"""
        pass

    def start_requests(self):
        yield Request(self.host_url, headers=self.headers, callback=self.to_login)

    def to_login(self, response):
        self.logger.info(response.xpath('//title/text()').extract_first())

    def is_login(self, response):
        pass

    def parse(self, response):
        pass

