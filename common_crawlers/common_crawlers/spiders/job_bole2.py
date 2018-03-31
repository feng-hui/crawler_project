# -*- coding: utf-8 -*-
import scrapy
import logging
import re
from scrapy.http import Request
from urllib import parse
from common_crawlers.items import CommonCrawlersItem
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
logger = logging.getLogger(__name__)


class JobBole2Spider(scrapy.Spider):
    name = 'job_bole2'
    allowed_domains = ['jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts123/']

    def parse(self, response):
        all_links = response.xpath('//a[@class="archive-title"]/@href').extract()
        print(all_links)
        if all_links:
            for each_link in all_links:
                yield Request(parse.urljoin(response.url, each_link), callback=self.parse_detail)

        # next_page = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        # if next_page:
        #     yield Request(next_page, callback=self.parse)

    @staticmethod
    def parse_detail(response):
        """
        使用xpath方法
        获取文章页面的标题、发布时间、内容、点赞数、评论数、文章标签等
        """
        logger.info('正在抓取的url是：{0}'.format(response.url))
        item = CommonCrawlersItem()
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()
        content = response.xpath('//div[@class="entry"]').extract_first("")
        like_num = response.xpath('//h10[contains(@id,"votetotal")]/text()').extract_first('0')
        comment_num = response.xpath('//a[@href="#article-comment"]/span/text()').extract()
        tags = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/'
                              'a[not(contains(text(),"评论"))]/text()').extract()
        create_time = re.search(r'(\d{4}/\d{2}/\d{2})', create_time[0].strip()).group(1) if create_time else ""
        comment_num = re.search(r'(\d+)', comment_num[0]).group(1).strip() \
            if comment_num and comment_num[0].strip() != "评论" else '0'
        tags = ','.join(tags).strip() if tags else ""
        item['title'] = title
        item['create_time'] = create_time
        # item['content'] = content
        item['like_num'] = like_num
        item['comment_num'] = comment_num
        item['tags'] = tags
        yield item

    @staticmethod
    def parse_detail2(response):
        """
        使用css方法
        获取文章页面的标题、发布时间、内容、点赞数、评论数、文章标签等
        """
        logger.info('正在抓取的url是：{0}'.format(response.url))
        title = response.css('.entry-header h1::text').extract_first()
        create_time = response.css('p.entry-meta-hide-on-mobile::text').extract()
        content = response.css('div.entry').extract_first("")
        like_num = response.css('h10[id*="votetotal"]::text').extract_first('0')
        comment_num = response.css('a[href="#article-comment"] span::text').extract()
        tags = response.css('p.entry-meta-hide-on-mobile a:not(:contains("评论"))::text').extract()
        create_time = re.search(r'(\d{4}/\d{2}/\d{2})', create_time[0].strip()).group(1) if create_time else ""
        comment_num = re.search(r'(\d+)', comment_num[0]).group(1).strip() \
            if comment_num and comment_num[0].strip() != "评论" else '0'
        tags = ','.join(tags).strip() if tags else ""
        logger.info('标题为：{0}， 发布时间为：{1}， 点赞数为：{2}， 留言数为：{3}， 标签为：{4}'.
                    format(title, create_time, like_num, comment_num, tags))
