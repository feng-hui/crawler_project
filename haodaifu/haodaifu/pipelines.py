# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from pymysql.cursors import DictCursor
from twisted.enterprise import adbapi


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


class MysqlPipeline(object):

    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        params = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DB'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True
        )
        db_pool = adbapi.ConnectionPool('pymysql', **params)
        return cls(db_pool)

    def process_item(self, item, spider):
        query = self.db_pool.runInteraction(self.do_insert, item)
        query.addErrback(self.trace_error, item, spider)
        return item

    @staticmethod
    def do_insert(cursor, item):
        sql, params = item.get_sql_info()
        cursor.execute(sql, params)

    @staticmethod
    def trace_error(failure, item, spider):
        spider.logger.error('The reason of failure: {}'.format(repr(failure)))
