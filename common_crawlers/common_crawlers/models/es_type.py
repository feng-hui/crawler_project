# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/4/21 19:38'
# @email = 'fengh@asto-inc.com'
from elasticsearch_dsl import DocType, Text, Keyword, Integer, Date, Completion
from elasticsearch_dsl.connections import create_connection
create_connection(hosts=["localhost"])


class JobBoleEsType(DocType):
    suggest = Completion()
    title = Text(analyzer="ik_max_word")
    thumbnail_url = Keyword()
    article_url = Keyword()
    article_url_id = Keyword()
    create_time = Date()
    content = Text(analyzer="ik_max_word")
    like_num = Integer()
    comment_num = Integer()
    tags = Text(analyzer="ik_max_word")

    class Meta:
        index = "job_bole"


if __name__ == "__main__":
    JobBoleEsType.init()