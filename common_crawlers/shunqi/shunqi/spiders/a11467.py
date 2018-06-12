# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from shunqi.items import ShunqiItem, ShunQiItemLoader
from urllib.parse import urljoin


class A11467Spider(scrapy.Spider):
    name = '11467'
    allowed_domains = ['11467.com']
    host = 'http://b2b.11467.com'
    urls_list = [
        '//b2b.11467.com/search/3338-{}.htm',
        # '//b2b.11467.com/search/3339-{}.htm',
        # '//b2b.11467.com/search/3340-{}.htm',
        # '//b2b.11467.com/search/3341-{}.htm',
        # '//b2b.11467.com/search/3342-{}.htm',
        # '//b2b.11467.com/search/3343-{}.htm',
        # '//b2b.11467.com/search/3344-{}.htm',
        # '//b2b.11467.com/search/3345-{}.htm',
        # '//b2b.11467.com/search/3346-{}.htm',
        # '//b2b.11467.com/search/3347-{}.htm',
        # '//b2b.11467.com/search/3348-{}.htm',
        # '//b2b.11467.com/search/3349-{}.htm',
        # '//b2b.11467.com/search/3350-{}.htm',
        # '//b2b.11467.com/search/3351-{}.htm',
        # '//b2b.11467.com/search/3352-{}.htm',
        # '//b2b.11467.com/search/3353-{}.htm',
        # '//b2b.11467.com/search/3354-{}.htm',
        # '//b2b.11467.com/search/3355-{}.htm',
        # '//b2b.11467.com/search/3356-{}.htm',
        # '//b2b.11467.com/search/3357-{}.htm',
        # '//b2b.11467.com/search/3358-{}.htm',
        # '//b2b.11467.com/search/3359-{}.htm',
        # '//b2b.11467.com/search/3360-{}.htm',
        # '//b2b.11467.com/search/3361-{}.htm',
        # '//b2b.11467.com/search/3362-{}.htm',
        # '//b2b.11467.com/search/3363-{}.htm',
        # '//b2b.11467.com/search/3364-{}.htm',
        # '//b2b.11467.com/search/3365-{}.htm',
        # '//b2b.11467.com/search/3366-{}.htm',
        # '//b2b.11467.com/search/3367-{}.htm',
        # '//b2b.11467.com/search/3368-{}.htm',
        # '//b2b.11467.com/search/3369-{}.htm',
        # '//b2b.11467.com/search/3371-{}.htm',
        # '//b2b.11467.com/search/3372-{}.htm',
        # '//b2b.11467.com/search/3374-{}.htm',
        # '//b2b.11467.com/search/11739-{}.htm',
        # '//b2b.11467.com/search/12104-{}.htm'
    ]
    start_urls = [
        urljoin('http://b2b.11467.com', each_url.format(str(i))) for each_url in urls_list for i in range(1, 21)
    ]

    def start_requests(self):
        for each_url in self.start_urls:
            request = Request(each_url, callback=self.parse)
            request.meta['HOST'] = 'b2b.11467.com'
            request.meta['Referer'] = 'http://www.11467.com/'
            yield request

    def parse(self, response):
        comp_url_list = response.xpath('//div[@class="f_l"]/h4/a/@href').extract()
        if comp_url_list:
            for each_comp in comp_url_list:
                request = Request(each_comp.replace('//', 'http://'), callback=self.parse_detail)
                request.meta['HOST'] = 'www.11467.com'
                request.meta['Referer'] = response.url
                yield request

    def parse_detail(self, response):
        self.log('正在抓取的企业最终页的链接为：{}'.format(response.url))
        loader = ShunQiItemLoader(item=ShunqiItem(), response=response)
        loader.add_xpath('name', '//div[@id="logo"]/h1/text()')
        loader.add_xpath('address', '//dl[@class="codl"]/dd[1]/text()')
        loader.add_xpath('tel', '//dl[@class="codl"]/dd[2]/text()')
        loader.add_xpath('contact', '//dl[@class="codl"]/dd[3]/text()')
        loader.add_xpath('mobile', '//dl[@class="codl"]/dd[4]/text()')
        loader.add_xpath('email', '//dl[@class="codl"]/dd[5]/text()')
        if '在线QQ咨询' not in response.body.decode():
            loader.add_xpath('postal_code', '//dl[@class="codl"]/dd[6]/text()')
            loader.add_xpath('fax', '//dl[@class="codl"]/dd[7]/text()')
        else:
            loader.add_xpath('postal_code', '//dl[@class="codl"]/dd[7]/text()')
            loader.add_xpath('fax', '//dl[@class="codl"]/dd[8]/text()')
        loader.add_value('url', response.url)
        comp_item = loader.load_item()
        yield comp_item

