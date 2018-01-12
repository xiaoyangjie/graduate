# coding=utf-8
"""
实现CSDN网页html的采集
"""
import time
from pymongo import MongoClient
from pymongo.errors import PyMongoError

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
from Selenium import Selenium
from multiprocessing import Queue

class HtmlCapture(object):

    def __init__(self):
        self.findLocation = FindLocation()
        print MONGO_DEFAULT
        self.mongoClient = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_WEBSITE_PARSE]
        self.codeClient = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_CODE]
        # self.cookie = None
        self.result = {}
        self.urlRule = [0]
        self.websiteHead = 'https://'
        self.websiteDomain = None
        self.originalContent = None
        self.isSame = False
        self.uniqueClassTagList = {}
        self.totalUniqueClassTagNum = 0
        self.verifyUrl = None
        self.showFinishUrlQueue = Queue()

    def getDriver(self):
        try:
            self.driverAPI.quit()
        except:
            pass
        self.driverAPI = Selenium()

    def htmlCapture(self):
        print '++++++++++++++++++++++'
        self.mongoClient.delete_many({})
        print '----------------------'
        content = self.driverAPI.getPageSource()
        if content is None:
            return False
        content = str(BeautifulSoup(content, "lxml"))
        self.mongoClient.insert({'num': 0, 'tag': 'html', 'soup_str': content, 'fatherNum': -1, 'class': None,
                                 'isFinish': False, 'content': None, 'fatherNumList': [], 'imageUrlList' : []})
        self.findLocation.findAllTag()
        return True

    def extendCpature(self, labelList=None, urlsHost=MONGO_DEFAULT, urlsDatabase='yj', urlsCollection='Url',
                        contentHost=MONGO_DEFAULT, contentDatabase='yj', contentCollection='WebsiteContent',):

        self.urlsClient = MongoClient(urlsHost)[urlsDatabase][urlsCollection]
        self.contentClient = MongoClient(contentHost)[contentDatabase][contentCollection]
        self.labelList = labelList
        ###########################################################
        # originalUrl = 'https://book.qidian.com/info/1010496369'
        # self.websiteDomain = originalUrl.split('/')[2]
        # self.websiteHead = originalUrl.split('//')[0] + '//'

        ##############以后记得把这句话删掉############
        self.urlsClient.delete_many({})
        currentUrl = self.driverAPI.getCurrentUrl()
        self.websiteHead = currentUrl.split('//')[0] + '//'  #即https://
        self.websiteDomain = currentUrl.split('/')[2]
        self.urlRule = [0]
        self.genetorUrlRule()
        if self.urlRule != [0]:
            print u"可以扩展链接"
            ##############说明扩展链接的唯一性、可扩展性、随机性、可靠性、收敛性###################
            if self.verifyUrlRule():
                print '扩展规则有效'
                ##############以后记得把这句话删掉############
                # self.urlsClient.delete_many({})
                ###########################################
                self.urlsClient.update({'url': currentUrl},{'$set':{'isRead':False, 'url' : currentUrl}},upsert=True)
                #######下面的变量以后写到单线程去##############
                self.result = {}
                self.elementName = ''
                self.elementType = ''

                print u'++++++++++++++开始采集+++++++++++++++++++'
                self.contentClient.delete_many({})
                self.getContent()

    def getContent(self):
        while True:
            originalUrl = self.urlsClient.find_one({'isRead':False})
            if originalUrl == None:
                break
            try:
                pageSource = self.driverAPI.getUrl(originalUrl['url'])
                self.result = {}
                self.elementName = ''
                soup = BeautifulSoup(pageSource, "lxml")
                for label in self.labelList:
                    _label = self.codeClient.find_one({'elementName': label})
                    procedureList = _label['procedureList']
                    self.elementName = _label['elementName']
                    self.elementType = _label['elementType']

                    if self.elementType in ('list', 'listDicString'):
                        self.result[self.elementName] = []
                    else:
                        self.result[self.elementName] = None
                    try:

                        self._getContent(soup, procedureList, loc=0)
                    except :
                        print originalUrl['url'] + u":" + label + u"不存在"

                #扩展链接
                if self.urlRule != [0]:
                    self.extendUrls(soup)
                # if self.result.get('extendUrls'):
                #     try:
                #         for url in self.result['extendUrls']:
                #             self.urlsClient.insert({'isRead':False,'url':url})
                #     except PyMongoError:
                #         pass
                #     self.result.pop('extendUrls')
                self.result['url'] = originalUrl['url']
                self.contentClient.update({'url': originalUrl['url']},{'$set':self.result},upsert=True)
                self.urlsClient.update({'url': originalUrl['url']},{'$set':{'isRead':True}})
                self.showFinishUrlQueue.put(originalUrl['url'])
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
                for i in soup.find_all(tag, recursive=False):
                    self._getContent(i, procedureList, loc=loc)
        elif num == 0:
            if class_:
                soup = soup.find_all(tag, attrs={'class': class_})[num]
            else:
                soup = soup.find_all(tag, recursive=False)[num]
            self._getContent(soup, procedureList, loc=loc)
        elif num > 0:
            soup = soup.find_all(tag, recursive=False)[num]
            self._getContent(soup, procedureList, loc=loc)

    def get(self, soup, getElement=None, procedureList=None, loc=0):
        element = soup.get(getElement)
        if self.elementType in ('list', 'listDicString'):
            self.result[self.elementName].append(element)
        elif self.elementType == 'string':
            self.result[self.elementName] = element
        elif self.elementType == 'listString':
            self.result[self.elementName] = self.result[self.elementName] + element

        print element

    def getText(self, soup, procedureList=None, loc=0):
        text = soup.text
        if self.elementType in ('list', 'listDicString'):
            self.result[self.elementName].append(text)
        elif self.elementType == 'string':
            self.result[self.elementName] = text
        elif self.elementType == 'listString':
            self.result[self.elementName] = self.result[self.elementName] + text

        if self.originalContent == text: #主要是用于判断扩展链接内容是否相同，即是不是同一个链接
            self.isSame = True
        print text

    def getDomain(self):
        url = self.driverAPI.getCurrentUrl()
        return url.split('/')[2]

    def extendUrls(self, soup):
        """
        获取网页里的所有链接
        :param soup:
        :return:
        """
        for i in soup.find_all('a'):
            url = i.get('href')
            if url != None:
                self.dealUrl(url)

    def dealUrl(self, url):
        """
        处理链接，并判断链接是否满足扩展链接，满足的链接存入数据库中
        :param url:
        :return:
        """
        flag = True
        originalUrl = url
        if '?' in url:
            url = url.split('?')[0]

        urlList = url.split('/')
        if len(urlList) == self.urlRule[0]:
            for i in range(1, self.urlRule[0]):
                if self.urlRule[i]['type'] == 'fixed':
                    if urlList[i - 1] != self.urlRule[i]['value']:
                        flag = False
        else:
            flag = False

        if flag:
            if 'https:' in originalUrl or 'http:' in originalUrl:    #即https://www.linkedin.com/in/thomas7733/ 或者 http://www.linkedin.com/in/thomas7733/
                url = originalUrl
            elif '//' in originalUrl: #//www.linkedin.com/in/thomas7733/
                url = self.websiteHead + originalUrl.split('//')[1]
            else: #/in/sdada
                url = self.websiteHead + self.websiteDomain + originalUrl
            try:
                self.urlsClient.insert({'isRead':False, 'url' : url})
            except PyMongoError: #主要是为了防止链接重复的错误
                pass

    def genetorUrlRule(self):
        """
        产生url获取规则   urlRule= [2, {'type': 'fixed', 'value': 'subject'}, {'type': 'unfixed'}]
        :return:
        """
        pageSource = self.mongoClient.find_one({'num': 0})['soup_str']
        soup = BeautifulSoup(pageSource, 'lxml')
        validUrlsList = {}
        successNum = 0
        self.getUniqueClassTag()

        for i in soup.find_all('a'):
            originalUrl = i.get('href')
            url = originalUrl
            if url != None:
                if len(url.split('//')) == 1:
                    if url[0] == '/':
                        url = self.websiteHead + self.websiteDomain + url
                else:
                    if url.split('//')[0] == '': #//www.zhihu.com/pin/927216298040659968
                        url = self.websiteHead + url.split('//')[1]
                print '__________________________'
                print url

                totalNum = len(self.labelList)
                successNum = 0
                sameNum = 0

                self.result = {}
                self.elementName = ''
                urlBefore = self.driverAPI.getCurrentUrl() #用于判断链接是否是改变，防止有些链接不变，使得认为内容符合条件
                try:
                    # pageSource = requests.get(url).content
                    pageSource = self.driverAPI.getUrl(url)
                except:
                    continue
                if urlBefore == self.driverAPI.getCurrentUrl():
                    continue
                soup = BeautifulSoup(pageSource, "lxml")
                for label in self.labelList:
                    _label = self.codeClient.find_one({'elementName': label})
                    procedureList = _label['procedureList']
                    self.elementName = _label['elementName']
                    self.elementType = _label['elementType']

                    if self.elementType in ('list', 'listDicString'):
                        self.result[self.elementName] = []
                    else:
                        self.result[self.elementName] = None
                    try:
                        self.originalContent = _label['originalContent']
                        self.isSame = False
                        self._getContent(soup, procedureList, loc=0)
                        successNum += 1
                        if self.isSame:
                            sameNum += 1
                    except :
                        print url + u":" + label + u"不存在"
                if sameNum * 2 < len(self.labelList) and successNum > 0: #剔除同一个网页并且只少有一个标签获取
                    if not validUrlsList.has_key(originalUrl):
                        simiScore = self.similarity(soup)
                        labelScore = float(successNum) / totalNum
                        validUrlsList[originalUrl] = self.score(simiScore, labelScore)
                        print successNum, simiScore, labelScore, validUrlsList[originalUrl]
                        print '++++++++++++++'
                        print url
                        print '++++++++++++++'
                    # validUrlsList.add(originalUrl)


        validUrlsList = sorted(validUrlsList.items(), lambda x, y: cmp(y[1], x[1]))

        scoreList = []
        for i in validUrlsList:
            scoreList.append(i[1])
        print scoreList
        if self._urlRule(validUrlsList):
            print '产生了链路扩展规则'
            print self.urlRule
        ##########################

    def _urlRule(self, validUrlsList):
        flag = False #用于判断是否产生扩展链接
        if len(validUrlsList) <= 1:
            print "无法扩展链接"
            flag = False
        else:
            print validUrlsList
            print '++++++++++++++'
            for i in range(0, len(validUrlsList)):
                if flag:
                    break
                firstUrl = validUrlsList[i][0]
                for j in range(i + 1, len(validUrlsList)):
                    lastUrl = validUrlsList[j][0]
                    firstUrl = firstUrl.split('?')[0]
                    lastUrl = lastUrl.split('?')[0]
                    firstUrlList = firstUrl.split('/')
                    lastUrlList = lastUrl.split('/')
                    if len(firstUrlList) != len(lastUrlList):
                        print "url有问题:" + firstUrl + ',' + lastUrl
                    else:
                        self.urlRule[0] = len(firstUrlList)
                        for i in range(0, len(firstUrlList)):
                            if firstUrlList[i] == lastUrlList[i]:
                                self.urlRule.append({'type' : 'fixed', 'value' : firstUrlList[i]})
                            else:
                                self.urlRule.append({'type': 'unfixed'})

                        print self.urlRule
                        self.verifyUrl = validUrlsList[j][0]
                        flag = True
                        break
        return flag

    def _similarity(self):
        """
        网页的相似性比较
        :return:
        """
        client = MongoClient('mongodb://localhost:27020')['yj']['qidian']
        soup_str = self.mongoClient.find_one({'num' : 0})['soup_str']

        soup = BeautifulSoup(soup_str, 'lxml')
        uniqueClassTagList = {}
        totalNum = 0
        for data in self.mongoClient.find():
            if data['class'] != None:
                if len(soup.find_all(data['tag'], class_=data['class'])) == 1:
                    if uniqueClassTagList.has_key(data['tag']):
                        uniqueClassTagList[data['tag']].append(data['class'])
                    else:
                        uniqueClassTagList[data['tag']] = []
                        uniqueClassTagList[data['tag']].append(data['class'])
                    totalNum += 1
        print uniqueClassTagList, totalNum

        _totalNum = 0
        rateList = []
        for i in client.find():
            _totalNum = 0
            soup = BeautifulSoup(i['soup_str'], 'lxml')
            for key in uniqueClassTagList.keys():
                for j in uniqueClassTagList[key]:
                    if len(soup.find_all(key, class_=j)) == 1:
                        _totalNum += 1
            print '________________'
            print _totalNum, i['url'], i['originalUrl']
            # if self.mongoClient.find({'class': {'$regex': data['class']}}).count() == 1:
            rateList.append(float(_totalNum)/totalNum)
        print rateList

    def getUniqueClassTag(self):
        soup_str = self.mongoClient.find_one({'num': 0})['soup_str']
        soup = BeautifulSoup(soup_str, 'lxml')
        self.totalUniqueClassTagNum = 0
        self.uniqueClassTagList = {}
        for data in self.mongoClient.find():
            if data['class'] != None:
                if len(soup.find_all(data['tag'], class_=data['class'])) == 1:
                    if self.uniqueClassTagList.has_key(data['tag']):
                        self.uniqueClassTagList[data['tag']].append(data['class'])
                    else:
                        self.uniqueClassTagList[data['tag']] = []
                        self.uniqueClassTagList[data['tag']].append(data['class'])
                    self.totalUniqueClassTagNum += 1

    def similarity(self, soup):
        """
        网页的相似性比较
        :return:
        """
        _totalNum = 0
        rateList = []
        _totalNum = 0
        for key in self.uniqueClassTagList.keys():
            for j in self.uniqueClassTagList[key]:
                if len(soup.find_all(key, class_=j)) == 1:
                    _totalNum += 1
        print '________________'
        return float(_totalNum)/self.totalUniqueClassTagNum

    def score(self, simiScore, labelScore):
        num = labelScore * 0.8 + simiScore * 0.2
        return num

    def verifyUrlRule(self):
        """
        证明链接扩展规则的各种特性(积分公式的可靠性，扩展链接规则的唯一性（自定义），可扩展性（有很多其他链接），收敛性指的是链接有限)
        :return:
        """
        if len(self.verifyUrl.split('//')) == 1:
            if self.verifyUrl[0] == '/':
                self.verifyUrl = self.websiteHead + self.websiteDomain + self.verifyUrl
        else:
            if self.verifyUrl.split('//')[0] == '':  # //www.zhihu.com/pin/927216298040659968
                self.verifyUrl = self.websiteHead + self.verifyUrl.split('//')[1]
        print '__________________________'
        print self.verifyUrl

        try:
            self.driverAPI.getUrl(self.verifyUrl)
            if self.htmlCapture():
                urlRuleSave = self.urlRule
                self.urlRule = [0]
                self.genetorUrlRule()
                print '------------' , urlRuleSave
                print '--------------' , self.urlRule
                if urlRuleSave == self.urlRule:
                    return True
                else:
                    return False

        except:
            print 'url获取有问题'
            return False


htmlCaptureAPI = HtmlCapture()
# htmlCaptureAPI._similarity()
# htmlCaptureAPI.extendCpature(labelList=[u'作品信息', u'标签', u'字数', u'章节数', u'作者简介', u'月票数', u'作品讨论数'])