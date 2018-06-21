# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class HaodaifuPipeline(object):

    def __init__(self, mongodb_uri, mongodb_db, mongodb_col):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        self.client = pymongo.MongoClient(host=mongodb_uri)
        self.db = self.client[mongodb_db]
        self.mongodb_doc = mongodb_col

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get('MONGODB_URI'),
            mongodb_db=crawler.settings.get('MONGODB_DATABASE'),
            mongodb_col=crawler.settings.get('MONGODB_DOC')
        )

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.mongodb_doc].insert(dict(item))
        return item


