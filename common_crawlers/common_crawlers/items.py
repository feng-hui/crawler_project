# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re
import scrapy
import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


class CommonCrawlersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    thumbnail_url = scrapy.Field()
    thumbnail_path = scrapy.Field()
    article_url = scrapy.Field()
    article_url_id = scrapy.Field()
    create_time = scrapy.Field()
    content = scrapy.Field()
    like_num = scrapy.Field()
    comment_num = scrapy.Field()
    tags = scrapy.Field()


class JobBoleItem(scrapy.Item):
    title = scrapy.Field(
        # input_processor=MapCompose(lambda x: x + '----test_job'),
        # output_processor=TakeFirst()
    )
    thumbnail_url = scrapy.Field()
    thumbnail_path = scrapy.Field()
    article_url = scrapy.Field()
    article_url_id = scrapy.Field()
    create_time = scrapy.Field()
    content = scrapy.Field()
    like_num = scrapy.Field()
    comment_num = scrapy.Field()
    tags = scrapy.Field()


def get_number(values_text):
    """返回文本里的数值"""
    values = re.search('(\d+)', values_text)
    if values:
        return values.group(1)
    else:
        return '0'


def standard_time(values_text):
    values = re.search('(\d{4}/\d{2}/\d{2})', values_text)
    if values:
        return datetime.datetime.strptime(values.group(1), '%Y/%m/%d').date()
    else:
        return datetime.datetime.now().date()


class CustomItemLoader(ItemLoader):
    """custom item loaders"""
    default_output_processor = TakeFirst()
    create_time_in = MapCompose(standard_time)
    like_num_in = comment_num_in = MapCompose(get_number)
    tags_out = Join(',')
