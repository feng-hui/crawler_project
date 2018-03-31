# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from common_crawlers.items import CommonCrawlersItem


class SegmentLinkExtractor2Spider(CrawlSpider):
    name = 'segment_link_extractor2'
    allowed_domains = ['segmentfault.com']
    start_urls = [
        # 'https://segmentfault.com/q/1010000014100380'
        'https://segmentfault.com/questions',
        'https://segmentfault.com/t/python/questions',
        # 'http://www.jianshu.com'
    ]

    rules = (
        Rule(LinkExtractor(allow=('/q/\d+', ),
                           deny=('/u/.*?', '/q/\d+/a-\d+', '/q/\d+\?',
                                 '/t/.*?')), callback='parse_link', follow=True),
    )

    def parse_link(self, response):
        self.logger.info('正在抓取的url：{0}'.format(response.url))
        item = CommonCrawlersItem()
        item['title'] = response.xpath('//h1[@id="questionTitle"]/a/text()').extract_first()
        return item
