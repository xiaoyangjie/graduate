# coding=utf-8
"""
生成代码，采集特定元素
"""
__date__ = '2017/12/5'
__author__ = 'YJ'
__version__ = '1.0'
from pymongo import MongoClient
import requests
from Configure import *
from bs4 import BeautifulSoup
from lxml import etree

class CSDNGenerateCode(object):

    def __init__(self):
        self.mongoClient = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_WEBSITE_PARSE]
        self.mongoCode = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_CODE]
        self.mongoCode.delete_many({})
        self.storageElement()

    def storageElement(self):
        elementList = ELEMENT_LIST
        for i in elementList:
            result = {}
            result['elementName'] = i['name']
            result['elementContent'] = i['content']
            result['elementType'] = i['type']
            if isinstance(i['content'], (str,unicode)):
                result['elementResultType'] = 'string'
            if isinstance(i['content'], list):
                if isinstance(i['content'][0], (str,unicode)):
                    result['elementResultType'] = 'list'
                # if isinstance(i['content'][0], ):
                #     result['elementResultType'] = 'listDicString'

            self.mongoCode.insert(result)

    # def getElement(self, CSDNUrl):
    #     outcome = {}
    #     try:
    #         r = requests.get(CSDNUrl)
    #     except Exception:
    #         pass
    #     soup = BeautifulSoup(r.content, "lxml")
    #     outcome['url'] = "soup.find_all(class_=\'clearfix csdn-tracking-statistics\')[1].find('dd').find('a').get('href')"
    #     result = eval(outcome['url'])
    #     print result

    def generateProcedure(self):
        for eachElement in self.mongoCode.find():
            procedureList = []
            if isinstance(eachElement['elementContent'],list):
                contentList = eachElement['elementContent']
                commonList = []
                commonFatherNum = 0
                commonFatherLoc = 0
                content = contentList[0]
                data = None
                for i in self.mongoClient.find({'content': content}):
                    data = i
                if data == None:
                    print "数据无效"
                else:
                    commonList = data['fatherNumList']
                    content = contentList[1]
                    for i in self.mongoClient.find({'content': content}):
                        data = i
                    if data == None:
                        print "数据无效"
                    else:
                        length = len(data['fatherNumList']) - 1
                        while True:
                            if data['fatherNumList'][length] in commonList:
                                commonFatherNum = data['fatherNumList'][length]
                                commonFatherLoc = length
                                break
                            length -= 1
                _data = self.mongoClient.find_one({'num': commonFatherNum})

                ##################相对路径，弃用#####################################
                # if self.mongoClient.find({'class':_data['class'], 'tag' : _data['tag']}).count() == 1:
                #     ##说明唯一，可以使用相对路径。。。其实基本上，都会用相对路径，因为class基本上就是唯一的，但是有时是li这种情况，没有class
                #     # 为什么需要相对路径  ， 因为一般我们需要的内容都在内容块中的，减少其他路径对主内容块的干扰。
                #     procedure = {}
                #
                # else:
                #     for i in commonList:
                #         procedure = {}
                #         self.mongoClient.find_one({'num': i})
                ########################################################
                #不能使用相对路径，直接使用绝对路径

                data['fatherNumList'].append(data['num'])
                commonList = data['fatherNumList']
                for common in commonList:
                    procedure = {}
                    data = self.mongoClient.find_one({'num': common})

                    procedure['class'] = data['class']
                    procedure['type'] = 'find'
                    procedure['tag'] = data['tag']
                    procedure['num'] = 0

                    if self.mongoClient.find({'class': data['class'], 'tag': data['tag'], 'fatherNum': data['fatherNum']}).count() > 1:
                        locNum = 0
                        for father in self.mongoClient.find({'class': data['class'], 'tag': data['tag'], 'fatherNum': data['fatherNum']}):
                            if father['num'] == data['num']:
                                break
                            locNum += 1
                        procedure['num'] = locNum

                    if common == commonList[commonFatherLoc + 1]:
                        procedure['num'] = -1

                    procedureList.append(procedure)

                #最后定位元素的操作
                procedure = {}
                if eachElement['elementType'] == 'text':
                    procedure['type'] = 'getText'
                else:
                    procedure['type'] = 'get'
                    procedure['getElement'] = 'href'
                procedureList.append(procedure)

            if isinstance(eachElement['elementContent'], unicode):
                data = None
                content = eachElement['elementContent']
                print content
                for i in self.mongoClient.find({'content': content}):
                    data = i
                data['fatherNumList'].append(data['num'])
                commonList = data['fatherNumList']
                for common in commonList:
                    procedure = {}
                    data = self.mongoClient.find_one({'num': common})

                    procedure['class'] = data['class']
                    procedure['type'] = 'find'
                    procedure['tag'] = data['tag']
                    procedure['num'] = 0
                    
                    if self.mongoClient.find({'class': data['class'], 'tag': data['tag'], 'fatherNum': data['fatherNum']}).count() > 1:
                        locNum = 0
                        for father in self.mongoClient.find({'class': data['class'], 'tag': data['tag'], 'fatherNum': data['fatherNum']}):
                            if father['num'] == data['num']:
                                break
                            locNum += 1
                        procedure['num'] = locNum

                    procedureList.append(procedure)

                # 最后定位元素的操作
                procedure = {}
                if eachElement['elementType'] == 'text':
                    procedure['type'] = 'getText'
                else:
                    procedure['type'] = 'get'
                    procedure['getElement'] = 'href'
                procedureList.append(procedure)

            self.mongoCode.update({'elementName':eachElement['elementName']},{'$set':{'procedureList':procedureList}})

    def _generateProcedure(self):
        procedureList = []
        # if
        return procedureList


# if __name__ == '__main__':
#     api = CSDNGenerateCode()
#     api.generateProcedure()
    # api.getElement('http://blog.csdn.net/yown/article/details/51525035')
