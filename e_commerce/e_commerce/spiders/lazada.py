# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from e_commerce.items import ECommerceLoader, ECommerceItem


class LazadaSpider(scrapy.Spider):
    name = 'lazada'
    allowed_domains = ['lazada.com.my']
    start_urls = ['https://www.lazada.com.my/shop-mobiles/']

    headers = {
        ':authority': 'www.lazada.com.my',
        ':method': 'GET',
        ':path': '/shop-mobiles/',
        ':scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 5,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 3,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 64.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 16
    }
    host = 'http://yyk.39.net/'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        all_products = response.xpath('//div[@class="c3KeDq"]')
        for each_product in all_products:
            product_name = each_product.xpath('')
