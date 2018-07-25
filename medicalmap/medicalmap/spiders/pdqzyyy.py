# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem


class PdqzyyySpider(scrapy.Spider):
    """
    郫都区中医医院
    """
    name = 'pdqzyyy'
    allowed_domains = ['pdqzyyy.com']
    start_urls = ['http://www.pdqzyyy.com/pdqzyyjj/8.jhtml']

    hospital_intro_link = 'http://www.pdqzyyy.com/pdqzyyjj/8.jhtml'
    dept_link = 'http://www.pdqzyyy.com/lcks/index.jhtml'
    doctor_url_list = ['myg', 'nk', 'wk', 'fk', 'ek', 'pfk', 'gck',
                       'yk', 'ebhk', 'kqk', 'kfkybq', 'kfkebq',
                       'qt', 'zjk', 'pxgsk']
    doctor_links = ['http://www.pdqzyyy.com/{}/index.jhtml'.format(each_doctor)
                    for each_doctor in doctor_url_list]
    entry_url = 'http://www.pdqzyyy.com/jyzn/index.jhtml'
    hospital_name = '郫县中医医院 '
    host = 'http://www.pdqzyyy.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.pdqzyyy.com',
        'Referer': 'http://www.pdqzyyy.com/pdqzyyjj/index.jhtml',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        'DOWNLOAD_DELAY': 3,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 5.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        # 'CONCURRENT_REQUESTS': 16
    }

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url,
                          headers=self.headers,
                          callback=self.parse,
                          dont_filter=True)

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('>>>>>>正在抓取{}:医院信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '门诊上午_8:00-12:00;门诊下午_14:00-17:30')
        loader.add_value('hospital_level', '三级乙等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '中医医院')
        loader.add_value('hospital_addr', '四川省成都市郫都区南大街342号')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '郫都区')
        loader.add_value('hospital_phone', '咨询电话_028-87920858;急诊电话_028-87925131;预约挂号_028-87925042;'
                                           '投诉电话_028-87920858;人事招聘_028-87925158;医保出入院处_028-87925172;'
                                           '体验科_028-87922056')
        loader.add_xpath('hospital_intro', '//div[@class="rightPanel"]/p[position()>2]', MapCompose(remove_tags))
        loader.add_value('is_medicare', '是')
        loader.add_value('registered_channel', '官方微信公众号或华医通APP')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        # 医院信息
        yield hospital_info_item
        # 获取科室信息
        dept_request = Request(self.dept_link,
                               headers=self.headers,
                               callback=self.parse_hospital_dep,
                               dont_filter=True)
        dept_request.meta['Referer'] = self.entry_url
        yield dept_request
        # 获取医生信息
        for each_dept_link in self.doctor_links:
            dept_request = Request(each_dept_link,
                                   headers=self.headers,
                                   callback=self.parse_doctor_info,
                                   dont_filter=True)
            dept_request.meta['Referer'] = each_dept_link
            yield dept_request

    def parse_hospital_dep(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        dept_links = response.xpath('//div[@class="rightPanel"]/table/tr[position()>1]')
        for each_dept_link in dept_links:
            dept_type = each_dept_link.xpath('td[1]/text()').extract_first('')
            all_dept_links = each_dept_link.xpath('td[2]/a[not(contains(@href,"javascript:void(0)"))]')
            if dept_type and all_dept_links:
                for dept_link in all_dept_links:
                    dept_name = dept_link.xpath('text()').extract_first('')
                    dept_url = dept_link.xpath('@href').extract_first('')
                    if dept_name and dept_url:
                        dept_request = Request(urljoin(self.host, dept_url),
                                               headers=self.headers,
                                               callback=self.parse_hospital_dep_2,
                                               meta={'dept_name': dept_name,
                                                     'dept_type': dept_type},
                                               dont_filter=True)
                        dept_request.meta['Referer'] = response.url
                        yield dept_request

    def parse_hospital_dep_2(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室信息[中转页面]>>>>>>'.format(self.hospital_name))
        dept_type = response.meta['dept_type']
        dept_name = response.meta['dept_name']
        dept_detail_link = response.xpath('//div[@class="rightPanel"]/ul/li[1]/p[1]/a/@href').extract_first('')
        if dept_detail_link:
            dep_detail_request = Request(dept_detail_link,
                                         headers=self.headers,
                                         callback=self.parse_hospital_dep_detail,
                                         meta={'dept_name': dept_name,
                                               'dept_type': dept_type},
                                         dont_filter=True)
            dep_detail_request.meta['Referer'] = response.url
            yield dep_detail_request

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>'.format(self.hospital_name))
        dept_type = response.meta['dept_type']
        dept_name = response.meta['dept_name']
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_value('dept_name', dept_name)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('dept_type', dept_type)
        loader.add_xpath('dept_info',
                         '//div[@class="rightPanel"]/p[position()>2]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//div[@class="rightPanel"]/div[2]/div/ul/li')
        for each_doctor_link in doctor_links:
            doctor_link = each_doctor_link.xpath('a/@href').extract_first('')
            doctor_name = each_doctor_link.xpath('a/text()').extract_first('')
            if doctor_link and doctor_name:
                doctor_detail_request = Request(doctor_link,
                                                headers=self.headers,
                                                callback=self.parse_doctor_info_detail,
                                                meta={'doctor_name': doctor_name},
                                                dont_filter=True)
                doctor_detail_request.meta['Referer'] = response.url
                yield doctor_detail_request
        next_page = response.xpath('//div[@class="rightPanel"]/div[2]/div[3]/div/'
                                   'a[3]/@onclick').extract_first('')
        if next_page:
            next_page_link = re.search(r'encodeURI\(\'(.*?)\'\);', next_page)
            if next_page_link:
                next_page_link = urljoin(response.url, next_page_link.group(1))
                next_request = Request(next_page_link,
                                       headers=self.headers,
                                       callback=self.parse_doctor_info)
                next_request.meta['Referer'] = response.url
                yield next_request

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生详细信息>>>>>>'.format(self.hospital_name))
        doctor_name = response.meta['doctor_name']
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_value('doctor_name', doctor_name)
        loader.add_xpath('dept_name',
                         '//div[@class="doctor"]/h1/text()',
                         MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_xpath('doctor_level',
                         '//p[@class="profession"]/span/text()',
                         MapCompose(custom_remove_tags))
        loader.add_xpath('doctor_intro',
                         '//div[@class="abstract"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_xpath('doctor_goodAt',
                         '//div[@class="specialty"]/p/text()',
                         MapCompose(custom_remove_tags))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
