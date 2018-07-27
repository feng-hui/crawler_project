# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, clean_info
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem


class CdwhyySpider(scrapy.Spider):
    """
    成都市武侯区妇幼保健院
    """
    name = 'cdwhyy'
    allowed_domains = ['cdwhyy.com']
    start_urls = ['http://cdwhyy.com/']

    hospital_intro_link = 'http://www.cdwhyy.com/HTML/yiyuangaikuang/yiyuanjianjie/'
    dept_link = ''
    doctor_link = 'http://www.cdwhyy.com/HTML/zhuanjiajieshao/'
    hospital_name = '成都市武侯区妇幼保健院'
    host = 'http://www.cdwhyy.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.cdwhyy.com',
        'Referer': 'http://www.cdwhyy.com/',
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
        # 医院信息
        # yield Request(self.hospital_intro_link, headers=self.headers, callback=self.parse)
        # 科室信息
        # yield Request(self.dept_link, headers=self.headers, callback=self.parse_hospital_dep)
        # 医生信息
        yield Request(self.doctor_link, headers=self.headers, callback=self.parse_doctor_info)

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('>>>>>>正在抓取{}:医院信息>>>>>>'.format(self.hospital_name))
        # loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        # loader.add_value('hospital_name', self.hospital_name)
        # loader.add_value('consulting_hour', '上午_8:00—12:00;下午_2:00—5:30')
        # loader.add_value('hospital_level', '三级乙等')
        # loader.add_value('hospital_type', '公立')
        # loader.add_value('hospital_category', '妇幼保健院')
        # loader.add_value('hospital_addr', '成都市广福桥街16号')
        # loader.add_value('hospital_pro', '四川省')
        # loader.add_value('hospital_city', '成都市')
        # loader.add_value('hospital_county', '')
        # loader.add_value('hospital_phone', '预约_028-81735329;门诊_028-81735586;'
        #                                    '办公/人事/医务_028-81735308;非工作日值班电话_13308039516;'
        #                                    '急诊_028-85076122')
        # loader.add_xpath('hospital_intro',
        #                  '//div[@class="page_sum2"]/p',
        #                  MapCompose(remove_tags, custom_remove_tags))
        # # loader.add_value('is_medicare', '是')
        # # loader.add_value('medicare_type', '')
        # loader.add_value('registered_channel', '现场挂号')
        # loader.add_value('dataSource_from', '医院官网')
        # loader.add_value('update_time', now_day())
        # hospital_info_item = loader.load_item()
        # yield hospital_info_item
        # 科室信息
        dept_links = response.xpath('//ul[@id="nav"]/li[position()=4]/dl/dd')
        for each_dept_link in dept_links:
            dept_link = each_dept_link.xpath('a/@href').extract_first('')
            dept_type = each_dept_link.xpath('a/text()').extract_first('')
            if dept_link and dept_type:
                dept_link = '{0}{1}'.format(dept_link, '/')
                dept_request = Request(urljoin(self.host, dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep,
                                       meta={'dept_type': dept_type})
                dept_request.meta['Referer'] = response.url
                yield dept_request

    def parse_hospital_dep(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        dept_links = response.xpath('//ul[@class="e2"]/li/a[1]/@href').extract()
        if dept_links:
            for each_dept_link in dept_links:
                dept_request = Request(urljoin(self.host, each_dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep_detail,
                                       dont_filter=True,
                                       meta={'dept_type': response.meta['dept_type']})
                dept_request.meta['Referer'] = response.url
                yield dept_request
        next_page = response.xpath('//ul[@class="pagelist"]/li/a[contains(text(),"下一页")]'
                                   '/@href').extract_first('')
        if next_page:
            next_page_link = urljoin(response.url, next_page)
            next_request = Request(next_page_link,
                                   headers=self.headers,
                                   callback=self.parse_hospital_dep,
                                   meta={'dept_type': response.meta['dept_type']})
            self.headers['Referer'] = response.url
            yield next_request

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_xpath('dept_name',
                         '//div[@class="page_sum2_tit"]/text()',
                         MapCompose(custom_remove_tags, clean_info))
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('dept_type', response.meta['dept_type'])
        loader.add_xpath('dept_info',
                         '//div[@class="page_sum2"]/*['
                         'not(contains(@class,"listsum_block2")) and'
                         'not(contains(@class,"page_tit")) and'
                         'not(contains(@class,"page_sum2_tit"))]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//ul[@class="e2"]/li/a[1]/@href').extract()
        for each_doctor_link in doctor_links:
            doctor_detail_request = Request(urljoin(self.host, each_doctor_link),
                                            headers=self.headers,
                                            callback=self.parse_doctor_info_detail,
                                            dont_filter=True)
            doctor_detail_request.meta['Referer'] = response.url
            yield doctor_detail_request
        next_page = response.xpath('//ul[@class="pagelist"]/li/a[contains(text(),"下一页")]'
                                   '/@href').extract_first('')
        if next_page:
            next_page_link = urljoin(response.url, next_page)
            next_request = Request(next_page_link,
                                   headers=self.headers,
                                   callback=self.parse_doctor_info)
            next_request.meta['Referer'] = response.url
            yield next_request

    def parse_doctor_info_detail(self, response):
        # self.logger.info('>>>>>>正在抓取{}:医生详细信息>>>>>>'.format(self.hospital_name))
        # loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        # loader.add_xpath('doctor_name',
        #                  '//div[@class="page_sum2"]/table/tr[1]/td[3]',
        #                  MapCompose(remove_tags, custom_remove_tags, match_special))
        # loader.add_xpath('dept_name',
        #                  '//div[@class="page_sum2"]/table/tr[3]/td',
        #                  MapCompose(remove_tags, custom_remove_tags, match_special))
        # loader.add_value('hospital_name', self.hospital_name)
        # loader.add_xpath('doctor_level',
        #                  '//div[@class="page_sum2"]/table/tr[2]/td',
        #                  MapCompose(remove_tags, custom_remove_tags, match_special))
        # loader.add_xpath('doctor_intro',
        #                  '//div[@class="listsum_block"]',
        #                  MapCompose(remove_tags, custom_remove_tags, clean_info))
        # loader.add_value('doctor_goodAt', '')
        # loader.add_value('update_time', now_day())
        # doctor_item = loader.load_item()
        # yield doctor_item
        # 医生排班信息
        self.logger.info('>>>>>>正在抓取{}:医生排班信息>>>>>>'.format(self.hospital_name))

        reg_loader = CommonLoader2(item=DoctorRegInfoItem(), response=response)
        reg_loader.add_xpath('doctor_name',
                             '//div[@class="page_sum2"]/table/tr[1]/td[3]',
                             MapCompose(remove_tags, custom_remove_tags, match_special))
        reg_loader.add_xpath('dept_name',
                             '//div[@class="page_sum2"]/table/tr[3]/td',
                             MapCompose(remove_tags, custom_remove_tags, match_special))
        reg_loader.add_value('hospital_name', self.hospital_name)
        reg_loader.add_xpath('reg_info',
                             '//div[@class="page_sum2"]/table/tr[5]/td|'
                             '//div[@class="listsum_block"]',
                             MapCompose(remove_tags, custom_remove_tags, match_special))
        reg_loader.add_value('update_time', now_day())
        reg_item = reg_loader.load_item()
        yield reg_item

    def parse_doctor_reg_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生排班信息>>>>>>'.format(self.hospital_name))
