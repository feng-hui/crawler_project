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


class ZhiHuQuestionsItem(scrapy.Item):
    """
    知乎问题items
    问题标题、问题内容、问题id、问题url、问题评论数、问题关注数、问题浏览数
    """
    title = scrapy.Field()
    content = scrapy.Field()
    question_id = scrapy.Field()
    question_url = scrapy.Field()
    comment_nums = scrapy.Field()
    focused_nums = scrapy.Field()
    viewed_nums = scrapy.Field()


class ZhiHuAnswersItem(scrapy.Item):
    """
    知乎答案items
    问题标题、问题内容、问题id、问题url、问题评论数、问题关注数、问题浏览数
    """
    pass
