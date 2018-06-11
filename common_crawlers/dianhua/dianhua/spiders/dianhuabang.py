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
    url_list = [
        'https://m.dianhua.cn/mianyang/c16/p{}?apikey=wap'.format(str(each_page)) for each_page in range(2, 11)
    ]
    start_urls = [
        'https://m.dianhua.cn/mianyang/c16?apikey=wap'
    ]
    start_urls.extend(url_list)

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.dianhua.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 '
                      '(KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Cookie': '_ga=GA1.2.2050639837.1528421351; _gid=GA1.2.1277505859.1528618861; temcity=mianyang; city_id=73; city_name=%E7%BB%B5%E9%98%B3; PHPSESSID=75oghiv683ajm3qpe6uecub431; nid=qdPf5eH2VVLaV2lyT+c2T1iUOmI=; Hm_lvt_c136e57774590cd52d5e684e6421f853=1528460267,1528618861,1528697614,1528720247; Hm_lvt_824f91d3a04800a1d320314f2fd53aad=1528421618,1528460550,1528697819,1528720273; accesstoken=8dcbb6b317b5af5215a67969dcf6f6d467f218b1; accessseed=79675979; _gat=1; Hm_lpvt_c136e57774590cd52d5e684e6421f853=1528727681; Hm_lpvt_824f91d3a04800a1d320314f2fd53aad=1528727685'
    }
    page_number = 1
    host = 'https://m.dianhua.cn/'
    handle_httpstatus_list = [401]

    def start_requests(self):
        for each_url in self.start_urls:
            self.log('正在抓取第{}页:'.format(str(self.page_number)))
            self.page_number += 1
            yield Request(each_url, callback=self.parse)

    def parse(self, response):
        # print(response.body.decode())
        if response.status == 401:
            self.log('出现验证码，请及时更换cookies……')
        else:
            self.log('未出现验证码，可正常抓取……')
            h_list = response.xpath('//*[@id="main"]/div/div[2]/div[2]/div[1]/div')
            if h_list:
                for each_hos in h_list:
                    loader = ItemLoader(item=DianhuaItem(), selector=each_hos)
                    loader.add_xpath('h_name', '//h5/a/text()')
                    loader.add_xpath('h_tel', '//div[@class="tel_list _c_tel"]/p/text()')
                    loader.add_xpath('h_address', '//div[@class="_c_addr"]/text()')
                    h_item = loader.load_item()
                    yield h_item
