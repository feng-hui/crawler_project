# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class HaodaifuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class DoctorItem(scrapy.Item):
    """
    doctor_id: 微医上医生id
    doctor_hid: 好大夫上医生id,未开通个人网站的不存
    """
    doctor_id = scrapy.Field()
    doctor_hid = scrapy.Field()
    search_url = scrapy.Field()
    doctor_url = scrapy.Field()
    crawl_time = scrapy.Field()


class DoctorArticleItem(scrapy.Item):
    """
    doctor_id: 微医上医生id
    article_title: 好大夫上医生发布的文章标题
    article_url: 好大夫上医生发布的文章链接
    """
    doctor_id = scrapy.Field()
    doctor_hid = scrapy.Field()
    article_title = scrapy.Field()
    article_url = scrapy.Field()
    doctor_url = scrapy.Field()
    personal_website = scrapy.Field()
    doctor_hos = scrapy.Field()
    doctor_dep = scrapy.Field()
    crawl_time = scrapy.Field()


class DoctorArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class HdfPersonalWebsiteItem(scrapy.Item):
    """
    好大夫第二批外呼数据,20180810
    需要数据包括科室,医生职称,科室
    """
    doctor_id = scrapy.Field()
    doctor_hid = scrapy.Field()
    personal_website = scrapy.Field()
    doctor_hos = scrapy.Field()
    doctor_dep = scrapy.Field()
    doctor_level = scrapy.Field()
    location_url = scrapy.Field()
    crawl_time = scrapy.Field()
    update_time = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into haodf_data(doctor_hid,personal_website,doctor_hos,doctor_dep," \
                     "doctor_level,location_url,crawl_time,update_time) values(%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [
            self.get('doctor_hid'),
            self.get('personal_website'),
            self.get('doctor_hos'),
            self.get('doctor_dep'),
            self.get('doctor_level'),
            self.get('location_url'),
            self.get('crawl_time'),
            self.get('update_time')
        ]
        return insert_sql, params
