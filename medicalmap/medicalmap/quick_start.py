#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-7-5 上午11:10
# @author : Feng_Hui
# @email  : capricorn1203@126.com
from scrapy.cmdline import execute
# execute('scrapy crawl jintangyy'.split())  # 金堂县第一人民医院
# execute('scrapy crawl pxfybjy'.split())  # 郫县妇幼保健院
# execute('scrapy crawl yihu'.split())  # 健康之路,预约挂号入口
# execute('scrapy crawl yihu3'.split())  # 健康之路,使用scrapy splash获取医生排班信息
# execute('scrapy crawl scgh114'.split())  # 114挂号
# execute('scrapy crawl djydermyy'.split())  # 都江堰市第二人民医院
# execute('scrapy crawl scslzyyy'.split())  # 双流区中医医院
# execute('scrapy crawl qbjzyy'.split())  # 成都市青白江区中医医院
# execute('scrapy crawl cdcj120'.split())  # 成都长江医院
# execute('scrapy crawl pdqzyyy'.split())  # 郫县中医医院
execute('scrapy crawl wjykyy'.split())  # 绵阳万江眼科医院
