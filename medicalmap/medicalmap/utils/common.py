#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-7-5 上午10:16
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import datetime


def now_day():
    """返回当前日期的年月日"""
    return datetime.datetime.now().strftime('%Y-%m-%d')


# if __name__ == "__main__":
#     print(now_day())
