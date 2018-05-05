#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-5-3 上午12:02
# @author : Feng_Hui
# @email  : capricorn1203@126.com
from scrapy.cmdline import execute
execute("scrapy crawl wx_btc".split())
# execute("scrapy crawl wx_btc -o wx_btc.csv -t csv".split())
