# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings


class XiciPipeline(object):

    def __init__(self):
        client = pymongo.MongoClient(host=settings['MONGODB_HOST'],
                                     port=settings['MONGODB_PORT'])
        db_name = client[settings['MONGODB_DBNAME']]
        self.doc_name = db_name[settings['MONGODB_DOCNAME']]

    def process_item(self, item, spider):
        proxy_info = dict(item)
        self.doc_name.insert(proxy_info)
        return item
