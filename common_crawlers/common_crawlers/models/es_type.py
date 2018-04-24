# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/4/21 19:38'
# @email = 'fengh@asto-inc.com'
from elasticsearch_dsl import DocType, Text, Keyword, Integer, Date, Completion, analyzer, tokenizer
from elasticsearch_dsl.connections import create_connection
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=['lowercase'])
# ik_analyzer = analyzer('ik_analyzer',
#                         tokenizer=tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
#                         filter=['lowercase']
# )


class JobBoleEsType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
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
