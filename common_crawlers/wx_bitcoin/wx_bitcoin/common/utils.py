# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/5/5 17:12'
# @email = 'fengh@asto-inc.com'
import re


def get_keyword(value):
    """返回链接中查询的关键词"""
    value = re.search(r'query=(.*?)&', value)
    if value:
        return value.group(1)
    else:
        return 'unknown'
