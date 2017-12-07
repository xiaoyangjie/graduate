# coding=utf-8
"""
实现CSDN网页html的采集
"""
from pymongo import MongoClient

__date__ = '2017/12/5'
__author__ = 'YJ'
__version__ = '1.0'


import requests
from LocationElement import FindLocation
from Configure import *
from bs4 import BeautifulSoup

class CSDNHtmlCapture(object):

    def __init__(self):
        self.findLocation = FindLocation()
        self.mongoClient = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_WEBSITE_PARSE]
        self.mongoClient.delete_many({})

    def htmlCapture(self):
        try:
            r = requests.get(DEFAULT_URL)
        except Exception:
            pass
        self.mongoClient.insert({'num': 0, 'tag': 'html', 'soup_str': r.content, 'fatherNum': -1, 'class': None,
                                 'isFinish': False, 'content': None, 'fatherNumList' : []})
        # self.findLocation.setParam()
        self.findLocation.findAllTag()

# if __name__ == '__main__':
#     api = CSDNHtmlCapture()
#     api.htmlCapture()