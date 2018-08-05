# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy import signals
from scrapy.http import Request
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, get_county
from medicalmap.items import CommonLoader2, HospitalInfoTestItem, HospitalDepItem, HospitalAliasItem


class AHospitalSpider(scrapy.Spider):
    name = 'a_hospital'
    allowed_domains = ['a-hospital.com']
    start_urls = ['http://www.a-hospital.com/w/%E5%85%A8%E5%9B%BD%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8']
    entry_url = 'http://www.a-hospital.com/w/%E9%A6%96%E9%A1%B5'
    host = 'http://www.a-hospital.com'
    test_url = 'http://www.a-hospital.com/w/%E4%B8%AD%E6%97%A5%E5%8F%8B%E5%A5%BD%E5%8C%BB%E9%99%A2'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.a-hospital.com',
        'Referer': 'http://www.a-hospital.com/w/%E9%A6%96%E9%A1%B5',
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
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 32
    }
    total_area_cnt = 0
    total_hospital_cnt = 0

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse, dont_filter=True)

        # 测试页面
        # self.headers['Referer'] = 'http://www.a-hospital.com/w/%E5%8C%97%E4%BA%AC%E5%B8%' \
        #                           '82%E6%9C%9D%E9%98%B3%E5%8C%BA%E5%8C%BB%E9%99%A2%E5%88%97%E8%A1%A8'
        # yield Request(self.test_url, headers=self.headers, callback=self.parse_hospital_detail, dont_filter=True)

    def parse(self, response):
        """
        获取所有国内所有地区的链接
        """
        self.logger.info('>>>>>>正在抓取全国医院列表……>>>>>>')
        try:
            # all_areas_list = response.xpath('//p/b/a[contains(text(),"医院列表")]/'
            #                                 'following::p[1]/a[not(contains(@href,"index"))]/@href').extract()
            special_areas_list = response.xpath('//p/b/a[contains(text(), "安徽省医院列表")]/'
                                                'following::p[1]/a[not(contains(@href,"index"))]')
            total_area_num = len(special_areas_list)
            self.logger.info('>>>>>>全国医院列表页面,总共有{}个地区待抓取……>>>>>>'.format(str(total_area_num)))
            self.total_area_cnt += total_area_num
            for each_area in special_areas_list:
                area_city = each_area.xpath('text()').extract_first('')
                area_link = each_area.xpath('@href').extract_first('')
                # print(hospital_city, hospital_link)
                self.headers['Referer'] = response.url
                yield Request(urljoin(self.host, area_link),
                              headers=self.headers,
                              callback=self.parse_area,
                              meta={'area_city': area_city},
                              dont_filter=True)
        except Exception as e:
            self.logger.error('抓取全国医院列表过程中出错了,错误的原因是:{}'.format(repr(e)))

    def parse_area(self, response):
        hospital_city = response.meta.get('area_city', '默认城市')
        self.logger.info('>>>>>>正在抓取[{}]医院列表……>>>>>>'.format(hospital_city))

        # 获取省市县等信息
        municipality = ['北京市', '上海市', '重庆市', '天津市']
        pro_or_city = response.xpath('//table[@class="nav"]/tr/'
                                     'td/a[3]/text()').extract_first('').replace('医院列表', '')
        if pro_or_city:
            if pro_or_city.strip() in municipality:
                # 直辖市,包括市、区等信息
                hos_prov = ''
                hos_city = pro_or_city
                hos_county = response.xpath('//h1[@id="firstHeading"]/text()').extract_first('').replace(hos_city, '')
            else:
                # 非直辖市,包括省、市、县或区等信息
                hos_prov = pro_or_city
                hos_city = response.xpath('//h1[@id="firstHeading"]'
                                          '/text()').extract_first('').replace('医院列表', '').replace(hos_prov, '')
                hos_county = ''
        else:
            hos_prov = hos_city = hos_county = None

        # 有医院最终页的医院
        # all_hospital_list = response.xpath('//div[@id="bodyContent"]/ul[3]/li/b/a/@href').extract()
        all_hospital_list2 = response.xpath('//h2/span[contains(text(),"医院列表")]/'
                                            'following::ul[1]/li/b/a[not(contains(@href,"index"))]')
        special_hospital_list = response.xpath('//h2/span[contains(text(),"医院列表")]/'
                                               'following::ul[1]/li/b/a[(contains(@href,"index"))]/ancestor::li[1]')
        area_hos_cnt = len(all_hospital_list2) + len(special_hospital_list)
        self.logger.info('>>>>>>[{}]总共有{}家医院……>>>>>>'.format(hospital_city, str(area_hos_cnt)))
        self.total_hospital_cnt += area_hos_cnt
        self.crawler.signals.connect(self.output_statistics, signals.spider_closed)
        try:
            # 有医院最终页的
            for each_hospital in all_hospital_list2:
                hospital_name = each_hospital.xpath('text()').extract_first('')
                hospital_link = each_hospital.xpath('@href').extract_first('')
                self.headers['Referer'] = response.url
                yield Request(urljoin(self.host, hospital_link),
                              headers=self.headers,
                              callback=self.parse_hospital_detail,
                              meta={'hospital_name': hospital_name},
                              dont_filter=True)
            # 没有医院最终页的
            for each_special_hospital in special_hospital_list:
                hospital_name = each_special_hospital.xpath('b/a/text()').extract_first('')
                hospital_url = each_special_hospital.xpath('b/a/@href').extract_first('')
                hos_county = hos_county if hos_county else get_county(hos_prov, hos_city, hospital_name)
                loader = CommonLoader2(item=HospitalInfoTestItem(), response=response)
                loader.add_xpath('hospital_name', hospital_name)
                loader.add_xpath('hospital_level',
                                 'ul[1]/li/b[contains(text(),"医院等级")]/ancestor::li[1]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_xpath('hospital_category',
                                 'ul[1]/li/b[contains(text(),"医院类型")]/ancestor::li[1]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_xpath('hospital_addr',
                                 'ul[1]/li/b[contains(text(),"医院地址")]/ancestor::li[1]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_value('hospital_pro', hos_prov, MapCompose(custom_remove_tags, match_special))
                loader.add_value('hospital_city', hos_city, MapCompose(custom_remove_tags, match_special))
                loader.add_value('hospital_county', hos_county, MapCompose(custom_remove_tags, match_special))
                loader.add_xpath('hospital_phone',
                                 'ul[1]/li/b[contains(text(),"联系电话")]/ancestor::li[1]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_value('hospital_intro', '')
                loader.add_xpath('hospital_postcode',
                                 'ul[1]/li/b[contains(text(),"邮政编码")]/ancestor::li[1]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_xpath('hospital_email',
                                 'ul[1]/li/b[contains(text(),"电子邮箱")]/ancestor::li[1]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_xpath('hospital_website',
                                 'ul[1]/li/b[contains(text(),"医院网站")]/ancestor::li[1]/'
                                 'a[not(contains(@href,"http://www.a-hospital.com"))]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_xpath('hospital_fax',
                                 'ul[1]/li/b[contains(text(),"传真号码")]/ancestor::li[1]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_xpath('operation_mode',
                                 'ul[1]/li/b[contains(text(),"经营方式")]/ancestor::li[1]',
                                 MapCompose(remove_tags, custom_remove_tags, match_special))
                loader.add_value('hospital_url', urljoin(self.host, hospital_url))
                loader.add_value('dataSource_from', '医学百科')
                loader.add_value('update_time', now_day())
                hospital_info_item = loader.load_item()
                yield hospital_info_item
        except Exception as e:
            self.logger.error('抓取[{}]医院列表的时候出错了,原因是:{}'.format(hospital_city, repr(e)))

    def parse_hospital_detail(self, response):
        hospital_name = response.meta.get('hospital_name', '默认医院')
        self.logger.info('>>>>>>正在抓取[{}]详细信息……>>>>>>'.format(hospital_name))

        # 获取省市县等信息
        municipality = ['北京市', '上海市', '重庆市', '天津市']
        pro_or_city = response.xpath('//table[@class="nav"]/tr/'
                                     'td/a[3]/text()').extract_first('').replace('医院列表', '')
        if pro_or_city:
            if pro_or_city.strip() in municipality:
                # 直辖市,包括市、区等信息
                hos_prov = ''
                hos_city = pro_or_city
                hos_county = response.xpath('//table[@class="nav"]/tr/'
                                            'td/a[4]/text()').extract_first('').replace(hos_city, '')
            else:
                # 非直辖市,包括省、市、县或区等信息
                hos_prov = pro_or_city
                hos_city = response.xpath('//table[@class="nav"]/tr/td/'
                                          'a[4]/text()').extract_first('').replace('医院列表', '').replace(hos_prov, '')
                hos_county = response.xpath('//table[@class="nav"]/tr/'
                                            'td/a[5]/text()').extract_first('').replace(hos_city, '')
        else:
            hos_prov = hos_city = hos_county = None

        # 获取医院概况
        hospital_intro = response.xpath('//h2/span[contains(text(),"概况")]/ancestor::h2[1]/following::p')
        i = 0
        for each_hi in hospital_intro:
            i += 1
            next_tag = each_hi.xpath('preceding::h2[1]/span[not(contains(text(),"概况"))]')
            if next_tag:
                i = i - 1
                hospital_intro = hospital_intro[:i].extract()
                break
        else:
            hospital_intro = hospital_intro.extract()

        # 医院信息item
        loader = CommonLoader2(item=HospitalInfoTestItem(), response=response)
        loader.add_xpath('hospital_name', '//table[@class="nav"]/tr/td/strong/text()')
        loader.add_xpath('hospital_level',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"医院等级")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_value('hospital_type', '')
        loader.add_xpath('hospital_category',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"医院类型")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_xpath('hospital_addr',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"医院地址")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_value('hospital_pro', hos_prov, MapCompose(custom_remove_tags, match_special))
        loader.add_value('hospital_city', hos_city, MapCompose(custom_remove_tags, match_special))
        loader.add_value('hospital_county', hos_county, MapCompose(custom_remove_tags, match_special))
        loader.add_xpath('hospital_phone',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"联系电话")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_value('hospital_intro', hospital_intro, MapCompose(remove_tags, custom_remove_tags))
        loader.add_xpath('hospital_postcode',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"邮政编码")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_xpath('hospital_email',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"电子邮箱")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_xpath('hospital_website',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"医院网站")]/ancestor::li[1]/'
                         'a[not(contains(@href,"http://www.a-hospital.com"))]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_xpath('hospital_fax',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"传真号码")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_xpath('operation_mode',
                         '//div[@id="bodyContent"]/ul[1]/li/'
                         'b[contains(text(),"经营方式")]/ancestor::li[1]',
                         MapCompose(remove_tags, custom_remove_tags, match_special))
        loader.add_value('hospital_url', response.url)
        loader.add_value('dataSource_from', '医学百科')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item

        # 科室信息
        dept_info = response.xpath('//div[@id="bodyContent"]/ul[1]/li/'
                                   'b[contains(text(),"重点科室")]/ancestor::li[1]')
        all_dept_info = match_special(dept_info.xpath('string(.)').extract_first(''))
        if all_dept_info:
            for each_dept in all_dept_info.split('、'):
                loader = CommonLoader2(item=HospitalDepItem(), response=response)
                loader.add_value('dept_name', each_dept, MapCompose(custom_remove_tags))
                loader.add_xpath('hospital_name',
                                 '//table[@class="nav"]/tr/td/strong/text()',
                                 MapCompose(custom_remove_tags))
                loader.add_value('update_time', now_day())
                dept_item = loader.load_item()
                yield dept_item

        # 医院别名信息
        hospital_name = response.xpath('//div[@id="bodyContent"]/p[1]/b/text()').extract_first('')
        hospital_name2 = response.xpath('//table[@class="nav"]/tr/td/strong/text()').extract_first('')
        if hospital_name and '（' in hospital_name:
            # alias_name = get_hospital_alias(hospital_name.replace(hospital_name2, ''))
            try:
                alias_name = re.search(r'^{}（(.*?)）$'.format(hospital_name2), hospital_name)
                if alias_name:
                    for each_alias_name in alias_name.group(1).split('、'):
                        alias_loader = CommonLoader2(item=HospitalAliasItem(), response=response)
                        alias_loader.add_xpath('hospital_name',
                                               '//table[@class="nav"]/tr/td/strong/text()',
                                               MapCompose(custom_remove_tags))
                        alias_loader.add_value('hospital_alias_name', each_alias_name)
                        alias_loader.add_value('update_time', now_day())
                        alias_item = alias_loader.load_item()
                        yield alias_item
            except Exception as e:
                self.logger.error('抓取[{}]别名的时候出错了,原因是:{}'.format(hospital_name, repr(e)))

    def output_statistics(self):
        """输出统计信息"""
        self.crawler.stats.set_value('total_area_cnt/count', self.total_area_cnt)
        self.crawler.stats.set_value('total_hospital_cnt/count', self.total_hospital_cnt)
