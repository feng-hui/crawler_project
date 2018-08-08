# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from scrapy_splash import SplashRequest
from scrapy.loader.processors import MapCompose
from medicalmap.items import DoctorRegInfoItem, YiHuLoader
from medicalmap.utils.common import custom_remove_tags, clean_info, now_day, now_year



class Yihu3Spider(scrapy.Spider):
    """
    利用scrapy splash来抓取健康之路医生排班信息
    """
    name = 'yihu3'
    allowed_domains = ['yihu.com']
    start_urls = ['https://www.yihu.com/hospital/23/241.shtml']
    start_entry_url = 'https://www.yihu.com/hospital/23/241.shtml'
    custom_settings = {
        'SPLASH_URL': 'http://101.132.105.200:8050/',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810
        },
        'SPIDER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100
        },
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
        # 'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage'
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.yihu.com',
        'Referer': 'https://www.yihu.com/hospital/',
        'Upgrade-Insecure-Requests': '1'
    }
    doctor_info = {}
    crawled_doctor_ids = set()
    host = 'https://www.yihu.com'

    def start_requests(self):
        yield SplashRequest(self.start_entry_url,
                            callback=self.parse,
                            splash_headers=self.headers)

    def parse(self, response):
        """
        获取医院信息
        """
        self.logger.info('>>>>>>正在获取医院信息……>>>>>>')
        all_hospital_links = response.xpath('//div[@class="c-hidden disen-list-hos c-f12"]/ul/li[14]')
        self.logger.info('该地区共{}家医院'.format(str(len(all_hospital_links))))
        for each_hospital_link in all_hospital_links:
            hospital_link = each_hospital_link.xpath('a/@href').extract_first('')
            dep_request = SplashRequest(hospital_link,
                                        splash_headers=self.headers,
                                        callback=self.parse_hospital_dep)
            self.headers['Referer'] = response.url
            yield dep_request

    def parse_hospital_dep(self, response):
        """
        获取科室信息
        """
        self.logger.info('>>>>>>正在抓取科室信息……>>>>>>')
        hospital_name = response.xpath('//div[@class="hos-info"]/h1/text()').extract_first('')
        all_dept_links = response.xpath('//dd[@class="ks-2"]/ul/li')
        self.logger.info('{}：共有{}个科室'.format(hospital_name, str(len(all_dept_links))))
        for each_dept_link in all_dept_links:
            # 获取科室挂号信息
            dept_link = each_dept_link.xpath('a/@href').extract_first('')
            dept_name = each_dept_link.xpath('a/text()').extract_first('')
            if dept_link:
                dept_link = urljoin(self.host, dept_link)
                reg_request = SplashRequest(dept_link,
                                            splash_headers=self.headers,
                                            callback=self.parse_doctor_reg_info,
                                            meta={'dept_name': dept_name},
                                            args={'images': 0, 'wait': 5})
                self.headers['Referer'] = response.url
                yield reg_request

    def parse_doctor_reg_info(self, response):
        """
        获取医生排班信息
        """
        self.logger.info('>>>>>>正在抓取医生排班信息……>>>>>>')
        dept_name = response.meta.get('dept_name')
        hospital_name = response.xpath('//div[@class="link-555"]/a/text()').extract_first('')
        all_doctors_link = response.xpath('//ul[@class="doc-results clearfix"]/li')
        self.logger.info('>>>>>>当前页共有{}个医生……'.format(str(len(all_doctors_link))))
        try:
            for each_doctor in all_doctors_link:
                doctor_name = each_doctor.xpath('div/dl[@class="doctor-info"]/dt/a/text()').extract_first('')
                reg_info_list = each_doctor.xpath('div[@class="doc-result-schedule"]/div/div/ul/li[@data-arrangeid]')
                self.logger.info('>>>>>>当前医生[{}]一周内的排班信息有{}条……'.format(doctor_name, str(len(reg_info_list))))
                for each_reg_info in reg_info_list:
                    loader = YiHuLoader(item=DoctorRegInfoItem(), selector=each_reg_info)
                    reg_date = each_reg_info.xpath('a/span/em[1]/text()').extract_first('')
                    reg_time = each_reg_info.xpath('a/span/em[2]/text()').extract_first('')
                    loader.add_value('doctor_name', doctor_name)
                    loader.add_value('dept_name', dept_name)
                    loader.add_value('hospital_name', hospital_name)
                    loader.add_value('reg_info',
                                     '{0}/{1}{2}'.format(now_year(), reg_date, reg_time).replace('/', '-'),
                                     MapCompose(custom_remove_tags, clean_info))
                    loader.add_value('update_time', now_day())
                    reg_info_item = loader.load_item()
                    yield reg_info_item

            # 翻页信息
            next_page = response.xpath('//a[@class="page-next"]/@onclick').extract_first('')
            if next_page:
                next_page_link = re.search(r'\'(.*?)\'', next_page)
                if next_page_link:
                    next_page_link = next_page_link.group(1)
                    reg_request = SplashRequest(next_page_link,
                                                splash_headers=self.headers,
                                                callback=self.parse_doctor_reg_info,
                                                meta={'dept_name': dept_name},
                                                args={'images': 0, 'wait': 5})
                    self.headers['Referer'] = response.url
                    yield reg_request
        except Exception as e:
            self.logger.error('抓取医生排班信息过程中出现错误,错误的眼因是:{}'.format(repr(e)))

