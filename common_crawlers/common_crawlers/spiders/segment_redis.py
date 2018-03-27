# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import logging
from common_crawlers.items import CommonCrawlersItem
logger = logging.getLogger(__name__)


class SegmentRedisSpider(RedisSpider):
    name = "segment_redis"
    allowed_domains = ["segment.com"]
    start_urls = ['https://segmentfault.com/t/python/questions']
    redis_key = "segment_redis:start_urls"
    host_url = "https://segmentfault.com"

    def parse(self, response):
        selector = response.xpath('//div[@class="stream-list question-stream "]/section')
        item = CommonCrawlersItem()
        for sel in selector:
            title = sel.xpath('div[@class="summary"]/h2/a/text()').extract()
            link = sel.xpath('div[@class="summary"]/h2/a/@href').extract()
            item['title'] = title[0] if title else ""
            item['link'] = '{0}{1}'.format(self.host_url, link[0]) if link else ""
            yield item

        next_page = selector.xpath('//li[@class="next"]/a/@href').extract()
        if next_page:
            next_page_link = '{0}{1}'.format(self.host_url, next_page[0])
            logger.info("the link of next page is {}".format(next_page_link))
