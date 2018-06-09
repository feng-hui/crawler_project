#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-6-9 下午8:28
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import requests


class LoginZhiHu(object):
    """使用已经登录的cookies信息来登录知乎"""

    headers = {
        'cookie': '_zap=b7f51755-8946-4ebd-85f1-fd374cd6c3ee; '
                   '__DAYU_PP=ZZY2EffFbf76EjM7rJaa2bfb790a4855; '
                   'z_c0="2|1:0|10:1523097519|4:z_c0|92:Mi4xLVhrckF3QUFBQUFBd0s5NHFmRm5EU1lBQUFCZ0FsVk5y'
                   'LTIxV3dEdFh5OERVSWV5UGtYNzhUOG0wRzJhZ1dGamZn|85c82184adec4e4eae16614268cc083c21ad8e04'
                   '19a2edf9c0b46eb0890b71a4"; __utma=155987696.1627079064.1523103719.1523103719.1523103719.1; '
                   '__utmz=155987696.1523103719.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); '
                   'q_c1=9bafa6f719af4c24ba286827377e51bc|1526015374000|1519307988000; '
                   'd_c0="AIDiJBQSog2PTiaNcQqLVJQjqf6vS_JGHjk=|1526994674"; '
                   'tgw_l7_route=e0a07617c1a38385364125951b19eef8; _xsrf=5021fd07-2d96-4380-a47f-34db9ba7aa84',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    headers2 = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }
    cookies = {
        '_zap': 'b7f51755-8946-4ebd-85f1-fd374cd6c3ee',
        '__DAYU_PP': 'ZZY2EffFbf76EjM7rJaa2bfb790a4855',
        'z_c0': '"2|1:0|10:1523097519|4:z_c0|92:Mi4xLVhrckF3QUFBQUFBd0s5NHFmRm5EU1lBQUFCZ0FsVk5y'
        'LTIxV3dEdFh5OERVSWV5UGtYNzhUOG0wRzJhZ1dGamZn|85c82184adec4e4eae16614268cc083c21ad8e04'
        '19a2edf9c0b46eb0890b71a4"',
        '__utma': '155987696.1627079064.1523103719.1523103719.1523103719.1',
        '__utmz': '155987696.1523103719.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        'q_c1': '9bafa6f719af4c24ba286827377e51bc|1526015374000|1519307988000',
        'd_c0': '"AIDiJBQSog2PTiaNcQqLVJQjqf6vS_JGHjk=|1526994674"',
        'tgw_l7_route': 'e0a07617c1a38385364125951b19eef8',
        '_xsrf': '5021fd07-2d96-4380-a47f-34db9ba7aa84'
    }

    host = "https://www.zhihu.com/"

    def login(self):
        """通过headers参数来登录知乎"""
        return requests.get(self.host, headers=self.headers).content.decode()

    def login2(self):
        """通过cookies参数来登录知乎"""
        return requests.get(self.host, headers=self.headers2, cookies=self.cookies).content.decode()


if __name__ == "__main__":
    login_zhihu = LoginZhiHu()
    print(login_zhihu.login2())
