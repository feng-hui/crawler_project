# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from scrapy.http import Request
from urllib.parse import urljoin
from scrapy.exceptions import IgnoreRequest
from scrapy.loader.processors import MapCompose
from haodaifu.utils.search_keywords import all_personal_websites
from haodaifu.items import HdfPersonalWebsiteItem, DoctorArticleItemLoader
from haodaifu.utils.common import get_host3, now_day, clean_info, clean_info2


class PersonalWebsiteSpider(scrapy.Spider):
    """
    抓取好大夫医生个人网站相关信息
    URL参考:https://tianjiangbo.haodf.com/
    """
    name = 'personal_website'
    allowed_domains = ['haodf.com']
    start_urls = []
    ignored_urls = []
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 1,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 100
    }
    headers = {}

    def start_requests(self):
        for each_kw in all_personal_websites:
            personal_website = '{0}{1}{2}'.format('https://', each_kw['hdf_id'], '.haodf.com')
            self.start_urls.append(personal_website)
        for each_url in self.start_urls:
            self.headers['Referer'] = urljoin(each_url, 'lanmu')
            self.headers['Host'] = get_host3(each_url)
            request = Request(each_url,
                              headers=self.headers,
                              callback=self.parse,
                              errback=self.err_collector,
                              dont_filter=True)
            yield request

    def parse(self, response):
        """
        获取好大夫网站上医生相关信息
        """
        try:
            self.logger.info('正在抓取的医生个人主页的url是{}:'.format(response.url))
            status_code = response.status
            if status_code == 200:
                doctor_name = response.xpath('//a[@class="space_b_link_url"]/'
                                             'text()').extract_first('').replace('大夫的个人网站', '')
                doctor_level = response.xpath('//h3[@class="doc_name f22 fl"]/'
                                              'text()').extract_first('').replace(doctor_name, '')
                doctor_level2 = clean_info(doctor_level)
                doctor_level = doctor_level2 if doctor_level2 else doctor_level
                loader = DoctorArticleItemLoader(item=HdfPersonalWebsiteItem(), response=response)
                loader.add_value('doctor_hid', get_host3(response.url).split('.')[0])
                loader.add_value('personal_website', response.url)
                loader.add_xpath('doctor_hos', '//div[@class="fl pr"]/p/a[1]/text()')
                loader.add_xpath('doctor_dep', '//div[@class="fl pr"]/p/a[2]/text()')
                loader.add_value('doctor_level', doctor_level, MapCompose(clean_info2))
                loader.add_value('crawl_time', now_day())
                loader.add_value('update_time', now_day())
                item = loader.load_item()
                yield item
            elif status_code == 301:
                location_url = response.url.headers.get('location')
                self.logger.info('该医生页面发生跳转,跳转后的url为:{}'.format(location_url))
                loader = DoctorArticleItemLoader(item=HdfPersonalWebsiteItem(), response=response)
                loader.add_value('doctor_hid', get_host3(response.url).split('.')[0])
                loader.add_value('personal_website', response.url)
                # loader.add_xpath('doctor_hos', '//div[@class="fl pr"]/p/a[1]/text()')
                # loader.add_xpath('doctor_dep', '//div[@class="fl pr"]/p/a[2]/text()')
                # loader.add_value('doctor_level', doctor_level, MapCompose(clean_info2))
                loader.add_value('crawl_time', now_day())
                loader.add_value('update_time', now_day())
                loader.add_value('location_url', location_url)
                item = loader.load_item()
                yield item
            else:
                pass
        except Exception as e:
            self.logger.error('>>>>>>在抓取医生个人主页过程中出错了,原因是：{}'.format(repr(e)))

    def err_collector(self, failure):
        """错误收集"""
        self.logger.error('发生错误的原因是:{}'.format(repr(failure)))
        try:
            if failure.check(IgnoreRequest):
                self.logger.info('错误的类型为:IgnoreRequest')
                response = failure.value.response
                failure_url = response.url
                self.ignored_urls.append(failure_url)
                self.crawler.signals.connect(self.deal_error, signals.spider_closed)
        except Exception as e:
            self.logger.error('收集错误的过程发生错误,原因是:{}'.format(repr(e)))

    def deal_error(self):
        """
        爬虫结束的时候,输出所有被忽略的url
        """
        self.crawler.stats.set_value('ignored_urls/all_ignored_urls_list', ','.join(self.ignored_urls))
        self.crawler.stats.set_value('ignored_urls/count', len(self.ignored_urls))
