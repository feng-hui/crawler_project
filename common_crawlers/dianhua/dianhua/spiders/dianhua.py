#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-6-9 下午5:12
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import os
import time
import requests
from lxml import etree
from urllib.parse import urljoin, urlencode
from selenium import webdriver


class DianHuaBang(object):

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'm.dianhua.cn',
        'Upgrade-Insecure-Requests': '1',
        'Referer': "https://m.dianhua.cn/mianyang/c16/p5?apikey=wap",
        'Cookie': '_ga=GA1.2.2050639837.1528421351; _gid=GA1.2.1277505859.1528618861; nid=T6vu+ckqvUXts+Eq9RB1TFAZEfE=; PHPSESSID=cajh9pp28f7qnddjrfg0g67015; Hm_lvt_c136e57774590cd52d5e684e6421f853=1528421351,1528460267,1528618861,1528697614; Hm_lvt_824f91d3a04800a1d320314f2fd53aad=1528361141,1528421618,1528460550,1528697819; Hm_lpvt_824f91d3a04800a1d320314f2fd53aad=1528698374; temcity=mianyang; city_id=73; city_name=%E7%BB%B5%E9%98%B3; Hm_lpvt_c136e57774590cd52d5e684e6421f853=1528699666; accesstoken=d041602c827b440b8431520f1e85230b5630977d; accessseed=16323002',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 '
                      '(KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
    }
    cookies = {
        'eccaa0c8b712b90a76c71ee4361db60b': 'p3o%3D',
        '_ga': 'GA1.2.2050639837.1528421351',
        '_gid': 'GA1.2.1161884930.1528421351',
        'Hm_lvt_c136e57774590cd52d5e684e6421f853': '1528421351,1528460267',
        'temcity': 'beijing',
        'city_id': '2',
        'city_name': '%E5%8C%97%E4%BA%AC',
        '902c6a917f61496b91edd92dc420be53': 'lw%3D%3D',
        'b93b21ff05a24fc7394f8156e7134afe': 'SrzMRR4O',
        '845615558499036799eb17494f2ffb21': 'p5Wey83QyA%3D%3D',
        'be1fbbb1d015aeb570a196bf7ef24e9f': 'lg%3D%3D',
        '86e7646b4bc0edc61575805946d49c42': 'p3o%3D',
        'nid': 'qdPf5eH2VVLaV2lyT+c2T1iUOmI=',
        'Hm_lvt_576991240afaa91ac2b98111144c3a1a': '1528360077,1528420562,1528460233,1528530385',
        'PHPSESSID': 'bu1e2af5tkbcsqv2iq463foa01',
        'accesstoken': '9ed9c0812973a3ec2ad3909aa455b5e3e9f52c1a',
        'accessseed': '26639311',
        'Hm_lpvt_576991240afaa91ac2b98111144c3a1a': '1528536416'
    }
    test_url = 'https://www.dianhua.cn/beijing/c16'
    test_url2 = 'https://www.dianhua.cn/beijing/c16/p3'
    test_url3 = 'https://m.dianhua.cn/mianyang/c16/p3?apikey=wap'
    host = 'https://www.dianhua.cn'
    auth_code_url = 'https://www.dianhua.cn/auth/code.php?'
    session = requests.Session()

    def get_http_status(self, url):
        """判断状态码，如果为401表示有验证码，否则正常"""
        http_status = self.session.get(url, headers=self.headers).status_code
        if http_status == 401:
            return False
        else:
            return True

    def get_html(self, url):
        """获取页面源代码"""
        return self.session.get(url, headers=self.headers).content.decode()

    def run(self, url):
        if not self.get_http_status(url):
            print('有验证码……')
            content = self.get_html(url)
            sel = etree.HTML(content)
            captcha = sel.xpath('//img[@id="captcha"]/@src')
            if captcha:
                captcha_link = urljoin(self.host, captcha[0]).replace('htpps', 'http')
                # print(captcha_link)
                # print(requests.get(captcha_link, headers=self.headers).status_code)
                image_con = requests.get(captcha_link, headers=self.headers).content
                image_path = os.path.join(os.path.dirname(__file__), 'captcha.jpeg')
                with open(image_path, 'wb') as f:
                    f.write(image_con)
                captcha_value = input('请在15内输入验证码：')
                self.post_auth_code(captcha_value)
                # print(self.get_html(url))
        else:
            print('没有验证码……')
            print(self.get_html(url))

    def post_auth_code(self, code):
        print('开始处理验证码')
        # data = {
        #     'code': code
        # }
        # print(self.auth_code_url + urlencode({'code': code}))
        html = self.session.get(
            self.auth_code_url + urlencode({'code': code}),
            headers=self.headers
        )
        time.sleep(10)
        # print(html.content.decode())
        print(html.status_code)
        # print(html.headers['location'])
        # print(self.run(self.test_url2))
        print(self.session.cookies)
        print(html.content.decode())

    def run2(self, url):
        driver = webdriver.Chrome()
        driver.get(url)
        import time
        time.sleep(20)
        print(driver.page_source)
        # cookies = driver.get_cookies()
        cookies = [(item['name'], item['value']) for item in driver.get_cookies()]
        # print(cookies)
        # cookies = ';'.join(cookies)
        dhb_cookies = {name: value for name, value in cookies}
        print(dhb_cookies)
        self.session.cookies.update(dhb_cookies)
        print(self.session.get('https://m.dianhua.cn/beijing/c16/p2?apikey=wap'))


if __name__ == "__main__":
    dhb = DianHuaBang()
    dhb.run(dhb.test_url3)
