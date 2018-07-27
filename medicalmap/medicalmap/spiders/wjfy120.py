# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, clean_info
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem


class Wjfy120Spider(scrapy.Spider):
    """
    成都市温江区妇幼保健院
    """
    name = 'wjfy120'
    allowed_domains = ['wjfy120.com']
    start_urls = ['http://wjfy120.com/']

    hospital_intro_link = 'https://www.wjfy120.com/News/View.asp?ID=1'
    dept_link = 'https://www.wjfy120.com/News/Category.asp?ID=27'
    doctor_link = 'https://www.wjfy120.com/News/Category.asp?ID=38'
    hospital_name = '成都市温江区妇幼保健院'
    host = 'http://www.wjfy120.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.wjfy120.com',
        'Referer': 'https://www.wjfy120.com/index.asp',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        'DOWNLOAD_DELAY': 3,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 10,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 5.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        # 'CONCURRENT_REQUESTS': 16
    }

    def start_requests(self):
        # 医院信息
        # yield Request(self.hospital_intro_link, headers=self.headers, callback=self.parse)
        # 科室信息
        # yield Request(self.dept_link, headers=self.headers, callback=self.parse_hospital_dep_detail)
        # 医生信息
        yield Request(self.doctor_link, headers=self.headers, callback=self.parse_doctor_info)

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('>>>>>>正在抓取{}:医院信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '')
        loader.add_value('hospital_level', '三级乙等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '妇幼保健院')
        loader.add_value('hospital_addr', '成都市温江区万春路140')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '')
        loader.add_value('hospital_phone', '24小时急救电话_028-82723131;咨询电话_围产期保健_028-82715727;'
                                           '咨询电话_妇科门诊_028-82711383;咨询电话_儿童保健_028-82711527;'
                                           '咨询电话_婚检科_028-82720337;'
                                           '投诉电话_028-82724901(上班时间);投诉电话_13688488598(下班时间)')
        loader.add_xpath('hospital_intro',
                         '//div[@id="info_txt"]',
                         MapCompose(remove_tags, custom_remove_tags))
        # loader.add_value('is_medicare', '是')
        # loader.add_value('medicare_type', '')
        loader.add_value('registered_channel', '电话预约;挂号窗口;医院微信公众号')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

    def parse_hospital_dep(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        dept_links = response.xpath('//ul[@id="list2"]/li[position()>1]/a/@href').extract()
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
        loader.add_value('dept_name',
                         '//div[@class="title"]h3/text()',
                         MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', self.hospital_name)
        # loader.add_value('dept_type', response.meta['dept_type'], MapCompose(custom_remove_tags))
        loader.add_xpath('dept_info',
                         '//div[@class="content"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item
        # 其他科室信息
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        dept_links = response.xpath('//ul[@id="list2"]/li[position()>1]/a/@href').extract()
        if dept_links:
            for each_dept_link in dept_links:
                dept_request = Request(urljoin(self.host, each_dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep_detail,
                                       dont_filter=True)
                self.headers['Referer'] = response.url
                yield dept_request

    def parse_doctor_info_transfer(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//a[contains(text(),"更多")]/@href').extract()
        for each_doctor_link in doctor_links:
            doctor_detail_request = Request(urljoin(self.host, each_doctor_link),
                                            headers=self.headers,
                                            callback=self.parse_doctor_info,
                                            dont_filter=True)
            self.headers['Referer'] = response.url
            yield doctor_detail_request

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:更多医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//div[@class="list1"]/ul/li')
        for each_doctor_link in doctor_links:
            doctor_link = each_doctor_link.xpath('a/@href').extract_first('')
            dept_name = response.xpath('//div[@id="current"]/a[2]/text()').extract_first('')
            if doctor_link and dept_name:
                doctor_detail_request = Request(urljoin(self.host, doctor_link),
                                                headers=self.headers,
                                                callback=self.parse_doctor_info_detail,
                                                meta={'dept_name': dept_name},
                                                dont_filter=True)
                self.headers['Referer'] = response.url
                yield doctor_detail_request

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生详细信息>>>>>>'.format(self.hospital_name))
        dept_name = response.meta['dept_name']
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_xpath('doctor_name',
                         '//div[@id="info_title"]/text()',
                         MapCompose(custom_remove_tags, match_special))
        loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', self.hospital_name)
        # loader.add_value('doctor_level', doctor_level, MapCompose(custom_remove_tags, match_special))
        loader.add_xpath('doctor_intro',
                         '//div[@id="info_txt"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_xpath('doctor_goodAt',
                         '//div[@id="info_txt"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
        # 医生排班信息
        params = re.search(r'.*\?(.*?)$', response.url)
        reg_url = 'http://www.scpz120.com/ajax/Doctor.aspx?'
        if params:
            reg_link = '{0}{1}'.format(reg_url, params.group(1).replace('&id', '&kid'))
            reg_request = Request(reg_link,
                                  headers=self.headers,
                                  callback=self.parse_doctor_reg_info,
                                  meta={'doctor_name': doctor_name,
                                        'dept_name': dept_name})
            self.headers['Referer'] = response.url
            yield reg_request

    def parse_doctor_reg_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生排班信息>>>>>>'.format(self.hospital_name))
        doctor_name = response.meta['doctor_name']
        dept_name = response.meta['dept_name']
        reg_tr_list = response.xpath('//table/tr[position()>1]')
        is_has_reg = response.xpath('//table/tr[position()>1]/td/img')
        # reg_date = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        reg_col = ['上午', '下午', '晚班']
        if is_has_reg:
            for each_td in reg_tr_list:
                reg_time = each_td.xpath('td[1]/text()').extract_first('')
                all_reg_info = each_td.xpath('td[position()>1]')
                for index, each_reg_info in enumerate(all_reg_info):
                    reg_info_date = reg_col[index]
                    has_reg = each_reg_info.xpath('img')
                    if has_reg:
                        reg_info = '{0}{1}'.format(reg_time, reg_info_date)
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