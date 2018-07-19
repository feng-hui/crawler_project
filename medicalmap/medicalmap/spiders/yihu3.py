# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy_splash import SplashRequest
from medicalmap.items import DoctorRegInfoItem, YiHuLoader
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import custom_remove_tags, clean_info, now_day
from scrapy.http import Request


class Yihu3Spider(scrapy.Spider):
    """
    利用scrapy splash来抓取健康之路医生排班信息
    """
    name = 'yihu3'
    allowed_domains = ['yihu.com']
    start_urls = ['https://www.yihu.com/hospital/guahao/30213E7BB0044D2C89B9C29BEA34143E.shtml']
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
        'Referer': 'https://www.yihu.com/hospital/sc/30213E7BB0044D2C89B9C29BEA34143E.shtml',
        'Upgrade-Insecure-Requests': '1'
    }
    doctor_info = {}
    crawled_doctor_ids = set()

    def start_requests(self):
        for each_url in self.start_urls:
            yield SplashRequest(each_url, callback=self.parse,splash_headers=self.headers)

    def parse(self, response):
        """获取医生排班信息"""
        self.logger.info(response.headers)
        hospital_name = response.xpath('//div[@class="hos-info"]/h1/text()').extract_first('')
        all_doctors_link = response.xpath('//ul[@class="doc-results clearfix"]/li')
        self.logger.info('>>>>>>当前页共有{}个医生……'.format(str(len(all_doctors_link))))
        for each_doctor in all_doctors_link:
            doctor_website = each_doctor.xpath('div/dl[@class="doctor-info"]/dt/a/@href').extract_first('')
            doctor_name = each_doctor.xpath('div/dl[@class="doctor-info"]/dt/a/text()').extract_first('')
            reg_info_list = each_doctor.xpath('div[@class="doc-result-schedule"]/div/div/ul/li[@data-arrangeid]')
            self.logger.info('>>>>>>当前医生一周内的排班信息有{}条……'.format(str(len(reg_info_list))))
            for each_reg_info in reg_info_list:
                loader = YiHuLoader(item=DoctorRegInfoItem(), selector=each_reg_info)
                reg_date = each_reg_info.xpath('a/span/em[1]/text()').extract_first('')
                reg_time = each_reg_info.xpath('a/span/em[2]/text()').extract_first('')
                loader.add_value('doctor_name', doctor_name)
                loader.add_value('hospital_name', hospital_name)
                loader.add_value('reg_info',
                                 '{0}{1}'.format(reg_date, reg_time),
                                 MapCompose(custom_remove_tags, clean_info))
                dept_name = self.doctor_info.get(doctor_name)
                self.logger.info('科室:{}'.format(dept_name))
                # 获取医生科室信息
                if doctor_website and not dept_name:
                    doctor_id = re.search(r'/sc/(.*?)\.shtml', doctor_website)
                    if doctor_id and doctor_id.group(1) not in self.crawled_doctor_ids:
                        self.crawled_doctor_ids.add(doctor_id.group(1))
                        self.logger.info('>>>>>>未抓取过该医生的科室信息,即将开始抓取医生个人主页相关信息……')
                        doctor_website_request = Request(doctor_website,
                                                         headers=self.headers,
                                                         callback=self.parse_doctor_website,
                                                         meta={'loader': loader, 'doctor_name': doctor_name})
                        doctor_website_request.meta['Referer'] = response.url
                        yield doctor_website_request
                else:
                    self.logger.info('>>>>>>已经抓取过该医生的科室信息……')
                    loader.add_value('dept_name', dept_name)
                    loader.add_value('update_time', now_day())
                    doctor_reg_info_item = loader.load_item()
                    yield doctor_reg_info_item

    def parse_doctor_website(self, response):
        self.logger.info('>>>>>>正在抓取医生个人主页相关信息……')
        dept_name = response.xpath('//div[@class="doctor-info"]/dl/dd[2]/a[2]/text()').extract_first('')
        doctor_name = response.meta['doctor_name']
        self.doctor_info.setdefault(doctor_name, dept_name)
        loader = response.meta['loader']
        loader.add_value('dept_name', dept_name)
        loader.add_value('update_time', now_day())
        doctor_reg_info_item = loader.load_item()
        yield doctor_reg_info_item
