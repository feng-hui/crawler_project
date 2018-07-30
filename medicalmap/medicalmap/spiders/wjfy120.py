# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, filter_info, filter_info2
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem


class Wjfy120Spider(scrapy.Spider):
    """
    成都市温江区妇幼保健院
    """
    name = 'wjfy120'
    allowed_domains = ['wjfy120.com']
    start_urls = ['http://wjfy120.com/']

    hospital_intro_link = 'https://www.wjfy120.com/News/View.asp?ID=1'
    dept_link = 'https://www.wjfy120.com/News/Category.asp?ID=27'
    dept_entry = 'https://www.wjfy120.com/News/Category.asp?ID=4'
    doctor_link = 'https://www.wjfy120.com/News/Category.asp?ID=38'
    doctor_entry = 'https://www.wjfy120.com/News/Category.asp?ID=5'
    hospital_name = '成都市温江区妇幼保健院'
    host = 'https://www.wjfy120.com'
    dept_crawled_cnt = 0
    doctor_crawled_cnt = 0
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.wjfy120.com',
        'Referer': 'https://www.wjfy120.com/index.asp',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        'DOWNLOAD_DELAY': 3,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 10,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 5.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        # 'CONCURRENT_REQUESTS': 16
    }

    def start_requests(self):
        # 医院信息
        yield Request(self.hospital_intro_link, headers=self.headers, callback=self.parse)
        # 科室信息
        dept_request = Request(self.dept_link, headers=self.headers, callback=self.parse_hospital_dep)
        self.headers['Referer'] = self.dept_entry
        yield dept_request
        # 医生信息
        doctor_request = Request(self.doctor_link, headers=self.headers, callback=self.parse_doctor_info)
        self.headers['Referer'] = self.doctor_entry
        yield doctor_request

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('>>>>>>正在抓取{}:医院信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '')
        loader.add_value('hospital_level', '三级乙等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '妇幼保健院')
        loader.add_value('hospital_addr', '成都市温江区万春路140')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '')
        loader.add_value('hospital_phone', '24小时急救电话_028-82723131;咨询电话_围产期保健_028-82715727;'
                                           '咨询电话_妇科门诊_028-82711383;咨询电话_儿童保健_028-82711527;'
                                           '咨询电话_婚检科_028-82720337;'
                                           '投诉电话_028-82724901(上班时间);投诉电话_13688488598(下班时间)')
        loader.add_xpath('hospital_intro',
                         '//div[@id="info_txt"]',
                         MapCompose(remove_tags, custom_remove_tags))
        # loader.add_value('is_medicare', '是')
        # loader.add_value('medicare_type', '')
        loader.add_value('registered_channel', '电话预约;挂号窗口;医院微信公众号')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

    def parse_hospital_dep(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        has_more_dept = response.xpath('//div[@id="current"]/span/a[contains(text(),"更多")]/@href').extract()
        if has_more_dept:
            for each_dept_link in has_more_dept:
                dept_request = Request(urljoin(self.host, each_dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep)
                self.headers['Referer'] = response.url
                yield dept_request
        else:
            dept_detail_link = response.xpath('//div[@class="list1"]/ul/li/a[contains(text(),"科室介绍") or '
                                              'contains(text(), "简介")]/@href').extract_first('')
            dept_name1 = response.xpath('//div[@class="list1"]/ul/li[2]/a/text()').extract_first('')
            dept_name2 = response.xpath('//div[@id="current"]/a[3]/text()').extract_first('')
            dept_detail_link2 = response.xpath('//div[@class="list1"]/ul/li[2]/a/@href').extract_first('')
            if dept_detail_link:
                # 科室介绍的名称中包含科室介绍或简介
                dept_detail_request = Request(urljoin(self.host, dept_detail_link),
                                              headers=self.headers,
                                              callback=self.parse_hospital_dep_detail)
                self.headers['Referer'] = response.url
                yield dept_detail_request
            elif dept_name1 == dept_name2 and dept_detail_link2:
                # 科室介绍的名称中不包含科室介绍或简介
                dept_detail_request = Request(urljoin(self.host, dept_detail_link2),
                                              headers=self.headers,
                                              callback=self.parse_hospital_dep_detail)
                self.headers['Referer'] = response.url
                yield dept_detail_request
            else:
                # 不存在二级科室
                loader = CommonLoader2(item=HospitalDepItem(), response=response)
                loader.add_xpath('dept_type',
                                 '//div[@id="current"]/a[2]/text()',
                                 MapCompose(custom_remove_tags))
                loader.add_value('hospital_name', self.hospital_name)
                loader.add_xpath('dept_name',
                                 '//div[@id="current"]/a[2]/text()',
                                 MapCompose(custom_remove_tags))
                loader.add_value('update_time', now_day())
                dept_item = loader.load_item()
                yield dept_item

        # 抓取其他科室信息
        other_dept_links = response.xpath('//div[@id="left1"]/span[position()>1]/a/@href').extract()
        self.dept_crawled_cnt += 1
        if self.dept_crawled_cnt <= 1 and other_dept_links:
            for each_other_dept in other_dept_links:
                dept_request = Request(urljoin(self.host, each_other_dept),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep)
                self.headers['Referer'] = response.url
                yield dept_request

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_xpath('dept_type',
                         '//div[@id="current"]/a[2]/text()',
                         MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_xpath('dept_name',
                         '//div[@id="current"]/a[last()]/text()',
                         MapCompose(custom_remove_tags))
        loader.add_xpath('dept_info',
                         '//div[@id="info_txt"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        """
        未过滤专家名称为：[专家介绍]的链接
        """
        self.logger.info('>>>>>>正在抓取{}:医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//div[@class="list1"]/ul/li')
        for each_doctor_link in doctor_links:
            doctor_link = each_doctor_link.xpath('a/@href').extract_first('')
            dept_name = response.xpath('//div[@id="current"]/a[2]/text()').extract_first('')
            if doctor_link and dept_name:
                doctor_detail_request = Request(urljoin(self.host, doctor_link),
                                                headers=self.headers,
                                                callback=self.parse_doctor_info_detail,
                                                meta={'dept_name': dept_name},
                                                dont_filter=True)
                self.headers['Referer'] = response.url
                yield doctor_detail_request

        # 抓取其他科室医生信息
        other_dept_links = response.xpath('//div[@id="left1"]/span[position()>1]/a/@href').extract()
        self.doctor_crawled_cnt += 1
        if self.doctor_crawled_cnt <= 1 and other_dept_links:
            for each_other_dept in other_dept_links:
                doctor_request = Request(urljoin(self.host, each_other_dept),
                                         headers=self.headers,
                                         callback=self.parse_doctor_info)
                self.headers['Referer'] = response.url
                yield doctor_request

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生详细信息>>>>>>'.format(self.hospital_name))
        dept_name = response.meta['dept_name']
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_xpath('doctor_name',
                         '//div[@id="info_title"]/text()',
                         MapCompose(custom_remove_tags, match_special))
        loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', self.hospital_name)
        # loader.add_value('doctor_level', doctor_level, MapCompose(custom_remove_tags, match_special))
        loader.add_xpath('doctor_intro',
                         '//div[@id="info_txt"]',
                         MapCompose(remove_tags, custom_remove_tags, filter_info2))
        loader.add_xpath('doctor_goodAt',
                         '//div[@id="info_txt"]',
                         MapCompose(remove_tags, custom_remove_tags, filter_info))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item

    def parse_doctor_reg_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生排班信息>>>>>>'.format(self.hospital_name))
