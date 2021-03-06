# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
# update_time: year-month-day[更新时间一律精确到天]

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, MapCompose
from w3lib.html import remove_tags
from medicalmap.utils.common import get_doctor_intro, custom_remove_tags, clean_info


class MedicalmapItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CommonLoader(ItemLoader):
    """通用ItemLoader"""
    default_output_processor = TakeFirst()
    doctor_intro_in = MapCompose(remove_tags, clean_info)
    doctor_goodAt_in = MapCompose(clean_info)


class MedicalMapLoader(ItemLoader):
    """金堂县第一人民医院loader"""
    default_output_processor = TakeFirst()
    hospital_intro_in = Join()
    dept_info_in = MapCompose(remove_tags)
    dept_info_out = Join()
    doctor_intro_in = doctor_goodAt_in = MapCompose(get_doctor_intro)


class PxfybjyLoader(ItemLoader):
    """郫县妇幼保健院loader"""
    default_output_processor = TakeFirst()
    hospital_intro_in = MapCompose(remove_tags, custom_remove_tags)
    hospital_intro_out = Join()
    dept_info_in = MapCompose(remove_tags, custom_remove_tags)
    dept_info_out = Join()
    dept_name_in = dept_type_in = doctor_name_in = doctor_intro_in = doctor_goodAt_in = MapCompose(custom_remove_tags)
    doctor_level_in = MapCompose(custom_remove_tags, str.strip)
    doctor_level_out = Join()
    doctor_intro_out = doctor_goodAt_out = Join()


class YiHuLoader(ItemLoader):
    """健康之路item loader"""
    default_output_processor = TakeFirst()
    hospital_intro_in = MapCompose(remove_tags, custom_remove_tags)
    # hospital_intro_out = Join()


class CommonLoader2(ItemLoader):
    default_output_processor = TakeFirst()
    # hospital_intro_in = MapCompose(remove_tags, custom_remove_tags)
    # dept_info_in = MapCompose(remove_tags, custom_remove_tags)
    # 适用于郫县中医医院
    # hospital_intro_in = dept_info_in = Join()
    # 适用于成都长江医院
    # dept_info_in = Join()
    # 适用于彭州市中医医院
    # doctor_intro_in = doctor_goodAt_in = Join()
    # 适用于医学百科
    hospital_intro_in = Join()


class HospitalInfoItem(scrapy.Item):
    """
    医院信息表
    hospital_name       医院名称
    consulting_hour     医院上班时间
    hospital_level      医院等级 二级甲等,二级乙等,二级丙等,三级甲等,三级乙等,三级丙等,一级甲等,一级丙等,一级乙等,未定级
    hospital_type       医院性质 公立 私立
    hospital_category   医院分类 综合医院,中医医院,专科医院,妇幼保健院,卫生服务中心,卫生院,疾病预防控制中心
    hospital_addr       医院地址
    hospital_pro        医院所属省
    hospital_city       医院所属市
    hospital_county     医院所属县
    hospital_phone      医院电话
    hospital_intro      医院简介
    is_medicare         是否接入医保
    medicare_type       医保类型
    vaccine_name        疫苗类型
    is_cpc              是否有胸痛中心
    is_bdc              是否有脑卒中中心
    cooperative_business和微医平台的合作业务
    hospital_district   院区
    registered_channel  挂号渠道
    update_time         更新时间
    # 新增字段           新增时间:2018.09.17
    hospital_postcode   邮编
    hospital_email      邮箱
    hospital_official_website 官方网站
    hospital_fax              传真
    hospital_operation_mode   经营模式（国营或民营等）
    hospital_id               医院ID
    hospital_tags             医院标签
    hospital_dept_num         医院科室数
    hospital_doctor_num       医院医生数
    hospital_route            到院路线
    hospital_staff_num        医院员工数
    hospital_logo_url         医院LOGO链接
    hospital_img_url          医院图片地址
    hospital_remarks          医院备注
    gmt_created               创建时间
    gmt_modified              更改时间
    """
    hospital_name = scrapy.Field()
    consulting_hour = scrapy.Field()
    hospital_level = scrapy.Field()
    hospital_type = scrapy.Field()
    hospital_category = scrapy.Field()
    hospital_addr = scrapy.Field()
    hospital_pro = scrapy.Field()
    hospital_city = scrapy.Field()
    hospital_county = scrapy.Field()
    hospital_phone = scrapy.Field()
    hospital_intro = scrapy.Field()
    is_medicare = scrapy.Field()
    medicare_type = scrapy.Field()
    vaccine_name = scrapy.Field()
    is_cpc = scrapy.Field()
    is_bdc = scrapy.Field()
    cooperative_business = scrapy.Field()
    hospital_district = scrapy.Field()
    registered_channel = scrapy.Field()
    dataSource_from = scrapy.Field()
    crawled_url = scrapy.Field()
    update_time = scrapy.Field()
    hospital_postcode = scrapy.Field()
    hospital_email = scrapy.Field()
    hospital_official_website = scrapy.Field()
    hospital_fax = scrapy.Field()
    hospital_operation_mode = scrapy.Field()
    hospital_id = scrapy.Field()
    hospital_tags = scrapy.Field()
    hospital_dept_num = scrapy.Field()
    hospital_doctor_num = scrapy.Field()
    hospital_route = scrapy.Field()
    hospital_staff_num = scrapy.Field()
    hospital_logo_url = scrapy.Field()
    hospital_img_url = scrapy.Field()
    hospital_remarks = scrapy.Field()
    gmt_created = scrapy.Field()
    gmt_modified = scrapy.Field()

    def get_sql_info(self):
        # 不更新,只插入
        insert_sql = "insert into hospital_info(hospital_name,consulting_hour,hospital_level,hospital_type," \
                     "hospital_category,hospital_addr,hospital_pro,hospital_city,hospital_county,hospital_phone," \
                     "hospital_intro,is_medicare,medicare_type,vaccine_name,is_cpc,is_bdc,cooperative_business," \
                     "hospital_district,registered_channel,dataSource_from,crawled_url,update_time," \
                     "hospital_postcode,hospital_email,hospital_official_website,hospital_fax," \
                     "hospital_operation_mode,hospital_id,hospital_tags,hospital_dept_num,hospital_doctor_num," \
                     "hospital_route,hospital_staff_num,hospital_logo_url,hospital_img_url,hospital_remarks," \
                     "gmt_created,gmt_modified) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                     "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # 适用于有主键更新的情况
        # insert_sql = "insert into hospital_info(hospital_name,consulting_hour,hospital_level,hospital_type," \
        #              "hospital_category,hospital_addr,hospital_pro,hospital_city,hospital_county,hospital_phone," \
        #              "hospital_intro,is_medicare,medicare_type,vaccine_name,is_cpc,is_bdc,cooperative_business," \
        #              "hospital_district,registered_channel,dataSource_from,update_time) " \
        #              "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) " \
        #              "on duplicate key update hospital_intro=values(hospital_intro)," \
        #              "hospital_pro=values(hospital_pro),hospital_city=values(hospital_city)," \
        #              "hospital_phone=values(hospital_phone),update_time=values(update_time)"
        params = [
            self.get('hospital_name', '暂无,出现异常'),
            self.get('consulting_hour'),
            self.get('hospital_level'),
            self.get('hospital_type'),
            self.get('hospital_category'),
            self.get('hospital_addr'),
            self.get('hospital_pro'),
            self.get('hospital_city'),
            self.get('hospital_county'),
            self.get('hospital_phone'),
            self.get('hospital_intro'),
            self.get('is_medicare'),
            self.get('medicare_type'),
            self.get('vaccine_name'),
            self.get('is_cpc'),
            self.get('is_bdc'),
            self.get('cooperative_business'),
            self.get('hospital_district'),
            self.get('registered_channel'),
            self.get('dataSource_from'),
            self.get('crawled_url'),
            self.get('update_time'),
            self.get('hospital_postcode'),
            self.get('hospital_email'),
            self.get('hospital_official_website'),
            self.get('hospital_fax'),
            self.get('hospital_operation_mode'),
            self.get('hospital_id'),
            self.get('hospital_tags'),
            self.get('hospital_dept_num'),
            self.get('hospital_doctor_num'),
            self.get('hospital_route'),
            self.get('hospital_staff_num'),
            self.get('hospital_logo_url'),
            self.get('hospital_img_url'),
            self.get('hospital_remarks'),
            self.get('gmt_created'),
            self.get('gmt_modified')
        ]
        return insert_sql, params


class HospitalInfoTestItem(scrapy.Item):
    """
    医院信息表_医学百科专用
    hospital_name       医院名称
    consulting_hour     医院上班时间
    hospital_level      医院等级 二级甲等,二级乙等,二级丙等,三级甲等,三级乙等,三级丙等,一级甲等,一级丙等,一级乙等,未定级
    hospital_type       医院性质 公立 私立
    hospital_category   医院分类 综合医院,中医医院,专科医院,妇幼保健院,卫生服务中心,卫生院,疾病预防控制中心
    hospital_addr       医院地址
    hospital_pro        医院所属省
    hospital_city       医院所属市
    hospital_county     医院所属县
    hospital_phone      医院电话
    hospital_intro      医院简介
    is_medicare         是否接入医保
    medicare_type       医保类型
    vaccine_name        疫苗类型
    is_cpc              是否有胸痛中心
    is_bdc              是否有脑卒中中心
    cooperative_business和微医平台的合作业务
    hospital_district   院区
    registered_channel  挂号渠道
    hospital_postcode   邮政编码
    hospital_email      医院邮箱
    hospital_website    医院网址
    hospital_fax        医院传真
    operation_mode      经营模式
    hospital_url        医院链接
    update_time         更新时间
    """
    hospital_name = scrapy.Field()
    consulting_hour = scrapy.Field()
    hospital_level = scrapy.Field()
    hospital_type = scrapy.Field()
    hospital_category = scrapy.Field()
    hospital_addr = scrapy.Field()
    hospital_pro = scrapy.Field()
    hospital_city = scrapy.Field()
    hospital_county = scrapy.Field()
    hospital_phone = scrapy.Field()
    hospital_intro = scrapy.Field()
    is_medicare = scrapy.Field()
    medicare_type = scrapy.Field()
    vaccine_name = scrapy.Field()
    is_cpc = scrapy.Field()
    is_bdc = scrapy.Field()
    cooperative_business = scrapy.Field()
    hospital_district = scrapy.Field()
    registered_channel = scrapy.Field()
    dataSource_from = scrapy.Field()
    hospital_postcode = scrapy.Field()
    hospital_email = scrapy.Field()
    hospital_website = scrapy.Field()
    hospital_fax = scrapy.Field()
    operation_mode = scrapy.Field()
    hospital_url = scrapy.Field()
    update_time = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into hospital_info(hospital_name,consulting_hour,hospital_level,hospital_type," \
                     "hospital_category,hospital_addr,hospital_pro,hospital_city,hospital_county,hospital_phone," \
                     "hospital_intro,is_medicare,medicare_type,vaccine_name,is_cpc,is_bdc,cooperative_business," \
                     "hospital_district,registered_channel,dataSource_from,hospital_postcode,hospital_email," \
                     "hospital_website,hospital_fax,operation_mode,hospital_url,update_time) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # insert_sql = "update hospital_info set hospital_name=%s,consulting_hour=%s,hospital_level=%s," \
        #              "hospital_type=%s,hospital_category=%s,hospital_addr=%s,hospital_pro=%s,hospital_city=%s," \
        #              "hospital_county=%s,hospital_phone=%s,hospital_intro=%s,is_medicare=%s," \
        #              "medicare_type=%s,vaccine_name=%s,is_cpc=%s,is_bdc=%s,cooperative_business=%s," \
        #              "hospital_district=%s,registered_channel=%s,dataSource_from=%s,hospital_postcode=%s," \
        #              "hospital_email=%s,hospital_website=%s,hospital_fax=%s,operation_mode=%s,hospital_url=%s," \
        #              "update_time=%s where hospital_url=%s"
        params = [
            self.get('hospital_name', '暂无,出现异常'),
            self.get('consulting_hour'),
            self.get('hospital_level'),
            self.get('hospital_type'),
            self.get('hospital_category'),
            self.get('hospital_addr'),
            self.get('hospital_pro'),
            self.get('hospital_city'),
            self.get('hospital_county'),
            self.get('hospital_phone'),
            self.get('hospital_intro'),
            self.get('is_medicare'),
            self.get('medicare_type'),
            self.get('vaccine_name'),
            self.get('is_cpc'),
            self.get('is_bdc'),
            self.get('cooperative_business'),
            self.get('hospital_district'),
            self.get('registered_channel'),
            self.get('dataSource_from'),
            self.get('hospital_postcode'),
            self.get('hospital_email'),
            self.get('hospital_website'),
            self.get('hospital_fax'),
            self.get('operation_mode'),
            self.get('hospital_url'),
            self.get('update_time'),
            # self.get('hospital_url')
        ]
        return insert_sql, params


class HospitalDepItem(scrapy.Item):
    """
    科室信息表
    hospital_id      医院ID
    dept_type        科室类别 一级科室名称
    dept_name        科室名称 二级科室名称
    dep_intro        科室介绍
    update_time      更新时间
    dept_id          科室ID
    hospital_id      医院ID
    dept_person_num  科室人数
    dept_url         科室链接
    gmt_created      创建时间
    gmt_modified     更改时间
    """
    dept_name = scrapy.Field()
    hospital_name = scrapy.Field()
    dept_type = scrapy.Field()
    dept_info = scrapy.Field()
    dataSource_from = scrapy.Field()
    crawled_url = scrapy.Field()
    update_time = scrapy.Field()
    dept_id = scrapy.Field()
    hospital_id = scrapy.Field()
    dept_person_num = scrapy.Field()
    dept_url = scrapy.Field()
    gmt_created = scrapy.Field()
    gmt_modified = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into department_info(dept_name,hospital_name,dept_type,dept_info,dataSource_from," \
                     "crawled_url,update_time,dept_id,hospital_id,dept_person_num,dept_url,gmt_created,gmt_modified) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key " \
                     "update update_time=values(update_time)"
        params = [
            self.get('dept_name', '暂无,出现异常'),
            self.get('hospital_name', '暂无,出现异常'),
            self.get('dept_type'),
            self.get('dept_info'),
            self.get('dataSource_from'),
            self.get('crawled_url'),
            self.get('update_time'),
            self.get('dept_id'),
            self.get('hospital_id'),
            self.get('dept_person_num'),
            self.get('dept_url'),
            self.get('gmt_created'),
            self.get('gmt_modified')
        ]
        return insert_sql, params


class DoctorInfoItem(scrapy.Item):
    """
    医生信息表
    doctor_name     医生姓名
    sex             医生性别
    hospital_id     所属医院
    dep_id          所属科室
    doctor_level    医生等级
    doctor_intro    医生简称
    doctor_goodAt   医生擅长
    diagnosis_amt   医生诊疗费用
    update_time     更新时间
    doctor_academic_title   医生学术职称(教授、副教授等)
    doctor_id       医生ID
    dept_id         科室ID
    hospital_id     医院ID
    doctor_photo_url 医生照片链接
    gmt_created      创建时间
    gmt_modified     更改时间
    """
    doctor_name = scrapy.Field()
    dept_name = scrapy.Field()
    hospital_name = scrapy.Field()
    sex = scrapy.Field()
    doctor_level = scrapy.Field()
    doctor_intro = scrapy.Field()
    doctor_goodAt = scrapy.Field()
    diagnosis_amt = scrapy.Field()
    dataSource_from = scrapy.Field()
    crawled_url = scrapy.Field()
    update_time = scrapy.Field()
    doctor_academic_title = scrapy.Field()
    doctor_id = scrapy.Field()
    dept_id = scrapy.Field()
    hospital_id = scrapy.Field()
    doctor_photo_url = scrapy.Field()
    gmt_created = scrapy.Field()
    gmt_modified = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into doctor_info(doctor_name,dept_name,hospital_name,sex,doctor_level," \
                     "doctor_intro,doctor_goodAt,diagnosis_amt,dataSource_from,crawled_url,update_time," \
                     "doctor_academic_title,doctor_id,dept_id,hospital_id,doctor_photo_url,gmt_created," \
                     "gmt_modified) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [
            self.get('doctor_name', '暂无,出现异常'),
            self.get('dept_name', '暂无,出现异常'),
            self.get('hospital_name', '暂无,出现异常'),
            self.get('sex'),
            self.get('doctor_level'),
            self.get('doctor_intro'),
            self.get('doctor_goodAt'),
            self.get('diagnosis_amt'),
            self.get('dataSource_from'),
            self.get('crawled_url'),
            self.get('update_time'),
            self.get('doctor_academic_title'),
            self.get('doctor_id'),
            self.get('dept_id'),
            self.get('hospital_id'),
            self.get('doctor_photo_url'),
            self.get('gmt_created'),
            self.get('gmt_modified')
        ]
        # insert_sql = "update doctor_info set doctor_intro=%s,doctor_goodat=%s,doctor_level=%s,dept_name=%s " \
        #              "where doctor_name=%s and hospital_name=%s"
        # params = [
        #     self.get('doctor_intro'),
        #     self.get('doctor_goodAt'),
        #     self.get('doctor_level'),
        #     self.get('dept_name', '暂无'),
        #     self.get('doctor_name'),
        #     self.get('hospital_name'),
        #
        # ]
        return insert_sql, params


class DoctorRegInfoItem(scrapy.Item):
    """
    医生排班信息表
    doctor_name     医生名称
    hospital_name   所属医院名称
    dept_name       科室名称
    reg_info        排班信息
    update_time     更新时间
    doctor_id       医生ID
    dept_id         科室ID
    hospital_id     医院ID
    gmt_created     创建时间
    gmt_modified    更改时间
    """
    doctor_name = scrapy.Field()
    hospital_name = scrapy.Field()
    dept_name = scrapy.Field()
    reg_info = scrapy.Field()
    dataSource_from = scrapy.Field()
    crawled_url = scrapy.Field()
    update_time = scrapy.Field()
    doctor_id = scrapy.Field()
    dept_id = scrapy.Field()
    hospital_id = scrapy.Field()
    gmt_created = scrapy.Field()
    gmt_modified = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into doctor_reg_info(doctor_name,hospital_name,dept_name,reg_info,dataSource_from," \
                     "crawled_url,update_time,doctor_id,dept_id,hospital_id,gmt_created,gmt_modified) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) " \
                     "on duplicate key update update_time=values(update_time)"
        params = [
            self.get('doctor_name', '暂无,出现异常'),
            self.get('hospital_name', '暂无,出现异常'),
            self.get('dept_name', '暂无,出现异常'),
            self.get('reg_info'),
            self.get('dataSource_from'),
            self.get('crawled_url'),
            self.get('update_time'),
            self.get('doctor_id'),
            self.get('dept_id'),
            self.get('hospital_id'),
            self.get('gmt_created'),
            self.get('gmt_modified')
        ]
        return insert_sql, params


class HospitalAliasItem(scrapy.Item):
    """
    医院别名表
    id                       id(自增)
    hospital_name            所属医院名称
    hospital_alisename       科室名称
    update_time             更新时间
    """
    hospital_name = scrapy.Field()
    hospital_alias_name = scrapy.Field()
    dataSource_from = scrapy.Field()
    update_time = scrapy.Field()
    gmt_created = scrapy.Field()
    gmt_modified = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into hospital_alias(hospital_name,hospital_alisename,dataSource_from,crawled_url," \
                     "update_time,gmt_created,gmt_modified) values(%s,%s,%s,%s,%s,%s,%s)"
        params = [
            self.get('hospital_name', '暂无,出现异常'),
            self.get('hospital_alias_name', '暂无,出现异常'),
            self.get('dataSource_from'),
            self.get('crawled_url'),
            self.get('update_time'),
            self.get('gmt_created'),
            self.get('gmt_modified')
        ]
        return insert_sql, params


class ComprehensiveRankingItem(scrapy.Item):
    """
    中国医院科技应影响力排行
    综合排行item
    hospital_pro          省份
    ranking               排名
    hospital_name         医院名称
    tech_investment       科技投入
    tech_output           科技产出
    academic_influence    学术影响
    total_score           总分
    create_time           创建时间
    update_time           更新时间
    """
    hospital_pro = scrapy.Field()
    ranking = scrapy.Field()
    hospital_name = scrapy.Field()
    tech_investment = scrapy.Field()
    tech_output = scrapy.Field()
    academic_influence = scrapy.Field()
    total_score = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into comprehensive_ranking(hospital_pro,ranking,hospital_name,tech_investment," \
                     "tech_output,academic_influence,total_score,create_time,update_time) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [
            self.get('hospital_pro'),
            self.get('ranking'),
            self.get('hospital_name', '暂无,出现异常'),
            self.get('tech_investment'),
            self.get('tech_output'),
            self.get('academic_influence'),
            self.get('total_score'),
            self.get('create_time'),
            self.get('update_time'),
        ]
        return insert_sql, params


class SubjectRankingItem(scrapy.Item):
    """
    中国医院科技应影响力排行
    学科排行item
    subject               学科名称
    hospital_pro          省份
    ranking               排名
    hospital_name         医院名称
    tech_investment       科技投入
    tech_output           科技产出
    academic_influence    学术影响
    total_score           总分
    create_time           创建时间
    update_time           更新时间
    """
    subject = scrapy.Field()
    hospital_pro = scrapy.Field()
    ranking = scrapy.Field()
    hospital_name = scrapy.Field()
    tech_investment = scrapy.Field()
    tech_output = scrapy.Field()
    academic_influence = scrapy.Field()
    total_score = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into subject_ranking(subject,hospital_pro,ranking,hospital_name,tech_investment," \
                     "tech_output,academic_influence,total_score,create_time,update_time) " \
                     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [
            self.get('subject', '暂无,出现异常'),
            self.get('hospital_pro'),
            self.get('ranking'),
            self.get('hospital_name', '暂无,出现异常'),
            self.get('tech_investment'),
            self.get('tech_output'),
            self.get('academic_influence'),
            self.get('total_score'),
            self.get('create_time'),
            self.get('update_time'),
        ]
        return insert_sql, params


class AreaRankingItem(scrapy.Item):
    """
    中国医院科技应影响力排行
    地区排行item
    subject             学科名称
    hospital_pro        省份
    ranking             排名
    hospital_name       医院名称
    create_time         创建时间
    update_time         更新时间
    """
    subject = scrapy.Field()
    hospital_pro = scrapy.Field()
    ranking = scrapy.Field()
    hospital_name = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()

    def get_sql_info(self):
        insert_sql = "insert into area_ranking(subject,hospital_pro,ranking,hospital_name," \
                     "create_time,update_time) values(%s,%s,%s,%s,%s,%s)"
        params = [
            self.get('subject', '暂无,出现异常'),
            self.get('hospital_pro'),
            self.get('ranking'),
            self.get('hospital_name', '暂无,出现异常'),
            self.get('create_time'),
            self.get('update_time'),
        ]
        return insert_sql, params
