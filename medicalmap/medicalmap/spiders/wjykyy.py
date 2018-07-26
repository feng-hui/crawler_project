# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, match_special2
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem


class WjykyySpider(scrapy.Spider):
    """
    绵阳万江眼科医院
    """
    name = 'wjykyy'
    allowed_domains = ['wjykyy.com']
    start_urls = ['http://www.wjykyy.com/index.php?m=&v=aboutus&mid=2&id=']

    hospital_intro_link = 'http://www.wjykyy.com/index.php?m=&v=aboutus&mid=2&id='
    dept_link = ''
    doctor_link = 'http://www.wjykyy.com/index.php?m=&v=experts&mid=37&id='
    hospital_name = '绵阳万江眼科医院'
    host = 'http://www.wjykyy.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.wjykyy.com',
        'Referer': 'http://www.wjykyy.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        'DOWNLOAD_DELAY': 5,
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
        # yield Request(self.dept_link, headers=self.headers, callback=self.parse_hospital_dep)
        # 医生信息
        yield Request(self.doctor_link, headers=self.headers, callback=self.parse_doctor_info)

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('>>>>>>正在抓取{}:医院信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '门诊时间(无假日医院)8:30-17:30')
        loader.add_value('hospital_level', '三级乙等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '专科医院')
        loader.add_value('hospital_addr', '绵阳市经开区红塔路16号（绵阳市红星街97号）')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '绵阳市')
        loader.add_value('hospital_county', '')
        loader.add_value('hospital_phone', '0816-2265553;0816-2261517')
        loader.add_xpath('hospital_intro',
                         '//div[@class="content-left pull-left"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('is_medicare', '是')
        # loader.add_value('medicare_type', '')
        loader.add_value('registered_channel', '现场预约(一楼挂号交费处);电话预约;官网')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item
        # 科室信息
        dept_links = response.xpath('//div[@class="ddsmoothmenu"]/ul/li[position()=4]/ul/li')
        for each_dept_link in dept_links:
            dept_link = each_dept_link.xpath('a/@href').extract_first('')
            dept_name = each_dept_link.xpath('a/text()').extract_first('')
            if dept_link and dept_name:
                dept_request = Request(dept_link,
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep,
                                       meta={'dept_name': dept_name})
                dept_request.meta['Referer'] = response.url
                yield dept_request

    def parse_hospital_dep(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        dept_links = response.xpath('//div[@class="middep_list"]/a[contains(text(),'
                                    '"详情")]/@href').extract_first('')
        if dept_links:
            dept_request = Request(dept_links,
                                   headers=self.headers,
                                   callback=self.parse_hospital_dep_detail,
                                   dont_filter=True,
                                   meta={'dept_name': response.meta['dept_name']})
            dept_request.meta['Referer'] = response.url
            yield dept_request

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_value('dept_name',
                         response.meta['dept_name'],
                         MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', self.hospital_name)
        # loader.add_value('dept_type', dept_type)
        loader.add_xpath('dept_info',
                         '//div[@class="content-left pull-left departmentintro"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//div[@class="divexpertimg"]/a/@href').extract()
        for each_doctor_link in doctor_links:
            doctor_detail_request = Request(urljoin(self.host, each_doctor_link),
                                            headers=self.headers,
                                            callback=self.parse_doctor_info_detail,
                                            dont_filter=True)
            doctor_detail_request.meta['Referer'] = response.url
            yield doctor_detail_request
        next_page = response.xpath('//div[@id="page"]/a[contains(text(),"下一页")]/@href').extract_first('')
        if next_page:
            next_page_link = urljoin(self.host, next_page)
            next_request = Request(next_page_link,
                                   headers=self.headers,
                                   callback=self.parse_doctor_info)
            next_request.meta['Referer'] = response.url
            yield next_request

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生详细信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_xpath('doctor_name',
                         '//div[@class="viewexpert_demo"]/p[1]/text()',
                         MapCompose(custom_remove_tags))
        loader.add_xpath('dept_name',
                         '//div[@class="viewexpert_demo"]/p[3]/text()',
                         MapCompose(custom_remove_tags, match_special))
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_xpath('doctor_level',
                         '//div[@class="viewexpert_demo"]/p[2]/text()',
                         MapCompose(custom_remove_tags, match_special, match_special2))
        loader.add_xpath('doctor_intro',
                         '//div[@class="viewexpert_detail"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_xpath('doctor_goodAt',
                         '//div[@class="viewexpert_demo"]/p[4]/text()',
                         MapCompose(custom_remove_tags))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
        # 获取医生排班信息
        reg_tr_list = response.xpath('//div[@class="viewexpert_detail"]/table/tr[position()>1]')
        is_has_reg = response.xpath('//div[@class="viewexpert_detail"]/table/tr[position()>1]/td/img')
        reg_date = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        if is_has_reg:
            for each_td in reg_tr_list:
                i = 0
                reg_time = each_td.xpath('td[1]/text()').extract_first('')
                all_reg_info = each_td.xpath('td[position()>1]')
                for each_reg_info in all_reg_info:
                    reg_info_date = reg_date[i]
                    i += 1
                    has_reg = each_reg_info.xpath('img')
                    if has_reg:
                        reg_info = '{0}{1}'.format(reg_info_date, reg_time)
                        reg_loader = CommonLoader2(item=DoctorRegInfoItem(), response=response)
                        reg_loader.add_xpath('doctor_name',
                                             '//div[@class="viewexpert_demo"]/p[1]/text()',
                                             MapCompose(custom_remove_tags))
                        reg_loader.add_xpath('dept_name',
                                             '//div[@class="viewexpert_demo"]/p[3]/text()',
                                             MapCompose(custom_remove_tags, match_special))
                        reg_loader.add_value('hospital_name', self.hospital_name)
                        reg_loader.add_value('reg_info', reg_info)
                        reg_loader.add_value('update_time', now_day())
                        reg_item = reg_loader.load_item()
                        yield reg_item

    def parse_doctor_reg_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生排班信息>>>>>>'.format(self.hospital_name))
