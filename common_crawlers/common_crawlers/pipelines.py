# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline


class CommonCrawlersPipeline(object):
    def process_item(self, item, spider):
        return item


class ThumbnailImagePipeline(ImagesPipeline):
    """保存缩略图的本地地址到item里"""
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_path = value.get('path', '')
            item['thumbnail_path'] = image_path
        return item
