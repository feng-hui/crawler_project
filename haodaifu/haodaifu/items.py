# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class HaodaifuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class DoctorItem(scrapy.Item):
    """
    doctor_id: 微医上医生id
    doctor_hid: 好大夫上医生id,未开通个人网站的不存
    """
    doctor_id = scrapy.Field()
    doctor_hid = scrapy.Field()
    search_url = scrapy.Field()
    doctor_url = scrapy.Field()
    crawl_time = scrapy.Field()


class DoctorArticleItem(scrapy.Item):
    """
    doctor_id: 微医上医生id
    article_title: 好大夫上医生发布的文章标题
    article_url: 好大夫上医生发布的文章链接
    """
    doctor_id = scrapy.Field()
    doctor_hid = scrapy.Field()
    article_title = scrapy.Field()
    article_url = scrapy.Field()
    doctor_url = scrapy.Field()
    crawl_time = scrapy.Field()
    personal_website = scrapy.Field()


class DoctorArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
