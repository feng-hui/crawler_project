#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-9-20 上午9:46
# @author : Feng_Hui
# @email  : capricorn1203@126.com
# 快医网 城市id字典
import json
from urllib.parse import quote


# 热门城市
carelink_web3_hot_city = [{
    "cityName": "北京",
    "cityPinyin": "beijing",
    "cityId": 110000,
    "provinceName": "",
    "provincePinyin": 'null',
    "provinceId": 0
}, {
    "cityName": "天津",
    "cityPinyin": "tianjin",
    "cityId": 120000,
    "provinceName": "",
    "provincePinyin": 'null',
    "provinceId": 0
}, {
    "cityName": "上海",
    "cityPinyin": "shanghai",
    "cityId": 310000,
    "provinceName": "",
    "provincePinyin": 'null',
    "provinceId": 0
}, {
    "cityName": "广州",
    "cityPinyin": "guangzhoushi",
    "cityId": 440100,
    "provinceName": "广东",
    "provincePinyin": "guangdong",
    "provinceId": 440000
}, {
    "cityName": "深圳",
    "cityPinyin": "shen圳shi",
    "cityId": 440300,
    "provinceName": "广东",
    "provincePinyin": "guangdong",
    "provinceId": 440000
}]


# 省份
carelink_web3_provinces = [{
    "pinyin": "beijing",
    "name": "北京",
    "id": 110000
}, {
    "pinyin": "tianjin",
    "name": "天津",
    "id": 120000
}, {
    "pinyin": "hebei",
    "name": "河北",
    "id": 130000
}, {
    "pinyin": "shanxi1",
    "name": "山西",
    "id": 140000
}, {
    "pinyin": "neimenggu",
    "name": "内蒙古",
    "id": 150000
}, {
    "pinyin": "liaoning",
    "name": "辽宁",
    "id": 210000
}, {
    "pinyin": "jilin",
    "name": "吉林",
    "id": 220000
}, {
    "pinyin": "heilongjiang",
    "name": "黑龙江",
    "id": 230000
}, {
    "pinyin": "shanghai",
    "name": "上海",
    "id": 310000
}, {
    "pinyin": "jiangsu",
    "name": "江苏",
    "id": 320000
}, {
    "pinyin": "zhejiang",
    "name": "浙江",
    "id": 330000
}, {
    "pinyin": "anhui",
    "name": "安徽",
    "id": 340000
}, {
    "pinyin": "fujian",
    "name": "福建",
    "id": 350000
}, {
    "pinyin": "jiangxi",
    "name": "江西",
    "id": 360000
}, {
    "pinyin": "shandong",
    "name": "山东",
    "id": 370000
}, {
    "pinyin": "henan",
    "name": "河南",
    "id": 410000
}, {
    "pinyin": "hubei",
    "name": "湖北",
    "id": 420000
}, {
    "pinyin": "hunan",
    "name": "湖南",
    "id": 430000
}, {
    "pinyin": "guangdong",
    "name": "广东",
    "id": 440000
}, {
    "pinyin": "guangxi",
    "name": "广西",
    "id": 450000
}, {
    "pinyin": "hainan",
    "name": "海南",
    "id": 460000
}, {
    "pinyin": "zhongqing",
    "name": "重庆",
    "id": 500000
}, {
    "pinyin": "sichuan",
    "name": "四川",
    "id": 510000
}, {
    "pinyin": "guizhou",
    "name": "贵州",
    "id": 520000
}, {
    "pinyin": "yunnan",
    "name": "云南",
    "id": 530000
}, {
    "pinyin": "shanxi2",
    "name": "陕西",
    "id": 610000
}, {
    "pinyin": "gansu",
    "name": "甘肃",
    "id": 620000
}, {
    "pinyin": "ningxia",
    "name": "宁夏",
    "id": 640000
}, {
    "pinyin": "xinjiang",
    "name": "新疆",
    "id": 650000
}, {
    "pinyin": "xianggang",
    "name": "香港",
    "id": 810000
}]


carelink2_web3_city_location = {
    "provinceId": 330000,
    "provinceName": "浙江",
    "provincePinyin": "zhejiang",
    "cityId": 0,
    "cityName": "不限",
    "cityPinyin": ""
}

care_link_cookies = 'carelink_web3_hot_city={0};carelink_web3_provinces={1};carelink2_web3_city_location={2};{3}'.format(
    quote(json.dumps(carelink_web3_hot_city)),
    quote(json.dumps(carelink_web3_provinces)),
    quote(json.dumps(carelink2_web3_city_location)),
    'carelink_web3_cookie_user_key=C7CE5C7ADA8F93A33C3783DB15B73F8D')

print(len(carelink_web3_provinces))
# care_link_cookies2 = {
#     'carelink_web3_hot_city': quote(json.dumps(carelink_web3_hot_city)),
#     'carelink_web3_provinces': quote(json.dumps(carelink_web3_provinces)),
#     'carelink2_web3_city_location':  carelink2_web3_city_location
# }
