# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy.http import Request, FormRequest
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, HospitalAliasItem
from medicalmap.utils.common import now_day, custom_remove_tags, get_county2, match_special2, get_city, \
    MUNICIPALITY2, match_special, clean_info2


class ZsyjjkwSpider(scrapy.Spider):
    name = 'zsyjjkw'
    allowed_domains = ['zsyjjkw.com']
    start_urls = ['http://yygh.zsyjjkw.com/hospital/list']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'yygh.zsyjjkw.com',
        'Referer': 'http://yygh.zsyjjkw.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 5,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 3,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 32.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 16
    }
    host = 'http://yygh.zsyjjkw.com/'
    entry_url = 'http://yygh.zsyjjkw.com/hospital/list'
    hospital_post_url = 'http://yygh.zsyjjkw.com/hospital/pageList'
    hospital_detail_url = 'http://yygh.zsyjjkw.com/hospital/hospitalInfo/{}'
    data_source_from = '中山市医院预约挂号平台'

    def start_requests(self):
        data = {
            'page': '1',
            'hospitalName': '',
            'showCount': '25'
        }
        self.headers.update({
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://yygh.zsyjjkw.com',
            'X-Requested-With': 'XMLHttpRequest'
        })
        yield FormRequest(self.hospital_post_url,
                          headers=self.headers,
                          formdata=data,
                          callback=self.parse,
                          meta={
                              'now_page': data.get('page', '1'),
                              'total_pages': data.get('showCount', '0'),
                          })

    def parse(self, response):
        self.logger.info('>>>>>>正在抓取所有医院信息>>>>>>')
        all_hospitals = json.loads(response.text)
        for each_hospital in all_hospitals.get('list'):
            hospital_name = each_hospital.get('hospitalname')
            hospital_address = each_hospital.get('address')
            hospital_county = get_county2('中国|广东省|广东|中山市|中山', hospital_address)
            loader = CommonLoader2(item=HospitalInfoItem(), response=response)
            loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
            loader.add_value('hospital_addr', hospital_address, MapCompose(custom_remove_tags))
            loader.add_value('hospital_pro', '广东省')
            loader.add_value('hospital_city', '中山市')
            loader.add_value('hospital_county', hospital_county, MapCompose(custom_remove_tags))
            loader.add_value('hospital_phone', each_hospital.get('telephoneno'), MapCompose(custom_remove_tags))
            loader.add_value('hospital_intro', each_hospital.get('information'), MapCompose(custom_remove_tags))
            loader.add_value('registered_channel', self.data_source_from)
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('hospital_url', response.url)
            loader.add_value('update_time', now_day())
            hospital_item = loader.load_item()
            yield hospital_item

            # 获取科室信息、医生信息
            hospital_id = each_hospital.get('hospitalid')
            if hospital_id:
                self.headers['Referer'] = self.entry_url
                yield Request(self.hospital_detail_url.format(hospital_id),
                              headers=self.headers,
                              callback=self.parse_hospital_dep,
                              meta={
                                  'hospital_name': hospital_name
                              })

    def parse_hospital_dep(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取:[{}]科室信息>>>>>>'.format(hospital_name))
        try:
            all_dept_links = response.xpath('//div[@id="one_2"]/div/div/table/tbody/tr/td[@class="contentTd"]/a')
            for each_dept_link in all_dept_links:
                dept_name = each_dept_link.xpath('text()').extract_first('')
                dept_detail_link = each_dept_link.xpath('@href').extract_first('')
                dept_loader = CommonLoader2(item=HospitalDepItem(), response=response)
                dept_loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
                dept_loader.add_xpath('hospital_name', hospital_name, MapCompose(custom_remove_tags))
                dept_loader.add_value('dataSource_from', self.data_source_from)
                dept_loader.add_value('update_time', now_day())

                # 获取科室详细信息
                if dept_name and dept_detail_link:
                    self.headers['Referer'] = response.url
                    yield Request(urljoin(self.host, dept_detail_link),
                                  headers=self.headers,
                                  callback=self.parse_hospital_dep_detail,
                                  meta={
                                      'dept_name': dept_name,
                                      'dept_loader': dept_loader,
                                      'hospital_name': hospital_name
                                  },
                                  dont_filter=True)
        except Exception as e:
            self.logger.error('在抓取医院科室信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_dep_detail(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取:[{}]科室详细信息>>>>>>'.format(hospital_name))
        try:
            # 获取科室详细信息
            dept_loader = response.meta.get('dept_loader')
            dept_info = ''.join(response.xpath('//div[@class="kuang-s04"]').extract())
            dept_loader.add_value('dept_info', dept_info, MapCompose(remove_tags, custom_remove_tags, clean_info2))
            dept_loader.add_value('crawled_url', response.url)
            dept_item = dept_loader.load_item()
            yield dept_item

            # 获取医生信息
            self.logger.info('>>>>>>正在抓取:[{}]医生信息>>>>>>'.format(hospital_name))
            all_doctors_in_dept = response.xpath('//div[@id="recoudOld"]/ul/li[1]/a/@href').extract()
            for each_doctor_link in all_doctors_in_dept:
                self.headers['Referer'] = response.url
                yield Request(urljoin(self.host, each_doctor_link),
                              headers=self.headers,
                              callback=self.parse_doctor_info_detail,
                              dont_filter=True)
        except Exception as e:
            self.logger.error('在抓取医院科室详细信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info_detail(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取[{}]医生详细信息>>>>>>'.format(hospital_name))
        try:
            doctor_name = response.meta.get('doctor_name')
            dept_name = response.meta.get('dept_name')
            doctor_level = response.meta.get('doctor_level')
            doc_gt1 = remove_tags(''.join(response.xpath('//div[@class="intro_more"]').extract()))
            doc_gt2 = response.xpath('//dd[contains(text(),"擅长领域")]/text()').extract_first('')
            doctor_good_at = doc_gt1.replace('[关闭]', '') if doc_gt1 else doc_gt2
            loader = CommonLoader2(item=DoctorInfoItem(), response=response)
            loader.add_value('doctor_name', doctor_name, MapCompose(custom_remove_tags))
            loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
            loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
            loader.add_value('doctor_level', doctor_level, MapCompose(custom_remove_tags))
            loader.add_xpath('doctor_intro',
                             '//div[@class="hos-guide-box1"]',
                             MapCompose(remove_tags, custom_remove_tags))
            loader.add_value('doctor_goodAt',
                             doctor_good_at,
                             MapCompose(custom_remove_tags, match_special, clean_info2))
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('crawled_url', response.url)
            loader.add_value('update_time', now_day())
            doctor_item = loader.load_item()
            yield doctor_item
        except Exception as e:
            self.logger.error('在抓取医生详细信息的过程中出错了,原因是：{}'.format(repr(e)))
