# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from medicalmap.items import HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from twisted.enterprise import adbapi
from pymysql.cursors import DictCursor


class MedicalmapPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, HospitalInfoItem):
            spider.logger.info('hospital_info_item')
        elif isinstance(item, HospitalDepItem):
            spider.logger.info('hospital_dep_item')
        elif isinstance(item, DoctorInfoItem):
            spider.logger.info('doctor_info_item')
        elif isinstance(item, DoctorRegInfoItem):
            spider.logger.info('doctor_reg_info_item')
        else:
            spider.logger.error('unknown error')
        return item


class MongodbPipeline(object):
    pass


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
            charset='utf-8',
            cursor=DictCursor,
            use_unicode=True
        )
        db_pool = adbapi.ConnectionPool('pymysql', **params)
        return cls(db_pool)

    def process_item(self, item, spider):
        if isinstance(item, HospitalInfoItem):
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
