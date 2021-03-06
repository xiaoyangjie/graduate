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
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, NoSuchWindowException,TimeoutException, \
    UnexpectedAlertPresentException


class Selenium(object):
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=os.getcwd() + '/adaptionCapture/selfAdaptionCaptureCode/chromedriver.exe')
        self.isRestart = True

    def restart(self):
        self.driver = webdriver.Chrome(executable_path=os.getcwd() + '/adaptionCapture/selfAdaptionCaptureCode/phantomjs.exe')


    def getUrl(self, url):
        flag = False
        while not flag:
            try:
                self.driver.get(url)
                time.sleep(3)
                ActionChains(self.driver).send_keys(Keys.END).perform()  # 拉到底
                time.sleep(3)
                flag = True
            except TimeoutException:
                print 'TimeoutException'
            except NoSuchWindowException:
                print "NoSuchWindowException"
                self.restart()
            except UnexpectedAlertPresentException:
                alert = self.driver.switch_to.alert
                alert.accept()
        return self.driver.page_source

    def getPageSource(self):
        content = None
        try:
            content = self.driver.page_source
        except NoSuchWindowException:
            pass
        except UnexpectedAlertPresentException:
            alert = self.driver.switch_to.alert
            alert.accept()
            content = self.driver.page_source
        return content

    def getCurrentUrl(self):
        try :
            current_url = self.driver.current_url
        except UnexpectedAlertPresentException:
            alert = self.driver.switch_to.alert
            alert.accept()
            current_url = self.driver.current_url
        return current_url

    def quit(self):
        self.driver.quit()