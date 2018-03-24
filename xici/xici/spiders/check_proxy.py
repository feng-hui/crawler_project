# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/3/23 15:43'
# @email = 'fengh@asto-inc.com'
import requests
import telnetlib
import pymongo


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
    def check2(ip, port):
        try:
            telnetlib.Telnet(ip, port=port, timeout=5)
        except:
            print('failed')
        else:
            print('success')

    def get_ip(self):
        client = pymongo.MongoClient(host='192.168.2.4', port=27017)
        db = client['richangts']
        doc = db['a66ip']
        one_record = doc.find()
        for each_record in one_record[0:30]:
            print(each_record)
            ip = each_record['ip']
            port = each_record['port']
            style = each_record['style'].lower()
            ip_dict = {'{}'.format(style): '{}://{}:{}'.format(style, ip, port)}
            timestamp = each_record['_id']
            # print(ip_dict)
            self.check2(ip, port)


if __name__ == "__main__":
    check_proxy = CheckProxy()
    # check_proxy.check2()
    check_proxy.get_ip()