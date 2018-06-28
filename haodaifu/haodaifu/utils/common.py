#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-6-18 下午3:29
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import re
from urllib.parse import urlparse


def get_host(value):
    """
    通过传进来的二级域名获得二级域名的名称
    例如:https://zgq0114.haodf.com/lanmu,返回zgq0114
    """
    value = re.search(r'//(.*?).haodf.com', value)
    if value:
        return value.group(1)
    else:
        return ''


def get_host2(value):
    """
    从域名中获取host
    例如：https://zgq0114.haodf.com/,返回值为zgq0114.haodf.com
    """
    value = re.search(r'https://(.*?)/', value)
    if value:
        return value.group(1)
    else:
        return ''


def get_host3(value):
    """
    从域名中获取host
    例如：https://zgq0114.haodf.com/,返回值为zgq0114.haodf.com
    改良版,可以通过urlparse函数来获取
    """
    res = urlparse(value)
    return res


# if __name__ == "__main__":
#     print(get_host('https://zgq0114.haodf.com/lanmu'))
