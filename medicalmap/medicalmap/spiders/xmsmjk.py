# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, get_county2, match_special2, now_year, now_time


class XmsmjkSpider(scrapy.Spider):
    name = 'xmsmjk'
    allowed_domains = ['xmsmjk.com']
    start_urls = [
        'http://www.xmsmjk.com/urponline',
        # 'http://www.xmsmjk.com/UrpOnline/Home/Community/'
    ]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.xmsmjk.com',
        'Referer': 'http://www.xmsmjk.com/',
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
    host = 'http://www.xmsmjk.com'
    hospital_url = 'http://www.xmsmjk.com/UrpOnline/Home/Hospital/{}'
    entry_url = ''
    data_source_from = '厦门市门诊预约统一平台'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        try:
            # all_hospital_links = response.xpath('//div[@id="scontent1"]/ul/li')
            all_hospital_links = response.xpath('//span[contains(text(),"社区列表")]/following::div[1]/ul/li|'
                                                '//span[contains(text(),"医院列表")]/following::div[1]/ul/li'
                                                )
            for each_hospital_link in all_hospital_links:
                hospital_link = each_hospital_link.xpath('a/@href').extract_first('')
                hospital_name = each_hospital_link.xpath('a/text()').extract_first('')

                # 获取医院信息
                if hospital_link:
                    hospital_link = urljoin(self.host, hospital_link).replace('_____1', '')
                    hospital_id = re.search(r'(\d+)', hospital_link)
                    if hospital_id:
                        hospital_id = hospital_id.group(1)
                        hospital_link = self.hospital_url.format(hospital_id)
                        self.headers['Referer'] = response.url
                        yield Request(hospital_link,
                                      headers=self.headers,
                                      callback=self.parse_hospital_info,
                                      dont_filter=True,
                                      meta={
                                          'hospital_name': hospital_name,
                                          'hospital_id': hospital_id
                                      })
        except Exception as e:
            self.logger.error('在抓取医院信息的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_info(self, response):
        hospital_name = response.meta.get('hospital_name')
        self.logger.info('>>>>>>正在抓取医院详细信息>>>>>>')
        try:
            hospital_id = response.meta.get('hospital_id')
            hospital_img_url = response.xpath('//div[@class="divLeft_Img"]/img/@src').extract_first('')
            hospital_img_url = urljoin(self.host, hospital_img_url) if hospital_img_url else ''
            hospital_address = response.xpath('//li[contains(text(),"地址")]/text()').extract_first('')
            hospital_county = get_county2('中国|福建省|福建|厦门市|厦门', match_special2(hospital_address))
            loader = CommonLoader2(item=HospitalInfoItem(), response=response)
            loader.add_xpath('hospital_name',
                             '//div[@class="divLeft_Info"]/ul/li[1]/span/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('hospital_addr', hospital_address, MapCompose(custom_remove_tags, match_special2))
            loader.add_value('hospital_pro', '福建省')
            loader.add_value('hospital_city', '厦门市')
            loader.add_value('hospital_county', hospital_county, MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_phone',
                             '//li[contains(text(),"电话")]/text()',
                             MapCompose(custom_remove_tags, match_special2))
            loader.add_xpath('hospital_intro',
                             '//div[@class="introduceSpan"]',
                             MapCompose(remove_tags, custom_remove_tags))
            loader.add_value('registered_channel', self.data_source_from)
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('crawled_url', response.url)
            loader.add_value('update_time', now_day())
            loader.add_xpath('hospital_official_website',
                             '//li[contains(text(),"官网")]/text()',
                             MapCompose(custom_remove_tags, match_special2))
            loader.add_xpath('hospital_route',
                             '//li[contains(text(),"公交线路")]/text()',
                             MapCompose(custom_remove_tags, match_special2))
            loader.add_value('hospital_img_url', hospital_img_url)
            loader.add_value('gmt_created', now_time())
            loader.add_value('gmt_modified', now_time())
            loader.add_value('hospital_id', hospital_id)
            hospital_item = loader.load_item()
            yield hospital_item

            # 科室信息
            all_dept_info = response.xpath('//div[@class="medicineOne"]|//div[@class="medicineTwo"]')
            for each_dept_info in all_dept_info:
                dept_type = each_dept_info.xpath('div[1]/span/text()').extract_first('')
                dept_names = each_dept_info.xpath('div[2]/div[1]')
                for each_dept_name in dept_names:
                    dept_name = each_dept_name.xpath('a/text()').extract_first('')
                    dept_link = each_dept_name.xpath('a/@href').extract_first('')
                    doctor_num_of_dept = each_dept_name.xpath('span/text()').extract_first('')

                    # 获取科室人数
                    if doctor_num_of_dept:
                        dept_person_num = re.search(r'(\d+)', doctor_num_of_dept)
                        dept_person_num = int(dept_person_num.group(1)) if dept_person_num else None
                    else:
                        dept_person_num = None

                    # 获取科室详细信息
                    dept_loader = CommonLoader2(item=HospitalDepItem(), response=response)
                    dept_loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
                    dept_loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
                    dept_loader.add_value('dept_type', dept_type, MapCompose(custom_remove_tags))
                    dept_loader.add_value('dataSource_from', self.data_source_from)
                    dept_info = ''.join(response.xpath('//p[contains(text(),"科室简介")]/ancestor::tr[1]').extract())
                    dept_loader.add_value('dept_info',
                                          dept_info,
                                          MapCompose(remove_tags, custom_remove_tags, match_special2))
                    dept_loader.add_value('crawled_url', response.url)
                    dept_loader.add_value('update_time', now_day())
                    dept_loader.add_value('dept_id', dept_link, MapCompose(match_special2))
                    dept_loader.add_value('hospital_id', hospital_id)
                    dept_loader.add_value('dept_person_num', dept_person_num)
                    dept_loader.add_value('dept_url', urljoin(self.host, dept_link))
                    dept_loader.add_value('gmt_created', now_time())
                    dept_loader.add_value('gmt_modified', now_time())
                    dept_item = dept_loader.load_item()
                    yield dept_item

                    # 获取医生信息
                    if dept_link and dept_person_num:
                        self.headers['Referer'] = response.url
                        yield Request(urljoin(self.host, dept_link),
                                      headers=self.headers,
                                      callback=self.parse_doctor_info,
                                      dont_filter=True,
                                      meta={
                                          'hospital_name': hospital_name,
                                          'dept_name': dept_name,
                                      })
        except Exception as e:
            self.logger.error('在抓取医院详细信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info(self, response):
        hospital_name = response.meta.get('hospital_name')
        dept_name = response.meta.get('dept_name')
        self.logger.info('>>>>>>正在抓取:[{}]医院-[{}]科室医生信息>>>>>>'.format(hospital_name, dept_name))
        try:
            all_doctor_links = response.xpath('//span[@class="doctornamespan"]/a')
            for each_doctor_link in all_doctor_links:
                doctor_link = each_doctor_link.xpath('@href').extract_first('')
                doctor_name = each_doctor_link.xpath('text()').extract_first('')
                self.headers['Referer'] = response.url
                yield Request(urljoin(self.host, doctor_link),
                              headers=self.headers,
                              callback=self.parse_doctor_info_detail,
                              meta={
                                  'dept_name': dept_name,
                                  'hospital_name': hospital_name,
                                  'doctor_name': doctor_name
                              },
                              dont_filter=True)

            # 医生翻页
            next_page = response.xpath('//a[@class="list_paging_btn"][contains(text(),"下一页")]'
                                       '/@href').extract_first('')
            if next_page:
                next_page_link = urljoin(self.host, next_page)
                self.headers['Referer'] = response.url
                yield Request(next_page_link,
                              headers=self.headers,
                              callback=self.parse_doctor_info,
                              meta={
                                  'dept_name': dept_name,
                                  'hospital_name': hospital_name,
                              })
        except Exception as e:
            self.logger.error('在抓取医生信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info_detail(self, response):
        hospital_name = response.meta.get('hospital_name')
        dept_name = response.meta.get('dept_name')
        doctor_name = response.meta.get('doctor_name')
        self.logger.info('>>>>>>正在抓取[{}]医院-[{}]医生详细信息>>>>>>'.format(hospital_name, doctor_name))
        try:
            # 获取医生信息
            doctor_photo_url = response.xpath('//div[@class="doctor_Img"]/img/@src').extract_first('')
            loader = CommonLoader2(item=DoctorInfoItem(), response=response)
            loader.add_value('doctor_name', doctor_name, MapCompose(custom_remove_tags))
            loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
            loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
            loader.add_xpath('sex',
                             '//span[@class="doctor_grade"]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('doctor_level',
                             '//span[@class="object_grade"]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('doctor_intro',
                             '//div[@class="doctor_Text_Major"]',
                             MapCompose(remove_tags, custom_remove_tags, match_special2))
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('crawled_url', response.url)
            loader.add_value('update_time', now_day())
            loader.add_value('doctor_id', response.url, MapCompose(match_special2))
            loader.add_xpath('dept_id',
                             '//div[@class="position_one"]/span/a[last()]/@href',
                             MapCompose(match_special2))
            loader.add_xpath('hospital_id',
                             '//div[@class="position_one"]/span/a[last()-1]/@href',
                             MapCompose(match_special2))
            loader.add_value('doctor_photo_url', urljoin(self.host, doctor_photo_url))
            loader.add_value('gmt_created', now_time())
            loader.add_value('gmt_modified', now_time())
            doctor_item = loader.load_item()
            yield doctor_item

            # 获取医生排班信息
            self.logger.info('>>>>>>正在抓取[{}]医生排班信息>>>>>>'.format(hospital_name))
            has_doctor_scheduling = response.xpath('//span[@class="yuyue"]/a[contains(text(),"预约")]')
            if has_doctor_scheduling:
                doctor_scheduling_list = response.xpath('//div[@class="whliesubscribe"]/ul/li[1]/div/'
                                                        'span/text()').extract()
                doctor_scheduling_length = len(doctor_scheduling_list)
                all_scheduling_date = response.xpath('//div[@class="datetable"]/ul/li[position()>1]/'
                                                     'span[1]/text()').extract()
                scheduling_date_list = custom_remove_tags(remove_tags(','.join(all_scheduling_date))).split(',')
                for i in range(1, doctor_scheduling_length + 1):
                    scheduling_info = response.xpath('//div[@class="whliesubscribe"]/ul/li[position()>1]'
                                                     '/div[{}]'.format(str(i)))
                    scheduling_time = doctor_scheduling_list[i - 1]
                    for index, each_s_i in enumerate(scheduling_info):
                        has_scheduling = each_s_i.xpath('span/a')
                        if has_scheduling:
                            each_scheduling_date = scheduling_date_list[index]
                            reg_info = '{0}-{1}{2}'.format(now_year(), each_scheduling_date, scheduling_time)
                            reg_loader = CommonLoader2(item=DoctorRegInfoItem(), response=response)
                            reg_loader.add_value('doctor_name', doctor_name, MapCompose(custom_remove_tags))
                            reg_loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
                            reg_loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
                            reg_loader.add_value('reg_info', reg_info)
                            reg_loader.add_value('dataSource_from', self.data_source_from)
                            reg_loader.add_value('crawled_url', response.url)
                            reg_loader.add_value('update_time', now_day())
                            reg_loader.add_value('doctor_id', response.url, MapCompose(match_special2))
                            reg_loader.add_xpath('dept_id',
                                                 '//div[@class="position_one"]/span/a[last()]/@href',
                                                 MapCompose(match_special2))
                            reg_loader.add_xpath('hospital_id',
                                                 '//div[@class="position_one"]/span/a[last()-1]/@href',
                                                 MapCompose(match_special2))
                            reg_loader.add_value('gmt_created', now_time())
                            reg_loader.add_value('gmt_modified', now_time())
                            reg_item = reg_loader.load_item()
                            yield reg_item
        except Exception as e:
            self.logger.error('在抓取医生详细信息的过程中出错了,原因是：{}'.format(repr(e)))
