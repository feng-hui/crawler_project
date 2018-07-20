# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, get_reg_info
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose, Join
from w3lib.html import remove_tags


class QbjzyySpider(scrapy.Spider):
    """
    成都市青白江区中医医院
    """
    name = 'qbjzyy'
    allowed_domains = ['qbjzyy.com']
    start_urls = ['http://qbjzyy.com/']
    doctor_link = ''
    hospital_intro_link = 'http://www.qbjzyy.com/about.aspx?mid=17'
    hospital_name = '成都市青白江区中医医院 '
    host = 'http://www.qbjzyy.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.qbjzyy.com',
        'Referer': 'http://www.qbjzyy.com/index.aspx',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('正在抓取{}:医院信息'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '门诊时间_8:30-17:30;急诊时间_7*24小时')
        loader.add_value('hospital_level', '二级甲等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '中医医院')
        loader.add_value('hospital_addr', '川化病区:青白江区化工北路41号（原川化医院）;'
                                          '城厢病区:青白江区城厢镇大南街51号（中医血防医院）;'
                                          '中医名医馆地址：中医医院川化病区一号楼1楼')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '青白江区')
        loader.add_value('hospital_phone', '24小时急诊电话_028-83632835')
        loader.add_xpath('hospital_intro', '//div[@class="right-about clearfix"]', MapCompose(remove_tags))
        loader.add_value('registered_channel', '医院挂号室')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        # 医院信息
        yield hospital_info_item
        # 获取科室信息
        dept_links = response.xpath('//ul[@id="navul"]/li[5]/ul/li|//ul[@id="navul"]/li[6]/ul/li')
        for each_dept_link in dept_links:
            dept_link = each_dept_link.xpath('a/@href').extract_first('')
            dept_name = each_dept_link.xpath('a/text()').extract_first('')
            if dept_link and dept_name:
                dept_request = Request(urljoin(self.host, dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep_detail,
                                       meta={'dept_name': dept_name})
                dept_request.meta['Referer'] = response.url
                yield dept_request
        # 获取医生信息
        doctor_links = response.xpath('//ul[@id="navul"]/li[8]/ul/li')
        for each_dept_link in doctor_links:
            dept_link = each_dept_link.xpath('a/@href').extract_first('')
            dept_name = each_dept_link.xpath('a/text()').extract_first('')
            if dept_link and dept_name:
                dept_request = Request(urljoin(self.host, dept_link),
                                       headers=self.headers,
                                       callback=self.parse_doctor_info,
                                       meta={'dept_name': dept_name})
                dept_request.meta['Referer'] = response.url
                yield dept_request

    def parse_hospital_dep(self, response):
        dept_links = response.xpath('//ul[@class="product3"]/li')
        for each_dept_link in dept_links:
            dept_link = each_dept_link.xpath('div[2]/h1/a/@href').extract_first('')
            dept_name = each_dept_link.xpath('div[2]/h1/a/text()').extract_first('')
            if dept_link and dept_name:
                dept_request = Request(urljoin(self.host, dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep_detail,
                                       meta={'dept_name': dept_name})
                dept_request.meta['Referer'] = response.url
                yield dept_request

    def parse_hospital_dep_detail(self, response):
        dept_name = response.meta['dept_name']
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_value('dept_name', dept_name)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_xpath('dept_info', '//div[@class="right-about clearfix"]', MapCompose(remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        dept_name = response.meta['dept_name']
        doctor_links = response.xpath('//ul[@class="right-photo clearfix"]/li')
        for each_doctor_link in doctor_links:
            doctor_link = each_doctor_link.xpath('a/@href').extract_first('')
            doctor_name = each_doctor_link.xpath('h3/text()').extract_first('')
            if doctor_link and doctor_name:
                doctor_detail_request = Request(urljoin(self.host, doctor_link),
                                                headers=self.headers,
                                                callback=self.parse_doctor_info_detail,
                                                meta={'doctor_name': doctor_name,
                                                      'dept_name': dept_name})
                doctor_detail_request.meta['Referer'] = response.url
                yield doctor_detail_request

    def parse_doctor_info_detail(self, response):
        dept_name = response.meta['dept_name']
        doctor_name = response.meta['doctor_name']
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_value('doctor_name', doctor_name)
        loader.add_value('dept_name', dept_name)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_xpath('doctor_intro', '//div[@class="right-about clearfix"]/p[2]', MapCompose(remove_tags))
        loader.add_xpath('doctor_goodAt',
                         '//div[@class="right-about clearfix"]/p[position()>2]',
                         MapCompose(remove_tags))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
