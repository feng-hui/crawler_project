#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-7-5 上午10:16
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import datetime
import re
from re import S


def now_year():
    """返回当前日期的年份"""
    return datetime.datetime.now().strftime('%Y')


def now_day():
    """返回当前日期的年月日"""
    return datetime.datetime.now().strftime('%Y-%m-%d')


def get_doctor_intro(value):
    """
    返回医生简介和医生擅长的信息,
    适用于金堂县第一人民医院获取医生擅长的信息可用
    """
    res = re.search(r'简介：(.*?)$', value, S)
    if res:
        return res.group(1)
    else:
        return ''


def custom_remove_tags(value):
    """正则表达式去除\n\t\r等相关字符"""
    return ''.join(re.findall(r'\S', value, S)).strip()


def remove_number(value):
    """获取除数字以外的其他信息 方法1"""
    return ''.join(re.findall(r'[^\d+]', value))


def remove_number2(value):
    """获取除数字以外的其他信息 方法2"""
    return re.sub(r'\d+', '', value)


def clean_info(value):
    """去除字段值一些无用的信息"""
    return re.sub(r'null|--|none|\(|\)', '', value).strip()


def match_special(value):
    return value.split('：')[-1]


#
# if __name__ == "__main__":
#     print(remove_number('701'))
#     print(now_year(), type(now_year()))
#     print(now_day(), type(now_day()))
