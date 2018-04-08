# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from common_crawlers.utils.common import get_number, standard_time


class CommonCrawlersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobBoleItem(scrapy.Item):
    """job_bole相关spiders的item"""
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


class CustomItemLoader(ItemLoader):
    """custom item loaders"""
    default_output_processor = TakeFirst()
    create_time_in = MapCompose(standard_time)
    like_num_in = comment_num_in = MapCompose(get_number)
    tags_out = Join(',')
