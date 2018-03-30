# -*- coding: utf-8 -*-
import scrapy
import logging
import re
logger = logging.getLogger(__name__)


class JobBole2Spider(scrapy.Spider):
    name = 'job_bole2'
    allowed_domains = ['jobbole.com']
    start_urls = ['http://blog.jobbole.com/113659/']

    # def parse(self, response):
    #     """
    #     使用xpath方法
    #     获取文章页面的标题、发布时间、内容、点赞数、评论数、文章标签等
    #     """
    #     title = response.xpath('//*[@id="post-69"]/div[1]/h1/text()').extract()
    #     create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()
    #     content = response.xpath('//div[@class="entry"]').extract()
    #     like_num = response.xpath('//h10[contains(@id,"votetotal")]/text()').extract()
    #     comment_num = response.xpath('//a[@href="#article-comment"]/span/text()').extract()
    #     tags = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/'
    #                           'a[not(contains(text(),"评论"))]/text()').extract()
    #     title = title[0].strip() if title else ""
    #     create_time = re.search(r'(\d{4}/\d{2}/\d{2})', create_time[0].strip()).group(1) if create_time else ""
    #     content = content[0] if content else ""
    #     like_num = like_num[0].strip() if like_num else '0'
    #     comment_num = re.search(r'(\d+)', comment_num[0]).group(1).strip() \
    #         if comment_num and comment_num[0].strip() != "评论" else '0'
    #     tags = ','.join(tags).strip() if tags else ""
    #     logger.info('标题为：{0}， 发布时间为：{1}， 点赞数为：{2}， 留言数为：{3}， 标签为：{4}'.
    #                 format(title, create_time, like_num, comment_num, tags))

    def parse(self, response):
        """
        使用css方法
        获取文章页面的标题、发布时间、内容、点赞数、评论数、文章标签等
        """
        title = response.css('.entry-header h1::text').extract()
        create_time = response.css('p.entry-meta-hide-on-mobile::text').extract()
        content = response.css('div.entry').extract()
        like_num = response.css('h10[id*="votetotal"]::text').extract()
        comment_num = response.css('a[href="#article-comment"] span::text').extract()
        tags = response.css('p.entry-meta-hide-on-mobile a:not(:contains("评论"))::text').extract()
        title = title[0].strip() if title else ""
        create_time = re.search(r'(\d{4}/\d{2}/\d{2})', create_time[0].strip()).group(1) if create_time else ""
        content = content[0] if content else ""
        like_num = like_num[0].strip() if like_num else '0'
        comment_num = re.search(r'(\d+)', comment_num[0]).group(1).strip() \
            if comment_num and comment_num[0].strip() != "评论" else '0'
        tags = ','.join(tags).strip() if tags else ""
        logger.info('标题为：{0}， 发布时间为：{1}， 点赞数为：{2}， 留言数为：{3}， 标签为：{4}'.
                    format(title, create_time, like_num, comment_num, tags))
