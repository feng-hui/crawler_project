# -*- coding: utf-8 -*-
import logging
from .f139_price import F139Price
from ..config import f139_config, f139_logger

__author__ = "Feng_Hui"
__time__ = "2018.02.08 08:30"
__remarks__ = "富宝报价抓取-模拟登录获取报价"
logger = logging.basicConfig()


class F139Fdp(F139Price):

    job_name = '富宝报价抓取——全国各地废电瓶价格行情'
    data_url = "http://data.f139.com/list.do?vid=137"
    title = '{}{}'.format(f139_config.prefix_of_title, "全国各地废电瓶价格行情")

    def run(self):
        f139_logger.logger.info('正在抓取: {}'.format(self.job_name))
        if not self.is_login():
            f139_logger.info('未登录,开始登录……')
            self.login()
        selector = self.get_selector(self.data_url)
        area = selector.xpath('//div[@id="#"]/div/table/tr/td[position()=2]')
        price = selector.xpath('//div[@id="#"]/div/table/tr/td[position()=4]')
        up_or_down = selector.xpath('//div[@id="#"]/div/table/tr/td[position()=5]')
        # content2 = selector.xpath('//div[@id="#"]/div/table/tr/td[position()>3]')
        # 第一列：地区
        first_column = [each_row.xpath('text()')[0].strip().replace('地区/来源', '地区') for each_row in area[0:18]]
        # 第二列：价格区间
        second_column = [each_row.xpath('text()')[0].strip().replace('价格', '价格区间') for each_row in price[0:18]]
        # 第三列：单位
        third_column = ['单位']
        third_column.extend(['元/吨' for _ in range(17)])
        # 第四列：涨跌
        fourth_column = []
        for each_row in up_or_down[0:18]:
            text_flat = each_row.xpath('text()')
            # print(text_flat)
            if text_flat and text_flat != ['\r\n\t\t\t\t\t\t\t', '\r\n\t\t\t\t\t']:
                fourth_column.append(text_flat[0].strip())
            else:
                # print(each_row.xpath('string(.)'))
                text_rise = each_row.xpath('font[@class="up"]/text()')
                # print(text_rise)
                if text_rise:
                    fourth_column.append('&uarr;' + text_rise[0].strip())
                else:
                    text_fall = each_row.xpath('font[@class="down"]/text()')
                    # print(text_fall)
                    if text_fall:
                        # print(text_fall)
                        fourth_column.append('&darr;' + text_fall[0].strip())
                    else:
                        fourth_column.append('')
        # 整合表格
        table = zip(first_column, second_column, third_column, fourth_column)
        single_tr = []

        # 构造表格
        for each_row in table:
            # print(each_row, type(each_row))
            single_tr.append('<tr>' + ''.join(['<td>' + str(each) + '</td>' for each in each_row]) + '</tr>')
        table_content = '<table>' + ''.join(single_tr) + '</table>'
        print(table_content)
        return table_content


# if __name__ == "__main__":
#     start_time = time.time()
#     f139_price = F139Price()
#     # f139_price.run()
#     print(f139_price.is_login2())
#     # import os
#     # print(os.pardir)
#     print('总共用时：', time.time() - start_time)
