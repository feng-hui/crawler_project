# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose


def remove_strip(value):
    return value.strip()


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field(
        input_processor=MapCompose(remove_strip)
    )
    url = scrapy.Field()
    price = scrapy.Field()
    all_images_url = scrapy.Field()
    details = scrapy.Field()
    asin = scrapy.Field()
    comments = scrapy.Field()
    stars = scrapy.Field()
