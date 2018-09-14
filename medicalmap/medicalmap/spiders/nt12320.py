# -*- coding: utf-8 -*-
import re
import scrapy
from re import S
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.http import Request, FormRequest
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, get_county2, match_special, match_special2, \
    clean_info, clean_info2, now_year


class Nt12320Spider(scrapy.Spider):
    name = 'nt12320'
    allowed_domains = ['nt12320.cn']
    start_urls = ['https://www.nt12320.cn/ntres/reservation/hos_search.do']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.nt12320.cn',
        'Referer': 'https://www.nt12320.cn/ntres/',
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
        'CONCURRENT_REQUESTS': 100
    }
    host = 'https://www.nt12320.cn'
    search_hos_url = 'https://www.nt12320.cn/ntres/reservation/hos_search.do'
    doctor_pagination_url = 'https://www.nt12320.cn/ntres/reservation/hos_showReservation.do?' \
                            'depid=&principalship=&docname=&depName=&hoscode={}&stdDepid=' \
                            '&parentStdDepid=&changeFlay=0&currentpage={}&currentWeekCount=1' \
                            '&disid=&bigCode=&allDoctors=0&startHour=&endHour=&schcode=' \
                            '&__multiselect_haveNum=&selectPage={}'
    data_source_from = '南通市预约挂号服务平台'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        try:
            all_hospital_links = response.xpath('//table[@class="tab"]/tbody/tr')
            for each_hospital_link in all_hospital_links:
                hospital_link = each_hospital_link.xpath('td[1]/b/a/@href').extract_first('')
                hospital_level = each_hospital_link.xpath('td[2]/p/span/text()').extract_first('')
                hospital_name = each_hospital_link.xpath('td[2]/h2/text()').extract_first('')
                all_doctor_links = each_hospital_link.xpath('td[3]/p/span/a'
                                                            '[contains(text(),"查看医生")]/@href').extract_first('')
                # 获取医院信息
                if hospital_link:
                    hospital_link = urljoin(self.host, hospital_link)
                    self.headers.update({
                        'Referer': response.url,
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'http://www.nt12320.cn'
                    })
                    yield Request(hospital_link,
                                  headers=self.headers,
                                  callback=self.parse_hospital_info,
                                  meta={'hospital_level': hospital_level},
                                  dont_filter=True)

                # 获取医生信息
                if all_doctor_links:
                    all_doctor_links = urljoin(self.host, all_doctor_links)
                    self.headers['Referer'] = response.url
                    yield Request(all_doctor_links,
                                  headers=self.headers,
                                  callback=self.parse_doctor_info,
                                  meta={'hospital_name': hospital_name},
                                  dont_filter=True)

            # 医院翻页
            next_page_number = response.xpath('//div[@id="fenye"]/'
                                              'a[contains(text(),"下一页")]/@href').extract_first('')
            now_page_number = response.xpath('//div[@id="fenye"]/a[@class="fenye_num_s"]/text()').extract_first('')
            if next_page_number and now_page_number:
                next_page_number = str(re.search(r'(\d+)', next_page_number).group(1))
                data = {
                    'currentpage': next_page_number,
                    'hoslevel': '',
                    'hosname': '',
                    'hostype': '',
                    'selectPage': now_page_number
                }
                self.headers['Referer'] = response.url
                yield FormRequest(self.search_hos_url,
                                  formdata=data,
                                  headers=self.headers,
                                  callback=self.parse,
                                  dont_filter=True)
        except Exception as e:
            self.logger.error('在抓取医院信息的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_info(self, response):
        self.logger.info('>>>>>>正在抓取:医院信息>>>>>>')

        try:
            # 获取区或县
            hospital_address = response.xpath('//div[@class="yy_js clearfix"]/div/dl/dd[1]/text()').extract_first('')
            if hospital_address:
                hospital_county = get_county2('中国|江苏省|江苏|南通市|南通', hospital_address)
            else:
                hospital_county = None

            # 获取医院信息
            loader = CommonLoader2(item=HospitalInfoItem(), response=response)
            loader.add_xpath('hospital_name', '//div[@class="yy_til"]/h2/text()', MapCompose(custom_remove_tags))
            loader.add_value('hospital_level',
                             response.meta.get('hospital_level'),
                             MapCompose(custom_remove_tags, clean_info))
            loader.add_xpath('hospital_addr',
                             '//div[@class="yy_js clearfix"]/div/dl/dd[1]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('hospital_pro', '江苏省')
            loader.add_value('hospital_city', '南通市')
            loader.add_value('hospital_county', hospital_county)
            loader.add_xpath('hospital_phone',
                             '//div[@class="yy_js clearfix"]/div/dl/dd[2]/text()',
                             MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_intro',
                             '//em[contains(text(),"简介")]/ancestor::div[1]',
                             MapCompose(remove_tags, custom_remove_tags, match_special, clean_info2))
            loader.add_value('registered_channel', self.data_source_from)
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('hospital_url', response.url)
            loader.add_value('update_time', now_day())
            hospital_info_item = loader.load_item()
            yield hospital_info_item

            # 获取科室信息
            # self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>')
            all_dept_links = response.xpath('//dl[@class="kfyy clearfix"]/dd/span/a/@href').extract()
            for each_dept_link in all_dept_links:
                dept_link = urljoin(self.host, re.sub(r';jsessionid=(.*?)\?', '?', each_dept_link))
                self.headers['Referer'] = response.url
                yield Request(dept_link, headers=self.headers, callback=self.parse_hospital_dep_detail)
        except Exception as e:
            self.logger.error('在抓取医院详细信息和科室的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取科室详细信息>>>>>>')
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_xpath('dept_name',
                         '//div[@class="zrys"]/p/strong/text()',
                         MapCompose(custom_remove_tags))
        loader.add_xpath('hospital_name', '//div[@class="yy_til"]/h2/text()', MapCompose(custom_remove_tags))
        loader.add_xpath('dept_info', '//div[@class="zrys"]/dl/dd', MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('dataSource_from', self.data_source_from)
        loader.add_value('crawled_url', response.url)
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取医生信息>>>>>>')
        try:
            all_doctors = response.xpath('//table[@class="tab"]/tbody/tr[position() mod 2!=0]')
            # hospital_name = response.xpath('//p[@class="search_num"]/strong/text()').extract_first('')
            for each_doctor in all_doctors:
                doctor_name = each_doctor.xpath('td[2]/a/text()').extract_first('')
                doctor_level = each_doctor.xpath('td[2]/i/text()').extract_first('')
                dept_name = each_doctor.xpath('td[2]/em/a/text()').extract_first('')
                doctor_link = each_doctor.xpath('td[2]/a/@href').extract_first('')
                hospital_name = each_doctor.xpath('td[2]/p/a/text()').extract_first('')
                if doctor_link:
                    doctor_link = urljoin(self.host, re.sub(r';jsessionid=(.*?)\?', '?', doctor_link))
                    # doctor_link2 = '{0}{1}'.format(doctor_link, '&currentWeekCount=2')
                    self.headers['Referer'] = response.url
                    yield Request(doctor_link,
                                  headers=self.headers,
                                  callback=self.parse_doctor_info_detail,
                                  meta={
                                      'doctor_name': doctor_name,
                                      'doctor_level': doctor_level,
                                      'dept_name': dept_name,
                                      'hospital_name': hospital_name
                                  },
                                  dont_filter=True)
            # 医生翻页
            hos_code = re.search(r'hoscode=(.*?)&', response.url) or re.search(r'hoscode=(.*?)$', response.url)
            next_page_number = response.xpath('//div[@id="fenye"]/a[contains(text(),"下一页")]/@href').extract_first('')
            now_page_number = response.xpath('//div[@id="fenye"]/a[@class="fenye_num_s"]/text()').extract_first('')
            if not now_page_number:
                now_page_number = '1'
            if hos_code and next_page_number:
                hos_code = str(hos_code.group(1))
                next_page_number = str(re.search(r'(\d+)', next_page_number).group(1))
                next_page_link = self.doctor_pagination_url.format(hos_code, next_page_number, now_page_number)
                self.headers['Referer'] = response.url
                yield Request(next_page_link, headers=self.headers, callback=self.parse_doctor_info, dont_filter=True)
        except Exception as e:
            self.logger.error('在抓取医生信息的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取医生详细信息>>>>>>')
        try:
            doctor_name = response.meta.get('doctor_name')
            dept_name = response.meta.get('dept_name')
            # dept_name = dept_name.split('-')[-1] if '-' in dept_name else dept_name
            doctor_level = response.meta.get('doctor_level')
            hospital_name = response.meta.get('hospital_name')
            # hospital_name2 = response.xpath('//div[@class="yy_til"]/h2/text()').extract_first('')
            # hospital_name = hospital_name2 if hospital_name2 else hospital_name1
            diagnosis_amt = response.xpath('//td/span[@class="doc_yuyue_time"]/a/@title').extract()
            if diagnosis_amt:
                res = re.search(r'.*挂号费：(.*?)$', diagnosis_amt[0], S)
                if res:
                    diagnosis_amt = res.group(1)
                else:
                    diagnosis_amt = None
            else:
                diagnosis_amt = None
            loader = CommonLoader2(item=DoctorInfoItem(), response=response)
            loader.add_value('doctor_name', doctor_name, MapCompose(custom_remove_tags))
            loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
            loader.add_value('hospital_name', hospital_name, MapCompose(custom_remove_tags))
            loader.add_value('doctor_level', doctor_level, MapCompose(custom_remove_tags, match_special2))
            loader.add_xpath('doctor_intro',
                             '//div[@class="zrys"]/dl/dd',
                             MapCompose(remove_tags, custom_remove_tags, clean_info2))
            loader.add_value('diagnosis_amt', diagnosis_amt)
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('crawled_url', response.url)
            loader.add_value('update_time', now_day())
            doctor_item = loader.load_item()
            yield doctor_item

            # 获取医生排班信息
            has_reg_info = response.xpath('//td/span[@class="doc_yuyue_time"]').extract()
            if has_reg_info:
                for each_reg_info in has_reg_info:
                    reg_info_date = re.search(r'.*出诊时间：(.*?)\n', each_reg_info, S)
                    reg_info_date = reg_info_date.group(1) if reg_info_date else None
                    reg_info = '{0}-{1}'.format(now_year(), reg_info_date).replace('月', '-').replace('日', '')
                    reg_loader = CommonLoader2(item=DoctorRegInfoItem(), response=response)
                    reg_loader.add_value('doctor_name', doctor_name, MapCompose(custom_remove_tags))
                    reg_loader.add_value('dept_name', dept_name, MapCompose(custom_remove_tags))
                    reg_loader.add_xpath('hospital_name',
                                         '//div[@class="yy_til"]/h2/text()',
                                         MapCompose(custom_remove_tags))
                    reg_loader.add_value('reg_info', reg_info, MapCompose(custom_remove_tags))
                    reg_loader.add_value('dataSource_from', self.data_source_from)
                    reg_loader.add_value('crawled_url', response.url)
                    reg_loader.add_value('update_time', now_day())
                    reg_item = reg_loader.load_item()
                    yield reg_item
        except Exception as e:
            self.logger.error('在抓取医生详细信息的过程中出错了,原因是：{}'.format(repr(e)))
