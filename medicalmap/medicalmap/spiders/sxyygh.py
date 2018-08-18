# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special2, get_hospital_info, get_number
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem


class SxyyghSpider(scrapy.Spider):
    name = 'sxyygh'
    allowed_domains = ['sxyygh.com']
    start_urls = ['http://sxyygh.com/gh/index_hos.asp?cityid=&addrcountryid=&gradeid=&simplespell='
                  '&hospitalname=&hosptype=1',
                  'http://sxyygh.com/gh/index_hos.asp?cityid=&addrcountryid=&gradeid=&simplespell='
                  '&hospitalname=&hosptype=3',
                  'http://sxyygh.com/gh/index_hos.asp?cityid=&addrcountryid=&gradeid=&simplespell='
                  '&hospitalname=&hosptype=2']
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
        # 'DOWNLOAD_DELAY': 5,
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
    doctor_entry = 'http://sxyygh.com/gh/index_doctor.asp'

    def start_requests(self):
        # 获取医院和科室信息
        for each_url in self.start_urls[0:1]:
            yield Request(each_url, headers=self.headers, callback=self.parse, dont_filter=True)

        # 获取医院信息
        # yield Request(self.doctor_entry, headers=self.headers, callback=self.parse_doctor_info, dont_filter=True)

    def parse(self, response):
        self.logger.info('>>>>>>正在抓取:医院信息>>>>>>')
        try:
            all_hospital_links = response.xpath('//table[@id="T1"]/tr/td[2]/a/@href').extract()
            hospital_type = response.xpath('//td[contains(text(),"类型")]/ancestor::tr[1]/td[2]'
                                           '/table/tr/td/span[@class="btn_x"]/a/text()').extract_first('')
            for each_hospital_link in all_hospital_links[0:1]:
                hospital_link = urljoin(self.hospital_host, each_hospital_link)
                self.headers['Referer'] = response.url
                yield Request(hospital_link,
                              headers=self.headers,
                              callback=self.parse_hospital_info,
                              dont_filter=True,
                              meta={'hospital_type': hospital_type})
            # 分页
            page_num = re.search(r'page=(.*?)$', response.url)
            if not page_num:
                page_num = '1'
            else:
                page_num = page_num.group(1)
            next_page = response.xpath(r'//form[@id="fy"]/b[contains(text(),"[{}]")]/'
                                       r'following::a[1]/@href'.format(page_num)).extract_first('')
            if next_page:
                next_page_link = urljoin(self.host, next_page)
                self.headers['Referer'] = response.url
                yield Request(next_page_link,
                              headers=self.headers,
                              callback=self.parse,
                              dont_filter=True)
        except Exception as e:
            self.logger.error('在抓取医院的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_info(self, response):
        self.logger.info('>>>>>>正在抓取:医院详细信息和科室信息>>>>>>')
        try:
            # 获取医院信息
            hospital_type = response.meta.get('hospital_type')
            hospital_category = '{0}{1}'.format(hospital_type, '医院') if hospital_type else None
            hospital_info = custom_remove_tags(remove_tags(''.join(response.xpath('//td[@class='
                                                                                  '"title_yh14"]').extract())))
            hospital_address = get_hospital_info(hospital_info, '地址：', '查看地图')
            hospital_phone = get_hospital_info(hospital_info, '电话：', '官网')
            hospital_intro = get_hospital_info(hospital_info, '简介：', '$').replace('...更多&gt;&gt;', '')
            loader = CommonLoader2(item=HospitalInfoItem(), response=response)
            loader.add_xpath('hospital_name', '//span[@class="title"]/text()', MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_level', '//span[@class="dj"]/text()', MapCompose(custom_remove_tags))
            loader.add_value('hospital_category', hospital_category)
            loader.add_value('hospital_addr', hospital_address, MapCompose(custom_remove_tags))
            loader.add_value('hospital_pro', '山西省')
            loader.add_xpath('hospital_city',
                             '//td[contains(text(),"山西")]/ancestor::tr[1]/td[1]/a[1]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_county',
                             '//td[contains(text(),"山西")]/ancestor::tr[1]/td[1]/a[2]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('hospital_phone', hospital_phone, MapCompose(custom_remove_tags))
            loader.add_value('hospital_intro', hospital_intro, MapCompose(custom_remove_tags))
            loader.add_value('registered_channel', '山西省预约诊疗服务平台')
            loader.add_value('dataSource_from', '山西省预约诊疗服务平台')
            loader.add_value('update_time', now_day())
            hospital_info_item = loader.load_item()
            yield hospital_info_item

            # 获取科室信息
            self.logger.info('>>>>>>正在抓取科室详细信息>>>>>>')
            all_dept_links = response.xpath('//tr[@class="h_bottom"]')
            for each_dept_link in all_dept_links:
                dept_type = each_dept_link.xpath('td[1]/text()').extract_first('')
                dept_name = each_dept_link.xpath('td[2]/table/tr/td/a/text()').extract()
                for each_dept_name in dept_name:
                    dept_loader = CommonLoader2(item=HospitalDepItem(), response=response)
                    dept_loader.add_value('dept_name', each_dept_name, MapCompose(custom_remove_tags, match_special2))
                    dept_loader.add_value('dept_type', dept_type, MapCompose(custom_remove_tags, match_special2))
                    dept_loader.add_xpath('hospital_name',
                                          '//span[@class="title"]/text()',
                                          MapCompose(custom_remove_tags))
                    dept_loader.add_value('dept_info', '')
                    dept_loader.add_value('update_time', now_day())
                    dept_item = dept_loader.load_item()
                    yield dept_item
        except Exception as e:
            self.logger.error('在抓取医院详细信息和科室的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取:医生信息>>>>>>')
        try:
            all_doctors = response.xpath('//table[@id="T1"]/tr')
            for each_hospital_link in all_doctors:
                doctor_link = each_hospital_link.xpath('td[2]/a/@href').extract_first('')
                diagnosis_fee = each_hospital_link.xpath('td[last()]').extract_first('')
                if doctor_link:
                    hospital_link = urljoin(self.hospital_host, doctor_link)
                    self.headers['Referer'] = response.url
                    yield Request(hospital_link,
                                  headers=self.headers,
                                  callback=self.parse_doctor_info_detail,
                                  dont_filter=True,
                                  meta={'diagnosis_fee': diagnosis_fee})
            # 分页
            page_num = re.search(r'page=(.*?)$', response.url)
            if not page_num:
                page_num = '1'
            else:
                page_num = page_num.group(1)
            next_page = response.xpath(r'//form[@id="fy"]/b[contains(text(),"[{}]")]/'
                                       r'following::a[1]/@href'.format(page_num)).extract_first('')
            if next_page:
                next_page_link = urljoin(self.host, next_page)
                self.headers['Referer'] = response.url
                yield Request(next_page_link,
                              headers=self.headers,
                              callback=self.parse_doctor_info,
                              dont_filter=True)
        except Exception as e:
            self.logger.error('在抓取医生信息的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取:医生详细信息>>>>>>')
        try:
            diagnosis_fee = response.meta.get('diagnosis_fee')
            doctor_info = custom_remove_tags(remove_tags(''.join(response.xpath('//td[@class="bk '
                                                                                'titletxt11"]').extract())))
            doctor_intro1 = get_hospital_info(doctor_info, '个人简介：', '荣誉集锦：')
            doctor_intro2 = get_hospital_info(doctor_info, '个人简介：', '出诊时间：')
            doctor_intro = doctor_intro2 if doctor_intro2 else doctor_intro1
            loader = CommonLoader2(item=DoctorInfoItem(), response=response)
            loader.add_xpath('doctor_name',
                             '//table[@id="m_jkzs"]/tr/td[1]/a[last()]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('dept_name',
                             '//table[@id="m_jkzs"]/tr/td[1]/a[last()-1]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_name',
                             '//table[@id="m_jkzs"]/tr/td[1]/a[last()-2]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('doctor_level',
                             '//span[@class="selecttxt"][contains(text(),"医师") or contains(text(),"专家")]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('doctor_intro', doctor_intro, MapCompose(custom_remove_tags))
            loader.add_xpath('doctor_goodAt',
                             '//span[@class="titletxt11"]/b[contains(text(),"擅长")]/ancestor::span[1]/text()',
                             MapCompose(remove_tags, custom_remove_tags))
            loader.add_value('diagnosis_amt',
                             diagnosis_fee,
                             MapCompose(remove_tags, custom_remove_tags, get_number))
            loader.add_value('update_time', now_day())
            doctor_item = loader.load_item()
            yield doctor_item
        except Exception as e:
            self.logger.error('在抓取医生详细信息的过程中出错了,原因是：{}'.format(repr(e)))



