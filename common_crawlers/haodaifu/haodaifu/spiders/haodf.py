# -*- coding: utf-8 -*-
import scrapy
from haodaifu.items import DoctorItem, DoctorArticleItem
from urllib.parse import urlencode
from .search_keywords import ALL_KEYWORDS
from scrapy.http import Request


class HaodfSpider(scrapy.Spider):
    name = 'haodf'
    allowed_domains = ['haodf.com']
    start_urls = []
    keywords = list(set(ALL_KEYWORDS))
    base_url = 'https://so.haodf.com/index/search?type=&'

    def start_requests(self):
        for each_kw in self.keywords:
            self.log('当前正在抓取的搜索关键词为：{}'.format(each_kw))
            params = urlencode({'kw': each_kw}, encoding='gb2312')
            self.start_urls.append('{0}{1}'.format(self.base_url, params))
        for each_url in self.start_urls:
            yield Request(each_url)

    def parse(self, response):
        """医生搜索页"""
        doctor_link = response.xpath('//div[@class="search-list"]/div[@class="sl-item"][1]/div/p/span/a/@href').extract()
        try:
            if doctor_link:
                # 存在该医生
                doctor_link = doctor_link[0]
                if 'www.haodf.com' in doctor_link:
                    # 不存在个人网站,不继续抓取
                    pass
                else:
                    # 存在个人网站,继续抓取文章内页
                    pass
            else:
                # 不存在该医生
                pass
        except Exception as e:
            self.logger.error('抓取过程中出现错误,错误的原因是:{}'.format(e))

    def parse_article(self, response):
        """
        文章栏目页，涉及翻页，需要的数据包括文章标题、文章链接
        """
        pass
