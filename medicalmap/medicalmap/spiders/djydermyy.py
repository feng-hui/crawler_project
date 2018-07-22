# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, get_reg_info
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose
from w3lib.html import remove_tags


class DjydermyySpider(scrapy.Spider):
    """
    都江堰市第二人民医院
    入口:官网
    """
    name = 'djydermyy'
    allowed_domains = ['djydermyy.com']
    start_urls = ['http://www.djydermyy.com/about.aspx?mid=17']
    doctor_link = 'http://www.djydermyy.com/dclist.aspx?mid=19'
    doctor_link_list = ['http://www.djydermyy.com/dclist.aspx?mid=19',
                        'http://www.djydermyy.com/dclist.aspx?mid=19&page=2',
                        'http://www.djydermyy.com/dclist.aspx?mid=19&page=3']
    dept_link = 'http://www.djydermyy.com/about.aspx?mid=93&sid=12'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.djydermyy.com',
        'Referer': 'http://www.djydermyy.com/default.aspx',
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
    hospital_name = '都江堰市第二人民医院'
    host = 'http://www.djydermyy.com'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('正在抓取{}:医院信息'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '上午_8:00-12:00;下午14:00-17:30')
        loader.add_value('hospital_level', '二级甲等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '综合医院')
        loader.add_value('hospital_addr', '四川都江堰市发展路89号')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '都江堰市')
        loader.add_value('hospital_county', '')
        loader.add_value('hospital_phone', '急救电话_028-68963120;免费咨询电话_028-69219766;投诉电话_028-69263900 ')
        loader.add_xpath('hospital_intro', '//div[@class="fleft wd740"]')
        loader.add_value('registered_channel', '电话')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        # 医院信息
        yield hospital_info_item
        # 科室信息
        # 第一版 获取导航菜单子菜单中的科室信息,不全只有10个
        # dept_links = response.xpath('//div[@id="head1_ksdh"]/div/div/a')

        # if dept_links:
        #     for each_dept_link in dept_links:
        #         dept_link = each_dept_link.xpath('@href').extract_first('')
        #         dept_name = each_dept_link.xpath('text()').extract_first('')
        #         if dept_link:
        #             dept_request = Request(urljoin(self.host, dept_link),
        #                                    headers=self.headers,
        #                                    callback=self.parse_hospital_dep_detail,
        #                                    meta={'dept_name': dept_name})
        #             dept_request.meta['Referer'] = response.url
        #             yield dept_request
        # 获取科室信息,第二版
        # 获取默认页面的科室信息
        dept_default_request = Request(self.dept_link,
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep_detail,
                                       meta={'dept_name': '门诊部'},
                                       dont_filter=True)
        dept_default_request.meta['Referer'] = response.url
        yield dept_default_request
        # 获取默认页面中的其他科室信息
        dept_request = Request(self.dept_link,
                               headers=self.headers,
                               callback=self.parse_hospital_dep,
                               dont_filter=True)
        dept_request.meta['Referer'] = response.url
        yield dept_request
        # 医生信息,官网翻页不太好用
        for each_doctor_link in self.doctor_link_list:
            doctor_request = Request(each_doctor_link, headers=self.headers, callback=self.parse_doctor_info)
            doctor_request.meta['Referer'] = response.url
            yield doctor_request

    def parse_hospital_dep(self, response):
        other_dept_links = response.xpath('//ul[@class="ARList"]/li[position()>1]')
        for each_dept_link in other_dept_links:
            dept_link = each_dept_link.xpath('a/@href').extract_first('')
            dept_name = each_dept_link.xpath('a/text()').extract_first('')
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
        loader.add_xpath('dept_info', '//div[@class="fleft wd740"]')
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        doctor_links = response.xpath('//ul[@class="dclist"]/li/div[1]/a')
        for each_doctor in doctor_links:
            doctor_link = each_doctor.xpath('@href').extract_first('')
            if doctor_link:
                doctor_detail_link = urljoin(self.host, doctor_link)
                doctor_detail_request = Request(doctor_detail_link,
                                                headers=self.headers,
                                                callback=self.parse_doctor_detail)
                doctor_detail_request.meta['Referer'] = response.url
                yield doctor_detail_request

    def parse_doctor_detail(self, response):
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_xpath('doctor_name',
                         '//div[@class="fleft wd740"]/div[1]/div[2]/p[2]/text()',
                         MapCompose(custom_remove_tags, match_special))
        loader.add_xpath('dept_name',
                         '//div[@class="fleft wd740"]/div[1]/div[2]/p[1]/text()',
                         MapCompose(custom_remove_tags, match_special))
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_xpath('doctor_level',
                         '//div[@class="fleft wd740"]/div[1]/div[2]/p[3]/text()',
                         MapCompose(custom_remove_tags, match_special))
        loader.add_xpath('doctor_intro',
                         '//div[@class="fleft wd740"]/div[1]/div[2]/div/p[1]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item
        reg_info = response.xpath('//div[@class="fleft wd740"]/div[1]/div[2]/p[4]/text()').extract_first('')
        if reg_info:
            reg_info_list = get_reg_info(reg_info)
            for each_reg_info in reg_info_list:
                reg_loader = CommonLoader2(item=DoctorRegInfoItem(), response=response)
                reg_loader.add_xpath('doctor_name',
                                     '//div[@class="fleft wd740"]/div[1]/div[2]/p[2]/text()',
                                     MapCompose(custom_remove_tags, match_special))
                reg_loader.add_xpath('dept_name',
                                     '//div[@class="fleft wd740"]/div[1]/div[2]/p[1]/text()',
                                     MapCompose(custom_remove_tags, match_special))
                reg_loader.add_value('hospital_name', self.hospital_name)
                reg_loader.add_value('reg_info', each_reg_info)
                reg_loader.add_value('update_time', now_day())
                reg_item = reg_loader.load_item()
                yield reg_item

    def parse_doctor_reg_info(self, response):
        pass
