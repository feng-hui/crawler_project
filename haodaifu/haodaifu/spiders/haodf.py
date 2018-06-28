# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
from haodaifu.items import DoctorArticleItem, DoctorArticleItemLoader
from urllib.parse import urlencode
from haodaifu.utils.search_keywords import my_dict
from scrapy.http import Request
from haodaifu.utils.common import get_host, get_host2
from urllib.parse import urljoin
from scrapy.exceptions import IgnoreRequest
from scrapy import signals
from twisted.internet.error import DNSLookupError
from scrapy.spidermiddlewares.httperror import HttpError


class HaodfSpider(scrapy.Spider):
    name = 'haodf'
    allowed_domains = ['haodf.com']
    start_urls = []
    keywords = my_dict
    base_url = 'https://so.haodf.com/index/search?type=&{}&doctor_id={}'
    ignored_urls = []
    error_urls = []

    def start_requests(self):
        for each_kw in self.keywords:
            search_kw = '{0} {1} {2}'.format(each_kw['doctor_name'],
                                             each_kw['h_pro'].replace('\\N', ''),
                                             each_kw['department_name'].replace('\\N', ''))
            doctor_id = each_kw['doctor_id']
            self.log('当前正在抓取的搜索关键词为：{}'.format(search_kw.strip()))
            params = urlencode({'kw': search_kw.strip()}, encoding='gb2312', errors='ignore')
            self.start_urls.append(self.base_url.format(params, str(doctor_id)))
        for each_url in self.start_urls:
            doctor_id = re.search(r'.*doctor_id=(.*?)$', each_url)
            if doctor_id:
                doctor_id = doctor_id.group(1)
                each_url = re.sub(r'&doctor_id=.*', '', each_url)
                yield Request(each_url,
                              callback=self.parse,
                              meta={'doctor_id': doctor_id},
                              errback=self.err_collector)

    def parse(self, response):
        """医生搜索页"""
        doctor_link = response.xpath('//div[@class="search-list"]/div[@class="sl-item"]'
                                     '[1]/div/p/span/a/@href').extract()
        doctor_id = response.meta['doctor_id']
        try:
            if doctor_link:
                # 存在该医生
                doctor_link = doctor_link[0]
                if 'www.haodf.com' in doctor_link:
                    # 不存在个人网站,不继续抓取
                    loader = DoctorArticleItemLoader(item=DoctorArticleItem(), response=response)
                    loader.add_value('doctor_id', doctor_id)
                    loader.add_value('doctor_hid', '未开通个人网站')
                    loader.add_value('article_url', '未开通个人网站')
                    loader.add_value('article_title', '未开通个人网站')
                    loader.add_value('doctor_url', doctor_link)
                    loader.add_value('crawl_time', datetime.datetime.now())
                    article_item = loader.load_item()
                    yield article_item
                else:
                    # 存在个人网站,继续抓取文章内页
                    article_list_link = urljoin(doctor_link.replace('//', 'https://'), 'lanmu')
                    request = Request(article_list_link,
                                      callback=self.parse_article,
                                      meta={'doctor_id': doctor_id},
                                      errback=self.err_collector)
                    request.meta['host'] = get_host2(article_list_link)
                    request.meta['Referer'] = doctor_link.replace('//', 'https://')
                    yield request
            else:
                # 不存在该医生
                loader = DoctorArticleItemLoader(item=DoctorArticleItem(), response=response)
                loader.add_value('doctor_id', doctor_id)
                loader.add_value('doctor_hid', '好大夫网站上没有该医生')
                loader.add_value('article_url', '好大夫网站上没有该医生')
                loader.add_value('article_title', '好大夫网站上没有该医生')
                loader.add_value('doctor_url', '好大夫网站上没有该医生')
                loader.add_value('crawl_time', datetime.datetime.now())
                article_item = loader.load_item()
                yield article_item
        except Exception as e:
            self.logger.error('抓取过程中出现错误,错误的原因是:{}'.format(e))

    def parse_article(self, response):
        """
        文章栏目页，涉及翻页，需要的数据包括文章标题、文章链接
        """
        self.logger.info('正在抓取的文章栏目页的url是{}:'.format(response.url))
        doctor_id = response.meta['doctor_id']
        all_article_links = response.xpath('//a[@class="art_t"]')
        if all_article_links:
            for each_article in all_article_links:
                # 发过文章
                article_loader = DoctorArticleItemLoader(item=DoctorArticleItem(), selector=each_article)
                article_loader.add_value('doctor_id', doctor_id)
                article_loader.add_value('doctor_hid', get_host(response.url))
                article_loader.add_xpath('article_url', '@href')
                article_loader.add_xpath('article_title', '@title')
                article_loader.add_value('doctor_url', '{0}{1}'.format('https://', get_host2(response.url)))
                article_loader.add_value('crawl_time', datetime.datetime.now())
                article_item = article_loader.load_item()
                yield article_item
        else:
            # 未发过文章
            article_loader = DoctorArticleItemLoader(item=DoctorArticleItem(), response=response)
            article_loader.add_value('doctor_id', doctor_id)
            article_loader.add_value('doctor_hid', get_host(response.url))
            article_loader.add_value('article_url', '未发文章')
            article_loader.add_value('article_title', '未发文章')
            article_loader.add_value('doctor_url', '{0}{1}'.format('https://', get_host2(response.url)))
            article_loader.add_value('crawl_time', datetime.datetime.now())
            article_item = article_loader.load_item()
            yield article_item
        next_page = response.xpath('//div[@class="page_turn"]/a[contains(text(), "下一页")]/@href').extract_first()
        if next_page:
            next_page_link = urljoin(response.url, next_page)
            request = Request(next_page_link,
                              callback=self.parse_article,
                              meta={'doctor_id': doctor_id},
                              errback=self.err_collector)
            request.meta['host'] = get_host2(response.url)
            request.meta['Referer'] = response.url
            yield request

    def err_collector(self, failure):
        """错误收集"""
        self.logger.error('发生错误的原因是:{}'.format(repr(failure)))
        if failure.check(IgnoreRequest):
            try:
                self.logger.info('错误的类型为:IgnoreRequest')
                response = failure.value.response
                failure_url = response.url
            except Exception as e:
                failure_url = failure.request.url
                self.logger.error('错误收集的时候,发生错误,原因是:{}'.format(str(e)))
            self.ignored_urls.append(failure_url)
            self.crawler.signals.connect(self.deal_error, signals.spider_closed)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.error_urls.append(request.url)
            self.crawler.signals.connect(self.deal_error, signals.spider_closed)
        elif failure.check(HttpError):
            try:
                self.logger.info('错误的类型为:HttpError')
                response = failure.value.response
                failure_url = response.url
            except Exception as e:
                failure_url = failure.request.url
                self.logger.error('错误收集的时候,发生错误,原因是:{}'.format(str(e)))
            self.ignored_urls.append(failure_url)
            self.crawler.signals.connect(self.deal_error, signals.spider_closed)

    def deal_error(self):
        """
        爬虫结束的时候,输出所有被忽略的url
        """
        self.crawler.stats.set_value('ignored_urls/all_ignored_urls_list', ','.join(self.ignored_urls))
        self.crawler.stats.set_value('ignored_urls/count', len(self.ignored_urls))
