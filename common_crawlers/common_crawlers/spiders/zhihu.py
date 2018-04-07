# -*- coding: utf-8 -*-
import time
import scrapy
import hmac
import json
from scrapy.http import Request, FormRequest


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    login_url = "https://www.zhihu.com/signup"
    login_url2 = "https://www.zhihu.com/api/v3/oauth/sign_in"
    test_url = "https://www.zhihu.com/inbox"
    host_url = "https://www.zhihu.com/"
    captcha_url = "https://www.zhihu.com/api/v3/oauth/captcha?lang=en"
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    headers = {
        'authorization': 'oauth {}'.format(client_id),
        'host': 'www.zhihu.com',
        'origin': 'https://www.zhihu.com',
        'refer': 'https://www.zhihu.com/signup?next=%2F',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
    }
    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 1.5
    }

    def parse(self, response):
        self.logger.info(response.text)

    def get_signature(self, grant_type, source, timestamp):
        """获取签名"""
        r = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod='sha1')
        r.update(grant_type.encode('utf-8'))
        r.update(self.client_id.encode('utf-8'))
        r.update(source.encode('utf-8'))
        r.update(timestamp.encode('utf-8'))
        signature = r.hexdigest()
        return signature

    def start_requests(self):
        """请求开始"""
        yield Request(self.captcha_url, headers=self.headers, callback=self.to_login)

    def to_login(self, response):
        """登录"""
        show_captcha = json.loads(response.body.decode('utf-8'))
        # self.logger.info(show_captcha)
        grant_type = 'password'
        timestamp = str(int(time.time() * 1000))
        source = 'com.zhihu.web'
        username = '18610379194'
        password = 'tuyue7208562'
        try:
            is_show_captcha = show_captcha['show_captcha']
            if not is_show_captcha:
                # 不显示验证码
                params = {
                    'client_id': self.client_id,
                    'grant_type': grant_type,
                    'timestamp': timestamp,
                    'source': source,
                    'signature': self.get_signature(grant_type, source, timestamp),
                    'username': username,
                    'password': password,
                    'captcha': '',
                    'lang': 'en',
                    'ref_source': 'homepage',
                    'utm_source': ''
                }
                yield FormRequest(self.login_url2, headers=self.headers, formdata=params, method='POST',
                                  callback=self.is_login)
            else:
                # 需要验证码
                pass
        except KeyError:
            # client id 过期或其他原因
            self.logger.error(show_captcha['error']['message'])

    def is_login(self, response):
        """检测是否登录成功"""
        # login_json = json.loads(response.text)
        # print(login_json)
        for url in self.start_urls:
            yield Request(url, headers=self.headers)
