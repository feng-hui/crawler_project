# -*- coding: utf-8 -*-
import scrapy
import logging
logger = logging.getLogger(__name__)

class JobBole2Spider(scrapy.Spider):
    name = 'job_bole2'
    allowed_domains = ['jobbole.com']
    start_urls = ['http://blog.jobbole.com/69/']

    def parse(self, response):
        title = response.xpath('//*[@id="post-69"]/div[1]/h1/text()').extract()
        if title:
            logger.info('返回的页面标题为：{0}'.format(title[0]))
        else:
            logger.info("没获取到文章标题")
