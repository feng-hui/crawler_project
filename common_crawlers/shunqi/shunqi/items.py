# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose


def remove_tags(value):
    return value.replace('+86-', '')


class ShunqiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    tel = scrapy.Field()
    contact = scrapy.Field()
    mobile = scrapy.Field(
        output_processor=MapCompose(remove_tags)
    )
    email = scrapy.Field()
    postal_code = scrapy.Field()
    fax = scrapy.Field()
