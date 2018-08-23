# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, get_county2, match_special, timestamp


class GuahaoSpider(scrapy.Spider):
    name = 'guahao'
    allowed_domains = ['guahao.gov.cn']
    start_urls = ['http://www.guahao.gov.cn/hospitallist.xhtml']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.guahao.gov.cn',
        'Referer': 'http://www.guahao.gov.cn/index.xhtml',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 5,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 3,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 32.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 100
    }
    host = 'http://www.guahao.gov.cn'
    hospital_info_url = 'http://www.guahao.gov.cn/hospdetail.xhtml?HIS_CD={}&channel=JSON'
    next_hospital_url = 'http://www.guahao.gov.cn/hospitallist.xhtml?ARE_ID=&PAG_NO={}&PAG_CNT={}&' \
                        'TOT_REC_NUM={}&t={}'
    dept_url = 'http://www.guahao.gov.cn/deplist.xhtml?HIS_CD={}'
    dept_url2 = 'http://www.guahao.gov.cn/hospital_branch.xhtml?HIS_CD={}'
    doctor_list_url = 'http://www.guahao.gov.cn/doctorslist.xhtml?HIS_CD={}&DEP_ID={}'
    doctor_url = 'http://www.guahao.gov.cn/doc_detail.xhtml?HIS_CD={}&DEP_ID={}&DOC_ID={}'
    next_doctor_url = 'http://www.guahao.gov.cn/doctorslist.xhtml?PAG_NO={}&PAG_CNT={}' \
                      '&TOT_REC_NUM={}&HIS_CD={}&DEP_ID={}&t={}'
    data_source_from = '广州市统一预约挂号系统'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, dont_filter=True, callback=self.parse)

    def parse(self, response):
        all_hospital = response.xpath('//div[@class="bg_kk hospitalInfo"]')
        for each_hospital in all_hospital:
            # 获取医院信息
            hospital_id = each_hospital.xpath('@attr').extract_first('')
            hospital_type = each_hospital.xpath('@attr_histyp').extract_first('')
            hospital_name = each_hospital.xpath('p[@class="hisNm"]/text()').extract_first('')
            if hospital_id and hospital_type == '1':
                hospital_link = self.hospital_info_url.format(hospital_id)
                dept_link = self.dept_url.format(hospital_id)

                # 获取医院信息
                self.headers['Referer'] = dept_link
                yield Request(hospital_link,
                              headers=self.headers,
                              callback=self.parse_hospital_info,
                              dont_filter=True,
                              meta={'hospital_type': hospital_type})

                # 获取科室信息
                self.headers['Referer'] = response.url
                yield Request(dept_link,
                              headers=self.headers,
                              callback=self.parse_hospital_dep,
                              dont_filter=True,
                              meta={'hospital_name': hospital_name})
            # elif hospital_id and hospital_type == '0':
            #     hospital_link = self.hospital_info_url.format(hospital_id)
            #     dept_link = self.dept_url2.format(hospital_id)
            #
            #     # 获取医院信息
            #     self.headers['Referer'] = dept_link
            #     yield Request(hospital_link,
            #                   headers=self.headers,
            #                   callback=self.parse_hospital_info,
            #                   dont_filter=True,
            #                   meta={'hospital_type': hospital_type})
            else:
                pass

        # 翻页
        has_next = response.xpath('//a[@class="pb_next"]')
        if has_next:
            now_page = response.xpath('////input[@name="PAG_NO"]/@value').extract_first('')
            total_page = response.xpath('////input[@name="PAG_CNT"]/@value').extract_first('')
            total_doctor_num = response.xpath('//input[@name="TOT_REC_NUM"]/@value').extract_first('')
            if now_page and total_page and total_doctor_num:
                next_page_num = int(now_page) + 1
                total_page_num = int(total_page)
                if next_page_num <= total_page_num:
                    next_page_link = self.next_hospital_url.format(str(next_page_num),
                                                                   total_page,
                                                                   total_doctor_num,
                                                                   timestamp())
                    self.headers['Referer'] = response.url
                    yield Request(next_page_link,
                                  headers=self.headers,
                                  callback=self.parse,
                                  dont_filter=True)

    def parse_hospital_info(self, response):
        self.logger.info('>>>>>>正在抓取:医院详细信息>>>>>>')
        try:
            # 获取医院信息
            hospital_info = json.loads(response.text)
            # 获取医院等级
            hospital_level_info = hospital_info.get('HIS_LVL')
            if hospital_level_info == '3':
                hospital_level = '三级'
            elif hospital_level_info == '2':
                hospital_level = '二级'
            elif hospital_level_info == '1':
                hospital_level = '一级'
            else:
                hospital_level = None
            # 获取医院所在区或县
            hospital_address = hospital_info.get('HIS_AD')
            if hospital_address:
                hospital_county = get_county2('中国|广东省|广东|广州市|广州', hospital_address)
            else:
                hospital_county = None
            loader = CommonLoader2(item=HospitalInfoItem(), response=response)
            loader.add_value('hospital_name', hospital_info.get('HIS_NM'))
            loader.add_value('hospital_level', hospital_level)
            loader.add_value('hospital_category', '')
            loader.add_value('hospital_addr', hospital_address)
            loader.add_value('hospital_pro', '广东省')
            loader.add_value('hospital_city', '广州市')
            loader.add_value('hospital_county', hospital_county)
            loader.add_value('hospital_phone', hospital_info.get('TEL_NO'))
            loader.add_value('hospital_intro', hospital_info.get('HIS_RM'))
            loader.add_value('registered_channel', self.data_source_from)
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('hospital_url', response.url)
            loader.add_value('update_time', now_day())
            hospital_info_item = loader.load_item()
            yield hospital_info_item
        except Exception as e:
            self.logger.error('在抓取医院详细信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_dep(self, response):
        self.logger.info('>>>>>>正在抓取科室信息>>>>>>')
        try:
            hospital_name = response.meta.get('hospital_name')
            all_dept_links = response.xpath('//div[@class="deptList-block mb20 clearfix"]')
            for each_dept_link in all_dept_links:
                dept_type = each_dept_link.xpath('b/text()').extract_first('')
                dept_info = each_dept_link.xpath('ul/li/a')
                for each_dept_info in dept_info:
                    # 获取科室信息
                    dept_name = each_dept_info.xpath('@title').extract_first('')
                    dept_link = each_dept_info.xpath('@onclick').extract_first('')
                    dept_link2 = each_dept_info.xpath('@href').extract_first('')
                    dept_loader = CommonLoader2(item=HospitalDepItem(), response=response)
                    dept_loader.add_value('dept_name', dept_name)
                    dept_loader.add_value('dept_type', dept_type)
                    dept_loader.add_value('hospital_name', hospital_name)
                    dept_loader.add_value('dept_info', '')
                    dept_loader.add_value('dataSource_from', self.data_source_from)
                    dept_loader.add_value('update_time', now_day())
                    dept_item = dept_loader.load_item()
                    yield dept_item

                    # 获取医生信息
                    if dept_link:
                        res = re.search(r'goNext\((.*?),\'(.*)\'\);', dept_link)
                        if res:
                            hospital_id = res.group(1)
                            dept_id = res.group(2)
                            doctor_list_url = self.doctor_list_url.format(hospital_id, dept_id)
                        else:
                            doctor_list_url = None
                    else:
                        doctor_list_url = urljoin(self.host, dept_link2)
                    if doctor_list_url:
                        self.headers['Referer'] = response.url
                        yield Request(doctor_list_url,
                                      headers=self.headers,
                                      callback=self.parse_doctor_info,
                                      meta={
                                          'dept_name': dept_name,
                                          'hospital_name': hospital_name
                                      })

        except Exception as e:
            self.logger.error('在抓取科室信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取:医生信息>>>>>>')
        try:
            dept_name = response.meta.get('dept_name')
            hospital_name = response.meta.get('hospital_name')
            all_doctors = response.xpath('//div[@class="docInfo docInfo-w-h"]')
            for each_doctor_link in all_doctors:
                doctor_link = each_doctor_link.xpath('p[1]/a/@href').extract_first('')
                doctor_name = each_doctor_link.xpath('p[1]/a/text()').extract_first('')
                doctor_level = each_doctor_link.xpath('p[2]/text()').extract_first('')
                doctor_intro = each_doctor_link.xpath('p[contains(text(),"简介")]/text()').extract_first('')
                doctor_intro = match_special(doctor_intro)
                if doctor_intro:
                    if doctor_link:
                        doctor_link = urljoin(self.host, doctor_link)
                        self.headers['Referer'] = response.url
                        yield Request(doctor_link,
                                      headers=self.headers,
                                      callback=self.parse_doctor_info_detail,
                                      dont_filter=True,
                                      meta={
                                          'doctor_name': doctor_name,
                                          'doctor_level': doctor_level,
                                          'dept_name': dept_name,
                                          'hospital_name': hospital_name
                                      })
                else:
                    loader = CommonLoader2(item=DoctorInfoItem(), response=response)
                    loader.add_value('doctor_name', doctor_name)
                    loader.add_value('dept_name', dept_name)
                    loader.add_value('hospital_name', hospital_name)
                    loader.add_value('doctor_level', doctor_level)
                    # loader.add_value('doctor_intro', '')
                    # loader.add_xpath('doctor_goodAt', '')
                    # loader.add_value('diagnosis_amt', '')
                    loader.add_value('dataSource_from', self.data_source_from)
                    loader.add_value('crawled_url', response.url)
                    loader.add_value('update_time', now_day())
                    doctor_item = loader.load_item()
                    yield doctor_item

            # 分页
            has_next = response.xpath('//a[@class="pb_next"]')
            if has_next:
                hos_id = re.search(r'HIS_CD=(.*?)&', response.url)
                dept_id = re.search(r'DEP_ID=(.*?)$', response.url)
                if hos_id and dept_id:
                    hos_id = hos_id.group(1)
                    dept_id = dept_id.group(1)
                    now_page = response.xpath('//a[@class="pb_on"]/text()').extract_first('')
                    total_page = response.xpath('//a[contains(text(),"尾页")]/@pagval').extract_first('')
                    total_doctor_num = response.xpath('//input[@name="TOT_REC_NUM"]/@value').extract_first('')
                    if now_page and total_page and total_doctor_num:
                        next_page_num = int(now_page) + 1
                        total_page_num = int(total_page)
                        if next_page_num <= total_page_num:
                            next_page_link = self.next_doctor_url.format(str(next_page_num),
                                                                         total_page,
                                                                         total_doctor_num,
                                                                         hos_id,
                                                                         dept_id,
                                                                         timestamp())
                            self.headers['Referer'] = response.url
                            yield Request(next_page_link,
                                          headers=self.headers,
                                          callback=self.parse_doctor_info,
                                          dont_filter=True,
                                          meta={
                                              'dept_name': dept_name,
                                              'hospital_name': hospital_name
                                          })
        except Exception as e:
            self.logger.error('在抓取医生信息的过程中出错了,原因是：{}'.format(repr(e)))

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取:医生详细信息>>>>>>')
        try:
            doctor_name = response.meta.get('doctor_name')
            hospital_name = response.meta.get('hospital_name')
            doctor_level = response.meta.get('doctor_level')
            dept_name = response.meta.get('dept_name')
            loader = CommonLoader2(item=DoctorInfoItem(), response=response)
            loader.add_value('doctor_name', doctor_name)
            loader.add_value('dept_name', dept_name)
            loader.add_value('hospital_name', hospital_name)
            loader.add_value('doctor_level', doctor_level)
            loader.add_xpath('doctor_intro',
                             '//p[@id="docSpeciality"]/text()',
                             MapCompose(custom_remove_tags, match_special))
            # loader.add_value('doctor_goodAt', '')
            # loader.add_value('diagnosis_amt', '')
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('crawled_url', response.url)
            loader.add_value('update_time', now_day())
            doctor_item = loader.load_item()
            yield doctor_item
        except Exception as e:
            self.logger.error('在抓取医生详细信息的过程中出错了,原因是：{}'.format(repr(e)))
