#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-6-13 下午2:24
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import pandas as pd
import os


class CsvToDict(object):

    now_path = os.path.dirname(__file__)

    def __init__(self, file_name):
        super(CsvToDict, self).__init__()
        self.file_name = file_name

    def read_file(self):
        """
        read data from csv
        """
        file_path = os.path.join('/home/cyzs/wksp/my_env/temp_file', self.file_name)
        # file_path = os.path.join('/home/fengh/wksp/crawler_project/common_crawlers/'
        #                          'haodaifu/haodaifu/spiders', self.file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError
        data = pd.read_csv(file_path,
                           iterator=True,
                           usecols=['doctor_id', 'doctor_name', 'h_pro', 'department_name']
                           )
        # data2 = pd.read_csv(file_path, index_col='doctor_id')
        # print(data2.head())
        # print(data2.info(memory_usage='deep'))
        chunk = data.get_chunk(20000)
        return chunk[11536:12000]


if __name__ == "__main__":
    excel_to_dict = CsvToDict('original_data2.csv')
    my_data = excel_to_dict.read_file()
    my_dict = my_data.to_dict(orient='records')
    print(my_dict)
    # for each_record in my_dict:
    #     print(each_record['doctor_id'], each_record['doctor_name'])
