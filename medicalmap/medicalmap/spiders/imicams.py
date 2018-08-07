# -*- coding: utf-8 -*-
import json
import random
import scrapy
from scrapy.http import FormRequest, Request
from medicalmap.items import CommonLoader2, ComprehensiveRankingItem, SubjectRankingItem, AreaRankingItem
from medicalmap.utils.common import now_day


class ImicamsSpider(scrapy.Spider):
    name = 'imicams'
    allowed_domains = ['imicams.ac.cn']
    start_urls = ['http://top100.imicams.ac.cn/home']
    host = 'http://top100.imicams.ac.cn'
    comprehensive_entry = 'http://top100.imicams.ac.cn/comprehensive'
    subject_entry = 'http://top100.imicams.ac.cn/subject'
    area_entry = 'http://top100.imicams.ac.cn/province'
    js_link = 'http://top100.imicams.ac.cn/assess_2017/public/ranking/rankingAction_search' \
              'RankByCode.action?d={}'.format(str(random.random))
    js_link2 = 'http://top100.imicams.ac.cn/assess_2017/public/ranking/rankingAction_compre' \
               'hensiveRankingByProvince.action?d={}'.format(str(random.random))
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01   ',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'top100.imicams.ac.cn',
        'Origin': 'http://top100.imicams.ac.cn',
        'Referer': 'http://top100.imicams.ac.cn/comprehensive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 1,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 100
    }

    def start_requests(self):
        # 综合排行
        # data = {
        #     'subject': '320',
        #     'year': '2017',
        #     'start': '1',
        #     'end': '100'
        # }
        # yield FormRequest(self.js_link,
        #                   headers=self.headers,
        #                   callback=self.parse,
        #                   dont_filter=True,
        #                   formdata=data)
        # 学科排行
        yield Request(self.subject_entry,
                      headers=self.headers,
                      callback=self.parse_subject)
        # 地区排行
        # yield Request(self.area_entry,
        #               headers=self.headers,
        #               callback=self.parse_area)

    def parse(self, response):
        """综合排行"""
        self.logger.info('>>>>>>正在抓取综合排行信息……>>>>>>')
        res = json.loads(response.text)
        for each_data in res.get('rows', []):
            loader = CommonLoader2(item=ComprehensiveRankingItem(), response=response)
            loader.add_value('hospital_pro', each_data.get('PROVINCE'))
            loader.add_value('ranking', each_data.get('RANK'))
            loader.add_value('hospital_name', each_data.get('HOSPNAME'))
            loader.add_value('tech_investment', each_data.get('INPUT'))
            loader.add_value('tech_output', each_data.get('OUTPUT'))
            loader.add_value('academic_influence', each_data.get('INFLUENCE'))
            loader.add_value('total_score', each_data.get('SUM'))
            loader.add_value('create_time', now_day())
            loader.add_value('update_time', now_day())
            ranking_item = loader.load_item()
            yield ranking_item

    def parse_subject(self, response):
        """学科排行"""
        self.logger.info('>>>>>>正在抓取学科排行信息……>>>>>>')
        all_subjects = response.xpath('//ul[@class="nav_left"]/li')
        for each_subject in all_subjects:
            subject_id = each_subject.xpath('a/@id').extract_first('')
            subject_name = each_subject.xpath('a/text()').extract_first('')
            if subject_id and subject_name:
                data = {
                    'subject': subject_id.split('_')[-1],
                    'year': '2017',
                    'start': '1',
                    'end': '100'
                }
                self.headers['Referer'] = self.subject_entry
                yield FormRequest(self.js_link,
                                  headers=self.headers,
                                  callback=self.parse_subject_detail,
                                  dont_filter=True,
                                  formdata=data,
                                  meta={'subject_name': subject_name})

    def parse_subject_detail(self, response):
        """学科排行详细信息"""
        self.logger.info('>>>>>>正在抓取学科排行详细信息……>>>>>>')
        subject_name = response.meta.get('subject_name')
        res = json.loads(response.text)
        for each_data in res.get('rows', []):
            loader = CommonLoader2(item=SubjectRankingItem(), response=response)
            loader.add_value('subject', subject_name)
            loader.add_value('hospital_pro', each_data.get('PROVINCE'))
            loader.add_value('ranking', each_data.get('RANK'))
            loader.add_value('hospital_name', each_data.get('HOSPNAME'))
            loader.add_value('tech_investment', each_data.get('INPUT'))
            loader.add_value('tech_output', each_data.get('OUTPUT'))
            loader.add_value('academic_influence', each_data.get('INFLUENCE'))
            loader.add_value('total_score', each_data.get('SUM'))
            loader.add_value('create_time', now_day())
            loader.add_value('update_time', now_day())
            ranking_item = loader.load_item()
            yield ranking_item

    def parse_area(self, response):
        """地区排行"""
        self.logger.info('>>>>>>正在抓取地区排行信息……>>>>>>')
        all_subjects = response.xpath('//ul[@class="nav_left"]/li')
        for each_subject in all_subjects:
            subject_id = each_subject.xpath('a/@id').extract_first('')
            subject_name = each_subject.xpath('a/text()').extract_first('')
            if subject_id and subject_name:
                data = {
                    'province_id': subject_id.split('_')[-1],
                    'year': '2017',
                    'start': '1',
                    'end': '100'
                }
                self.headers['Referer'] = self.area_entry
                yield FormRequest(self.js_link2,
                                  headers=self.headers,
                                  callback=self.parse_area_detail,
                                  dont_filter=True,
                                  formdata=data,
                                  meta={'subject_name': subject_name})

    def parse_area_detail(self, response):
        """地区排行详细信息"""
        self.logger.info('>>>>>>正在抓取地区排行详细信息……>>>>>>')
        subject_name = response.meta.get('subject_name')
        res = json.loads(response.text)
        for each_data in res.get('rows', []):
            loader = CommonLoader2(item=AreaRankingItem(), response=response)
            loader.add_value('subject', each_data.get('GB_NAME'))
            loader.add_value('hospital_pro', subject_name)
            loader.add_value('ranking', each_data.get('SHOW_RANK'))
            loader.add_value('hospital_name', each_data.get('HOSPNAME'))
            loader.add_value('create_time', now_day())
            loader.add_value('update_time', now_day())
            ranking_item = loader.load_item()
            yield ranking_item
