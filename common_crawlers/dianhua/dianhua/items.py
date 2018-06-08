# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DianhuaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    h_name = scrapy.Field()
    h_tel = scrapy.Field()
    h_address = scrapy.Field()
