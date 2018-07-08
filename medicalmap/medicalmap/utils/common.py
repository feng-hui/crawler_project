#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-7-5 上午10:16
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import datetime
import re
from re import S


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


# if __name__ == "__main__":
#     print(now_day())
