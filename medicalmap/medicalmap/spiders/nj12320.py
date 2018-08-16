# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import signals
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, get_county, \
    match_special2, get_county2
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, HospitalAliasItem, \
    DoctorInfoItem, DoctorRegInfoItem


class Nj12320Spider(scrapy.Spider):
    name = 'nj12320'
    allowed_domains = ['nj12320.org']
    start_urls = ['http://www.nj12320.org/njres/reservation/hos_search.do;jsessionid=4BD4BD5B72B6D2172C42B80FBBB7E688']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.nj12320.org',
        # 'Referer': 'http://www.a-hospital.com/w/%E9%A6%96%E9%A1%B5',
        # 'Cookie': 'JSESSIONID=EE70FD59432D986B935AAD35DE1D1DC4; JSESSIONID=6C4A977DB24C24813C35DB89841FBE73',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 1,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 100
    }
    host = 'http://www.nj12320.org'
    doctor_pagination_url = 'http://www.nj12320.org/njres/reservation/hos_showReservation.do?' \
                            'depid=&principalship=&docname=&depName=&hoscode={}&stdDepid=&parentStdDepid=' \
                            '&changeFlay=0&currentpage={}&disid=&bigCode=&allDoctors=0&currentWeekCount=1' \
                            '&schcode=&hosCfgCode=&__multiselect_haveNum=&selectPage={}'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        all_hospital_links = response.xpath('//table[@class="tab"]/tbody/tr')
        for each_hospital_link in all_hospital_links:
            hospital_link = each_hospital_link.xpath('td[1]/b/a/@href').extract_first('')
            hospital_level = each_hospital_link.xpath('td[2]/p/span/text()').extract_first('')
            hospital_name = each_hospital_link.xpath('td[2]/h2/text()').extract_first('')
            all_doctor_links = each_hospital_link.xpath('td[3]/p/span/a'
                                                        '[contains(text(),"查看医生")]/@href').extract_first('')
            # 获取医院信息
            if hospital_link:
                hospital_link = urljoin(self.host, hospital_link)
                self.headers['Referer'] = response.url
                yield Request(hospital_link,
                              headers=self.headers,
                              callback=self.parse_hospital_info,
                              meta={'hospital_level': hospital_level})

            # 获取医生信息
            if all_doctor_links:
                all_doctor_links = urljoin(self.host, all_hospital_links)
                self.headers['Referer'] = response.url
                yield Request(all_doctor_links,
                              headers=self.headers,
                              callback=self.parse_doctor_info,
                              meta={'hospital_name': hospital_name})

    def parse_hospital_info(self, response):
        self.logger.info('>>>>>>正在抓取:医院信息>>>>>>')

        # 获取区或县
        hospital_address = response.xpath('//div[@class="yy_js clearfix"]/div/dl/dd[1]/text()').extract_first('')
        if hospital_address:
            hospital_county = get_county2('', hospital_address)
        else:
            hospital_county = None

        # 获取医院信息
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_xpath('hospital_name', '//div[@class="yy_til"]/h2/text()', MapCompose(custom_remove_tags))
        loader.add_value('hospital_level', response.meta.get('hospital_level'), MapCompose(custom_remove_tags))
        loader.add_xpath('hospital_addr',
                         '//div[@class="yy_js clearfix"]/div/dl/dd[1]/text()',
                         MapCompose(custom_remove_tags))
        loader.add_value('hospital_pro', '江苏省')
        loader.add_value('hospital_city', '南京市')
        loader.add_value('hospital_county', hospital_county)
        loader.add_xpath('hospital_phone',
                         '//div[@class="yy_js clearfix"]/div/dl/dd[2]/text()',
                         MapCompose(custom_remove_tags))
        loader.add_xpath('hospital_intro', '//dd[@id="wrap"]', MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('registered_channel', '南京市预约挂号服务平台')
        loader.add_value('dataSource_from', '南京市预约挂号服务平台')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

        # 获取科室信息
        self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>')
        all_dept_links = response.xpath('//dl[@class="kfyy clearfix"]/dd/span/a/@href').extract()
        for each_dept_link in all_dept_links:
            dept_link = urljoin(self.host, each_dept_link)
            self.headers['Referer'] = response.url
            yield Request(dept_link, headers=self.headers, callback=self.parse_hospital_dep_detail)

        # 翻页

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取科室详细信息>>>>>>')
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_xpath('dept_name', '//div[@class="zrys"]/p/strong/text()', MapCompose(custom_remove_tags))
        loader.add_xpath('hospital_name', '//div[@class="yy_til"]/h2/text()', MapCompose(custom_remove_tags))
        loader.add_xpath('dept_info', '//div[@class="zrys"]/dl/dd', MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取医生信息>>>>>>')
        all_doctors = response.xpath('//table[@class="tab"]/tbody/tr[position()>1 and position() mod 2=0]')
        for each_doctor in all_doctors:
            doctor_name = each_doctor.xpath('td[2]/a/text()').extract_first('')
            doctor_level = each_doctor.xpath('td[2]/i/text()').extract_first('')
            dept_name = each_doctor.xpath('td[2]/em/a/text()').extract_first('')
            doctor_link = each_doctor.xpath('td[2]/a/@href').extract_first('')
            if doctor_link:
                doctor_link = urljoin(self.host, doctor_link)
                self.headers['Referer'] = response.url
                yield Request(doctor_link,
                              headers=self.headers,
                              callback=self.parse_doctor_info_detail,
                              meta={
                                  'doctor_name': doctor_name,
                                  'doctor_level': doctor_level,
                                  'dept_name': dept_name
                              })
        # 翻页
        hos_code = re.search(r'')


    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取医生详细信息>>>>>>')
        doctor_name = response.meta.get('doctor_name')
        dept_name = response.meta.get('dept_name')
        doctor_level = response.meta.get('doctor_level')
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_value('doctor_name', doctor_name, MapCompose(custom_remove_tags))
        loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
        loader.add_xpath('hospital_name', '//div[@class="yy_til"]/h2/text()', MapCompose(custom_remove_tags))
        loader.add_value('doctor_level', doctor_level, MapCompose(custom_remove_tags))
        loader.add_xpath('doctor_intro',
                         '//div[@class="zrys"]/dl/dd',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
