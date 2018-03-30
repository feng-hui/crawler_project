# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CommonCrawlersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    create_time = scrapy.Field()
    content = scrapy.Field()
    like_num = scrapy.Field()
    comment_num = scrapy.Field()
    tags = scrapy.Field()
