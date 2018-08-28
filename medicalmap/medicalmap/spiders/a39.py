# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, HospitalAliasItem
from medicalmap.utils.common import now_day, custom_remove_tags, get_county2, match_special, timestamp


class A39Spider(scrapy.Spider):
    name = '39'
    allowed_domains = ['39.net']
    start_urls = [
        'http://yyk.39.net/beijing/hospitals/',
        # 'http://yyk.39.net/shanghai/hospitals/'
    ]
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'yyk.39.net',
        'Referer': 'http://www.39.net/',
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
    host = 'http://yyk.39.net/'
    hospital_url = 'http://yyk.39.net/hospital/'
    dept_postfix = '_labs.html'
    data_source_from = '39健康网'

    def parse(self, response):
        self.logger.info('>>>>>>正在抓取所有医院信息>>>>>>')
        all_hospitals = response.xpath('//div[@class="serach-left-list"]/ul/li')
        self.headers['Referer'] = response.url
        for each_hospital in all_hospitals:

            # 获取医院信息
            each_hospital_link = each_hospital.xpath('a/@href').extract_first('')
            if each_hospital_link:
                yield Request(urljoin(self.host, each_hospital_link),
                              headers=self.headers,
                              callback=self.parse_hospital_info)

            # 获取科室信息
            hospital_id = re.search(r'.*/(.*?).html$', each_hospital_link)
            if hospital_id:
                hospital_id = hospital_id.group(1)
                dept_detail_url = '{0}{1}'.format(hospital_id, self.dept_postfix)
                dept_link = urljoin(self.hospital_url, dept_detail_url)
                yield Request(urljoin(self.host, dept_link),
                              headers=self.headers,
                              callback=self.parse_hospital_info)

            # 获取医生信息
            doctors_link = each_hospital.xpath('div[@class="as"]/a[contains(text(),'
                                               '"推荐专家")]/@href').extract_first('')
            if doctors_link:
                yield Request(urljoin(self.host, each_hospital_link),
                              headers=self.headers,
                              callback=self.parse_hospital_info)

        # 翻页
        has_next = response.xpath('//div[@class="next"]/a[contains(text(),"下一页")]/@href').extract_first('')
        if has_next:
            next_page_link = urljoin(self.host, has_next)
            yield Request(next_page_link, headers=self.headers, callback=self.parse)

    def parse_hospital_info(self, response):
        self.logger.info('>>>>>>正在抓取:医院详细信息>>>>>>')
        try:
            # 获取医院信息

            # 获取医院等级与地区
            hospital_info = response.xpath('//p[@class="yygh_box_top_p2"]').extract()
            hospital_info2 = custom_remove_tags(remove_tags(''.join(hospital_info)))
            hospital_level = hospital_info2.split(':')[1].replace('区域', '')
            hospital_county = hospital_info2.split(':')[2].replace('分类', '')
            if hospital_level:
                res = re.search(r'(.*等|.*级|.*甲).*', hospital_level)
                if res:
                    h_l = res.group(1)
                    h_c = res.group(2)
                    if h_c:
                        h_c_2 = re.sub(r'合格|医院', '', h_c)
                        if h_c_2:
                            h_c = '{0}{1}'.format(h_c_2, '医院')
                else:
                    h_l = h_c = None
            else:
                h_l = h_c = None
            loader = CommonLoader2(item=HospitalInfoItem(), response=response)
            loader.add_xpath('hospital_name', '//div[@class="l"]/h2/text()', MapCompose(custom_remove_tags))
            loader.add_value('hospital_level', h_l, MapCompose(custom_remove_tags))
            loader.add_value('hospital_category', h_c)
            loader.add_xpath('hospital_addr',
                             '//span[@class="yygh_box_con_dl_span1"]/ancestor::dl[1]/dd[1]/p/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('hospital_pro', '')
            loader.add_value('hospital_city', '北京市')
            loader.add_value('hospital_county', hospital_county, MapCompose(custom_remove_tags))
            loader.add_xpath('hospital_phone',
                             '//span[@class="yygh_box_con_dl_span3"]/ancestor::dl[1]/dd[1]/p/text()',
                             MapCompose(custom_remove_tags))
            loader.add_value('registered_channel', self.data_source_from)
            loader.add_value('dataSource_from', self.data_source_from)
            loader.add_value('hospital_url', response.url)
            loader.add_value('update_time', now_day())

            # 获取医院别名
            hospital_alias = response.xpath('//div[@class="l"]/p/text()').extract_first('')
            if hospital_alias:
                h_s = custom_remove_tags(hospital_alias)
                if h_s:
                    all_hospital_alias = h_s.split('，')
                    for each_alias in all_hospital_alias:
                        alias_loader = CommonLoader2(item=HospitalAliasItem(), response=response)
                        alias_loader.add_xpath('hospital_name',
                                               '//div[@class="l"]/h2/text()',
                                               MapCompose(custom_remove_tags))
                        alias_loader.add_value('hospital_alias_name', each_alias, MapCompose(custom_remove_tags))
                        alias_loader.add_value('dataSource_from', self.data_source_from)
                        alias_loader.add_value('update_time', now_day())
                        alias_item = alias_loader.load_item()
                        yield alias_item

            # 获取科室信息
            all_dept_links = response.xpath('//div[@class="kfyuks_yyksbox"]')
            for each_dept_link in all_dept_links:
                dept_type = each_dept_link.xpath('div[1]/text()').extract_first('')
                dept_info = each_dept_link.xpath('div[2]/div/ul/li/a/text()').extract()
                for each_dept_info in dept_info:
                    dept_loader = CommonLoader2(item=HospitalDepItem(), response=response)
                    dept_loader.add_value('dept_name', each_dept_info, MapCompose(custom_remove_tags))
                    dept_loader.add_value('dept_type', dept_type, MapCompose(custom_remove_tags))
                    dept_loader.add_xpath('hospital_name',
                                          '//p[@class="yygh_box_top_p"]/strong/text()',
                                          MapCompose(custom_remove_tags))
                    dept_loader.add_value('dept_info', '')
                    dept_loader.add_value('dataSource_from', self.data_source_from)
                    dept_loader.add_value('update_time', now_day())
                    dept_item = dept_loader.load_item()
                    yield dept_item
        except Exception as e:
            self.logger.error('在抓取医院详细信息过程中出错了,原因是：{}'.format(repr(e)))
