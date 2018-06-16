# # -*- coding: utf-8 -*-
# import scrapy
# from scrapy.http import Request
# from scrapy.loader import ItemLoader
# from shunqi.items import ShunqiItem
# from urllib.parse import urljoin
#
#
# class A11467Spider(scrapy.Spider):
#     name = '11467'
#     allowed_domains = ['11467.com']
#     urls_list = [
#         'http://m.11467.com/b2b/search/3338.htm'
#     ]
#     start_urls = [
#         '{0}{1}'.format(each_url.replace('.htm', ''), '-' + str(i) + '.htm')
#         for each_url in urls_list
#         for i in range(1, 2)
#     ]
#     host = 'http://m.11467.com'
#
#     def start_requests(self):
#         for each_url in self.start_urls:
#             request = Request(each_url, callback=self.parse)
#             request.meta['Referer'] = 'http://m.11467.com/b2b/'
#             yield request
#
#     def parse(self, response):
#         comp_url_list = response.xpath('//div[@class="f_l"]/h4/a/@href').extract()
#         if comp_url_list:
#             for each_comp in comp_url_list:
#                 request = Request(urljoin(self.host, each_comp), callback=self.parse_detail)
#                 request.meta['Referer'] = response.url
#                 yield request
#
#     def parse_detail(self, response):
#         self.log('正在抓取的企业最终页的链接为：{}'.format(response.url))
#         loader = ItemLoader(item=ShunqiItem(), response=response)
#         loader.add_xpath('name', '//span[@class="navleft"]/text()')
#         loader.add_xpath('address', '//div[@id="contact"]/div/dl/dd[1]/text()')
#         loader.add_xpath('tel', '//div[@id="contact"]/div/dl/dd[2]/em/text()')
#         loader.add_xpath('contact', '//div[@id="contact"]/div/dl/dd[3]/text()')
#         loader.add_xpath('mobile', '//div[@id="contact"]/div/dl/dd[4]/em/text()')
#         loader.add_xpath('email', '//div[@id="contact"]/div/dl/dd[5]/text()')
#         if '在线QQ咨询' not in response.body.decode():
#             loader.add_xpath('postal_code', '//div[@id="contact"]/div/dl/dd[6]/text()')
#             loader.add_xpath('fax', '//div[@id="contact"]/div/dl/dd[7]/text()')
#         else:
#             loader.add_xpath('postal_code', '//div[@id="contact"]/div/dl/dd[7]/text()')
#             loader.add_xpath('fax', '//div[@id="contact"]/div/dl/dd[8]/text()')
#         comp_item = loader.load_item()
#         yield comp_item
#
