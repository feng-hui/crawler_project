# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, filter_info3, filter_info4
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem


class SlbjySpider(scrapy.Spider):
    """
    双流区妇幼保健院
    """
    name = 'slbjy'
    allowed_domains = ['slbjy.cn']
    start_urls = ['http://slbjy.cn/']

    hospital_intro_link = 'http://www.slbjy.cn/about_us.html'
    dept_link = 'http://www.slbjy.cn/department/i=64&comContentId=64.html'
    doctor_link = 'http://www.slbjy.cn/expert_list/pmcId=48.html'
    hospital_name = '双流区妇幼保健院'
    host = 'http://www.slbjy.cn'
    dept_crawled_cnt = 0
    doctor_crawled_cnt = 0
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '__cfduid=d8c9a1fd2b8b6306b8e2ffbb4ccb708131531814176;'
                  'GUID=bf9f800b-58c2-4bdb-a3ed-852864a9cbf6;'
                  'yjs_id=783292eb06f48f0e78d0526179d2e69d;'
                  'BROWSEID=c7d95f37-6c7b-4824-bb6a-740409320163;'
                  'existFlag=1; rd=http%3A//www.slbjy.cn/;vct=9;ctrl_time=1;'
                  'JSESSIONID=AA68A50F5649C439B3B28C52A2771861.DLOG4J;'
                  'cf_clearance=66e65362cdbfac0d26f43364b4fa3de1d428e183-1533008001-1800;'
                  'zjll_productids=405&393&392&388&384&381&444&515&442&511&503&487&390&504&387&;pvc=98',
        'Host': 'www.slbjy.cn',
        'Referer': 'http://www.slbjy.cn/index.html',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        'DOWNLOAD_DELAY': 1,
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
        loader.add_value('consulting_hour', '上午8：00—12:00;下午2:00—5:30')
        loader.add_value('hospital_level', '三级乙等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '妇幼保健院')
        loader.add_value('hospital_addr', '四川省成都市双流区东升街道涧槽中街396号')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '')
        loader.add_value('hospital_phone', '母婴咨询热线_028-85884888(工作日);'
                                           '总值班电话_028-85808438;'
                                           '预约挂号电话_028-85801029(7:30-19:30)')
        loader.add_xpath('hospital_intro',
                         '//div[@class="describe htmledit"]',
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('is_medicare', '是')
        # loader.add_value('medicare_type', '')
        loader.add_value('registered_channel', '电话预约;自助挂号机;诊室预约;'
                                               '医院微信公众号;健康双流;现场')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

    # def parse_hospital_dep(self, response):
    #     self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))

    def parse_hospital_dep_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:科室详细信息>>>>>>'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_xpath('dept_type',
                         '//div[@class="title"]/h3/text()',
                         MapCompose(custom_remove_tags))
        loader.add_xpath('dept_name',
                         '//div[@class="title"]/h3/text()',
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
        dept_links = response.xpath('//ul[@class="list2"]/li[position()>1]/a/@href').extract()
        self.dept_crawled_cnt += 1

        if dept_links and self.dept_crawled_cnt == 1:
            for each_dept_link in dept_links:
                dept_request = Request(urljoin(self.host, each_dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep_detail,
                                       dont_filter=True)
                dept_request.meta['Referer'] = response.url
                yield dept_request

    def parse_doctor_info(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//li[@class="content column-num3"]')
        for each_doctor_link in doctor_links:
            doctor_level = dept_name = each_doctor_link.xpath('div[2]/ul/li[2]/text()').extract()
            doctor_link = each_doctor_link.xpath('div[1]/div/a/@href').extract_first('')
            loader = CommonLoader2(item=DoctorInfoItem(), selector=each_doctor_link)
            loader.add_xpath('doctor_name',
                             'div[1]/div/a/@title',
                             MapCompose(custom_remove_tags))
            loader.add_value('hospital_name', self.hospital_name)
            if doctor_link:
                doctor_detail_request = Request(urljoin(self.host, doctor_link),
                                                headers=self.headers,
                                                callback=self.parse_doctor_info_detail,
                                                dont_filter=True,
                                                meta={'loader': loader,
                                                      'dept_name': dept_name,
                                                      'doctor_level': doctor_level})
                self.headers['Referer'] = response.url
                yield doctor_detail_request

        # 医生信息下一页
        dept_id = re.search(r'.*pmcId=(.*?).html$', response.url)
        dept_id_2 = re.search(r'.*pmcId=(.*?)&pageNo_FrontProducts.*', response.url)
        # 获取科室id
        if dept_id_2:
            dept_id = dept_id_2.group(1)
        elif dept_id:
            dept_id = dept_id.group(1)
        else:
            dept_id = ''

        # 获取页码
        page_no = response.xpath('//a[contains(text(),"下一页")]/@onclick').extract_first('')
        if page_no:
            page_no = re.search(r'\((.*?)\)', page_no)
            if page_no:
                page_no = page_no.group(1).split(',')[0]
                next_page = 'http://www.slbjy.cn/expert_list/pmcId={}&pageNo_FrontProducts_list01-1482202374862={}' \
                            '&pageSize_FrontProducts_list01-1482202374862=12.html'
                next_page_link = next_page.format(dept_id, page_no)
                next_request = Request(next_page_link,
                                       headers=self.headers,
                                       callback=self.parse_doctor_info)
                self.headers['Referer'] = response.url
                yield next_request

        # 其他科室医生信息
        self.logger.info('>>>>>>正在抓取{}:科室信息>>>>>>'.format(self.hospital_name))
        doctor_links = response.xpath('//div[@class="menu-first"]/ul/li[position()>1]/a/@href').extract()
        self.doctor_crawled_cnt += 1
        if doctor_links and self.doctor_crawled_cnt == 1:
            for each_doctor_link in doctor_links:
                doctor_request = Request(urljoin(self.host, each_doctor_link),
                                         headers=self.headers,
                                         callback=self.parse_doctor_info,
                                         dont_filter=True)
                self.headers['Referer'] = response.url
                yield doctor_request

    def parse_doctor_info_detail(self, response):
        self.logger.info('>>>>>>正在抓取{}:医生详细信息>>>>>>'.format(self.hospital_name))
        loader = response.meta['loader']
        dept_name1 = custom_remove_tags(''.join(response.meta['dept_name']))
        doctor_level2 = response.xpath('//div[@class="FrontProducts_detail02-'
                                       '1482202997396_htmlbreak"]/p[1]/strong/text()').extract_first('')
        doctor_level1 = response.meta['doctor_level']
        dept_name2 = response.xpath('//div[@id="FrontPublic_breadCrumb01-1482202386120"]/div/'
                                    'a[last()]/text()').extract_first('').replace('专家', '').replace('类', '科')
        dept_name = re.sub(r'中医医师|中西医医师', '中医科', dept_name1) if dept_name1 else dept_name2
        doctor_level = custom_remove_tags(''.join(doctor_level1)) if doctor_level1 else doctor_level2
        doctor_intro = response.xpath('//div[@class="FrontProducts_detail02-'
                                      '1482202997396_htmlbreak"]/p[2]').extract_first('')
        loader.add_value('dept_name',
                         dept_name,
                         MapCompose(custom_remove_tags, filter_info3))
        loader.add_value('doctor_level',
                         doctor_level,
                         MapCompose(filter_info4, custom_remove_tags)
                         )
        loader.add_value('doctor_intro',
                         doctor_intro,
                         MapCompose(remove_tags, custom_remove_tags))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item

    # def parse_doctor_reg_info(self, response):
    #     self.logger.info('>>>>>>正在抓取{}:医生排班信息>>>>>>'.format(self.hospital_name))
