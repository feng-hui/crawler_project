# -*- coding: utf-8 -*-
import scrapy
from medicalmap.items import HospitalInfoItem, HospitalDepItem, DoctorInfoItem, PxfybjyLoader
from medicalmap.utils.common import now_day
from scrapy.http import Request
from urllib.parse import urljoin


class PxfybjySpider(scrapy.Spider):
    name = 'pxfybjy'
    allowed_domains = ['pxfybjy.cn']
    start_urls = ['http://www.pxfybjy.cn/comcontent_detail/i=2&comContentId=2.html']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.pxfybjy.cn',
        'Referer': 'http://www.pxfybjy.cn/index.html',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 5
    }
    hospital_name = '郫县妇幼保健院'
    dep_link = 'http://www.pxfybjy.cn/products_list/pmcId=22.html'
    doctor_link = 'http://www.pxfybjy.cn/doctor/pmcId=24.html'
    host = 'http://www.pxfybjy.cn'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('正在抓取{}:医院信息'.format(self.hospital_name))
        loader = PxfybjyLoader(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '门诊上午_8:00-12:00;门诊下午14:00-17:30')
        loader.add_value('hospital_level', '三级乙等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '郫都区')
        loader.add_value('hospital_phone', '产科急救_028-87922244;儿科急救_028-87931629;产检门诊_028-87924116;'
                                           '婚检_028-87885339;儿保科_028-87931911')
        loader.add_xpath('hospital_intro', '//div[@class="FrontComContent_detail01-1468317290474_htmlbreak"]/'
                                           'p[position()<9]/text()')
        loader.add_value('is_medicare', '')
        loader.add_value('medicare_type', '')
        loader.add_value('vaccine_name', '')
        loader.add_value('is_cpc', '')
        loader.add_value('is_bdc', '')
        loader.add_value('cooperative_business', '')
        loader.add_value('hospital_district', '')
        loader.add_value('registered_channel', '')
        loader.add_value('dataSource_from', '官网:http://www.pxfybjy.cn/index.html')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        # 医院信息
        yield hospital_info_item
        # 科室信息
        request = Request(self.dep_link, headers=self.headers, callback=self.parse_hospital_dep)
        request.meta['Referer'] = response.url
        yield request
        # 医生信息

    def parse_hospital_dep(self, response):
        """获取医院科室信息"""
        self.logger.info('正在抓取{}:科室信息'.format(self.hospital_name))
        dep_type = response.xpath('//div[@class="menu-first"]/ul/li')
        for each_dep_type in dep_type:
            loader = PxfybjyLoader(item=HospitalDepItem(), selector=each_dep_type)
            loader.add_xpath('dept_type', 'a/text()')
            loader.add_value('hospital_name', self.hospital_name)
            dept_link = each_dep_type.xpath('a/@href').extract_first('')
            if dept_link:
                request = Request(urljoin(self.host, dept_link),
                                  headers=self.headers,
                                  callback=self.parse_dept_info,
                                  meta={'loader': loader})
                request.meta['Referer'] = response.url
                yield request

    def parse_dept_info(self, response):
        loader = response.meta['loader']
        all_dept_names = response.xpath('//div[@class="pic"]')
        for each_dept_name in all_dept_names:
            dept_detail_link = each_dept_name.xpath('a/@href').extract_first('')
            if dept_detail_link:
                dept_detail_link = urljoin(self.host, dept_detail_link)
                request = Request(dept_detail_link,
                                  headers=self.headers,
                                  callback=self.parse_dept_detail,
                                  meta={'loader': loader})
                request.meta['Referer'] = response.url
                yield request

    def parse_dept_detail(self, response):
        """医院科室详细信息"""
        self.logger.info('正在抓取{}:科室详细信息'.format(self.hospital_name))
        loader = response.meta['loader']
        loader.add_xpath('dept_name', '//li[@class="name1"]/text()')
        loader.add_xpath('dept_info', '//div[@class="FrontProducts_detail02-1468396987105_htmlbreak"]/p')
        loader.add_value('update_time', now_day())
        hospital_dep_item = loader.load_item()
        yield hospital_dep_item

    def parse_doctor_info(self, response):
        """获取医院医生信息"""
        pass
