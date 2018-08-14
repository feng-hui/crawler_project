# -*- coding: utf-8 -*-
import re
import scrapy
from re import S
from scrapy.http import Request, FormRequest
from urllib.parse import urljoin, quote
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, clean_info, get_city
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from scrapy_splash.request import SplashRequest, SplashFormRequest


class HnyyghSpider(scrapy.Spider):
    name = 'hnyygh'
    allowed_domains = ['hnyygh.com']
    start_urls = ['http://www.hnyygh.com/']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.hnyygh.com',
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
    host = 'http://www.hnyygh.com/'
    data_source_from = '湖南省统一预约挂号服务平台'
    hospital_post_url = 'http://www.hnyygh.com/searchDeptmentAction.action'
    # lua script
    dept_script = """
    function main(splash, args)
      local ok, reason = splash:go{args.url, http_method="POST", formdata=args.data, headers=args.headers}
      splash:wait(5)
      if ok then
            return {html=splash:html()}
      end
    end
    """

    def start_requests(self):
        for each_url in self.start_urls:
            yield SplashRequest(each_url, callback=self.parse, splash_headers=self.headers)

    def parse(self, response):
        """获取医院信息"""
        all_hospital_links = response.xpath('//div[@id="fl_yiyuan_nr"]/div/ul/li/a['
                                            'not(contains(text(),"升级中")) and not(contains(text(),"建设中"))]')
        try:
            for each_hospital_link in all_hospital_links[0:1]:
                # hospital_name = each_link.xpath('text()').extract_first('')
                data_info = each_hospital_link.xpath('@onclick').extract_first('')
                if data_info:
                    data_info = ''.join(re.findall(r'\S+', data_info))
                    is_sp_time = re.search(r'isSpTime:\'(.*?)\'', data_info)
                    plat_form_hos_id = re.search(r'.*platformHosId:\'(.*?)\'', data_info, S)
                    pay_mode = re.search(r'paymode:\'(.*?)\'', data_info, S)
                    org_name = re.search(r'orgname:\'(.*?)\'', data_info, S)
                    if is_sp_time and plat_form_hos_id and pay_mode and org_name:
                        is_sp_time = is_sp_time.group(1)
                        plat_form_hos_id = plat_form_hos_id.group(1)
                        pay_mode = quote(pay_mode.group(1))
                        org_name = quote(org_name.group(1))
                        data = {
                            'isSpTime': is_sp_time,
                            'platformHosId': plat_form_hos_id,
                            'paymode': pay_mode,
                            'orgname': org_name
                        }
                        self.headers.update({
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Origin': 'http://www.hnyygh.com',
                            'Referer': 'http://www.hnyygh.com/'
                        })
                        splash_args = {
                            'url': self.hospital_post_url,
                            'headers': self.headers,
                            'lua_source': self.dept_script,
                            'data': data
                        }
                        yield SplashRequest(self.hospital_post_url,
                                            endpoint='execute',
                                            args=splash_args,
                                            dont_filter=True,
                                            callback=self.parse_hospital_info)
        except Exception as e:
            self.logger.error(repr(e))

    def parse_hospital_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医院信息和科室信息>>>>>>')
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_xpath('hospital_name', '//div[@class="jieshao_zi"]/p/font/text()')
        loader.add_value('consulting_hour', '')
        loader.add_xpath('hospital_level', '//div[@class="jieshao_zi"]/p[2]/text()', MapCompose(custom_remove_tags))
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '')
        loader.add_xpath('hospital_addr', '//div[@class="jieshao_zi"]/p[4]/text()', MapCompose(custom_remove_tags))
        loader.add_value('hospital_pro', '湖南省')
        loader.add_xpath('hospital_city',
                         '//div[@class="jieshao_zi"]/p[4]/text()',
                         MapCompose(custom_remove_tags, get_city))
        loader.add_value('hospital_county', '')
        loader.add_xpath('hospital_phone', '//div[@class="jieshao_zi"]/p[3]/text()', MapCompose(custom_remove_tags))
        loader.add_xpath('hospital_intro',
                         '//div[@id="starlist"]',
                         MapCompose(remove_tags, custom_remove_tags, clean_info))
        # loader.add_value('is_medicare', '是')
        # loader.add_value('medicare_type', '成都市医保、工伤保险定点医院')
        # loader.add_value('registered_channel', '')
        loader.add_value('dataSource_from', self.data_source_from)
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

    def parse_hospital_dep(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        dept_links = response.xpath('//div[@id="about-right-b"]/div[1]|'
                                    '//div[@id="about-right-b"]/div[3]'
                                    )
        if dept_links:
            for each_dept_link in dept_links:
                dept_type = each_dept_link.xpath('div/strong/text()').extract_first('')
                all_dept_links = each_dept_link.xpath('a')
                for dept_link in all_dept_links:
                    dept_detail_link = dept_link.xpath('@href').extract_first('')
                    dept_name = dept_link.xpath('text()').extract_first('')
                    if dept_detail_link and dept_name:
                        dept_request = Request(urljoin(self.host, dept_detail_link),
                                               headers=self.headers,
                                               callback=self.parse_hospital_dep_detail,
                                               dont_filter=True,
                                               meta={'dept_type': dept_type,
                                                     'dept_name': dept_name})
                        dept_request.meta['Referer'] = response.url
                        yield dept_request

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_value('dept_name', response.meta['dept_name'], MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('dept_type', response.meta['dept_type'], MapCompose(custom_remove_tags))
        loader.add_xpath('dept_info',
                         '//div[@class="kscontent"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//div[@class="product0"]')
        for each_doctor_link in doctor_links:
            doctor_link = each_doctor_link.xpath('a[1]/@href').extract_first('')
            doctor_name = each_doctor_link.xpath('a[2]/text()').extract_first('')
            dept_name = each_doctor_link.xpath('a[4]/text()').extract_first('')
            doctor_level = each_doctor_link.xpath('a[3]/text()').extract_first('')
            if doctor_link and doctor_name:
                doctor_detail_request = Request(urljoin(self.host, doctor_link),
                                                headers=self.headers,
                                                callback=self.parse_doctor_info_detail,
                                                meta={'doctor_name': doctor_name,
                                                      'dept_name': dept_name,
                                                      'doctor_level': doctor_level},
                                                dont_filter=True)
                doctor_detail_request.meta['Referer'] = response.url
                yield doctor_detail_request
        next_page = response.xpath('//div[@class="SplitPage"]/a[5]/@href').extract_first('')
        if next_page and next_page != response.url:
            next_request = Request(next_page,
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
                         '//div[@id="about-right-b"]/p',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_xpath('doctor_goodAt',
                         '//div[@id="about-right-b"]/p',
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
