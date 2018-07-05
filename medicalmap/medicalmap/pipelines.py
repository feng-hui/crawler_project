# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from medicalmap.items import HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem


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
