# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, get_county2, match_special2, now_year, now_time
from medicalmap.utils.city_code import care_link_cookies

class CarelinkSpider(scrapy.Spider):
    name = 'carelink'
    allowed_domains = ['carelink.cn']
    start_urls = ['https://www.carelink.cn/hos/hospital.htm']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': care_link_cookies,
        'Host': 'www.carelink.cn',
        'Referer': 'https://www.carelink.cn/index.htm',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': random.randint(1, 2),
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 16
    }
    host = 'https://www.carelink.cn'
    data_source_from = '快医网'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        try:
            all_hospital_links = response.xpath('//a[@class="search-result-hospital-name"]')
            for each_hospital_link in all_hospital_links:
                hospital_link = each_hospital_link.xpath('@href').extract_first('')
                hospital_name = each_hospital_link.xpath('text()').extract_first('')

                # 获取医院信息
                if hospital_link:
                    hospital_link = urljoin(self.host, hospital_link)
                    hospital_id = re.search(r'hi=(\d+)&', hospital_link)
                    self.headers['Referer'] = response.url
                    yield Request(hospital_link,
                                  headers=self.headers,
                                  callback=self.parse_hospital_info,
                                  dont_filter=True,
                                  meta={
                                      'hospital_name': hospital_name,
                                      'hospital_id': hospital_id
                                  })

                # 翻页
        except Exception as e:
            self.logger.error('在抓取医院信息的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_info(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取[{}]医院详细信息>>>>>>'.format(hospital_name))
        try:
            hospital_id = response.meta.get('hospital_id')
            hospital_img_url = response.xpath('//div[@class="divLeft_Img"]/img/@src').extract_first('')
            hospital_img_url = urljoin(self.host, hospital_img_url) if hospital_img_url else ''
            hospital_address = response.xpath('//div[@class="search-result-hospital-text"]/'
                                              'p[4]/text()').extract_first('')
            hospital_county = get_county2('中国|福建省|福建|厦门市|厦门', match_special2(hospital_address))
            loader = CommonLoader2(item=HospitalInfoItem(), response=response)
            loader.add_xpath('hospital_name',
                             '//span[@class="search-result-hospital-name"]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('hospital_addr', hospital_address, MapCompose(custom_remove_tags, match_special2))
            loader.add_value('hospital_pro', '')
            loader.add_value('hospital_city', '')
            loader.add_value('hospital_county', hospital_county, MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_phone',
                             '//div[@class="search-result-hospital-text"]/p[3]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_intro',
                             '//div[@class="introduceSpan"]',
                             MapCompose(remove_tags, custom_remove_tags))
            loader.add_value('registered_channel', self.data_source_from)
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('crawled_url', response.url)
            loader.add_value('update_time', now_day())
            loader.add_xpath('hospital_official_website',
                             '//li[contains(text(),"官网")]/text()',
                             MapCompose(custom_remove_tags, match_special2))
            loader.add_xpath('hospital_route',
                             '//li[contains(text(),"公交线路")]/text()',
                             MapCompose(custom_remove_tags, match_special2))
            loader.add_value('hospital_img_url', hospital_img_url)
            loader.add_value('gmt_created', now_time())
            loader.add_value('gmt_modified', now_time())
            loader.add_value('hospital_id', hospital_id)
            hospital_item = loader.load_item()
            yield hospital_item
        except Exception as e:
            self.logger.error('在抓取医院详细信息过程中出错了,原因是：{}'.format(repr(e)))
