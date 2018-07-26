# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem


class Cdcj120Spider(scrapy.Spider):
    """
    成都长江医院
    """
    name = 'cdcj120'
    allowed_domains = ['cdcj120.com']
    start_urls = ['http://www.cdcj120.com/About/introduce.html']

    hospital_intro_link = 'http://www.cdcj120.com/About/introduce.html'
    dept_link = 'http://www.cdcj120.com/Department/index.html'
    doctor_link = 'http://www.cdcj120.com/Expert/yishiinfo.html'
    hospital_name = '成都长江医院 '
    host = 'http://www.cdcj120.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.cdcj120.com',
        'Referer': 'http://www.cdcj120.com/About/index.html',
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
        yield Request(self.hospital_intro_link, headers=self.headers, callback=self.parse)
        # 科室信息
        yield Request(self.dept_link, headers=self.headers, callback=self.parse_hospital_dep)
        # 医生信息
        yield Request(self.doctor_link, headers=self.headers, callback=self.parse_doctor_info)

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('>>>>>>正在抓取{}:医院信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '门诊上午_8:00-12:00;门诊下午_14:00-17:30')
        loader.add_value('hospital_level', '二级甲等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '综合医院')
        loader.add_value('hospital_addr', '成都市东三环龙泉驿区十陵街道江华路8号')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '龙泉驿区')
        loader.add_value('hospital_phone', '急救电话_028-84615120;电话咨询_028-84604546转科室;'
                                           '24小时医护热线_028-84615789')
        loader.add_xpath('hospital_intro',
                         '//article[@class="content"]/div',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('is_medicare', '是')
        loader.add_value('medicare_type', '成都市医保、工伤保险定点医院')
        loader.add_value('registered_channel', '官网或官方微信公众号(工作日),法定节假日电话预约')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

    def parse_hospital_dep(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        dept_links = response.xpath('//div[@class="department-list"]/dd/span/a/@href').extract()
        if dept_links:
            for each_dept_link in dept_links:
                dept_request = Request(urljoin(self.host, each_dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep_detail,
                                       dont_filter=True)
                dept_request.meta['Referer'] = response.url
                yield dept_request

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_xpath('dept_name', '//div[@class="list-item fl"]/h1/text()', MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', self.hospital_name)
        # loader.add_value('dept_type', dept_type)
        loader.add_xpath('dept_info',
                         '//div[@class="list-item fl"]/p',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//ul[@class="expert-list clearfix"]/li')
        for each_doctor_link in doctor_links:
            doctor_link = each_doctor_link.xpath('h2/a/@href').extract_first('')
            doctor_name = each_doctor_link.xpath('h2/a/text()').extract_first('')
            dept_name = each_doctor_link.xpath('p/strong[1]/text()').extract_first('')
            doctor_level = each_doctor_link.xpath('p/strong[2]/text()').extract_first('')
            if doctor_link and doctor_name:
                doctor_detail_request = Request(urljoin(self.host, doctor_link),
                                                headers=self.headers,
                                                callback=self.parse_doctor_info_detail,
                                                meta={'doctor_name': doctor_name,
                                                      'dept_name': dept_name,
                                                      'doctor_level': doctor_level},
                                                dont_filter=True)
                # 测试排班信息
                # doctor_detail_request = Request('http://www.cdcj120.com/Expert/view/id/54.html',
                #                                 headers=self.headers,
                #                                 callback=self.parse_doctor_info_detail,
                #                                 meta={'doctor_name': doctor_name,
                #                                       'dept_name': dept_name,
                #                                       'doctor_level': doctor_level},
                #                                 dont_filter=True)
                doctor_detail_request.meta['Referer'] = response.url
                yield doctor_detail_request
        next_page = response.xpath('//a[@class="next"]/@href').extract_first('')
        if next_page:
            next_page_link = urljoin(self.host, next_page)
            next_request = Request(next_page_link,
                                   headers=self.headers,
                                   callback=self.parse_doctor_info)
            next_request.meta['Referer'] = response.url
            yield next_request

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生详细信息>>>>>>'.format(self.hospital_name))
        doctor_name = response.meta['doctor_name']
        dept_name = response.meta['dept_name']
        doctor_level = response.meta['doctor_level']
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_value('doctor_name', doctor_name)
        loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags, match_special))
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('doctor_level', doctor_level, MapCompose(custom_remove_tags, match_special))
        loader.add_xpath('doctor_intro',
                         '//div[@class="doctor-details"]/div[2]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_xpath('doctor_goodAt',
                         '//div[@class="doctor-details"]/div[2]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
        # 获取医生排班信息
        reg_tr_list = response.xpath('//div[@class="list-content doctor-clinic"]/table/tr[position()>1]')
        is_has_reg = response.xpath('//div[@class="list-content doctor-clinic"]/table/tr[position()>1]'
                                    '/td/span[@class="seleced blue"]')
        reg_date = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        if is_has_reg:
            for each_td in reg_tr_list:
                i = 0
                reg_time = each_td.xpath('td[1]/text()').extract_first('')
                all_reg_info = each_td.xpath('td[position()>1]')
                for each_reg_info in all_reg_info:
                    reg_info_date = reg_date[i]
                    i += 1
                    has_reg = each_reg_info.xpath('span[@class="seleced blue"]')
                    if has_reg:
                        reg_info = '{0}{1}'.format(reg_info_date, reg_time)
                        reg_loader = CommonLoader2(item=DoctorRegInfoItem(), response=response)
                        reg_loader.add_value('doctor_name', doctor_name)
                        reg_loader.add_value('dept_name',
                                             dept_name,
                                             MapCompose(custom_remove_tags, match_special))
                        reg_loader.add_value('hospital_name', self.hospital_name)
                        reg_loader.add_value('reg_info', reg_info)
                        reg_loader.add_value('update_time', now_day())
                        reg_item = reg_loader.load_item()
                        yield reg_item

    def parse_doctor_reg_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生排班信息>>>>>>'.format(self.hospital_name))
