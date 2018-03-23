# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/3/23 15:43'
# @email = 'fengh@asto-inc.com'
import requests
import telnetlib


class CheckProxy(object):

    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 '
                             '(KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1'}
    test_url = "https://www.baidu.com/"
    proxies = {
        'http': 'http://122.114.31.177:808'
    }

    def get_html(self):
        html = requests.get(self.test_url, headers=self.headers, proxies=self.proxies)
        return html

    def check(self):
        html = self.get_html()
        status = html.status_code
        print(html.text)
        print(status)

    @staticmethod
    def check2():
        try:
            telnetlib.Telnet('110.73.33.3', port='8123', timeout=10)
        except:
            print('failed')
        else:
            print('success')


if __name__ == "__main__":
    check_proxy = CheckProxy()
    check_proxy.check2()