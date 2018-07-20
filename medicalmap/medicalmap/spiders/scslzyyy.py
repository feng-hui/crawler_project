# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from medicalmap.items import CommonLoader2, HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem
from medicalmap.utils.common import now_day, custom_remove_tags, match_special, get_reg_info
from urllib.parse import urljoin
from scrapy.loader.processors import MapCompose, Join
from w3lib.html import remove_tags


class ScslzyyySpider(scrapy.Spider):
    """
    双流区中医医院
    """
    name = 'scslzyyy'
    allowed_domains = ['scslzyyy.com']
    start_urls = ['http://scslzyyy.com/']
    doctor_link = 'http://www.scslzyyy.com/product.aspx?mid=71&sid='
    hospital_intro_link = 'http://www.scslzyyy.com/about.aspx?mid=17&sid='
    dept_link_list = ['http://www.scslzyyy.com/product.aspx?mid=19&page=1',
                      'http://www.scslzyyy.com/product.aspx?mid=19&page=2',
                      'http://www.scslzyyy.com/product.aspx?mid=19&page=3']
    hospital_name = '双流区中医医院'
    host = 'http://www.scslzyyy.com'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.scslzyyy.com',
        'Referer': 'http://www.scslzyyy.com/17.do',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }

    def parse(self, response):
        """获取医院信息"""
        self.logger.info('正在抓取{}:医院信息'.format(self.hospital_name))
        loader = CommonLoader2(item=HospitalInfoItem(), response=response)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_value('consulting_hour', '8:00-17:00')
        loader.add_value('hospital_level', '三级乙等')
        loader.add_value('hospital_type', '公立')
        loader.add_value('hospital_category', '中医医院')
        loader.add_value('hospital_addr', '成都市双流区东升街道花园路二段（新院）,淳化街205号（老院）')
        loader.add_value('hospital_pro', '四川省')
        loader.add_value('hospital_city', '成都市')
        loader.add_value('hospital_county', '')
        loader.add_value('hospital_phone', '预约电话_028-69803716;体检咨_028-85808932')
        loader.add_xpath('hospital_intro', '//div[@class="text"]', MapCompose(remove_tags))
        loader.add_value('registered_channel', '实名制电话预约、现场预约、自助机预约、诊间预约')
        loader.add_value('dataSource_from', '医院官网')
        loader.add_value('update_time', now_day())
        hospital_info_item = loader.load_item()
        # 医院信息
        yield hospital_info_item
        # 获取科室信息
        for each_dept_link in self.dept_link_list:
            dept_request = Request(each_dept_link,
                                   headers=self.headers,
                                   callback=self.parse_hospital_dep,
                                   dont_filter=True)
            dept_request.meta['Referer'] = response.url
            yield dept_request

    def parse_hospital_dep(self, response):
        dept_links = response.xpath('//ul[@class="product3"]/li')
        for each_dept_link in dept_links:
            dept_link = each_dept_link.xpath('div[2]/h1/a/@href').extract_first('')
            dept_name = each_dept_link.xpath('div[2]/h1/a/text()').extract_first('')
            if dept_link and dept_name:
                dept_request = Request(urljoin(self.host, dept_link),
                                       headers=self.headers,
                                       callback=self.parse_hospital_dep_detail,
                                       meta={'dept_name': dept_name})
                dept_request.meta['Referer'] = response.url
                yield dept_request

    def parse_hospital_dep_detail(self, response):
        dept_name = response.meta['dept_name']
        loader = CommonLoader2(item=HospitalDepItem(), response=response)
        loader.add_value('dept_name', dept_name)
        loader.add_value('hospital_name', self.hospital_name)
        loader.add_xpath('dept_info', '//div[@style="text-indent: 2em"]', MapCompose(remove_tags))
        loader.add_value('update_time', now_day())
        dept_item = loader.load_item()
        yield dept_item
