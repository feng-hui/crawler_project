# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/5/8 9:44'
# @email = 'fengh@asto-inc.com'
import requests
import json
import time
import logging
logger = logging.getLogger(__name__)


class YunDaMa(object):
    """
    通过云打码网站,自动识别验证码
    云打码官方网站:http://www.yundama.com/
    """
    app_id = 4839
    app_key = "6f99e7dd7c531e5534ac2ed2f802b658"
    filename = "captcha.bmp"
    code_type = 1006
    timeout = 60
    captcha_url = "http://api.yundama.com/api.php?method=upload"
    captcha_result_url = "http://api.yundama.com/api.php?cid={}&method=result"

    def __init__(self, username, password):
        """
        实例化的时候获取云打码网站的账号密码
        """
        self.username = username
        self.password = password

    def get_captcha(self, filename):
        data = {
            'method': 'upload',
            'username': self.username,
            'password': self.password,
            'appid': self.app_id,
            'appkey': self.app_key,
            'codetype': self.code_type,
            'timeout': self.timeout
        }

        file = {'file': filename}
        response = requests.post(self.captcha_url, data, files=file).text
        response_dict = json.loads(response)
        result = response_dict['text']

        if result:
            return result
        else:
            cid = response_dict['cid']
            while self.timeout > 0:
                response = requests.post(
                    self.captcha_result_url.format(cid)).text
                response_dict = json.loads(response)
                print(response_dict, '还剩{}秒……'.format(self.timeout))
                captcha = response_dict['text']
                if captcha:
                    return captcha
                time.sleep(1)
                self.timeout -= 1
