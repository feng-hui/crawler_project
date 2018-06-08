# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from dianhua.items import DianhuaItem
from scrapy.http import FormRequest
import requests


class DianhuabangSpider(scrapy.Spider):
    name = 'dianhuabang'
    allowed_domains = ['dianhua.cn']
    # start_urls = [
    #     'https://m.dianhua.cn/mianyang/c16/p{}?apikey=wap'.format(str(each_page)) for each_page in range(2, 11)
    # ]
    start_urls = [
        'https://www.dianhua.cn/mianyang/c16/p2'
    ]
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        # 'Cookie': '_ga=GA1.2.2050639837.1528421351; _gid=GA1.2.1161884930.1528421351; temcity=mianyang; city_id=73; city_name=%E7%BB%B5%E9%98%B3; nid=qdPf5eH2VVLaV2lyT+c2T1iUOmI=; PHPSESSID=3drpt8phbma2pn0oei6f6u2in1; Hm_lvt_c136e57774590cd52d5e684e6421f853=1528421351,1528460267; Hm_lvt_824f91d3a04800a1d320314f2fd53aad=1528361141,1528421618,1528460550; Hm_lpvt_824f91d3a04800a1d320314f2fd53aad=1528460724; accesstoken=1898d950cd721646cbbc2d85b1f2fda860fa7f8e; accessseed=34339665; _gat=1; Hm_lpvt_c136e57774590cd52d5e684e6421f853=1528460825',
        'Host': 'www.dianhua.cn',
        'Upgrade-Insecure-Requests': '1',
        # 'Referer': "https://m.dianhua.cn/mianyang/c16/p1?apikey=wap",
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 '
                      '(KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
    }
    page_number = 1
    host = 'https://m.dianhua.cn/'
    # handle_httpstatus_list = [401]

    def start_requests(self):
        for each_url in self.start_urls:
            self.log('正在抓取第{}页:'.format(str(self.page_number)))
            self.page_number += 1
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        h_list = response.xpath('//title/text()').extract()
        print(h_list)
        # if h_list:
        #     for each_hos in h_list:
        #         loader = ItemLoader(item=DianhuaItem(), response=each_hos)
        #         loader.add_xpath('h_name', '//h5/a/text()')
        #         loader.add_xpath('h_tel', '//div[@class="tel_list _c_tel"]/p/text()')
        #         loader.add_xpath('h_address', '//div[@class="_c_addr"]/text()')
        #         h_item = loader.load_item()
        #         yield h_item
        # else:
        #     self.log('wrong')


    # def parse(self, response):
    #     self.log(response.status)
    #     all_hospital_links = response.xpath('//div[@class="list"]/a/@href').extract()
    #     if all_hospital_links:
    #         for each_link in all_hospital_links:
    #             each_link = urljoin(self.host, each_link)
    #             # self.log(each_link)
    #             # self.log(response.status)
    #             yield Request(each_link, headers=self.headers, callback=self.parse_detail)

    # def parse_detail(self, response):
    #     self.log('正在抓取内页，状态码为：{}'.format(str(response.status)))
    #     if response.status == 401:
    #         self.log('正在处理验证码，请手动输入验证码')
    #         # print(response.body)
    #         captcha = response.xpath('//img[@id="captcha"]/@src').extract()
    #         if captcha:
    #             captcha_link = urljoin(self.host, captcha[0]).replace('htpps', 'http')
    #             image_con = requests.get(captcha_link, headers=self.headers, allow_redirects=False).content
    #             with open('/home/fengh/wksp/captcha.jpeg', 'wb') as f:
    #                 f.write(image_con)
    #             self.log('请输入验证码，输入时间15s内：{}'.format(input()))
    #             # yield Request(captcha_link, headers=self.headers, callback=self.deal_auth_code)
    #             # yield FormRequest()
    #     else:
    #         self.log('正在抓取内页……')
    #         loader = ItemLoader(item=DianhuaItem(), response=response)
    #         loader.add_xpath('h_name', '//div[@class="info"]/h1/text()')
    #         loader.add_xpath('h_tel', '//*[@id="main_body"]/section[2]/dl[1]/dt/div/h1/a/text()')
    #         loader.add_xpath('h_address', '//*[@id="main_body"]/section[2]/dl[2]/dt/div/p/text()')
    #         h_item = loader.load_item()
    #         yield h_item
