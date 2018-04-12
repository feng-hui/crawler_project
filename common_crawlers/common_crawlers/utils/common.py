#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-4-1 上午11:53
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import re
import hashlib
import datetime
from datetime import datetime as dt


def get_md5(url):
    """字符串转换成md5格式"""
    if isinstance(url, str):
        url = url.encode(encoding='utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def get_number(values_text):
    """返回文本里的数值,默认获取过滤到的第一个数字"""
    values = re.search('(\d+)', values_text)
    if values:
        return values.group(1)
    else:
        return '0'


def standard_time(values_text):
    """获取文本字符串中的年月日,格式为：2018/01/01"""
    values = re.search('(\d{4}/\d{2}/\d{2})', values_text)
    if values:
        return datetime.datetime.strptime(values.group(1), '%Y/%m/%d').date()
    else:
        return datetime.datetime.now().date()


def timestamp_to_date(value):
    """时间戳转化字符串时间"""
    value = input(value) if isinstance(value, str) else value
    assert isinstance(value, int)
    return dt.strftime(dt.fromtimestamp(value), '%Y-%m-%d %H:%M:%S')


def now_time():
    """返回当前时间"""
    return datetime.datetime.now()


def str_to_int(value):
    """如139,99,88格式的数字转化为数字"""
    assert isinstance(value, str)
    return int(''.join(value.split(',')))


if __name__ == "__main__":
    # print(get_md5("http://jobbole.com"))
    print(timestamp_to_date(1520822831))