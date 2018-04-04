# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    login_url = "https://www.zhihu.com/signup"
    test_url = "https://www.zhihu.com/inbox"
    host_url = "https://www.zhihu.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
    }

    def start_requests(self):
        return Request(self.host_url, headers=self.headers, callback=self.to_login)

    def to_login(self, response):
        xsrf = response.xpath('//')
        pass

    def is_login(self, response):
        pass

    def parse(self, response):
        pass
