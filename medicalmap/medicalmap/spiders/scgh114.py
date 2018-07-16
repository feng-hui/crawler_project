# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.http import FormRequest
from medicalmap.items import HospitalInfoItem, HospitalDepItem, DoctorInfoItem, DoctorRegInfoItem, CommonLoader
from medicalmap.utils.common import now_day


class Scgh114Spider(scrapy.Spider):
    name = 'scgh114'
    allowed_domains = ['scgh114.com']
    start_urls = ['http://scgh114.com/']
    start_area_id = ['10100', '10101', '10116']  # 成都、绵阳、眉山三个城市的ID
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.scgh114.com',
        'Origin': 'http://www.scgh114.com',
        'Referer': 'http://www.scgh114.com/web/index',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    hospital_link = 'http://www.scgh114.com/web/hospital/findHospital'
    dept_link = 'http://www.scgh114.com/web/hospital/findDepartByHosId'
    doctor_link = 'http://www.scgh114.com/web/hospital/searchDoctor'
    doctor_detail_link = 'http://www.scgh114.com/web/hospital/findDoctorById'
    doctor_reg_info_lik = 'http://www.scgh114.com/web/hospital/findDoctorWorkInfoById'
    source_from = '114'
    custom_settings = {
        # 延迟设置
        # 'DOWNLOAD_DELAY': 3,
        # 自动限速设置
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 5.0,
        'AUTOTHROTTLE_DEBUG': False,
        # 并发请求数的控制,默认为16
        'CONCURRENT_REQUESTS': 16
    }

    def start_requests(self):
        for each_area_id in self.start_area_id[0:1]:
            data = {
                'areaId': each_area_id
            }
            yield FormRequest(self.hospital_link,
                              callback=self.parse,
                              headers=self.headers,
                              formdata=data,
                              method='POST',
                              dont_filter=True)

    def parse(self, response):
        """获取医院相关信息"""
        self.logger.info('>>>>>>正在抓取医院相关信息……')
        hospital_info = json.loads(response.text)
        for each_hospital in hospital_info[3:4]:
            is_medicare = '是' if str(each_hospital.get('Ismedicalcard', '')) == '1' else '否'
            loader = CommonLoader(item=HospitalInfoItem(), response=response)
            loader.add_value('hospital_name', each_hospital.get('hospitalname', ''))
            loader.add_value('hospital_level', each_hospital.get('levelName', ''))
            loader.add_value('hospital_addr', each_hospital.get('address', ''))
            loader.add_value('hospital_pro', '四川')
            loader.add_value('hospital_city', each_hospital.get('areaName', ''))
            loader.add_value('is_medicare', is_medicare)
            loader.add_value('dataSource_from', self.source_from)
            loader.add_value('update_time', now_day())
            hospital_item = loader.load_item()
            yield hospital_item
            hospital_id = each_hospital.get('hospitalid')
            if hospital_id:
                dept_request = FormRequest(self.dept_link,
                                           headers=self.headers,
                                           callback=self.parse_dept_info,
                                           formdata={'hospitalId': str(hospital_id)},
                                           dont_filter=True)
                self.headers['Referer'] = 'http://www.scgh114.com/web/register/gh'
                yield dept_request

    def parse_dept_info(self, response):
        self.logger.info('>>>>>>正在抓取医院科室相关信息……')
        dept_info = json.loads(response.text)
        for each_dept in dept_info['responseData']['data']['data']['depart']:
            loader = CommonLoader(item=HospitalDepItem(), response=response)
            loader.add_value('dept_name', each_dept['deptname'])
            loader.add_value('hospital_name', dept_info['responseData']['data']['data']['hospital']['hospitalName'])
            loader.add_value('update_time', now_day())
            dept_item = loader.load_item()
            yield dept_item
            dept_id = each_dept.get('deptid', '')
            if dept_id:
                data = {
                    'key': '',
                    'deptId': str(dept_id),
                    'pageIndex': '1',
                    'pageSize': '100'
                }
                doctor_request = FormRequest(self.doctor_link,
                                             headers=self.headers,
                                             callback=self.parse_doctor_info,
                                             formdata=data,
                                             meta={'dept_id': dept_id},
                                             dont_filter=True)
                self.headers['Referer'] = 'http://www.scgh114.com/web/register/doctor'
                yield doctor_request

    def parse_doctor_info(self, response):
        # dept_id = response.meta['dept_id']
        doctor_info = json.loads(response.text)
        # page_index = doctor_info[0].get('pageIndex', '1')
        # total_page = doctor_info[0].get('totalpage', 1)
        for each_doctor in doctor_info[0]['data']:
            doctor_name = each_doctor.get('doctorName', '')
            loader = CommonLoader(item=DoctorInfoItem(), response=response)
            loader.add_value('doctor_name', doctor_name)
            loader.add_value('dept_name', each_doctor.get('deptName', ''))
            loader.add_value('hospital_name', each_doctor.get('hospitalName', ''))
            loader.add_value('doctor_level', each_doctor.get('degree', ''))
            loader.add_value('doctor_goodAt', each_doctor.get('extexperts', ''))
            doctor_id = each_doctor.get('doctorId', '')
            # 获取医生排班信息以及医生详细信息
            if doctor_id:
                self.headers['Referer'] = 'http://www.scgh114.com/web/hospital/doctorinfoP'
                # 医生详细信息
                doctor_detail_request = FormRequest(self.doctor_detail_link,
                                                    headers=self.headers,
                                                    callback=self.parse_doctor_detail,
                                                    formdata={'doctorId': str(doctor_id)},
                                                    meta={'loader': loader},
                                                    dont_filter=True)
                yield doctor_detail_request
                # 医生排班信息
                doctor_reg_request = FormRequest(self.doctor_reg_info_lik,
                                                 headers=self.headers,
                                                 callback=self.parse_doctor_reg_info,
                                                 formdata={'doctorId': str(doctor_id)},
                                                 meta={'doctor_name': doctor_name},
                                                 dont_filter=True)

                yield doctor_reg_request
        # 医生翻页信息
        # if int(total_page) > 1:
        #     self.logger.info('>>>>>>总共有{}页医生信息……'.format(str(total_page)))
        #     remain_pages = total_page - 1
        #     for each_page in range(remain_pages):
        #         page_index = str(int(page_index) + 1)
        #         self.logger.info('>>>>>>正在抓取第{}页医生信息……'.format(str(page_index)))
        #         data = {
        #             'key': '',
        #             'deptId': str(dept_id),
        #             'pageIndex': page_index,
        #             'pageSize': '10'
        #         }
        #         doctor_request = FormRequest(self.doctor_link,
        #                                      headers=self.headers,
        #                                      callback=self.parse_doctor_info,
        #                                      formdata=data,
        #                                      meta={'dept_id': dept_id},
        #                                      dont_filter=True)
        #         self.headers['Referer'] = 'http://www.scgh114.com/web/register/doctor'
        #         yield doctor_request

    def parse_doctor_detail(self, response):
        self.logger.info('>>>>>>正在抓取医生详细信息……')
        loader = response.meta['loader']
        doctor_detail = json.loads(response.text)
        loader.add_value('doctor_intro', doctor_detail['data'].get('extDetails', ''))
        loader.add_value('doctor_goodAt', doctor_detail['data'].get('extExperts', ''))
        loader.add_value('update_time', now_day())
        doctor_item = loader.load_item()
        yield doctor_item

    def parse_doctor_reg_info(self, response):
        self.logger.info('>>>>>>正在抓取医生排班信息……')
        doctor_reg_info = json.loads(response.text)
        reg_info_list = doctor_reg_info['data']['selWork']
        doctor_name = doctor_reg_info['data']['doctor'][0].get('doctorName', '')
        hospital_name = doctor_reg_info['data']['doctor'][0].get('hospitalName', '')
        dept_name = doctor_reg_info['data']['doctor'][0].get('deptName', '')
        for each_reg_info in reg_info_list:
            duty_date = each_reg_info['dutydate']
            sel_works = each_reg_info['selWorks']
            for each_work_info in sel_works:
                duty_time = each_work_info['dutytime']
                if int(duty_time) == 1:
                    duty_time = '上午'
                elif int(duty_time) == 3:
                    duty_time = '上午'
                else:
                    # duty_time 4 晚上 doctorId 3329 成都中医药大学附属医院
                    duty_time = '晚上'
                reg_info = '{0}{1}'.format(duty_date, duty_time)
                loader = CommonLoader(item=DoctorRegInfoItem(), response=response)
                loader.add_value('doctor_name', doctor_name)
                loader.add_value('hospital_name', hospital_name)
                loader.add_value('dept_name', dept_name)
                loader.add_value('reg_info', reg_info)
                loader.add_value('update_time', now_day())
                reg_info_item = loader.load_item()
                yield reg_info_item
