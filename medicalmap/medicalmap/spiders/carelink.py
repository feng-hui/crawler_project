# -*- coding: utf-8 -*-
import re
import json
import scrapy
from cpca import transform
from scrapy.http import Request
from w3lib.html import remove_tags
from urllib.parse import urljoin, quote
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, match_special2, now_time, clean_info2, MUNICIPALITY2
from medicalmap.utils.city_code import carelink2_web3_city_location, carelink_web3_provinces, carelink_web3_hot_city


class CarelinkSpider(scrapy.Spider):
    name = 'carelink'
    allowed_domains = ['carelink.cn']
    start_urls = ['https://www.carelink.cn/hos/hospital.htm']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '',
        'Host': 'www.carelink.cn',
        'Referer': 'https://www.carelink.cn/index.htm',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': random.randint(1, 2),
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 16
    }
    host = 'https://www.carelink.cn'
    doctor_image_host = 'https://image.carelink.cn'
    data_source_from = '快医网'
    dept_url = 'https://www.carelink.cn/dep/departments.htm?hi={}&dep_id={}&sub_dep_id=0'
    doctor_url = 'https://www.carelink.cn/hos/doctorsByDepartmentId.htm?hi={}&dep_id=0&' \
                 'sub_dep_id=0&consult_type=1&curr={}'
    doctor_url2 = ''
    hospital_entry = 'https://www.carelink.cn/hos/hospital.htm'
    hospital_url = 'https://www.carelink.cn/hos/index.htm?hi={}&sd_id=0&sds_id=0'
    hospital_next_url = 'https://www.carelink.cn/hos/getHospital.htm?cityId=0&hl=0&sdId=0&sdsId=0' \
                        '&pubPreId={}&priPreId={}'
    pub_pre_id = '0'
    pri_pre_id = '0'

    def start_requests(self):
        for each_province in carelink_web3_provinces:
            province_name = each_province.get('name')
            carelink2_web3_city_location['provinceId'] = each_province.get('id')
            carelink2_web3_city_location['provinceName'] = province_name
            carelink2_web3_city_location['provincePinyin'] = each_province.get('pinyin')
            care_link_cookies = 'carelink_web3_hot_city={0};carelink_web3_provinces={1};' \
                                'carelink2_web3_city_location={2}'.format(quote(json.dumps(carelink_web3_hot_city)),
                                                                          quote(json.dumps(carelink_web3_provinces)),
                                                                          quote(json.dumps(carelink2_web3_city_location)))
            # cookies = care_link_cookies
            # print(care_link_cookies)
            # care_link_cookies = {
            #     'carelink_web3_hot_city': quote(json.dumps(carelink_web3_hot_city)),
            #     'carelink_web3_provinces': quote(json.dumps(carelink_web3_provinces)),
            #     'carelink2_web3_city_location': quote(json.dumps(carelink2_web3_city_location))
            # }
            self.headers['Cookie'] = care_link_cookies
            yield Request(self.hospital_entry,
                          headers=self.headers,
                          # cookies=care_link_cookies,
                          callback=self.parse,
                          dont_filter=True,
                          meta={
                              'province_name': province_name,
                              'cookies': care_link_cookies
                          })

    def parse(self, response):
        try:
            province_name = response.meta.get('province_name')
            all_hospital_links = response.xpath('//ul[@id="hospital-list"]/li')
            for each_hospital_link in all_hospital_links:
                hospital_link = each_hospital_link.xpath('a/@href').extract_first('')
                hospital_name = each_hospital_link.xpath('div[2]/p[1]/a/text()').extract_first('')
                data_type = each_hospital_link.xpath('div[1]/@data-type').extract_first('')
                hospital_id = each_hospital_link.xpath('div[1]/@data-id').extract_first('')

                # 获取医院信息
                if hospital_link:
                    hospital_link = urljoin(self.host, hospital_link)
                    self.headers['Referer'] = response.url
                    yield Request(hospital_link,
                                  headers=self.headers,
                                  callback=self.parse_hospital_info,
                                  dont_filter=True,
                                  meta={
                                      'hospital_name': hospital_name,
                                      'hospital_id': hospital_id,
                                      'data_type': data_type,
                                      'province_name': province_name
                                  })
            # 翻页
            has_next = response.xpath('//li[@id="more-hospital"][not(contains(@class,"hide"))]')
            if has_next:
                pub_pre_id = response.xpath('//ul[@id="hospital-list"]/li/div[1][@data-type="1"]/@data-id').extract()
                pri_pre_id = response.xpath('//ul[@id="hospital-list"]/li/div[1][@data-type="2"]/@data-id').extract()

                pub_pre_id = pub_pre_id[-1] if pub_pre_id else '0'
                pri_pre_id = pri_pre_id[-1] if pri_pre_id else '0'

                next_page_url = self.hospital_next_url.format(pub_pre_id, pri_pre_id)
                yield Request(next_page_url,
                              headers=self.headers,
                              callback=self.parse_next_hospital_info,
                              meta={
                                  'province_name': province_name
                              })
        except Exception as e:
            self.logger.error('在抓取医院信息的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_info(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取[{}]医院详细信息>>>>>>'.format(hospital_name))
        try:
            hospital_id = response.meta.get('hospital_id')
            data_type = response.meta.get('data_type')
            hospital_pro = response.meta.get('province_name')
            if data_type == '1':
                hospital_address = response.xpath('///div[@class="search-result-hospital-text"]/'
                                                  'p[4]/text()').extract_first('')
                hospital_phone = response.xpath('//div[@class="search-result-hospital-text"]/'
                                                'p[3]/text()').extract_first('')
                check_phone = re.search('(\d{6,})', hospital_phone)
                if not check_phone and not hospital_address:
                    hospital_address = hospital_phone
                    hospital_phone = ''
                # hospital_city = get_city('', hospital_address)
                # hospital_county = get_county2('', match_special2(hospital_address))
                df = transform([hospital_address])
                # hospital_pro = df.head()['省'][0]
                hospital_city = df.head()['市'][0]
                hospital_county = df.head()['区'][0]
                if hospital_pro in MUNICIPALITY2:
                    hospital_city = '{0}{1}'.format(hospital_pro, '市')
                    hospital_pro = ''
                else:
                    hospital_pro = '{0}{1}'.format(hospital_pro, '省')
                loader = CommonLoader2(item=HospitalInfoItem(), response=response)
                loader.add_xpath('hospital_name',
                                 '//span[@class="search-result-hospital-name"]/text()',
                                 MapCompose(custom_remove_tags))
                loader.add_xpath('hospital_level',
                                 '//div[@class="search-result-hospital-text"]/p[2]/text()',
                                 MapCompose(custom_remove_tags, clean_info2))
                loader.add_value('hospital_addr', hospital_address, MapCompose(custom_remove_tags))
                loader.add_value('hospital_pro', hospital_pro)
                loader.add_value('hospital_city', hospital_city)
                loader.add_value('hospital_county', hospital_county, MapCompose(custom_remove_tags))
                loader.add_value('hospital_phone', hospital_phone, MapCompose(custom_remove_tags))
                loader.add_xpath('hospital_intro',
                                 '//li[@id="info"]/p',
                                 MapCompose(remove_tags, custom_remove_tags))
                loader.add_value('registered_channel', self.data_source_from)
                loader.add_value('dataSource_from', self.data_source_from)
                loader.add_value('crawled_url', response.url)
                loader.add_value('update_time', now_day())
                loader.add_xpath('hospital_route',
                                 '//div[@class="search-result-hospital-text"]/p[5]/text()',
                                 MapCompose(custom_remove_tags, match_special2))
                loader.add_xpath('hospital_img_url', 'div[@class="search-result-hospital-img"]/img/@src')
                loader.add_value('hospital_tags', '1')
                loader.add_value('gmt_created', now_time())
                loader.add_value('gmt_modified', now_time())
                loader.add_value('hospital_id', hospital_id)
                hospital_item = loader.load_item()
                yield hospital_item

                # 获取科室信息
                # 从一级科室获取二级科室信息
                all_dept = response.xpath('//ul[@id="parent-list"]/li[@id]')
                for each_dept in all_dept:
                    each_dept_id = each_dept.xpath('@id').extract_first('')
                    each_dept_type = each_dept.xpath('div/span/text()').extract_first('')
                    self.headers['Referer'] = response.url
                    dept_link = self.dept_url.format(hospital_id, each_dept_id)
                    yield Request(dept_link,
                                  headers=self.headers,
                                  callback=self.parse_hospital_dep,
                                  meta={
                                      'hospital_name': hospital_name,
                                      'hospital_id': hospital_id,
                                      'dept_type': each_dept_type
                                  })

                # 获取医生信息
                self.headers['Referer'] = response.url
                doctor_info_link = self.doctor_url.format(hospital_id, '1')
                yield Request(doctor_info_link,
                              headers=self.headers,
                              callback=self.parse_doctor_info,
                              meta={
                                  'hospital_name': hospital_name,
                                  'hospital_id': hospital_id
                              })
            elif data_type == '2':
                hospital_address = response.xpath('//p[@class="hospital-private-address-line fc-6"]'
                                                  '[contains(text(),"地址")]/text()').extract_first('')
                # hospital_city = get_city('', hospital_address)
                # hospital_county = get_county2('', match_special2(hospital_address))
                df = transform([hospital_address])
                # hospital_pro = df.head()['省'][0]
                hospital_city = df.head()['市'][0]
                hospital_county = df.head()['区'][0]
                if hospital_pro in MUNICIPALITY2:
                    hospital_city = '{0}{1}'.format(hospital_pro, '市')
                    hospital_pro = ''
                else:
                    hospital_pro = '{0}{1}'.format(hospital_pro, '省')
                loader = CommonLoader2(item=HospitalInfoItem(), response=response)
                loader.add_xpath('hospital_name',
                                 '//p[@class="hospital-private-content-tit"]/text()',
                                 MapCompose(custom_remove_tags))
                loader.add_value('hospital_addr', hospital_address, MapCompose(custom_remove_tags, match_special2))
                loader.add_value('hospital_pro', hospital_pro)
                loader.add_value('hospital_city', hospital_city)
                loader.add_value('hospital_county', hospital_county, MapCompose(custom_remove_tags))
                loader.add_xpath('hospital_phone',
                                 '//div[@class="search-result-hospital-text"]/p[3]/text()',
                                 MapCompose(custom_remove_tags))
                loader.add_xpath('hospital_intro',
                                 '//li[@id="info"]/p',
                                 MapCompose(remove_tags, custom_remove_tags))
                loader.add_value('registered_channel', self.data_source_from)
                loader.add_value('dataSource_from', self.data_source_from)
                loader.add_value('crawled_url', response.url)
                loader.add_value('update_time', now_day())
                loader.add_xpath('hospital_route',
                                 '//li[@id="address"]/p[3]/text()',
                                 MapCompose(custom_remove_tags, match_special2))
                # loader.add_xpath('hospital_img_url', 'div[@class="search-result-hospital-img"]/img/@src')
                loader.add_value('hospital_tags', '2')
                loader.add_value('gmt_created', now_time())
                loader.add_value('gmt_modified', now_time())
                loader.add_value('hospital_id', hospital_id)
                hospital_item = loader.load_item()
                yield hospital_item

                # 获取科室信息
                # 从一级科室获取二级科室信息
                all_dept = response.xpath('//ul[@id="parent-list"]/li[position()>1]')
                for each_dept in all_dept:
                    dept_id = each_dept.xpath('div/@id').extract_first('')
                    dept_name = each_dept.xpath('div/span/text()').extract_first('')
                    dept_loader = CommonLoader2(item=HospitalDepItem(), response=response)
                    dept_loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
                    dept_loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
                    dept_loader.add_value('dataSource_from', self.data_source_from)
                    dept_loader.add_value('crawled_url', response.url)
                    dept_loader.add_value('update_time', now_day())
                    dept_loader.add_value('dept_id', dept_id.replace('subDepLi-', ''))
                    dept_loader.add_value('dept_url', response.url)
                    dept_loader.add_value('gmt_created', now_time())
                    dept_loader.add_value('gmt_modified', now_time())
                    dept_item = dept_loader.load_item()
                    yield dept_item

                    # 获取医生信息
                    self.headers['Referer'] = response.url
                    doctor_info_link = self.doctor_url.format(hospital_id, '1')
                    yield Request(doctor_info_link,
                                  headers=self.headers,
                                  callback=self.parse_doctor_info,
                                  meta={
                                      'hospital_name': hospital_name,
                                      'hospital_id': hospital_id,
                                      'dept_name': dept_name
                                  })
        except Exception as e:
            self.logger.error('在抓取医院详细信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_next_hospital_info(self, response):
        """翻页之后的医院信息"""
        self.logger.info('>>>>>>正在抓取医院信息2>>>>>>')
        try:
            province_name = response.meta.get('province_name')
            res_js = json.loads(response.text)
            all_hospital_info = res_js.get('data')
            total_pages = res_js.get('hospitalCount')
            if all_hospital_info:
                for each_hospital_info in all_hospital_info:
                    hospital_id = each_hospital_info.get('id')
                    hospital_type = each_hospital_info.get('hospitalType')
                    if hospital_type == 1:
                        self.pub_pre_id = hospital_id
                    else:
                        self.pri_pre_id = hospital_id
                    hospital_link = self.hospital_url.format(hospital_id)
                    yield Request(hospital_link,
                                  headers=self.headers,
                                  callback=self.parse_hospital_info,
                                  meta={
                                      'data_type': str(hospital_type),
                                      'hospital_id': hospital_id,
                                      'hospital_name': each_hospital_info.get('name'),
                                      'province_name': province_name
                                  })

            # 翻页
            has_next_cal = int(total_pages) - 10
            has_next = has_next_cal > 0 if total_pages else 0
            if has_next:
                next_page_url = self.hospital_next_url.format(self.pub_pre_id, self.pri_pre_id)
                yield Request(next_page_url,
                              headers=self.headers,
                              callback=self.parse_next_hospital_info,
                              meta={
                                  'province_name': province_name
                              })
        except Exception as e:
            self.logger.error('在抓取医院信息2过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_dep(self, response):
        hospital_name = response.meta.get('hospital_name')
        dept_type = response.meta.get('dept_type')
        self.logger.info('>>>>>>正在抓取:[{}]医院-[{}]科室信息>>>>>>'.format(hospital_name, dept_type))
        try:
            dept_info = json.loads(response.text)
            sub_dept_list = dept_info.get('data').get('subDepList')
            for each_dept_info in sub_dept_list:
                dept_name = each_dept_info.get('name')
                dept_id = each_dept_info.get('id')
                dept_loader = CommonLoader2(item=HospitalDepItem(), response=response)
                dept_loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
                dept_loader.add_value('dept_type', dept_type, MapCompose(custom_remove_tags))
                dept_loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
                dept_loader.add_value('dataSource_from', self.data_source_from)
                dept_loader.add_value('crawled_url', response.url)
                dept_loader.add_value('update_time', now_day())
                dept_loader.add_value('dept_id', dept_id)
                dept_loader.add_value('dept_url', response.url)
                dept_loader.add_value('gmt_created', now_time())
                dept_loader.add_value('gmt_modified', now_time())
                dept_item = dept_loader.load_item()
                yield dept_item
        except Exception as e:
            self.logger.error('在抓取医院科室信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取[{}]医院医生详细信息>>>>>>'.format(hospital_name))
        try:
            # 获取医生信息
            hospital_id = response.meta.get('hospital_id')
            doctor_info = json.loads(response.text)
            doctor_info_pages = doctor_info.get('data').get('pages')
            doctor_info_list = doctor_info.get('data').get('doctorPageList')
            current_page_num = re.search(r'&curr=(\d+)$', response.url)
            for each_doctor_info in doctor_info_list:
                portrait = each_doctor_info.get('portrait')
                doctor_photo_url = urljoin(self.doctor_image_host, portrait) if portrait else ''
                loader = CommonLoader2(item=DoctorInfoItem(), response=response)
                loader.add_value('doctor_name', each_doctor_info.get('name'), MapCompose(custom_remove_tags))
                loader.add_value('dept_name', each_doctor_info.get('departmentName'))
                loader.add_value('hospital_name', each_doctor_info.get('hospitalName'))
                loader.add_value('doctor_level', each_doctor_info.get('doctorTitleName'))
                loader.add_value('dataSource_from', self.data_source_from)
                loader.add_value('crawled_url', response.url)
                loader.add_value('update_time', now_day())
                loader.add_value('doctor_id', each_doctor_info.get('id'))
                loader.add_value('hospital_id', hospital_id)
                loader.add_value('doctor_photo_url', doctor_photo_url)
                loader.add_value('gmt_created', now_time())
                loader.add_value('gmt_modified', now_time())
                doctor_item = loader.load_item()
                yield doctor_item

            # 医生翻页
            if doctor_info_pages and current_page_num:
                current_page_num = int(current_page_num.group(1))
                total_pages = int(doctor_info_pages)
                next_page = current_page_num + 1
                if next_page <= total_pages:
                    next_doctor_url = self.doctor_url.format(str(hospital_id), str(next_page))
                    yield Request(next_doctor_url,
                                  headers=self.headers,
                                  callback=self.parse_doctor_info,
                                  meta={
                                      'hospital_name': hospital_name,
                                      'hospital_id': hospital_id
                                  })
        except Exception as e:
            self.logger.error('在抓取医生详细信息的过程中出错了,原因是：{}'.format(repr(e)))
