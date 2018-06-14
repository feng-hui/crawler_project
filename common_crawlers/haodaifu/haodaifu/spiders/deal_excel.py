#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @time   : 18-6-13 下午2:24
# @author : Feng_Hui
# @email  : capricorn1203@126.com
import pandas as pd
import os
# import json


class ExcelToDict(object):

    now_path = os.path.dirname(__file__)

    def __init__(self, file_name):
        super(ExcelToDict, self).__init__()
        self.file_name = file_name

    def read_file(self):
        """
        read data from excel
        """
        file_path = os.path.join(self.now_path, self.file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError
        data = pd.read_csv(file_path, iterator=True, sep=',')
        chunk = data.get_chunk(1000)
        return chunk

    def exchange_type(self):
        """
        change file type
        """
        pass


if __name__ == "__main__":
    excel_to_dict = ExcelToDict('original_data.csv')
    my_data = excel_to_dict.read_file()
    my_dict = my_data.to_dict(orient='index')
    # my_json = json.dumps(my_dict)
    data_list = ['{0} {1} {2}'.format(value['doctor_name'],
                                      value['h_pro'].replace('\\N', '').strip(),
                                      value['department_name']).replace('\\N', '').strip()
                 for value in my_dict.values()]
    print(data_list)
