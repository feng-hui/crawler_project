# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
# from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from amazon.items import AmazonItem


class HuaweiSpider(scrapy.Spider):
    name = 'huawei'
    allowed_domains = ['amazon.cn']
    start_urls = [
        # 'https://www.amazon.cn/s/ref=nb_sb_noss?__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%99&'
        # 'url=search-alias%3Delectronics&field-keywords=%E5%8D%8E%E4%B8%BA&rh=n%3A2016116051%2Ck%3A%E5%8D%8E%E4%B8%BA',
        'https://www.amazon.cn/s/ref=sr_pg_2?rh=n%3A2016116051%2Ck%3A%E5%8D%8E%E4%B8%BA&page={}&'
        'keywords=%E5%8D%8E%E4%B8%BA&ie=UTF8&qid=1527834626'.format(str(each_page)) for each_page in range(1, 53)
    ]
    host = 'https://www.amazon.cn'
    headers = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'zh-CN,zh;q=0.9',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      'Cookie': 'x-wl-uid=17XfG5DPp2fEcAljkwI3yQ4UaRXCFO4OAn3Qxc7y1F4HqhXv8oc8t7t6tl2/EAhGEN14K3c3s9B4=; '
                'session-id=457-7575037-0301321; ubid-acbcn=458-7930000-5256857; '
                'session-token="CKXvc9BWMIwVazbihmW9Fa+694zXy5T0G+SEsjTd+/BZ41ZeFOOjC+HYi64dhrQrnOzxBEVSBcF'
                'ZKBEiA9VbpwkqL89WchSEsBHICFlR+xQqRkrVcHBH98jZHCSCqchgGLM9uZhFFZVWHeEL0FYoqXkqI/z76mXcmswTE2Z6DwRmWgy'
                'hmrAKJKtW1xaFW6dfQEKQpfmqLWrMz+SFhXMZY9hx+73s1wSL90OLoaBLwRXq3gIkdnwuMg=="; '
                'session-id-time=2082729601l; '
                'csm-hit=tb:106N90SAQRW10FASCZYG+s-E0QZK02VPJN4XJJB8AZW|1527823424012&adb:adblk_no',
      'Host': 'www.amazon.cn',
      'Referer': 'https://www.amazon.cn/s/ref=nb_sb_noss?__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%'
                 '99&url=search-alias%3Delectronics&field-keywords=%E5%8D%8E%E4%B8%BA&rh=n%3A2016116051%2Ck%3A%E5'
                 '%8D%8E%E4%B8%BA',
      'Upgrade-Insecure-Requests': '1'
      # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      #               'Chrome/66.0.3359.181 Safari/537.36'
    }
    number = 1

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, callback=self.parse)

    def parse(self, response):
        all_electrics_links = response.xpath('//div[@class="a-section a-spacing-none a-inline-block '
                                             's-position-relative"]/a/@href').extract()
        for each_link in all_electrics_links:
            yield Request(each_link, callback=self.parse_detail, headers=self.headers)

        # next_page = response.xpath('//a[@id="pagnNextLink"]/@href')
        # if next_page:
        #     next_page_link = urljoin(self.host, next_page.extract_first())
        #     yield Request(next_page_link, callback=self.parse)

    def parse_detail(self, response):
        self.log('正在抓取的url为：{}'.format(response.url))
        self.log('正在抓取第{}条:'.format(str(self.number)))
        self.number += 1
        loader = ItemLoader(item=AmazonItem(), response=response)
        loader.add_xpath('title', '//span[@id="productTitle"]/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//span[@id="priceblock_ourprice"]/text()')
        loader.add_xpath('all_images_url', '//*[@id="landingImage"]/@data-a-dynamic-image')
        loader.add_xpath('details', '//*[@id="prodDetails"]/div[2]/div[1]/div/div[2]/div/div/table/tbody/tr/td/text()')
        loader.add_xpath('asin', '//*[@id="prodDetails"]/div[2]/div[2]/div[1]/div[2]/div/div/table/tbody/tr[1]/'
                                 'td[2]/text()')
        loader.add_xpath('comments', '//span[@data-hook="total-review-count"]/text()')
        loader.add_xpath('stars', '//span[@data-hook="rating-out-of-text"]/text()')
        product_item = loader.load_item()
        yield product_item
