# -*- coding: utf-8 -*-
import datetime
import scrapy
from scrapy.http import Request
from shunqi.items import ShunqiItem, ShunQiItemLoader
from urllib.parse import urljoin
from shunqi.type_id import TYPE_ID_LIST
from scrapy.exceptions import CloseSpider


class A11467Spider(scrapy.Spider):
    name = '11467'
    allowed_domains = ['11467.com']
    host = 'http://b2b.11467.com'
    id_list = list(set(TYPE_ID_LIST))
    start_urls = [
        'http://b2b.11467.com/search/{}.htm'.format(each_id) for each_id in id_list
    ]

    def start_requests(self):
        for each_url in self.start_urls:
            request = Request(each_url, callback=self.parse)
            request.meta['HOST'] = 'b2b.11467.com'
            request.meta['Referer'] = 'http://www.11467.com/'
            yield request

    def parse(self, response):
        self.log('正在抓取的列表页的链接为：{}'.format(response.url))
        comp_url_list = response.xpath('//div[@class="f_l"]/h4/a/@href').extract()
        if comp_url_list:
            for each_comp in comp_url_list:
                request = Request(each_comp.replace('//', 'http://'), callback=self.parse_detail)
                request.meta['HOST'] = 'www.11467.com'
                request.meta['Referer'] = response.url
                yield request
            next_page = response.xpath('//div[@class="pages"]/a[contains(text(), "下一页")]/@href').extract_first()
            if next_page:
                next_page_url = urljoin(self.host, next_page)
                request_next = Request(next_page_url, callback=self.parse)
                request_next.meta['HOST'] = 'b2b.11467.com'
                request_next.meta['Referer'] = response.url
                yield request_next

    def parse_detail(self, response):
        source_code = response.body.decode()
        self.log('正在抓取的企业最终页的链接为：{}'.format(response.url))
        if '采集大神饶命' in source_code:
            self.log('该ip已经被反爬……')
            # raise CloseSpider('爬取频率过高,出现反爬,请降低频率或使用代理ip……')
        loader = ShunQiItemLoader(item=ShunqiItem(), response=response)
        loader.add_xpath('name', '//div[@id="logo"]/h1/text()')
        loader.add_xpath('address', '//dl[@class="codl"]/dd[1]/text()')
        loader.add_xpath('tel', '//dl[@class="codl"]/dd[2]/text()')
        loader.add_xpath('contact', '//dl[@class="codl"]/dd[3]/text()')
        loader.add_xpath('mobile', '//dl[@class="codl"]/dd[4]/text()')
        loader.add_xpath('email', '//dl[@class="codl"]/dd[5]/text()')
        loader.add_value('crawl_time', datetime.datetime.now())
        if '在线QQ咨询' not in source_code:
            loader.add_xpath('postal_code', '//dl[@class="codl"]/dd[6]/text()')
            loader.add_xpath('fax', '//dl[@class="codl"]/dd[7]/text()')
        else:
            loader.add_xpath('postal_code', '//dl[@class="codl"]/dd[7]/text()')
            loader.add_xpath('fax', '//dl[@class="codl"]/dd[8]/text()')
        loader.add_value('url', response.url)
        comp_item = loader.load_item()
        yield comp_item
