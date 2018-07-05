# -*- coding: utf-8 -*-
import scrapy
from medicalmap.items import HospitalInfoItem, HospitalDepItem, MedicalMapLoader, DoctorInfoItem
from medicalmap.utils.common import now_day
from scrapy.http import Request
from urllib.parse import urljoin


class JintangyySpider(scrapy.Spider):
    """
    金堂县第一人民医院相关信息,包含医院、科室等相关信息
    """
    name = 'jintangyy'
    allowed_domains = ['jintangyy.com']
    start_urls = ['http://www.jintangyy.com/about.aspx?mid=299']
    dep_link = 'http://www.jintangyy.com/section.aspx?mid=330'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.jintangyy.com',
        'Referer': 'http://www.jintangyy.com/index.aspx',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    hospital_name = '金堂县第一人民医院'
    hospital_id = '2f25c9624c31c190faa6bea604a03aee'
    host = 'http://www.jintangyy.com/'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        self.logger.info('正在抓取{}:医院信息'.format(self.hospital_name))
        loader = MedicalMapLoader(item=HospitalInfoItem(), response=response)
        # loader.add_value('hospital_id', self.hospital_id)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '普通门诊上午_8:00-12:00;普通门诊下午13：00-16：30')
        loader.add_value('hospital_level', '三级乙等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '综合医院')
        loader.add_value('hospital_addr', '四川省金堂县赵镇金广路886号')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '金堂县')
        loader.add_value('hospital_phone', '医院服务电话_028-84902884;服务质量监督投诉电话_028-84932532;'
                                           '急诊急救电话_18181938532;产科急救电话_18181938532;'
                                           '医保结算电话_028-84932721;'
                                           '预约挂号电话_028-84931443;预约挂号电话_028-84902884;预约挂号电话_028-61568616')
        loader.add_xpath('hospital_intro', '//div[@class="baseRight-intro"]/p[position()>1 '
                                           'and position()<=6]/span/text()')
        loader.add_value('is_medicare', '')
        loader.add_value('medicare_type', '')
        loader.add_value('vaccine_name', '')
        loader.add_value('is_cpc', '')
        loader.add_value('is_bdc', '')
        loader.add_value('cooperative_business', '')
        loader.add_value('hospital_district', '')
        loader.add_value('is_bdc', '')
        loader.add_value('registered_channel', '微信公众号_' + self.hospital_name)
        loader.add_value('up_date', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item
        request = Request(self.dep_link, callback=self.parse_hospital_dep)
        yield request

    def parse_hospital_dep(self, response):
        """科室信息"""
        self.logger.info('正在抓取{}:科室信息'.format(self.hospital_name))
        dep_type = response.xpath('//div[@class="part"]/div[@class="part01"]')
        for each_dep_type in dep_type:
            dep_link = each_dep_type.xpath('//ul/li/div/a[1]/@href').extract_first('')
            dep_doctor_link = each_dep_type.xpath('//ul/li/div/a[2]/@href').extract_first('')
            loader = MedicalMapLoader(item=HospitalDepItem(), selector=each_dep_type)
            # loader.add_value('hospital_id', self.hospital_id)
            loader.add_value('hospital_id', self.hospital_id)
            loader.add_xpath('dep_type', '//div[@class="partTitle"]/div/text()')
            loader.add_xpath('dep_name', '//ul/li/h3/text()')
            self.headers['Referer'] = dep_link
            if dep_link:
                dep_link = urljoin(self.host, dep_link)
                dep_detail_link = dep_link.replace('sectionshow', 'classsysdetail')
                yield Request(dep_detail_link,
                              headers=self.headers,
                              callback=self.parse_dep_detail,
                              meta={'loader': loader})
            if dep_doctor_link:
                dep_doctor_link = urljoin(self.host, dep_doctor_link)
                yield Request(dep_doctor_link,
                              headers=self.headers,
                              callback=self.parse_doctor_info)

    def parse_dep_detail(self, response):
        """科室详细信息"""
        self.logger.info('正在抓取{}:科室详细信息'.format(self.hospital_name))
        loader = response.meta['loader']
        loader.add_xpath('dep_intro', '//div[@class="baseRight-intro"]/p')
        loader.add_value('up_date', now_day())
        hospital_dep_item = loader.load_item()
        yield hospital_dep_item

    def parse_doctor_info(self, response):
        """医生信息"""
        self.logger.info('正在抓取{}:医生信息'.format(self.hospital_name))
        doctor_list = response.xpath('//div[@class="contents2"]/ul/li')
        for each_doc in doctor_list:
            loader = MedicalMapLoader(item=DoctorInfoItem(), selector=each_doc)
            loader.add_xpath('doctor_name', '//h4[@class="name"]/text()')
            loader.add_value('hospital_id', self.hospital_id)
            loader.add_xpath('dep_id', '//p[@class="office"]/text()')
            loader.add_xpath('doctor_level', 'p[@class="post"]/text()')
            doctor_link = each_doc.xpath('//div[@class="contents2"]/ul/li/a[1]/@href')
            if doctor_link:
                doctor_link = urljoin(self.host, doctor_link)
                self.headers['Referer'] = response.url
                yield Request(doctor_link,
                              headers=self.headers,
                              callback=self.parse_doctor_detail,
                              meta={'loader': loader})

    def parse_doctor_detail(self, response):
        """医生详细信息"""
        self.logger.info('正在抓取{}:医生详细信息'.format(self.hospital_name))
        loader = response.meta['loader']
        loader.add_xpath('doctor_intro', '//div[@class="article"]/text()')
        loader.add_xpath('doctor_goodat', '//div[@class="article"]/text()')
        loader.add_value('up_date', now_day())
        doctor_info_item = loader.load_item()
        yield doctor_info_item

    def parse_doctor_reg_info(self, response):
        """医生排班信息"""
        pass
