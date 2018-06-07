# -*- coding: utf-8 -*-
import scrapy
import datetime
from wx_bitcoin.items import WxBitcoinItem, WxBtcItemLoader
# from scrapy.http.request import Request
from wx_bitcoin.common.utils import get_keyword


class WxBtcSpider(scrapy.Spider):
    name = 'wx_btc'
    allowed_domains = ['sogou.com']
    start_urls = [
        'http://weixin.sogou.com/weixin?query={}&_sug_type_=&s_from=input&_sug_=n&type=2&page={}&ie=utf8'.format(
            each_keyword, str(each_page)) for each_keyword in ['btc', 'eth', 'eos'] for each_page in range(1, 101)
    ]
    host_url = "http://weixin.sogou.com/weixin"
    # handle_httpstatus_list = [301, 302, 303, 307, 308]

    def parse(self, response):
        self.logger.info('正在抓取的链接为：{}'.format(response.url))
        keyword = get_keyword(response.url)
        data_list = response.xpath('//ul[@class="news-list"]/li')
        # print(data_list)
        for each_data in data_list:
            wx_item = WxBtcItemLoader(item=WxBitcoinItem(), selector=each_data)
            wx_item.add_xpath('title', 'div[@class="txt-box"]/h3/a')
            wx_item.add_xpath('link', 'div[@class="txt-box"]/h3/a/@href')
            wx_item.add_xpath('author', 'div[@class="txt-box"]/div/a/text()')
            wx_item.add_value('keyword', keyword)
            wx_item.add_value('crawl_time', datetime.datetime.now())
            yield wx_item.load_item()

        # 下一页,未登录获取前10页数据
        # next_page = response.xpath('//a[@id="sogou_next"]/@href')
        # if next_page:
        #     next_page_url = self.host_url + next_page.extract_first()
        #     yield Request(next_page_url, callback=self.parse)
