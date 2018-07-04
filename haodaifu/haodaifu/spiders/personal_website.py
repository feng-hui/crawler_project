# -*- coding: utf-8 -*-
import scrapy
import datetime
from scrapy.http import Request
from urllib.parse import urljoin
from haodaifu.items import DoctorArticleItem, DoctorArticleItemLoader
from haodaifu.utils.common import get_host, get_host3
from haodaifu.utils.search_keywords import all_personal_websites
from scrapy.exceptions import IgnoreRequest
from scrapy import signals


class PersonalWebsiteSpider(scrapy.Spider):
    """
    抓取好大夫医生个人网站发布的全部文章
    URL参考:https://tianjiangbo.haodf.com/
    """
    name = 'personal_website'
    allowed_domains = ['haodf.com']
    start_urls = []
    ignored_urls = []
    custom_settings = {}
    headers = {}

    def start_requests(self):
        for each_kw in all_personal_websites:
            personal_website = urljoin('https://', each_kw['doctor_url'])
            self.start_urls.append(personal_website)
        for each_url in self.start_urls:
            self.headers['Referer'] = each_url
            self.headers['Host'] = get_host3(each_url)
            request = Request(urljoin(each_url, 'lanmu'),
                              headers=self.headers,
                              callback=self.parse,
                              errback=self.err_collector)
            # request.meta['host'] = get_host3(each_url)
            # request.meta['Referer'] = each_url
            yield request

    def parse(self, response):
        """
        文章栏目页，涉及翻页，需要的数据包括文章标题、文章链接
        """
        # self.logger.info(response.request.headers)
        self.logger.info('正在抓取的文章栏目页的url是{}:'.format(response.url))
        doctor_hos = response.xpath('//div[@class="fl pr"]/p/a[1]/text()').extract_first('')
        doctor_dep = response.xpath('//div[@class="fl pr"]/p/a[2]/text()').extract_first('')
        all_article_links = response.xpath('//a[@class="art_t"]')
        if all_article_links:
            for each_article in all_article_links:
                # 发过文章
                article_loader = DoctorArticleItemLoader(item=DoctorArticleItem(), selector=each_article)
                article_loader.add_value('doctor_hid', get_host(response.url))
                article_loader.add_xpath('article_url', '@href')
                article_loader.add_xpath('article_title', '@title')
                article_loader.add_value('personal_website', urljoin('https://', get_host3(response.url)))
                article_loader.add_value('doctor_hos', doctor_hos)
                article_loader.add_value('doctor_dep', doctor_dep)
                article_loader.add_value('crawl_time', datetime.datetime.now())
                article_item = article_loader.load_item()
                yield article_item
        else:
            # 未发过文章
            article_loader = DoctorArticleItemLoader(item=DoctorArticleItem(), response=response)
            article_loader.add_value('doctor_hid', get_host(response.url))
            article_loader.add_value('article_url', '')
            article_loader.add_value('article_title', '')
            article_loader.add_value('personal_website', urljoin('https://', get_host3(response.url)))
            article_loader.add_value('doctor_hos', doctor_hos)
            article_loader.add_value('doctor_dep', doctor_dep)
            article_loader.add_value('crawl_time', datetime.datetime.now())
            article_item = article_loader.load_item()
            yield article_item
        next_page = response.xpath('//div[@class="page_turn"]/a[contains(text(), "下一页")]/@href').extract_first()
        if next_page:
            next_page_link = urljoin(response.url, next_page)
            request = Request(next_page_link,
                              callback=self.parse,
                              errback=self.err_collector)
            request.meta['host'] = get_host3(response.url)
            request.meta['Referer'] = response.url
            yield request

    def err_collector(self, failure):
        """错误收集"""
        self.logger.error('发生错误的原因是:{}'.format(repr(failure)))
        if failure.check(IgnoreRequest):
            self.logger.info('错误的类型为:IgnoreRequest')
            response = failure.value.response
            failure_url = response.url
            self.ignored_urls.append(failure_url)
            self.crawler.signals.connect(self.deal_error, signals.spider_closed)

    def deal_error(self):
        """
        爬虫结束的时候,输出所有被忽略的url
        """
        self.crawler.stats.set_value('ignored_urls/all_ignored_urls_list', ','.join(self.ignored_urls))
        self.crawler.stats.set_value('ignored_urls/count', len(self.ignored_urls))
