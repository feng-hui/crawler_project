# -*- coding: utf-8 -*-
import scrapy


class SxyyghSpider(scrapy.Spider):
    name = 'sxyygh'
    allowed_domains = ['sxyygh.com']
    start_urls = ['http://sxyygh.com/']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.nj12320.org',
        'Referer': 'http://www.nj12320.org/njres/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        'DOWNLOAD_DELAY': 5,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 16
    }
    host = 'http://www.nj12320.org'

    def parse(self, response):
        pass
