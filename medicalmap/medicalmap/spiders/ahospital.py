# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, get_hospital_alias
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, HospitalAliasItem


class AHospitalSpider(scrapy.Spider):
    name = 'a_hospital'
    allowed_domains = ['a-hospital.com']
    start_urls = ['http://www.a-hospital.com/w/%E5%85%A8%E5%9B%BD%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8']
    entry_url = 'http://www.a-hospital.com/w/%E9%A6%96%E9%A1%B5'
    host = 'http://www.a-hospital.com'
    test_url = 'http://www.a-hospital.com/w/%E4%B8%AD%E6%97%A5%E5%8F%8B%E5%A5%BD%E5%8C%BB%E9%99%A2'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.a-hospital.com',
        'Referer': 'http://www.a-hospital.com/w/%E9%A6%96%E9%A1%B5',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        'DOWNLOAD_DELAY': 1,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        # 'CONCURRENT_REQUESTS': 16
    }

    def start_requests(self):
        # for each_url in self.start_urls:
        #     yield Request(each_url, headers=self.headers, callback=self.parse)

        # 测试页面
        self.headers['Referer'] = 'http://www.a-hospital.com/w/%E5%8C%97%E4%BA%AC%E5%B8%' \
                                  '82%E6%9C%9D%E9%98%B3%E5%8C%BA%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8'
        yield Request(self.test_url, headers=self.headers, callback=self.parse_hospital_detail)

    def parse(self, response):
        """
        获取所有国内所有地区的链接
        """
        self.logger.info('>>>>>>正在抓取全国医院列表……>>>>>>')
        all_areas_list = response.xpath('//p/b/a[contains(text(),"医院列表")]/'
                                        'following::p[1]/a[not(contains(@href,"index"))]/@href').extract()
        try:
            for each_area in all_areas_list[0:1]:
                self.headers['Referer'] = response.url
                yield Request(urljoin(self.host, each_area),
                              headers=self.headers,
                              callback=self.parse_area)
        except Exception as e:
            self.logger.error('抓取全国医院列表过程中出错了,错误的原因是:{}'.format(repr(e)))

    def parse_area(self, response):
        self.logger.info('>>>>>>正在抓取地区医院列表……>>>>>>')
        all_hospital_list = response.xpath('//div[@id="bodyContent"]/ul[3]/li/b/a/@href').extract()
        for each_hospital in all_hospital_list[0:1]:
            self.headers['Referer'] = response.url
            yield Request(urljoin(self.host, each_hospital),
                          headers=self.headers,
                          callback=self.parse_hospital_detail)

    def parse_hospital_detail(self, response):
        self.logger.info('>>>>>>正在抓取医院详细信息……>>>>>>')
        # 医院信息
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_xpath('hospital_name', '//table[@class="nav"]/tr/td/strong/text()')
        # loader.add_value('consulting_hour', '')
        loader.add_value('hospital_level', '')
        loader.add_value('hospital_type', '')
        loader.add_value('hospital_category', '')
        loader.add_value('hospital_addr', '')
        loader.add_value('hospital_pro', '')
        loader.add_value('hospital_city', '')
        loader.add_value('hospital_county', '')
        loader.add_value('hospital_phone',
                         '//div[@id="bodyContent"]/ul[1]/li/b[contains(text(),"联系电话")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special)
                         )
        loader.add_xpath('hospital_intro',
                         '//div[@class="describe htmledit"]',
                         MapCompose(remove_tags, custom_remove_tags))
        # loader.add_value('is_medicare', '是')
        # loader.add_value('medicare_type', '')
        # loader.add_value('registered_channel', '')
        loader.add_value('dataSource_from', '医学百科')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

        # 科室信息
        dept_info = response.xpath('//div[@id="bodyContent"]/ul[1]/li/'
                                   'b[contains(text(),"重点科室")]/ancestor::li[1]')
        all_dept_info = match_special(dept_info.xpath('string(.)').extract_first(''))
        for each_dept in all_dept_info.split('、'):
            loader = CommonLoader2(item=HospitalDepItem(), response=response)
            loader.add_value('dept_name', each_dept, MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_name',
                             '//table[@class="nav"]/tr/td/strong/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('update_time', now_day())
            dept_item = loader.load_item()
            yield dept_item

        # 医院别名信息
        hospital_name = response.xpath('//div[@id="bodyContent"]/p[1]/b/text()').extract_first('')
        if hospital_name and '（' in hospital_name:
            alias_name = get_hospital_alias(hospital_name)
            if alias_name:
                alias_loader = CommonLoader2(item=HospitalAliasItem(), response=response)
                alias_loader.add_xpath('hospital_name',
                                       '//table[@class="nav"]/tr/td/strong/text()',
                                       MapCompose(custom_remove_tags))
                alias_loader.add_value('hospital_alias_name', alias_name)
                alias_loader.add_value('update_time', now_day())
                alias_item = alias_loader.load_item()
                yield alias_item
