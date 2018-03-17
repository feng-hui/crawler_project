# -*- coding: utf-8 -*-
import time
from .f139_price import F139Price
from ..config import f139_config, f139_logger

__author__ = 'Feng_hui'
__time__ = '2018/2/9 15:23'


class F139JsFt(F139Price):
    job_name = '富宝报价抓取——江苏地区废铜价格'
    data_url = 'http://data.f139.com/list.do?pid=&vid=16&qw=3:37'
    title = '{}{}'.format(f139_config.prefix_of_title, "江苏地区废铜价格")

    def run(self):
        f139_logger.logger.info('正在抓取: {}'.format(self.job_name))
        if not self.is_login():
            f139_logger.info('未登录,开始登录……')
            self.login()
        selector = self.get_selector(self.data_url)
        name = selector.xpath('//div[@id="#"]/div/table/tr/td[position()=1]/a')
        area = selector.xpath('//div[@id="#"]/div/table/tr/td[position()=2]')
        rate = selector.xpath('//div[@id="#"]/div/table/tr/td[position()=3]')
        price = selector.xpath('//div[@id="#"]/div/table/tr/td[position()=5]')
        up_or_down = selector.xpath('//div[@id="#"]/div/table/tr/td[position()=6]')
        # 第一列：地区
        first_column = [each_row.xpath('text()')[0].strip().replace('地区/来源', '省份')
                        for each_row in area]
        # 第二列：含量
        second_column = [each_row.xpath('text()')[0].strip() for each_row in rate]
        # 第三列：品名
        third_column = ['品名']
        third_column.extend([each_row.xpath('text()')[0].strip() for each_row in name])
        # 第四列：价格
        fourth_column = [each_row.xpath('text()')[0].strip().replace('价格', '不含税价（元/吨）')
                         for each_row in price]
        # 第四列：涨跌
        fifth_column = []
        for each_row in up_or_down:
            text_flat = each_row.xpath('text()')
            # print(text_flat)
            if text_flat and text_flat != ['\r\n\t\t\t\t\t\t\t', '\r\n\t\t\t\t\t']:
                fifth_column.append(text_flat[0].strip())
            else:
                # print(each_row.xpath('string(.)'))
                text_rise = each_row.xpath('font[@class="up"]/text()')
                # print(text_rise)
                if text_rise:
                    fifth_column.append('&uarr;' + text_rise[0].strip())
                else:
                    text_fall = each_row.xpath('font[@class="down"]/text()')
                    # print(text_fall)
                    if text_fall:
                        # print(text_fall)
                        fifth_column.append('&darr;' + text_fall[0].strip())
                    else:
                        fifth_column.append('')
        # 整合表格
        table = zip(first_column[0:4], second_column[0:4], third_column[0:4], fourth_column[0:4], fifth_column[0:4])
        single_tr = []

        # 构造表格
        for each_row in table:
            # print(each_row, type(each_row))
            single_tr.append('<tr>' + ''.join(['<td>' + str(each) + '</td>' for each in each_row]) + '</tr>')
        table_content = '<table>' + ''.join(single_tr) + '</table>'
        print(table_content)
        return table_content


if __name__ == "__main__":
    start_time = time.time()
    f139_price = F139JsFt()
    f139_price.run()
    # import os
    # print(os.pardir)
    print('总共用时：', time.time() - start_time)