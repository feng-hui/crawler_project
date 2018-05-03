# -*- coding: utf-8 -*-
import json
import codecs

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class WxBitcoinPipeline(object):
    def process_item(self, item, spider):
        return item


class CustomJsonPipeline(object):
    """自定义存储结果到json文件中"""

    def __init__(self):
        super(CustomJsonPipeline, self).__init__()
        self.file = codecs.open('wx_btc.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        self.file.write(json.dumps(dict(item), ensure_ascii=False) + '\n')
        return item

    def close_spider(self, spider):
        self.file.close()
