# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractor import LinkExtractor
import logging
logger = logging.getLogger(__name__)


class SegmentLinkExtractorSpider(scrapy.Spider):
    name = 'segment_link_extractor'
    allowed_domains = ['segment.com']
    start_urls = ['https://segmentfault.com/t/python/blogs']

    def parse(self, response):
        """获取列表里指定方式下的所有链接"""

        # 方法1：restrict_xpaths
        # link = LinkExtractor(restrict_xpaths='//div[@class="stream-list blog-stream"]/section/div/h2')

        # 方法2：allow,使用正则表达式来匹配
        # pattern = '/a/.*?'
        # link = LinkExtractor(allow=pattern)

        # 方法3：deny，跟方法2相反，需要去除的链接过多
        # pattern = '/u/.*?|/t/.*?|/app'
        # link = LinkExtractor(deny=pattern)

        # 方法4：allow_domains
        # domain = ['segmentfault.com']
        # link = LinkExtractor(allow_domains=domain)

        # 方法5：deny_domains
        # domain = ['segmentfault.com']
        # link = LinkExtractor(deny_domains=domain)

        # 方法6：tags、attrs，返回页面所有的链接
        # link = LinkExtractor(tags='a', attrs='href')

        # 方法7：restric_css
        link = LinkExtractor(restrict_css='.stream-list > section > div > h2')

        all_links = link.extract_links(response)
        if all_links:
            for each_link in all_links:
                logger.info('符合要求的链接：{}'.format(each_link.url))
