# coding=utf-8
"""
生成代码，采集特定元素
"""
import re

__date__ = '2017/12/5'
__author__ = 'YJ'
__version__ = '1.0'
from pymongo import MongoClient
import requests
from Configure import *
from bs4 import BeautifulSoup
from lxml import etree

class GenerateCode(object):

    def __init__(self):
        self.mongoClient = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_WEBSITE_PARSE]
        self.mongoCode = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_CODE]

    def storageElement(self, name, content, _type='text'):
        result = {}
        result['elementName'] = name
        result['elementContent'] = content
        result['elementType'] = _type
            # if isinstance(i['content'], (str,unicode)):
            #     result['elementResultType'] = 'string'
            # if isinstance(i['content'], list):
            #     if isinstance(i['content'][0], (str,unicode)):
            #         result['elementResultType'] = 'list'
                # if isinstance(i['content'][0], ):
                #     result['elementResultType'] = 'listDicString'

        self.mongoCode.insert(result)

    def getMayContent(self, content):
        """
        获取最后3条内容？？为什么，凭什么..基本上满足了,给用户看，让用户知道这些内容在哪里
        逻辑：
        首先精确查询，如果遇到一模一样的两个内容，每个返回3个，同时在页面上增加一个按钮，表示还有。
        如果精确查询查不到，那么就模糊查询。
        :param content:
        :return:  返回的数据是[[{},{}],[{},{}]]这种形式
        """
        contentList = []
        ####使用完全匹配可以缩短时间################
        contentList = self.getMayContentComplete(content)
        if contentList == []:
            print "开始模糊匹配"
            contentList = self.getMayContentRegex(content)
        return contentList

    def getMayContentComplete(self, content):
        contentList = []
        content = self.dealSpecialSymbol(content)
        numList = []
        for _each in self.mongoClient.find({'content': content}):
            numList.append(_each['num'])
        #####################获取不同分支节点#############################################
        _numList = []
        while numList != []:
            fatherNumList = self.mongoClient.find_one({'num' : numList[len(numList) - 1]})['fatherNumList']
            _numList.append(numList[len(numList) - 1])
            numList.pop()
            __numList = []
            for num in numList:
                if num in fatherNumList:
                    __numList.append(num)  # 获取相同的分支
            for num in __numList:
                numList.remove(num)  # 去掉相同的分支

        numListAll = []
        _num = 0
        for num in _numList:
            data = self.mongoClient.find_one({'num' : num})
            numList = data['fatherNumList']
            numList.append(num)
            if len(numList) > 2:
                numList = sorted(numList)[len(numList) - 3: len(numList)]
            else:
                numList = sorted(numList)
            print numList
            numList = sorted(numList, reverse=True)
            numListAll.append(numList)
            _num += 1

        ################获取内容#######################################
        for _numList in numListAll:
            _contentList = []
            for num in _numList:
                data = self.mongoClient.find_one({'num': num})
                data.pop('_id')
                _contentList.append(data)
            contentList.append(_contentList)
        return contentList

    def getMayContentRegex(self, content):
        dataList = []
        contentList = self.dealEnter(self.dealSpecialSymbol(content))

        ###############################获取满足正则匹配的节点##########################
        numListAll = []
        for _content in contentList:
            numList = []
            for _each in self.mongoClient.find({'content': {'$regex' : _content}}):
                numList.append(_each['num'])
            if numList != []:
                numListAll.append(numList)
        numList = []
        flag = True
        if numListAll != []:
            for num in numListAll[0]:
                flag = True
                for i in numListAll:
                    if num not in i :
                        flag = False
                        break
                if flag:
                    numList.append(num)

        #####################获取不同分支节点#############################################
            _numList = []
            while numList != []:
                fatherNumList = self.mongoClient.find_one({'num':numList[len(numList) - 1]})['fatherNumList']
                _numList.append(numList[len(numList) - 1])
                numList.pop()
                __numList = []
                for num in numList:
                    if num in fatherNumList:
                        __numList.append(num) #获取相同的分支
                for num in __numList:
                    numList.remove(num)  #去掉相同的分支
            numListAll = []
            print _numList
            _num = 0
            for num in _numList:
                data = self.mongoClient.find_one({'num' : num})
                numList = data['fatherNumList']
                numList.append(num)
                if len(numList) > 2:
                    numList = sorted(numList)[len(numList) - 3: len(numList)]
                else:
                    numList = sorted(numList)
                numList = sorted(numList, reverse=True)
                numListAll.append(numList)
                _num += 1
            for _numList in numListAll:
                _contentList = []
                for num in _numList:
                    data = self.mongoClient.find_one({'num': num})
                    data.pop('_id')
                    _contentList.append(data)
                dataList.append(_contentList)

        return dataList

    def dealSpecialSymbol(self, content):
        """
        处理特殊字符 ['\\', '.', '^', '$', '*', '+', '?' '{', '}', '[', ']', '|', '(', ')']
        :param content:
        :return:
        """
        strList = ['\\', '.', '^', '$', '*', '+', '?' '{', '}', '[', ']', '|', '(', ')']
        for i in strList:
            content = content.replace(i, '\\' + i)
        return content

    def dealEnter(self, content):
        """
        处理掉空格，回车等,进行分段
        :param content:
        :return:
        """
        content = content.replace('\n', ' ').replace('\t', ' ')
        return content.split(' ')


    def generateProcedure(self, name, num, _type):
        result = {}
        procedureList = []
        result['elementName'] = name
        result['elementType'] = _type
        data = self.mongoClient.find_one({'num': int(num)})
        data['fatherNumList'].append(data['num'])
        commonList = data['fatherNumList']
        for common in commonList:
            procedure = {}
            data = self.mongoClient.find_one({'num': common})
            procedure['class'] = data['class']
            procedure['type'] = 'find'
            procedure['tag'] = data['tag']
            procedure['num'] = 0
            if self.mongoClient.find({'class': data['class']}).count() == 1:
                procedureList = []
            ##找出绝对路径
            elif self.mongoClient.find({'tag': data['tag'], 'fatherNum': data['fatherNum']}).count() > 1:
                locNum = 0
                for father in self.mongoClient.find({'tag': data['tag'], 'fatherNum': data['fatherNum']}):
                    if father['num'] == data['num']:
                        break
                    locNum += 1
                procedure['num'] = locNum

            procedureList.append(procedure)

        # 最后定位元素的操作
        procedure = {}
        if _type == 'image':
            procedure['type'] = 'getImage'
        if _type == 'text':
            procedure['type'] = 'getText'
        procedureList.append(procedure)

        result['procedureList'] = procedureList

        self.mongoCode.update({'elementName': name},{'$set':result},upsert=True)

generateCodeAPI = GenerateCode()

