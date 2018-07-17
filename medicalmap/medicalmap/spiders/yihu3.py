# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from medicalmap.items import DoctorRegInfoItem, YiHuLoader


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

    def start_requests(self):
        for each_url in self.start_urls:
            yield SplashRequest(each_url, callback=self.parse)

    def parse(self, response):
        """获取医生排班信息"""
        hospital_name = response.xpath('//div[@class="hos-info"]/h1/text()').extract_first('')
        all_doctors_link = response.xpath('//ul[@class="doc-results clearfix"]/li')
        self.logger.info('>>>>>>当前页共有{}个医生'.format(str(len(all_doctors_link))))
        for each_doctor in all_doctors_link:
            loader = YiHuLoader(item=DoctorRegInfoItem(), selector=each_doctor)
            loader.add_xpath('doctor_name', 'div/dl[@class="doctor-info"]/dt/a/text()')
            loader.add_value('hospital_name', hospital_name)
            doctor_reg_info_item = loader.load_item()
            yield doctor_reg_info_item

