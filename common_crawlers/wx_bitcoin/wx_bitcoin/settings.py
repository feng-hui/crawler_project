# -*- coding: utf-8 -*-
import random

# Scrapy settings for wx_bitcoin project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'wx_bitcoin'

SPIDER_MODULES = ['wx_bitcoin.spiders']
NEWSPIDER_MODULE = 'wx_bitcoin.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'wx_bitcoin (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = random.randint(1, 5)
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Encoding': 'gzip, deflate',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Connection': 'keep-alive',
  'Host': 'weixin.sogou.com',
  'Referer': 'http://weixin.sogou.com/weixin?query=btc&_sug_type_=&s_from=input&_sug_=n&type=2&page=9&ie=utf8',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) '
                'Version/9.0 Mobile/13B143 Safari/601.1',
  'Cookie': 'SMYUV=1493633115778785; SUV=1519382100527513; SUID=AD152EDE3965860A58FB519000069DC2; '
            'LSTMV=227%2C78; LCLKINT=3722; sct=6; CXID=6D0E8521D589DCBA1F90B71B02BDAF18; usid=PZLCSvduA49NEEtR; '
            'wuid=AAFHX7B/IAAAAAqLE2Nv2gsAQAU=; ad=flllllllll2zdpsHlllllV7Y@Xllllll5a4$dkllllwlllllxCxlw@@@@@@@@@@@; '
            'ABTEST=0|1528375734|v1; SNUID=96B692245752395AE395B82D57F77E41; IPLOC=CN3301; '
            'JSESSIONID=aaaUd-nHS8fUzcw4dqknw'
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'wx_bitcoin.middlewares.WxBitcoinSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    # 'wx_bitcoin.middlewares.UserAgentMiddleWare': 542,
#    'wx_bitcoin.middlewares.ProxyMiddleWare': 543,
#    # 'wx_bitcoin.middlewares.WxRedirectMiddleWare': 543
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'wx_bitcoin.pipelines.CustomJsonPipeline': 300,
# }

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
# USER_AGENT_LIST = [
#     'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) '
#     'Version/9.0 Mobile/13B143 Safari/601.1'
# ]
