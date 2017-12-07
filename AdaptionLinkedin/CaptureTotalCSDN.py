# coding=utf-8
"""
采集全网
"""
from CSDNGenerateCode import CSDNGenerateCode

__date__ = '2017/12/7'
__author__ = 'YJ'
__version__ = '1.0'

from pymongo import MongoClient
from pymongo.errors import PyMongoError
import requests
import requests.exceptions
from Configure import *
from bs4 import BeautifulSoup
from CSDNHtmlCapture import CSDNHtmlCapture


class CaptureTotalCSDN(object):

    def __init__(self):
        self.mongoCode = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_CODE]
        self.mongoUrl = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_URL]
        self.mongoCSDN = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_WEBSITE_CONTENT]
        self.mongoUrl.delete_many({})
        self.mongoUrl.insert({'isRead':False, 'url' : DEFAULT_URL})
        #######下面的变量以后写到单线程去##############
        self.result = {}
        self.elementName = ''
        self.elementResultType = ''

    def getContent(self):
        while True:
            originalUrl = self.mongoUrl.find_one({'isRead':False})
            if originalUrl == None:
                break
            try:
                r = requests.get(originalUrl['url'])
                self.result = {}
                self.elementName = ''
                for i in self.mongoCode.find():
                    self.elementName = i['elementName']
                    self.elementResultType = i['elementResultType']
                    if self.elementResultType in ('list', 'listDicString'):
                        self.result[self.elementName] = []
                    else:
                        self.result[self.elementName] = ""
                    procedureList = i['procedureList']
                    soup = BeautifulSoup(r.content, "lxml")
                    self._getContent(soup, procedureList, loc=0)
                    # try:
                    #     self._getContent(soup, procedureList, loc=0)
                    # except:
                    #     self.mongoUrl.update({'url': originalUrl['url']}, {'$set': {'isRead': True, 'isCapture': False}})

                #扩展链接
                if self.result.get('url'):
                    try:
                        for url in self.result['url']:
                            self.mongoUrl.insert({'isRead':False,'url':url})
                    except PyMongoError:
                        pass
                    self.result.pop('url')
                self.result['url'] = originalUrl['url']
                self.mongoCSDN.update({'url': originalUrl['url']},{'$set':self.result},upsert=True)
                self.mongoUrl.update({'url': originalUrl['url']},{'$set':{'isRead':True}})
            except requests.exceptions:
                pass

    def _getContent(self, soup, procedureList, loc=0):
        procedure = procedureList[loc]
        loc += 1
        if procedure['type'] == 'find':
            self.findAll(soup, tag=procedure['tag'], class_=procedure['class'], procedureList=procedureList, loc=loc, num=procedure['num'])
        if procedure['type'] == 'get':
            self.get(soup, getElement=procedure['getElement'], procedureList=procedureList, loc=loc)
        if procedure['type'] == 'getText':
            self.getText(soup, procedureList=procedureList, loc=loc)

    def findAll(self, soup, tag=None, class_= None, procedureList=None, loc=0, num=-1):
        """
        num为-1表示获取list列表的全部内容，如果不是-1，表示同级中标签与class无法区别，即无法准确定位。
        如<a href="ssss"></a>
          <a href="rrrr"></a>
        当需要后一个a的href时，无法使用find（只会找到第一个元素）
        :param soup:
        :param tag:
        :param class_:
        :param procedureList:
        :param loc:
        :param num:
        :return:
        """

        if num == -1:
            if class_:
                for i in soup.find_all(tag, attrs={'class' : class_}):
                    self._getContent(i, procedureList, loc=loc)
            else :
                for i in soup.find_all(tag):
                    self._getContent(i, procedureList, loc=loc)
        else:
            if class_:
                print class_,num
                soup = soup.find_all(tag, attrs={'class': class_})[num]
            else:
                soup = soup.find_all(tag)[num]
            self._getContent(soup, procedureList, loc=loc)

    def get(self, soup, getElement=None, procedureList=None, loc=0):
        element = soup.get(getElement)
        if self.elementResultType in ('list', 'listDicString'):
            self.result[self.elementName].append(element)
        elif self.elementResultType == 'string':
            self.result[self.elementName] = element
        elif self.elementResultType == 'listString':
            self.result[self.elementName] = self.result[self.elementName] + element

        print element

    def getText(self, soup, procedureList=None, loc=0):
        text = soup.text
        if self.elementResultType in ('list', 'listDicString'):
            self.result[self.elementName].append(text)
        elif self.elementResultType == 'string':
            self.result[self.elementName] = text
        elif self.elementResultType == 'listString':
            self.result[self.elementName] = self.result[self.elementName] + text
        print text

if __name__ == '__main__':
    CSDNHtmlCapture().htmlCapture()
    print 11111111111111111111
    api = CSDNGenerateCode()
    api.generateProcedure()
    print 2222222222222222222222
    api = CaptureTotalCSDN()
    api.getContent()