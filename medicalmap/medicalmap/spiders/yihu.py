# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from medicalmap.items import YiHuLoader, HospitalInfoItem, HospitalDepItem, DoctorInfoItem
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import remove_number2, now_day
from urllib.parse import urljoin


class YihuSpider(scrapy.Spider):
    """
    健康之路网站：成都、眉山、绵阳三个地市的数据
    目前只有成都有数据
    入口：预约挂号
    """
    name = 'yihu'
    allowed_domains = ['yihu.com']
    start_urls = ['https://www.yihu.com/hospital/23/241.shtml']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.yihu.com',
        'Referer': 'https://www.yihu.com/hospital/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    host = 'https://www.yihu.com'
    hospital_host = 'https://www.yihu.com/hospital/'
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 5,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 5.0,
        'AUTOTHROTTLE_DEBUG': False,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 32
    }

    def start_requests(self):
        for each_area_url in self.start_urls:
            yield Request(each_area_url, headers=self.headers)

    def parse(self, response):
        """获取医院信息"""
        all_hospital_links = response.xpath('//div[@class="c-hidden disen-list-hos c-f12"]/ul/li')
        self.logger.info('该地区共{}家医院'.format(str(len(all_hospital_links))))
        for each_hospital_link in all_hospital_links:
            loader = YiHuLoader(item=HospitalInfoItem(), selector=each_hospital_link)
            loader.add_xpath('hospital_name', 'a/text()')
            loader.add_xpath('hospital_level', 'span/text()', MapCompose(remove_number2))
            hospital_link = each_hospital_link.xpath('a/@href').extract_first('')
            if hospital_link:
                # 医院信息
                hospital_detail_link = re.sub(r'/sc/', '/detail/', hospital_link)
                contact_hos_link = re.sub(r'/sc/', '/contact/', hospital_link)
                hospital_detail_request = Request(hospital_detail_link,
                                                  headers=self.headers,
                                                  callback=self.parse_hospital_detail,
                                                  meta={'loader': loader,
                                                        'contact_hos_link': contact_hos_link})
                self.headers['Referer'] = response.url
                yield hospital_detail_request
                # 医院科室信息
                dep_request = Request(hospital_link,
                                      headers=self.headers,
                                      callback=self.parse_hospital_dep)
                self.headers['Referer'] = response.url
                yield dep_request

    def parse_hospital_dep(self, response):
        """
        获取科室信息
        """
        self.logger.info('>>>>>>正在抓取科室信息……')
        hospital_name = response.xpath('//div[@class="hos-info"]/h1/text()').extract_first('')
        all_dept_links = response.xpath('//dd[@class="ks-2"]/ul/li')
        self.logger.info('{}：共有{}个科室'.format(hospital_name, str(len(all_dept_links))))
        for each_dept_link in all_dept_links:
            # 获取科室信息
            dep_loader = YiHuLoader(item=HospitalDepItem(), selector=each_dept_link)
            dep_loader.add_xpath('dept_type', 'a/text()')
            dep_loader.add_xpath('dept_name', 'a/text()')
            dep_loader.add_value('hospital_name', hospital_name)
            dep_loader.add_value('update_time', now_day())
            dep_item = dep_loader.load_item()
            yield dep_item
            # 获取科室医生信息
            dept_link = each_dept_link.xpath('a/@href').extract_first('')
            if dept_link:
                dept_link = urljoin(self.host, dept_link)
                # doctor_link = re.sub(r'/arrange/', '/7002/', dept_link)
                dept_request = Request(dept_link,
                                       headers=self.headers,
                                       callback=self.parse_dept_link)
                self.headers['Referer'] = response.url
                yield dept_request

    def parse_doctor_reg_info(self, response):
        self.logger.info('>>>>>>正在抓取医生排班信息……')
        loader = YiHuLoader(item=DoctorInfoItem(), response=response)
        loader.add_xpath('hospital_name', '//div[@class="link-555"]/a/text()')
        loader.add_xpath('dept_name', '//div[@class="hos-info"]/h1/text()')

    def parse_hospital_detail(self, response):
        self.logger.info('>>>>>>正在抓取医院概况……')
        loader = response.meta['loader']
        contact_hos_link = response.meta['contact_hos_link']
        hospital_intro = response.xpath('//div[@class="section-con"]').extract_first('')
        loader.add_value('hospital_intro', hospital_intro)
        contact_hos_request = Request(contact_hos_link,
                                      headers=self.headers,
                                      callback=self.parse_hospital_contact,
                                      meta={'loader': loader})
        self.headers['Referer'] = response.url
        yield contact_hos_request

    def parse_hospital_contact(self, response):
        self.logger.info('>>>>>>正在抓取医院联系方式……')
        loader = response.meta['loader']
        hospital_address = response.xpath('//div[@class="section sec-article"]/div[2]/div/table/tr/'
                                          'td[2]/text()').extract_first('')
        hospital_phone = response.xpath('//div[@class="section sec-article"]/div[2]/div/table/tr/'
                                        'td[4]/text()').extract_first('')
        loader.add_value('hospital_addr', hospital_address)
        loader.add_value('hospital_phone', hospital_phone)
        loader.add_value('dataSource_from', '健康之路')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

    def parse_dept_link(self, response):
        self.logger.info('>>>>>>正在抓取科室挂号页面……')
        doctor_link = response.xpath('//div[@class="hos-nav"]/ul/li[2]/a/@href').extract_first('')
        if doctor_link:
            doctor_request = Request(urljoin(self.host, doctor_link),
                                     headers=self.headers,
                                     callback=self.parse_doctor_link)
            self.headers['Referer'] = response.url
            yield doctor_request

    def parse_doctor_link(self, response):
        self.logger.info('>>>>>>正在抓取医生列表页相关信息……')
        all_doctor_links = response.xpath('//div[@class="c-hidden doc-list"]/a/@href').extract()
        for each_doctor_link in all_doctor_links:
            doctor_website_request = Request(each_doctor_link,
                                             headers=self.headers,
                                             callback=self.parse_doctor_website)
            self.headers['Referer'] = response.url
            yield doctor_website_request
        next_page = response.xpath('//a[@class="page-next"]/@href').extract_first('')
        if next_page:
            next_page_link = urljoin(self.host, next_page)
            request = Request(next_page_link,
                              headers=self.headers,
                              callback=self.parse_doctor_link)
            self.headers['Referer'] = response.url
            yield request

    def parse_doctor_website(self, response):
        self.logger.info('>>>>>>正在抓取医生个人主页相关信息……')
        # 获取医生相关信息
        loader = YiHuLoader(item=DoctorInfoItem(), response=response)
        loader.add_xpath('doctor_name', '//span[@class="c-f22 c-333"]/text()')
        loader.add_xpath('dept_name', '//div[@class="doctor-info"]/dl/dd[2]/a[2]/text()')
        loader.add_xpath('hospital_name', '//div[@class="doctor-info"]/dl/dd[2]/a[1]/text()')
        loader.add_xpath('doctor_level', '//div[@class="doctor-info"]/dl/dd[1]/text()')
        loader.add_xpath('doctor_intro', '//table[@class="pop-myinfo-tb"]/tr[@class="last"]/td/p/text()')
        loader.add_xpath('doctor_goodAt', '//table[@class="pop-myinfo-tb"]/tr[5]/td/text()')
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
