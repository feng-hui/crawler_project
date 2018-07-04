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

    def read_file(self, size=None, use_cols=None):
        """
        :param size:chunk size
        :param use_cols:columns needed
        :return:chunk data
        """
        file_path = os.path.join('/home/cyzs/wksp/my_env/temp_file', self.file_name)
        # file_path = os.path.join('/home/fengh/wksp/crawler_project/haodaifu/haodaifu/my_data', self.file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError
        data = pd.read_csv(file_path,
                           iterator=True,
                           usecols=use_cols
                           )
        # data2 = pd.read_csv(file_path, index_col='doctor_id')
        # print(data2.head())
        # print(data2.info(memory_usage='deep'))
        chunk = data.get_chunk(size=size)
        # print(len(chunk))
        return chunk[2794:2795]


if __name__ == "__main__":
    excel_to_dict = CsvToDict('haodf_0703.csv')
    my_data = excel_to_dict.read_file(use_cols=['doctor_url'])
    my_dict = my_data.to_dict(orient='records')
    print(my_dict)
