# coding=utf-8
"""
模拟浏览器获取
"""
import os
__date__ = '2017/12/5'
__author__ = 'YJ'
__version__ = '1.0'

import time
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, NoSuchWindowException,TimeoutException

class Selenium(object):
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=os.getcwd() + '/adaptionCapture/selfAdaptionCaptureCode/chromedriver.exe')
        self.loginUrl = 'https://www.linkedin.com/uas/login'
        self.username = '1019177406@qq.com'
        self.password = 'yj15923365092'
        # self.login()
        print '+++++++++++++++++++++'
        print "领英登陆成功"
        print '+++++++++++++++++++++'

    def restart(self):
        self.driver = webdriver.PhantomJS(executable_path=os.getcwd() + '/adaptionCapture/selfAdaptionCaptureCode/phantomjs.exe')
        flag = True
        # if self.login():
        #     print "重启成功"

    # def login(self):
    #     """
    #     使用账户名和密码进行登录
    #     :param email:
    #     :param password:
    #     :return:登录成功返回true
    #     """
    #     flag = True
    #     try:
    #         self.driver.get(self.loginUrl)
    #         self.driver.find_element_by_id('session_key-login').send_keys(self.username)
    #         self.driver.find_element_by_id('session_password-login').send_keys(self.password)
    #         self.driver.find_element_by_css_selector('input#btn-primary.btn-primary').click()
    #         time.sleep(6)
    #     except:
    #         flag = False
    #     return flag

    # def getPageSource(self, url):
    #     flag = False
    #     while not flag:
    #         try:
    #             self.driver.get(url)
    #             time.sleep(3)
    #             ActionChains(self.driver).send_keys(Keys.END).perform()  # 拉到底
    #             time.sleep(3)
    #             flag = True
    #         except NoSuchWindowException:
    #             print "NoSuchWindowException"
    #             self.restart()
    #     return self.driver.page_source

    def getPageSource(self):
        return self.driver.page_source

driverAPI = Selenium()