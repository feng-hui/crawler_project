# -*- coding: utf-8 -*-
import scrapy
import datetime
from scrapy.http import Request
from urllib.parse import urljoin
from haodaifu.items import DoctorArticleItem, DoctorArticleItemLoader
from haodaifu.utils.common import get_host, get_host2


class PersonalWebsiteSpider(scrapy.Spider):
    """
    抓取好大夫医生个人网站发布的全部文章
    URL参考:https://tianjiangbo.haodf.com/
    """
    name = 'personal_website'
    allowed_domains = ['haodf.com']
    start_urls = ['http://haodf.com/']

    def parse(self, response):
        pass

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
