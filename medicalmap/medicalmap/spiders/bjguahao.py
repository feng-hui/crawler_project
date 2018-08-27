# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags
from w3lib.html import remove_tags


class BjguahaoSpider(scrapy.Spider):
    name = 'bjguahao'
    allowed_domains = ['bjguahao.gov.cn']
    start_urls = ['http://www.bjguahao.gov.cn/hp.htm']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.bjguahao.gov.cn',
        'Referer': 'http://www.bjguahao.gov.cn/index.htm',
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
    host = 'http://www.bjguahao.gov.cn'
    data_source_from = '北京预约挂号统一平台'
    next_hospital_url = 'http://www.bjguahao.gov.cn/hp/{},0,0,0.htm?'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        all_hospital_links = response.xpath('//p[@class="yiyuan_co_titl"]/a/@href').extract()
        for each_hospital_link in all_hospital_links:
            self.headers['Referer'] = response.url
            yield Request(urljoin(self.host, each_hospital_link),
                          headers=self.headers,
                          callback=self.parse_hospital_info)

        # 翻页
        has_next = response.xpath('//a[@class="yiyuan_list_fer"]/@href').extract_first('')
        if has_next:
            next_info = re.search(r'(\d+)', has_next)
            if next_info:
                next_page_num = next_info.group(1)
                next_page_link = self.next_hospital_url.format(str(next_page_num))
                self.headers['Referer'] = response.url
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
                res = re.search(r'(.*等|.*级|.*合格|.*甲)(.*?)$', hospital_level)
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
            loader.add_xpath('hospital_name',
                             '//p[@class="yygh_box_top_p"]/strong/text()',
                             MapCompose(custom_remove_tags))
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

            # 获取医院介绍
            hospital_intro_link = response.xpath('//a[contains(text(),"医院介绍")]/@href').extract_first('')
            if hospital_intro_link:
                hospital_intro_link = urljoin(self.host, hospital_intro_link)
                self.headers['Referer'] = response.url
                yield Request(hospital_intro_link,
                              headers=self.headers,
                              callback=self.parse_hospital_detail_info,
                              meta={
                                  'loader': loader
                              })

            # 获取科室信息
            # all_dept_links = response.xpath('//div[@class="kfyuks_yyksbox"]')
            # for each_dept_link in all_dept_links:
            #     dept_type = each_dept_link.xpath('div[1]/text()').extract_first('')
            #     dept_info = each_dept_link.xpath('div[2]/div/ul/li/a/text()').extract()
            #     for each_dept_info in dept_info:
            #         dept_loader = CommonLoader2(item=HospitalDepItem(), response=response)
            #         dept_loader.add_value('dept_name', each_dept_info, MapCompose(custom_remove_tags))
            #         dept_loader.add_value('dept_type', dept_type, MapCompose(custom_remove_tags))
            #         dept_loader.add_xpath('hospital_name',
            #                               '//p[@class="yygh_box_top_p"]/strong/text()',
            #                               MapCompose(custom_remove_tags))
            #         dept_loader.add_value('dept_info', '')
            #         dept_loader.add_value('dataSource_from', self.data_source_from)
            #         dept_loader.add_value('update_time', now_day())
            #         dept_item = dept_loader.load_item()
            #         yield dept_item
        except Exception as e:
            self.logger.error('在抓取医院详细信息过程中出错了,原因是：{}'.format(repr(e)))

    def parse_hospital_detail_info(self, response):
        self.logger.info('>>>>>>正在抓取:医院详情>>>>>>')
        try:
            loader = response.meta.get('loader')
            hospital_intro = response.xpath('//div[@class="yiyuanjieshao_context"]').extract_first('')
            loader.add_value('hospital_intro', hospital_intro, MapCompose(remove_tags, custom_remove_tags))
            hospital_info_item = loader.load_item()
            yield hospital_info_item
        except Exception as e:
            self.logger.error('在抓取医院详情过程中出错了,原因是：{}'.format(repr(e)))
