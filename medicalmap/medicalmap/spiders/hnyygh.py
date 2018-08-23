# -*- coding: utf-8 -*-
import re
import scrapy
from re import S
from urllib.parse import quote
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from scrapy_splash.request import SplashRequest
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, clean_info, get_city, get_county2


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
        # 'DOWNLOAD_DELAY': 3,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 5.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        # 'CONCURRENT_REQUESTS': 16
        'SPLASH_URL': 'http://localhost:8050/',
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
    dept_detail_url = 'http://www.hnyygh.com/searchOrderNumInfoAction.action'
    doctor_url = 'http://www.hnyygh.com/ajaxSearchOrderNumInfoAction.action'
    doctor_detail_url = 'http://www.hnyygh.com/forwardDocInfo.action'

    # lua script
    dept_script = """
    function main(splash, args)
      splash.js_enabled = true
      local ok, reason = splash:go{args.url, http_method="POST", formdata=args.data}
      if ok then
            splash:wait(5)
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
            for each_hospital_link in all_hospital_links[12:13]:
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
                                            headers=self.headers,
                                            args=splash_args,
                                            dont_filter=True,
                                            callback=self.parse_hospital_info,
                                            meta={'hospital_name': org_name})
        except Exception as e:
            self.logger.error(repr(e))

    def parse_hospital_info(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取[{}]医院信息和科室信息>>>>>>'.format(hospital_name))
        hospital_city = response.xpath('//div[@class="jieshao_zi"]/p[4]/text()').extract()
        if hospital_city:
            hospital_address = custom_remove_tags(''.join(hospital_city))
            hospital_city2 = get_city(hospital_address)
            hospital_county = get_county2(hospital_city2, hospital_address)
        else:
            hospital_county = None
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_xpath('hospital_name', '//div[@class="jieshao_zi"]/p/font/text()', MapCompose(custom_remove_tags))
        loader.add_xpath('hospital_level', '//div[@class="jieshao_zi"]/p[2]/text()', MapCompose(custom_remove_tags))
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '')
        loader.add_xpath('hospital_addr', '//div[@class="jieshao_zi"]/p[4]/text()', MapCompose(custom_remove_tags))
        loader.add_value('hospital_pro', '湖南省')
        loader.add_xpath('hospital_city',
                         '//div[@class="jieshao_zi"]/p[4]/text()',
                         MapCompose(custom_remove_tags, get_city))
        loader.add_value('hospital_county', hospital_county)
        loader.add_xpath('hospital_phone', '//div[@class="jieshao_zi"]/p[3]/text()', MapCompose(custom_remove_tags))
        loader.add_xpath('hospital_intro',
                         '//div[@id="starlist"]',
                         MapCompose(remove_tags, custom_remove_tags, clean_info))
        loader.add_value('registered_channel', self.data_source_from)
        loader.add_value('dataSource_from', self.data_source_from)
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

        # 获取科室信息
        self.logger.info('>>>>>>正在抓取[{}]科室信息>>>>>>'.format(hospital_name))
        dept_links = response.xpath('//div[@class="xuanze_kslb"]')
        if dept_links:
            for each_dept_link in dept_links:
                dept_type = each_dept_link.xpath('div[1]/ul/li/text()').extract_first('')
                all_dept_links = each_dept_link.xpath('div[2]/ul/li/a')
                for dept_link in all_dept_links:
                    # dept_name = dept_link.xpath('text()').extract_first('')
                    data_info = dept_link.xpath('@onclick').extract_first('')
                    if data_info:
                        data_info = ''.join(re.findall(r'\S+', data_info))
                        is_sp_time = re.search(r'isSpTime:\'(.*?)\'', data_info)
                        pay_mode = re.search(r'paymode:\'(.*?)\'', data_info)
                        dept_id = re.search(r'platformDeptId:\'(.*?)\'', data_info)
                        hos_id = re.search(r'platformHosId:\'(.*?)\'', data_info, S)
                        dept_name = re.search(r'tempDeptName:\'(.*?)\'', data_info, S)
                        org_name = re.search(r'orgname:\'(.*?)\'', data_info, S)
                        if dept_id and hos_id and dept_name and org_name:
                            is_sp_time = is_sp_time.group(1)
                            pay_mode = pay_mode.group(1)
                            dept_id = dept_id.group(1)
                            hos_id = hos_id.group(1)
                            dept_name = dept_name.group(1)
                            org_name = org_name.group(1)
                            data = {
                                'isSpTime': str(is_sp_time),
                                'paymode': quote(pay_mode),
                                'doctorCollectResult': '',
                                'platformDeptId': str(dept_id),
                                'orgname': quote(org_name),
                                'tempDeptName': quote(dept_name),
                                'platformHosId': str(hos_id),
                                'platformDoctorId': ''
                            }
                            self.headers.update({
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Origin': 'http://www.hnyygh.com',
                                'Referer': 'http://www.hnyygh.com/searchDeptmentAction.action',
                                'Pragma': 'no-cache'
                            })
                            splash_args = {
                                'url': self.dept_detail_url,
                                'headers': self.headers,
                                'lua_source': self.dept_script,
                                'data': data
                            }
                            yield SplashRequest(self.dept_detail_url,
                                                endpoint='execute',
                                                args=splash_args,
                                                dont_filter=True,
                                                headers=self.headers,
                                                callback=self.parse_hospital_dep_detail,
                                                meta={'dept_type': dept_type,
                                                      'dept_name': dept_name,
                                                      'hospital_name': org_name})
                            # 获取医生信息
                            data = {
                                'platformDeptId': dept_id,
                                'platformHosId': hos_id,
                                'platformDoctorId': '',
                                'nextNumInfo': '0'
                            }
                            self.headers.update({
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Origin': 'http://www.hnyygh.com',
                                'Referer': 'http://www.hnyygh.com/searchOrderNumInfoAction.action'
                            })
                            splash_args = {
                                'url': self.doctor_url,
                                'headers': self.headers,
                                'lua_source': self.dept_script,
                                'data': data
                            }
                            yield SplashRequest(self.doctor_url,
                                                endpoint='execute',
                                                args=splash_args,
                                                dont_filter=True,
                                                headers=self.headers,
                                                callback=self.parse_doctor_info,
                                                meta={'dept_type': dept_type,
                                                      'dept_name': dept_name,
                                                      'dept_id': dept_id,
                                                      'hospital_name': org_name})

    def parse_hospital_dep_detail(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取[{}]科室详细信息>>>>>>'.format(hospital_name))
        dept_type = response.meta.get('dept_type')
        dept_name = response.meta.get('dept_name')
        if dept_name and hospital_name:
            loader = CommonLoader2(item=HospitalDepItem(), response=response)
            loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
            # loader.add_xpath('hospital_name',
            #                  '//div[@class="schedule_zi"]/p[1]/font[1]/text()',
            #                  MapCompose(custom_remove_tags))
            loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
            loader.add_value('dept_type', dept_type, MapCompose(custom_remove_tags))
            loader.add_xpath('dept_info',
                             '//div[@id="schedule_jienr"]',
                             MapCompose(remove_tags, custom_remove_tags))
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('update_time', now_day())
            dept_item = loader.load_item()
            yield dept_item

    def parse_doctor_info(self, response):
        # 获取医生信息
        self.logger.info('>>>>>>正在抓取[{}]医生信息>>>>>>'.format(response.meta.get('hospital_name')))
        dept_type = response.meta.get('dept_type')
        dept_id_backup = response.meta.get('dept_id')
        # doctor_links = response.xpath('//div[@class="time_middle"]/div[1]/div[2]/div/b/a/onclick').extract()
        try:
            # doctor_links = response.xpath('//a[@title="查看医生详情"]/@onclick').extract()
            doctor_links = response.xpath('//div[@class="yisheng_tu"]/a/@onclick').extract()
            if doctor_links:
                for each_doctor_info in doctor_links:
                    data_info = ''.join(re.findall(r'\S+', each_doctor_info))
                    is_sp_time = re.search(r'isSpTime:(.*?),', data_info)
                    dept_name = re.search(r'deptName:\'(.*?)\'', data_info, S)
                    doctor_name = re.search(r'doctName:\'(.*?)\'', data_info, S)
                    org_code = re.search(r'orgcode:\'(.*?)\'', data_info, S)
                    doctor_id = re.search(r'platformDoctId:\'(.*?)\'', data_info, S)
                    visit_level = re.search(r'visitLevel:\'(.*?)\'', data_info)
                    org_name = re.search(r'orgname:\'(.*?)\'', data_info, S)
                    dept_id = re.search(r'platformDeptId:\'(.*?)\'', data_info, S)
                    pay_mode = re.search(r'paymode:\'(.*?)\'', data_info, S)
                    if is_sp_time and dept_name and doctor_name and org_code \
                            and doctor_id and visit_level and org_name and dept_id and pay_mode:
                        is_sp_time = is_sp_time.group(1)
                        dept_name = dept_name.group(1)
                        doctor_name = doctor_name.group(1)
                        org_code = org_code.group(1)
                        doctor_id = doctor_id.group(1)
                        visit_level = visit_level.group(1)
                        org_name = org_name.group(1)
                        dept_id = dept_id.group(1)
                        pay_mode = pay_mode.group(1)
                        doctor_level = visit_level.replace(dept_name, '')
                        data = {
                            'isSpTime': is_sp_time.strip(),
                            'docInfo.deptName': quote(dept_name),
                            'docInfo.doctName': quote(doctor_name),
                            'docInfo.platformDeptId': str(dept_id) if dept_id else dept_id_backup,
                            'docInfo.orgcode': str(org_code),
                            'docInfo.platformDoctId': str(doctor_id),
                            'docInfo.visitLevel': quote(visit_level),
                            'orgname': quote(org_name),
                            'platformDeptId': dept_id if dept_id else dept_id_backup,
                            'paymode': quote(pay_mode)
                        }
                        self.headers.update({
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'Origin': 'http://www.hnyygh.com',
                            'Referer': 'http://www.hnyygh.com/searchOrderNumInfoAction.action'
                        })
                        splash_args = {
                            'url': self.doctor_detail_url,
                            'headers': self.headers,
                            'lua_source': self.dept_script,
                            'data': data
                        }
                        yield SplashRequest(self.doctor_detail_url,
                                            endpoint='execute',
                                            args=splash_args,
                                            dont_filter=True,
                                            callback=self.parse_doctor_info_detail,
                                            meta={'dept_type': dept_type,
                                                  'dept_name': dept_name,
                                                  'doctor_level': doctor_level,
                                                  'hospital_name': org_name,
                                                  'doctor_name': doctor_name})
        except Exception as e:
            self.logger.error(repr(e))

    def parse_doctor_info_detail(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取[{}]医生详细信息>>>>>>'.format(hospital_name))
        dept_name = response.meta.get('dept_name')
        doctor_level = response.meta.get('doctor_level')
        doctor_name = response.meta.get('doctor_name')
        loader = CommonLoader2(item=DoctorInfoItem(), response=response)
        loader.add_value('doctor_name', doctor_name, MapCompose(custom_remove_tags))
        # loader.add_xpath('doctor_name', '//span[@class="info-name"]/text()', MapCompose(custom_remove_tags))
        loader.add_value('dept_name', dept_name)
        # loader.add_xpath('hospital_name',
        #                  '//div[@class="item gray"]/span[1]/a/text()',
        #                  MapCompose(custom_remove_tags))
        loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
        loader.add_value('doctor_level', doctor_level)
        loader.add_xpath('doctor_intro',
                         '//div[@class="info-main"]/div[3]/span',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_xpath('doctor_goodAt',
                         '//div[@class="info-main"]/div[4]/span',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_value('dataSource_from', self.data_source_from)
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
