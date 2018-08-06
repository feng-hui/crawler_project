# -*- coding: utf-8 -*-
import random
import scrapy
from scrapy import signals
from scrapy.http import Request
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, get_county, match_special2
from medicalmap.items import CommonLoader2, HospitalInfoTestItem, HospitalDepItem, HospitalAliasItem


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
        pass

    def parse(self, response):
        """综合排行"""
        self.logger.info('>>>>>>正在抓取综合排行信息……>>>>>>')


    def parse_subject(self, response):
        """学科排行"""
        self.logger.info('>>>>>>正在抓取学科排行信息……>>>>>>')

    def parse_area(self, response):
        """地区排行"""
        self.logger.info('>>>>>>正在抓取地区排行信息……>>>>>>')
