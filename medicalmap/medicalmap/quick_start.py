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
# execute('scrapy crawl djydermyy'.split())  # 都江堰市第二人民医院 2018-07-19
# execute('scrapy crawl qbjzyy'.split())  # 成都市青白江区中医医院 2018-07-23 医院+科室+医生+排班
# execute('scrapy crawl scslzyyy'.split())  # 双流区中医医院 2018-07-24
# execute('scrapy crawl cdcj120'.split())  # 成都长江医院 2018-07-25 医院+科室+医生+排班
# execute('scrapy crawl pdqzyyy'.split())  # 郫县中医医院 2018-07-25
# execute('scrapy crawl wjykyy'.split())  # 绵阳万江眼科医院 2018-07-26 医院+科室+医生+排班
# execute('scrapy crawl cdwhyy'.split())  # 成都市武侯区妇幼保健院  2018-07-26 医院+科室+医生+排班
# execute('scrapy crawl scpz120'.split())  # 彭州市中医医院  2018-07-27 医院+科室+医生+排班
# execute('scrapy crawl wjfy120'.split())  # 成都市温江区妇幼保健院  2018-07-30 医院+科室+医生
# execute('scrapy crawl slbjy'.split())  # 双流区妇幼保健院  2018-07-31 医院+科室+医生
# execute('scrapy crawl a_hospital'.split())  # 医学百科  2018-07-31 医院+科室+医院别名
# execute('scrapy crawl imicams'.split())  # 中国医院科技影响力排行  2018-08-07 排行信息
# execute('scrapy crawl hnyygh'.split())  # 湖南省统一预约挂号系统  2018-08-13 医院+科室+医生+排班
# execute('scrapy crawl nj12320'.split())  # 南京市统一预约挂号系统  2018-08-16 医院+科室+医生+排班
# execute('scrapy crawl sxyygh'.split())  # 山西省统一预约挂号系统  2018-08-17 医院+科室+医生+排班
execute('scrapy crawl guahao'.split())  # 广州市统一预约挂号系统  2018-08-22 医院+科室+医生+排班
