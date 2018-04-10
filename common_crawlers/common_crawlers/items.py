# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from common_crawlers.utils.common import get_number, standard_time, str_to_int


class CommonCrawlersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobBoleItem(scrapy.Item):
    """job_bole相关spiders的item"""
    title = scrapy.Field()
    thumbnail_url = scrapy.Field()
    thumbnail_path = scrapy.Field()
    article_url = scrapy.Field()
    article_url_id = scrapy.Field()
    create_time = scrapy.Field()
    content = scrapy.Field()
    like_num = scrapy.Field()
    comment_num = scrapy.Field()
    tags = scrapy.Field()


class CustomItemLoader(ItemLoader):
    """custom item loaders"""
    default_output_processor = TakeFirst()
    create_time_in = MapCompose(standard_time)
    like_num_in = comment_num_in = MapCompose(get_number)
    tags_out = Join(',')


class ZhiHuQuestionsItem(scrapy.Item):
    """
    知乎问题items
    问题标题、问题内容、问题id、问题url、问题评论数、问题关注数、问题浏览数
    """
    title = scrapy.Field()
    content = scrapy.Field()
    question_id = scrapy.Field()
    question_url = scrapy.Field()
    comment_nums = scrapy.Field()
    focused_nums = scrapy.Field()
    viewed_nums = scrapy.Field()
    answer_nums = scrapy.Field()
    topics = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_sql_info(self):
        """返回sql语句与参数信息"""
        now_time = datetime.datetime.now()
        # insert_sql = "insert into zhihu_questions(title,content,question_id,question_url,comment_nums" \
        #              "focused_nums,viewed_nums,answer_nums,topics,crawl_time,crawl_update_time) " \
        #              "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        insert_sql = "insert into zhihu_questions(title) values(%s)"
        params = [self['title'][0]]
        return insert_sql, params


class ZhiHuAnswersItem(scrapy.Item):
    """
    知乎答案items
    问题标题、问题内容、问题id、问题url、问题评论数、问题关注数、问题浏览数
    """
    answer_id = scrapy.Field()
    answer_url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    answer_content = scrapy.Field()
    answer_praise_nums = scrapy.Field()
    answer_comments_nums = scrapy.Field()
    answer_create_time = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_sql_info(self):
        """返回sql语句与参数信息"""
        now_time = datetime.datetime.now()
        insert_sql = "insert into zhihu_answers(answer_id,answer_url,question_id,author_id,answer_content" \
                     "answer_praise_nums,answer_comments_nums,answer_create_time,crawl_time," \
                     "crawl_update_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [int(self.answer_id[0]), self.answer_url[0], int(self.question_id[0]), self.author_id[0],
                  self.answer_content[0], int(self.answer_praise_nums[0]), int(self.answer_comments_nums[0]),
                  self.answer_create_time[0], now_time, now_time]
        return insert_sql, params
