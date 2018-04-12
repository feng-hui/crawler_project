# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/4/11 19:24'
# @email = 'fengh@asto-inc.com'
from cralwers import jobs, config
import logging
from requests import Session
import time
from http import cookiejar


class MainFunc(object):
    """
    通过cookiejar保存cookies
    """
    session = Session()
    session1 = Session()
    session.cookies = cookiejar.LWPCookieJar('./data/f139_cookies2.config')

    def __init__(self):
        super(MainFunc, self).__init__()

    def main(self):
        """富宝废有色抓取主函数2"""
        try:
            self.session.cookies.load(ignore_discard=True)
            logging.info("成功加载本地cookies")
            # for each_crawler in jobs.all_fys_crawlers:
            #     try:
            #         job = each_crawler(self.session)
            #         job.run()
            #         time.sleep(3)
            #     except Exception as e:
            #         logging.info("抓取过程中出错了,报错的原因是：{}".format(str(e)))
            #         continue
        except IOError:
            logging.info("未能成功加载cookies")
        except FileNotFoundError:
            logging.info("本地不存在f139_cookies2.config这样的文件")
        finally:
            for each_crawler in jobs.all_fys_crawlers:
                try:
                    job = each_crawler(self.session1)
                    job.run()
                    time.sleep(3)
                except Exception as e:
                    logging.info("抓取过程中出错了,报错的原因是：{}".format(str(e)))
                    continue
            self.session1.cookies.save()


if __name__ == "__main__":
    main_func = MainFunc()
    main_func.main()
