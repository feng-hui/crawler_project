# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from medicalmap.items import YiHuLoader, HospitalInfoItem, HospitalDepItem, DoctorInfoItem
from medicalmap.utils.common import now_day
from urllib.parse import urljoin


class Yihu2Spider(scrapy.Spider):
    """
    健康之路网站：成都、眉山、绵阳三个地市的数据
    入口：咨询医生
    """
    name = 'yihu2'
    allowed_domains = ['yihu.com']
    dept_links = ['https://www.yihu.com/zixun/3.shtml', 'https://www.yihu.com/zixun/4.shtml',
                  'https://www.yihu.com/zixun/5.shtml', 'https://www.yihu.com/zixun/80.shtml',
                  'https://www.yihu.com/zixun/11.shtml', 'https://www.yihu.com/zixun/12.shtml',
                  'https://www.yihu.com/zixun/10.shtml', 'https://www.yihu.com/zixun/19.shtml',
                  'https://www.yihu.com/zixun/13.shtml', 'https://www.yihu.com/zixun/50.shtml',
                  'https://www.yihu.com/zixun/16.shtml', 'https://www.yihu.com/zixun/54.shtml',
                  'https://www.yihu.com/zixun/27.shtml', 'https://www.yihu.com/zixun/14.shtml',
                  'https://www.yihu.com/zixun/21.shtml', 'https://www.yihu.com/zixun/52.shtml',
                  'https://www.yihu.com/zixun/15.shtml', 'https://www.yihu.com/zixun/81.shtml',
                  'https://www.yihu.com/zixun/78.shtml']
    start_urls = [urljoin(each_dept, '?provinceId=23&cityId=252&standardDeptId=0') for each_dept in dept_links]
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.yihu.com',
        'Referer': 'https://www.yihu.com/zixun/     ',
        'Upgrade-Insecure-Requests': '1',
        # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
        #               'Chrome/65.0.3325.181 Safari/537.36'
    }
    host = 'https://www.yihu.com'
    hospital_host = 'https://www.yihu.com/hospital/'
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 5,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 5.0,
        'AUTOTHROTTLE_DEBUG': False,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 32
    }
    crawled_ids = set()
    crawled_dept = set()

    def start_requests(self):
        for each_url in self.start_urls:
            yield Request(each_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        """获取医生信息"""
        self.logger.info('>>>>>>正在抓取医生信息……')
        all_doctor_links = response.xpath('//div[@class="pt20 pb20 border-f2 c-hidden"]/a/@href').extract()
        self.logger.info('>>>>>>该页面共有{}个医生'.format(str(len(all_doctor_links))))
        if all_doctor_links:
            for each_doctor_link in all_doctor_links:
                doctor_request = Request(each_doctor_link, headers=self.headers, callback=self.parse_doctor_website)
                doctor_request.meta['Referer'] = each_doctor_link
                yield doctor_request
        # 咨询医生页面翻页
        next_page = response.xpath('//a[@class="page-next"]/@href').extract_first('')
        if next_page:
            next_page_link = urljoin(self.host, next_page)
            next_page_request = Request(next_page_link, headers=self.headers, callback=self.parse)
            next_page_request.meta['Referer'] = response.url
            yield next_page_request

    def parse_doctor_website(self, response):
        self.logger.info('>>>>>>正在抓取医生个人主页相关信息……')
        # 获取医生相关信息
        loader = YiHuLoader(item=DoctorInfoItem(), response=response)
        loader.add_xpath('doctor_name', '//span[@class="c-f22 c-333"]/text()')
        loader.add_xpath('dept_name', '//div[@class="doctor-info"]/dl/dd[2]/a[2]/text()')
        loader.add_xpath('hospital_name', '//div[@class="doctor-info"]/dl/dd[2]/a[1]/text()')
        loader.add_xpath('doctor_level', '//div[@class="doctor-info"]/dl/dd[1]/text()')
        loader.add_xpath('doctor_intro', '//table[@class="pop-myinfo-tb"]/tr[@class="last"]/td/p/text()')
        loader.add_xpath('doctor_goodAt', '//table[@class="pop-myinfo-tb"]/tr[5]/td/text()')
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item
        # 获取医院相关信息
        hos_link = response.xpath('//div[@class="doctor-info"]/dl/dd[2]/a[1]/@href').extract_first('')
        dept_link = response.xpath('//div[@class="doctor-info"]/dl/dd[2]/a[2]/@href').extract_first('')
        # 抓取医院详细信息
        if hos_link:
            hos_id = re.search(r'/sc/(.*?).shtml', hos_link)
            if hos_id and hos_id.group(1) not in self.crawled_ids:
                self.crawled_ids.add(hos_id.group(1))
                hos_intro_link = re.sub(r'/sc/', '/detail/', hos_link)
                hos_con_link = re.sub(r'/sc/', '/contact/', hos_link)
                hos_loader = YiHuLoader(item=HospitalInfoItem(), response=response)
                hos_loader.add_xpath('hospital_name', '//div[@class="doctor-info"]/dl/dd[2]/a[1]/text()')
                hospital_detail_request = Request(hos_intro_link,
                                                  headers=self.headers,
                                                  callback=self.parse_hospital_detail,
                                                  meta={'loader': hos_loader,
                                                        'contact_hos_link': hos_con_link})
                hospital_detail_request.meta['Referer'] = response.url
                yield hospital_detail_request
        # 存储科室信息
        if dept_link:
            dept_link_id = re.search(r'/arrange/(.*?).shtml', dept_link)
            if dept_link_id and dept_link_id.group(1) not in self.crawled_dept:
                self.crawled_dept.add(dept_link_id.group(1))
                dept_loader = YiHuLoader(item=HospitalDepItem(), response=response)
                dept_loader.add_xpath('dept_name', '//div[@class="doctor-info"]/dl/dd[2]/a[2]/text()')
                dept_loader.add_xpath('hospital_name', '//div[@class="doctor-info"]/dl/dd[2]/a[1]/text()')
                dept_loader.add_value('update_time', now_day())
                dept_item = dept_loader.load_item()
                yield dept_item

    def parse_hospital_detail(self, response):
        self.logger.info('>>>>>>正在抓取医院概况……')
        loader = response.meta['loader']
        contact_hos_link = response.meta['contact_hos_link']
        hospital_intro = response.xpath('//div[@class="section-con"]').extract_first('')
        loader.add_value('hospital_intro', hospital_intro)
        contact_hos_request = Request(contact_hos_link,
                                      headers=self.headers,
                                      callback=self.parse_hospital_contact,
                                      meta={'loader': loader})
        self.headers['Referer'] = response.url
        yield contact_hos_request

    def parse_hospital_contact(self, response):
        self.logger.info('>>>>>>正在抓取医院联系方式……')
        loader = response.meta['loader']
        hospital_address = response.xpath('//div[@class="section sec-article"]/div[2]/div/table/tr/'
                                          'td[2]/text()').extract_first('')
        hospital_phone = response.xpath('//div[@class="section sec-article"]/div[2]/div/table/tr/'
                                        'td[4]/text()').extract_first('')
        loader.add_value('hospital_addr', hospital_address)
        loader.add_value('hospital_pro', '四川')
        loader.add_value('')
        loader.add_value('hospital_phone', hospital_phone)
        loader.add_value('dataSource_from', '健康之路')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        yield hospital_info_item
