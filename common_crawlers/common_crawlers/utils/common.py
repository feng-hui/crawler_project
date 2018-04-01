#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-4-1 上午11:53
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode(encoding='utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == "__main__":
    print(get_md5("http://jobbole.com"))
