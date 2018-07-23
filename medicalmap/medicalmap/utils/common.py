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
    return re.sub(r'null|--|none|\(|\)|:|：|川化病区内科查房指导|门诊坐诊、内科查房指导|科室介绍|暂无内容',
                  '',
                  value).strip()


def match_special(value):
    """
    选择冒号右边的字符串
    适用于类似[简介：相关文字]这样需要冒号右边文字的字符串的获取
    """
    return value.split('：')[-1]


def get_reg_info(value):
    """
    只适用于都江堰市第二人民医院门诊时间的处理上
    """
    value = custom_remove_tags(value)
    res = []
    reg_list = [{each_reg.split(':')[0]: each_reg.split(':')[-1].split('、')}
                for each_reg in re.sub(r'门诊时间：', '', value).split(',')]
    for each_reg in reg_list:
        for key, value in each_reg.items():
            res.extend(['{0}{1}'.format(key, each_value) for each_value in value])
    return res


def get_doctor_intro2(value):
    """
    适用于成都市青白江区中医医院
    获取医生简介
    """
    res = re.search(r'(.*?)擅长', value)
    res2 = re.search(r'(.*?)尤其擅长', value)
    if res2:
        return clean_info(res2.group(1))
    elif res:
        return clean_info(res.group(1))
    else:
        return ''


def get_doctor_good_at(value):
    """
        适用于成都市青白江区中医医院
        获取医生简介
        """
    res = re.search(r'擅长(.*?)坐诊时间', value, S)
    res2 = re.search(r'擅长(.*?)名医馆坐诊时间', value, S)
    if res2:
        return '{0}{1}'.format('擅长', clean_info(res2.group(1)))
    elif res:
        return '{0}{1}'.format('擅长', clean_info(res.group(1)))
    else:
        return ''


if __name__ == "__main__":
    print(remove_number('701'))
    print(now_year(), type(now_year()))
    print(now_day(), type(now_day()))
    print(get_reg_info('门诊时间：星期二:下午,星期三:上午、下午、晚班'))

