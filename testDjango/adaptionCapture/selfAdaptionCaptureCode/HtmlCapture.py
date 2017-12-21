# coding=utf-8
"""
实现CSDN网页html的采集
"""
import time
from pymongo import MongoClient

__date__ = '2017/12/5'
__author__ = 'YJ'
__version__ = '1.0'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, NoSuchWindowException,TimeoutException
import requests.exceptions
import requests
from LocationElement import FindLocation
from Configure import *
from bs4 import BeautifulSoup
import os
from Selenium import driverAPI

class HtmlCapture(object):

    def __init__(self):
        self.findLocation = FindLocation()
        self.mongoClient = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_WEBSITE_PARSE]
        self.mongoClient.delete_many({})

    def htmlCapture(self, url):
        try:
            print url
            print '+++++++++++++++++++'
            content = driverAPI.getPageSource()
            content = str(BeautifulSoup(content, "lxml"))
            fp = open(os.getcwd() + '/adaptionCapture/templates/adaptionCapture/template.html','w')
            fp.write(content)
            fp.close()
            self.mongoClient.insert({'num': 0, 'tag': 'html', 'soup_str': content, 'fatherNum': -1, 'class': None,
                                     'isFinish': False, 'content': None, 'fatherNumList': [], 'imageUrlList' : []})
            self.findLocation.findAllTag()
        except requests.exceptions:
            pass
