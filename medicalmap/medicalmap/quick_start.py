#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-7-5 上午11:10
# @author : Feng_Hui
# @email  : capricorn1203@126.com
from scrapy.cmdline import execute
# execute('scrapy crawl jintangyy'.split())  # 金堂县第一人民医院
# execute('scrapy crawl pxfybjy'.split())  # 郫县妇幼保健院
# execute('scrapy crawl yihu'.split())  # 健康之路,预约挂号入口
execute('scrapy crawl yihu2'.split())  # 健康之路,咨询医生入口
# execute('scrapy crawl scgh114'.split())  # 114挂号
