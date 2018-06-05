# -*- coding: utf-8 -*-
import random

# Scrapy settings for amazon project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'amazon'

SPIDER_MODULES = ['amazon.spiders']
NEWSPIDER_MODULE = 'amazon.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'amazon (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/66.0.3359.181 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = random.randint(1, 3)
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#   'Accept-Encoding': 'gzip, deflate, br',
#   'Accept-Language': 'zh-CN,zh;q=0.9',
#   'Cache-Control': 'max-age=0',
#   'Connection': 'keep-alive',
#   'Cookie': 'x-wl-uid=17XfG5DPp2fEcAljkwI3yQ4UaRXCFO4OAn3Qxc7y1F4HqhXv8oc8t7t6tl2/EAhGEN14K3c3s9B4=; '
#             'session-id=457-7575037-0301321; ubid-acbcn=458-7930000-5256857; '
#             'session-token="CKXvc9BWMIwVazbihmW9Fa+694zXy5T0G+SEsjTd+/BZ41ZeFOOjC+HYi64dhrQrnOzxBEVSBcF'
#             'ZKBEiA9VbpwkqL89WchSEsBHICFlR+xQqRkrVcHBH98jZHCSCqchgGLM9uZhFFZVWHeEL0FYoqXkqI/z76mXcmswTE2Z6DwRmWgy'
#             'hmrAKJKtW1xaFW6dfQEKQpfmqLWrMz+SFhXMZY9hx+73s1wSL90OLoaBLwRXq3gIkdnwuMg=="; '
#             'session-id-time=2082729601l; '
#             'csm-hit=tb:106N90SAQRW10FASCZYG+s-E0QZK02VPJN4XJJB8AZW|1527823424012&adb:adblk_no',
#   'Host': 'www.amazon.cn',
#   'Referer': 'https://www.amazon.cn/s/ref=nb_sb_noss?__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%'
#              '99&url=search-alias%3Delectronics&field-keywords=%E5%8D%8E%E4%B8%BA&rh=n%3A2016116051%2Ck%3A%E5'
#              '%8D%8E%E4%B8%BA',
#   'Upgrade-Insecure-Requests': '1'
#   # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
#   #               'Chrome/66.0.3359.181 Safari/537.36'
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'amazon.middlewares.AmazonSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'amazon.middlewares.ProxyMiddleWare': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'amazon.pipelines.AmazonPipeline': 300,
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
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'amazon'
MONGO_DOC = 'huawei3'