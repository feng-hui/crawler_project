# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, get_county2, match_special2, clean_info, clean_info2
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem


class SxyyghSpider(scrapy.Spider):
    name = 'sxyygh'
    allowed_domains = ['sxyygh.com']
    start_urls = ['http://sxyygh.com/gh/index_hos.asp?cityid=&addrcountryid=&gradeid=&simplespell='
                  '&hospitalname=&hosptype=1']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'sxyygh.com',
        'Referer': 'http://sxyygh.com/index.asp',
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
    host = 'http://sxyygh.com'
    hospital_host = 'http://sxyygh.com/gh/'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        self.logger.info('>>>>>>正在抓取:医院信息>>>>>>')
        try:
            all_hospital_links = response.xpath('/table[@id="T1"]/tbody/tr/td[2]/a/@href').extract()
            for each_hospital_link in all_hospital_links:
                hospital_link = urljoin(self.hospital_host, each_hospital_link)
                self.headers['Referer'] = response.url
                yield Request(hospital_link,
                              headers=self.headers,
                              callback=self.parse_hospital_info,
                              dont_filter=True)
        except Exception as e:
            self.logger.error('在抓取医院的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_info(self, response):
        self.logger.info('>>>>>>正在抓取:医院详细信息和科室信息>>>>>>')
        try:
            # 获取医院信息
            loader = CommonLoader2(item=HospitalInfoItem(), response=response)
            loader.add_xpath('hospital_name', '//div[@class="yy_til"]/h2/text()', MapCompose(custom_remove_tags))
            loader.add_value('hospital_level',
                             response.meta.get('hospital_level'),
                             MapCompose(custom_remove_tags, clean_info))
            loader.add_xpath('hospital_addr',
                             '//div[@class="yy_js clearfix"]/div/dl/dd[1]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('hospital_pro', '山西省')
            loader.add_value('hospital_city', '')
            loader.add_value('hospital_county', )
            loader.add_xpath('hospital_phone',
                             '//div[@class="yy_js clearfix"]/div/dl/dd[2]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_intro', '//dd[@id="wrap"]', MapCompose(remove_tags, custom_remove_tags))
            loader.add_value('registered_channel', '山西省预约诊疗服务平台')
            loader.add_value('dataSource_from', '山西省预约诊疗服务平台')
            loader.add_value('update_time', now_day())
            hospital_info_item = loader.load_item()
            yield hospital_info_item

            # 获取科室信息
            # self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>')
            all_dept_links = response.xpath('//dl[@class="kfyy clearfix"]/dd/span/a/@href').extract()
            for each_dept_link in all_dept_links:
                dept_link = urljoin(self.host, re.sub(r';jsessionid=(.*?)\?', '?', each_dept_link))
                self.headers['Referer'] = response.url
                yield Request(dept_link, headers=self.headers, callback=self.parse_hospital_dep_detail)
        except Exception as e:
            self.logger.error('在抓取医院详细信息和科室的过程中出错了,原因是：{}'.format(repr(e)))



