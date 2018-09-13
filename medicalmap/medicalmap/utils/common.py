#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-7-5 上午10:16
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import re
import time
import datetime
from re import S
MUNICIPALITY = ['北京市', '上海市', '天津市', '重庆市']
MUNICIPALITY2 = ['北京', '上海', '天津', '重庆']


def now_year():
    """返回当前日期的年份"""
    return datetime.datetime.now().strftime('%Y')


def now_day():
    """返回当前日期的年月日"""
    return datetime.datetime.now().strftime('%Y-%m-%d')


def timestamp():
    """返回当前时间的时间戳,13位"""
    return str(int(time.time() * 1000))


def custom_remove_tags(value):
    """正则表达式去除\n\t\r等相关字符"""
    return ''.join(re.findall(r'\S', value, S)).strip()


def remove_number(value):
    """获取除数字以外的其他信息 方法1"""
    return ''.join(re.findall(r'[^\d+]', value))


def remove_number2(value):
    """获取除数字以外的其他信息 方法2"""
    return re.sub(r'\d+', '', value)


def get_number(value):
    """获取字符串里的数字"""
    res = re.search(r'(\d+.\d+)', value)
    if res:
        # return res.group(1)
        return '{0}{1}'.format(res.group(1), '元')
    else:
        return None


def clean_info(value):
    """
    去除字段值一些无用的信息
    只适用于成都市青白江区中医医院:|川化病区内科查房指导|门诊坐诊、内科查房指导|科室介绍|暂无内容
    替换各种符号为空

    """
    return re.sub(r'[：:()\[\]]', '', value).strip()


def clean_info2(value):
    """去掉多余字样"""
    return re.sub('暂无介绍内容|暂无介绍信息|暂无介绍|暂无简介|暂无相关信息|暂无科室介绍信息|'
                  '暂无科室介绍|暂无相应资料。|null|未知|暂无|\[详细\]-->',
                  '',
                  value).strip()


def match_special(value):
    """
    选择冒号右边的字符串
    适用于类似[简介：相关文字]这样需要冒号右边文字的字符串的获取
    """
    if '：' in value:
        return value.split('：')[-1]
    elif ':' in value:
        return value.split(':')[-1]
    elif '|' in value:
        return value.split('|')[0]
    else:
        return value


def match_special2(value):
    """
    选择(右边的字符串
    适用于类似[内三科（老..]这样需要冒号右边文字的字符串的获取
    主要适用于：双流区中医医院科室信息
    """
    if '（' in value:
        return value.split('（')[0].strip()
    elif '(' in value:
        return value.split('(')[0].strip()
    elif '-' in value:
        return value.split('-')[-1].strip()
    elif '_' in value:
        return value.split('_')[0].strip()
    elif ':' in value:
        return value.split(':')[-1].strip()
    elif '：' in value:
        return value.split('：')[-1].strip()
    elif '/' in value:
        return value.split('/')[0].strip()
    elif '、' in value:
        return value.split('、')[0].strip()
    elif '，' in value:
        return value.split('，')[0].strip()
    else:
        return value


def get_county2(useless_info, hospital_address):
    """
    :param useless_info
    :param h_city: the name of the city
    :param hospital_address: the address og hospital
    :return: hospital county
    """
    res = re.sub(r'{0}'.format(useless_info), '', hospital_address)
    if res:
        try:
            county = re.search(r'^((.*?)县)|^((.*?)区)', res)
            if county:
                return county.group(0)
            else:
                return None
        except Exception as e:
            print('获取三级地址的时候出错了,原因是:{}'.format(repr(e)))
            return None
    else:
        return None


def get_city(useless_info, hospital_address):
    """获取医院所在市信息"""
    value = re.sub(r'{0}'.format(useless_info), '', hospital_address)
    if value:
        res = re.search(r'^((.*?)市)', value)
        if res:
            return res.group(0)
        else:
            return None
    else:
        return None


# 非通用系列
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


def filter_info(value):
    """
    适用于成都市温江区妇幼保健院,医生信息获取
    """
    good_at = re.search(r'.*擅长专业(.*?)医生简介', value, S)
    if good_at:
        return clean_info(good_at.group(1).strip())
    else:
        return None


def filter_info2(value):
    """
    适用于成都市温江区妇幼保健院,医生信息获取
    """
    good_at = re.search(r'.*医生简介(.*?)我们的使命', value, S)
    good_at2 = re.search(r'.*医生简介(.*?)我的宗旨', value, S)
    good_at3 = re.search(r'.*医生简介(.*?)$', value, S)
    if good_at:
        return clean_info(custom_remove_tags(good_at.group(1)))
    elif good_at2:
        return clean_info(custom_remove_tags(good_at2.group(1)))
    elif good_at3:
        return clean_info(custom_remove_tags(good_at3.group(1)))
    else:
        return None


def filter_info3(value):
    """
    只适用于双流区妇幼保健院
    获取科室信息
    """
    ret_info = None
    try:
        ret_info = re.search(r'((.*?)科)(.*?)$', value)
    except Exception as e:
        print(value)
        print(e)
    finally:
        if ret_info:
            return ret_info.group(1)
        else:
            return value


def filter_info4(value):
    """
    只适用于双流区妇幼保健院
    获取医生级别信息
    """
    ret_info = None
    try:
        ret_info = re.search(r'((.*?)科)(.*?)$', value)
    except Exception as e:
        print(e)
    finally:
        if ret_info:
            return ret_info.group(3)
        else:
            return value.split(' ')[0]


def get_hospital_alias(value):
    """
    适用于：医学百科
    获取医院别名
    """
    # hospital_alias_name = re.search(r'（(.*?)）', value)
    hospital_alias_name = re.sub(r'^（|）$', '', value)
    alias_name = None
    try:
        if hospital_alias_name:
            alias_name = hospital_alias_name
    except Exception as e:
        print(e)
    finally:
        return alias_name


def get_county(h_pro, h_city, hospital_address):
    """
    :param h_pro:province
    :param h_city:city
    :param hospital_name:hospital name
    :return:the county of address
    """
    res = match_special(hospital_address).replace(h_pro, '').replace(h_city, '')
    if res:
        try:
            county = re.search(r'^((.*?)县)|^((.*?)区)|^((.*?)市)', res)
            if county:
                # print(county)
                return county.group(0)
            else:
                return None
        except Exception as e:
            print('获取三级地址的时候出错了,原因是:{}'.format(repr(e)))
            return None
    else:
        return None


def get_hospital_info(hospital_info, cut_start, cut_end):
    """
    :param hospital_info: 医院信息
    :param cut_start: 需要匹配的信息开始
    :param cut_end: 需要匹配的信息结束
    :return: 返回对应的信息,适用于陕西省预约诊疗服务平台 2018-08-18
    """
    if hospital_info:
        res = re.search(r'{}(.*?){}'.format(cut_start, cut_end), hospital_info.replace('<关闭>', ''), S)
        if res:
            return res.group(1)
        else:
            return None
    else:
        return None


# if __name__ == "__main__":
#     # print(remove_number('701'))
#     # print(now_year(), type(now_year()))
#     # print(now_day(), type(now_day()))
#     # print(get_reg_info('门诊时间：星期二:下午,星期三:上午、下午、晚班'))
#     # print(get_hospital_alias('中日友好医院（卫生部中日友好医院）'))
#     print(get_county('四川省', '成都市', '四川省成都市晋江县锦江区红星路四段14号'))
#     print(clean_info('08/17(上午)'))
#     print(get_city('衡阳市珠晖区湖北路36号（火车站斜对面）'))
#     print(get_number('参考费用：25.00元'))
#     ss = '等级:二级合格医院区域:海淀区分类:北京大学附属医院'
#     res2 = ss.split(':')
#     print(res2)
#     res = re.search(r'(.*等|.*级|.*合格)(.*?)$', res2[1].replace('区域', ''))
#     print(res.group(2))
