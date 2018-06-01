# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings


class AmazonPipeline(object):

    client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
    db = client[settings['MONGO_DB']]
    doc = db[settings['MONGO_DOC']]

    def process_item(self, item, spider):
        item = dict(item)
        self.doc.insert(item)
        return item
