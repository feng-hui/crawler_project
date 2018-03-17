# -*- coding: utf-8 -*-
# @author = 'Feng_hui'
# @time = '2018/3/6 8:41'
# @email = 'fengh@asto-inc.com'
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import logging


class F139Login(object):

    def __init__(self, username, password):
        """
        初始化,获取富宝登录账号与密码
        """
        self.username = username
        self.password = password

    def login(self):
        """
        登录模块1:使用selenium、PhantomJS
        """
        driver = webdriver.PhantomJS(executable_path='C:\\Users\\Administrator\\AppData\\Roaming\\npm\\'
                                                     'node_modules\\phantomjs\\lib\\phantom\\bin\\phantomjs.exe')
        driver.get('http://passport.f139.com/')
        # print(driver.get_cookies())
        f139_cookies = self.to_login(driver)
        return f139_cookies

    def login2(self):
        """
        登录模块2:使用selenium与headless chrome
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path='E:\\wksp\\test_module\\python3_test\\f139\\cralwers'
                                                  '\\chromedriver_win32\\chromedriver.exe',
                                  chrome_options=chrome_options)
        driver.get('http://passport.f139.com/')
        # print(driver.get_cookies())
        f139_cookies = self.to_login(driver)
        return f139_cookies

    def to_login(self, driver):
        """登录"""
        try:
            driver.find_element_by_name("userName").send_keys(self.username)
        except NoSuchElementException:
            logging.error("没有这个元素,请检查name是否正确")
        except Exception as e:
            logging.error("获取用户名失败,原因是: ".format(e))

        try:
            driver.find_element_by_name("passWord").send_keys(self.password)
        except NoSuchElementException:
            logging.error("没有这个元素,请检查name是否正确")
        except Exception as e:
            logging.error("获取密码失败,原因是：", format(e))

        driver.find_element_by_name("Submit").click()
        cookies = [(item['name'], item['value']) for item in driver.get_cookies()]
        # print(cookies)
        # cookies = ';'.join(cookies)
        f139_cookies = {name: value for name, value in cookies}
        return f139_cookies


if __name__ == "__main__":
    login = F139Login('Judyhe', '123456')
    print(login.login2())