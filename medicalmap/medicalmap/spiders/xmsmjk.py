# -*- coding: utf-8 -*-
import re
import scrapy
from re import S
from urllib.parse import urljoin
from w3lib.html import remove_tags
from scrapy.http import Request, FormRequest
from scrapy.loader.processors import MapCompose
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, get_county2, match_special, match_special2, \
    clean_info, clean_info2, now_year


class XmsmjkSpider(scrapy.Spider):
    name = 'xmsmjk'
    allowed_domains = ['xmsmjk.com']
    start_urls = ['http://www.xmsmjk.com/urponline']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.xmsmjk.com',
        'Referer': 'http://www.xmsmjk.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': random.randint(1, 2),
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 16.0,
        'AUTOTHROTTLE_DEBUG': True,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 100
    }
    host = 'http://www.xmsmjk.com'

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        try:
            all_hospital_links = response.xpath('//table[@class="tab"]/tbody/tr')
            for each_hospital_link in all_hospital_links:
                hospital_link = each_hospital_link.xpath('td[1]/b/a/@href').extract_first('')
                hospital_level = each_hospital_link.xpath('td[2]/p/span/text()').extract_first('')
                hospital_name = each_hospital_link.xpath('td[2]/h2/text()').extract_first('')
                all_doctor_links = each_hospital_link.xpath('td[3]/p/span/a'
                                                            '[contains(text(),"查看医生")]/@href').extract_first('')
                # 获取医院信息
                if hospital_link:
                    hospital_link = urljoin(self.host, hospital_link)
                    self.headers.update({
                        'Referer': response.url,
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'http://www.nt12320.cn'
                    })
                    yield Request(hospital_link,
                                  headers=self.headers,
                                  callback=self.parse_hospital_info,
                                  meta={'hospital_level': hospital_level},
                                  dont_filter=True)

                # 获取医生信息
                if all_doctor_links:
                    all_doctor_links = urljoin(self.host, all_doctor_links)
                    self.headers['Referer'] = response.url
                    yield Request(all_doctor_links,
                                  headers=self.headers,
                                  callback=self.parse_doctor_info,
                                  meta={'hospital_name': hospital_name},
                                  dont_filter=True)

            # 医院翻页
            next_page_number = response.xpath('//div[@id="fenye"]/'
                                              'a[contains(text(),"下一页")]/@href').extract_first('')
            now_page_number = response.xpath('//div[@id="fenye"]/a[@class="fenye_num_s"]/text()').extract_first('')
            if next_page_number and now_page_number:
                next_page_number = str(re.search(r'(\d+)', next_page_number).group(1))
                data = {
                    'currentpage': next_page_number,
                    'hoslevel': '',
                    'hosname': '',
                    'hostype': '',
                    'selectPage': now_page_number
                }
                self.headers['Referer'] = response.url
                yield FormRequest(self.search_hos_url,
                                  formdata=data,
                                  headers=self.headers,
                                  callback=self.parse,
                                  dont_filter=True)
        except Exception as e:
            self.logger.error('在抓取医院信息的过程中出错了,原因是：{}'.format(repr(e)))
