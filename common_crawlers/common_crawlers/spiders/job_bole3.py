# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from common_crawlers.utils.common import get_md5
from common_crawlers.items import CommonCrawlersItem
from urllib import parse


class JobBole3Spider(scrapy.Spider):
    name = 'job_bole3'
    allowed_domains = ['jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/page/21/']

    def parse(self, response):
        all_links = response.xpath('//div[@id="archive"]/div/div[@class="post-thumb"]/a')
        if all_links:
            for each_link in all_links:
                each_url = each_link.xpath('@href')
                img_url = each_link.xpath('img/@src')
                if img_url:
                    thumbnail_url = img_url.extract()[0]
                else:
                    thumbnail_url = ""
                yield Request(parse.urljoin(response.url, each_url.extract()[0]),
                              callback=self.parse_detail, meta={'thumbnail_url': thumbnail_url})

        # next_page = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        # self.logger.info('下一页的链接是：{}'.format(next_page))
        # if next_page:
        #     yield Request(next_page, callback=self.parse)

    def parse_detail(self, response):
        """
        使用xpath方法
        获取文章页面的标题、发布时间、内容、点赞数、评论数、文章标签等
        """
        self.logger.info('正在抓取的url是：{0}'.format(response.url))
        l = ItemLoader(item=CommonCrawlersItem(), response=response)
        l.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        l.add_value('thumbnail_url', response.meta['thumbnail_url'])
        l.add_value('article_url', response.url)
        l.add_value('article_url_id', get_md5(response.url))
        l.add_xpath('create_time', '//p[@class="entry-meta-hide-on-mobile"]/text()')
        l.add_xpath('content', '//div[@class="entry"]')
        l.add_xpath('like_num', '//h10[contains(@id,"votetotal")]/text()')
        l.add_xpath('comment_num', '//a[@href="#article-comment"]/span/text()')
        l.add_xpath('tags', '//p[@class="entry-meta-hide-on-mobile"]/a[not(contains(text(),"评论"))]/text()')
        return l.load_item()
        # create_time = re.search(r'(\d{4}/\d{2}/\d{2})', create_time[0].strip()).group(1) if create_time else ""
        # comment_num = re.search(r'(\d+)', comment_num[0]).group(1).strip() \
        #     if comment_num and comment_num[0].strip() != "评论" else '0'
        # tags = ','.join(tags).strip() if tags else ""