# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from common_crawlers.utils.common import get_number, standard_time, str_to_int, remove_splash
from w3lib.html import remove_tags


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
        # now_time = datetime.datetime.now()
        insert_sql = "insert into zhihu_questions(title,content,question_id,question_url,comment_nums," \
                     "focused_nums,viewed_nums,answer_nums,topics,crawl_time,crawl_update_time) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update " \
                     "content=values(content),comment_nums=values(comment_nums)," \
                     "focused_nums=values(focused_nums),viewed_nums=values(viewed_nums)," \
                     "crawl_update_time=values(crawl_update_time)" \
                     ""
        params = [self['title'][0],
                  self['content'][0],
                  int(self['question_id'][0]),
                  self['question_url'][0],
                  get_number(self['comment_nums'][0]),
                  str_to_int(self['focused_nums'][0]),
                  str_to_int(self['viewed_nums'][1]),
                  int(self['answer_nums'][0]),
                  ','.join(self['topics']),
                  self['crawl_time'][0],
                  self['crawl_update_time'][0]]
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
    answer_update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_sql_info(self):
        """返回sql语句与参数信息"""
        # now_time = datetime.datetime.now()
        insert_sql = "insert into zhihu_answers(answer_id,answer_url,question_id,author_id,answer_content," \
                     "answer_praise_nums,answer_comments_nums,answer_create_time,answer_update_time," \
                     "crawl_time,crawl_update_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) " \
                     "on duplicate key update answer_content=values(answer_content)," \
                     "answer_praise_nums=values(answer_praise_nums)," \
                     "answer_comments_nums=values(answer_comments_nums)," \
                     "crawl_update_time=values(crawl_update_time)"
        params = [int(self['answer_id'][0]),
                  self['answer_url'][0],
                  int(self['question_id'][0]),
                  self['author_id'][0],
                  self['answer_content'][0],
                  int(self['answer_praise_nums'][0]),
                  int(self['answer_comments_nums'][0]),
                  self['answer_create_time'][0],
                  self['answer_update_time'][0],
                  self['crawl_time'][0],
                  self['crawl_update_time'][0]]
        return insert_sql, params


class LaGouItemLoader(ItemLoader):
    """拉勾custom item loader"""
    default_output_processor = TakeFirst()
    job_tags_in = Join(',')
    job_addr_in = MapCompose(remove_tags, remove_splash)
    job_degree_need_in = job_city_in = job_comp_name_in = \
        job_work_years_in = job_publish_time_in = MapCompose(remove_splash)
    job_desc_in = Join()


class LaGouJobItem(scrapy.Item):
    """拉勾职位item"""
    job_url = scrapy.Field()
    job_url_id = scrapy.Field()
    job_title = scrapy.Field()
    min_job_salary = scrapy.Field()
    max_job_salary = scrapy.Field()
    job_city = scrapy.Field()
    job_work_years = scrapy.Field()
    job_degree_need = scrapy.Field()
    job_type = scrapy.Field()
    job_publish_time = scrapy.Field()
    job_tags = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field()
    job_comp_url = scrapy.Field()
    job_comp_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_sql_info(self):
        """return sql info"""
        sql = "insert into lagou_jobs(job_url,job_url_id,job_title,min_job_salary,max_job_salary," \
              "job_city,job_work_years,job_degree_need,job_type,job_publish_time,job_tags,job_advantage," \
              "job_desc,job_addr,job_comp_url,job_comp_name,crawl_time,crawl_update_time) " \
              "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [self['job_url'],
                  self['job_url_id'],
                  self['job_title'],
                  self['min_job_salary'],
                  self['max_job_salary'],
                  self['job_city'],
                  self['job_work_years'],
                  self['job_degree_need'],
                  self['job_type'],
                  self['job_publish_time'],
                  self['job_tags'],
                  self['job_advantage'],
                  self['job_desc'],
                  self['job_addr'],
                  self['job_comp_url'],
                  self['job_comp_name'],
                  self['crawl_time'],
                  self['crawl_update_time']
                  ]
        return sql, params
