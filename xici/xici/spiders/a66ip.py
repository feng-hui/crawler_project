# -*- coding: utf-8 -*-
import re
import time
import scrapy
from xici.items import XiciItem


class A66ipSpider(scrapy.Spider):
    name = '66ip'
    allowed_domains = ['66ip.cn']
    start_urls = ['http://www.66ip.cn/{}.html'.format(_) for _ in ['index'] + list(range(2, 5))]
    urls_extent = ['http://www.66ip.cn/areaindex_{}/{}.html'.format(m, n)
                   for m in range(1, 35)
                   for n in range(1, 101)]
    start_urls.extend(urls_extent)

    def parse(self, response):
        selector = response.xpath('//table[@bordercolor="#6699ff"]/tr[position()>1]')
        item = XiciItem()
        for sel in selector:
            ip = sel.xpath('td[1]/text()').extract()
            port = sel.xpath('td[2]/text()').extract()
            address = sel.xpath('td[3]/text()').extract()
            status = sel.xpath('td[4]/text()').extract()
            style = ""
            v_time = sel.xpath('td[5]/text()').extract()
            # 检测当前正在抓取的ip的验证时间是否为今年
            if v_time and not self.validate_time(v_time[0]):
                continue
            item['ip'] = ip[0] if ip else ""
            item['port'] = port[0] if port else ""
            item['address'] = address[0] if address else ""
            item['status'] = status[0] if status else ""
            item['style'] = style
            yield item

    @staticmethod
    def validate_time(v_time):
        """检测当前抓取的ip的验证时间是否为今年"""
        year = re.search(r'\d+年', v_time)
        now_year = str(time.localtime().tm_year)
        if year:
            year = year.group().replace('年', '')
            if year == now_year:
                return True
            else:
                return False
        else:
            return False
