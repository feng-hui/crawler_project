# -*- coding: utf-8 -*-
import random

# Scrapy settings for dianhua project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'dianhua'

SPIDER_MODULES = ['dianhua.spiders']
NEWSPIDER_MODULE = 'dianhua.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'dianhua (+http://www.yourdomain.com)'
# USER_AGENT = 'Mozilla/5.0 (compatible;Baiduspider-render/2.0; +http://www.baidu.com/search/spider.html)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = random.randint(15, 30)
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = headers = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
   'Accept-Encoding': 'gzip, deflate, br',
   'Accept-Language': 'zh-CN,zh;q=0.9',
   'Connection': 'keep-alive',
   'Host': 'www.dianhua.cn',
   'Upgrade-Insecure-Requests': '1',
   # 'Referer': "http://www.dianhua.cn/beijing/c16/p1",
   'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 '
                '(KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
   'Cookie': '_ga=GA1.2.2050639837.1528421351; _gid=GA1.2.1277505859.1528618861; temcity=mianyang; city_id=73; city_name=%E7%BB%B5%E9%98%B3; PHPSESSID=75oghiv683ajm3qpe6uecub431; nid=qdPf5eH2VVLaV2lyT+c2T1iUOmI=; Hm_lvt_c136e57774590cd52d5e684e6421f853=1528460267,1528618861,1528697614,1528720247; Hm_lvt_824f91d3a04800a1d320314f2fd53aad=1528421618,1528460550,1528697819,1528720273; Hm_lpvt_824f91d3a04800a1d320314f2fd53aad=1528727685; _gat=1; accesstoken=21d7534246aa21b03fc331303d949f6c24c823c5; accessseed=83574137; Hm_lpvt_c136e57774590cd52d5e684e6421f853=1528727975'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'dianhua.middlewares.DianhuaSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'dianhua.middlewares.DianhuaDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'dianhua.pipelines.DianhuaPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
