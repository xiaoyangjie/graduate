# coding=utf-8
from pymongo import MongoClient
import time
from bs4 import BeautifulSoup
from test import *
from Configure import *

"""
实现每个需要采集内容的定位

方法：
广度优先

格式 :
[[tag,class,soup],[],[]]

"""

class FindLocation(object):
    """

    """

    def __init__(self):
        """,

        """
        #1、以前称作教育背景，现在叫教育经历（用内容来进一步确认）2、background_summary有很大程度不同。3、数据存储格式最好就两种，就string和list_dic_string。对于需要整形或者其他的类型数据，用时再转换。
        self.increase_num = 0
        self.outcome = {}
        self.mongoClient = MongoClient(MONGO_DEFAULT)[MONGO_DB][MONGO_WEBSITE_PARSE]
        # self.tagsList = {'num':1'tag':'body','soup_str':self.soupTotal,'fatherNum':0,'class':None} #num是唯一的

    def setParam(self,):
        self.mongoClient = MongoClient(MONGO_DEFAULT)['yj']['CSDNUrl']
        self.increase_num = 0
        # self.aim = {'name': 'Alexis Madrigal', 'location': 'Oakland, California',
        #             'background_summary': 'I write about technology and the cultures that animate it.',
        #             'title': 'The Atlantic', 'work_experience': {'': ''}}

    def getElementFromDatabase(self): #self.aim的获取
        pass

    """
    将每一个标签的内容保存在数据库中。
    soup_str,fatherNum,className,content,tag,num,isFinish共7个标签
    """
    def findAllTag(self):
        while True:
            data = self.mongoClient.find_one({'isFinish':False})
            if data is None:
                break
            soup_str = data['soup_str']
            fatherNum = data['num']
            fatherNumList = data['fatherNumList']
            className = None
            content = None
            soup = BeautifulSoup(soup_str, "lxml")
            _soup = soup.find_all(data['tag'])[0]
            for i in _soup.children:
                print i.name
                if i.name != None:
                    try:
                        classNameList = i.get('class')
                        ###########将list数据变为 string的class#########################
                        if classNameList != [] and classNameList != None:
                            length = len(classNameList)
                            count = 0
                            className = ""
                            while True:
                                className = className + classNameList[count]
                                count += 1
                                if (count == length):break
                                else:
                                    className = className + ' '
                        else:
                            className = None
                        ############################################

                    except:pass
                    ################获取文本################
                    try:
                        content = i.text
                    except:pass
                    #################获取图片链接##########
                    imageUrlList = []
                    try:
                        for _imgUrl in i.find_all('img'):
                            if _imgUrl.get('src') != None:
                                imageUrlList.append(_imgUrl.get('src'))
                    except:
                        pass
                    fatherNumList.append(fatherNum)
                    self.mongoClient.update({'num':self.increase_num+1},{'isFinish': False,'content':content,'num':self.increase_num+1,'soup_str':str(i),
                                            'tag':i.name,'class':className,'fatherNum':fatherNum, 'fatherNumList': fatherNumList, 'imageUrlList' : imageUrlList},upsert=True)
                    fatherNumList.pop()
                    self.increase_num += 1
            self.mongoClient.update({'num': fatherNum},{'$set':{'isFinish': True}})

                    # try:
                    #     if i.text == aim:
                    #         print i
                    #         self.outcome['name'] = "soupTotal.find_all(%s).text" %className[0]
                    #         # result = eval(outcome['name'])
                    #         # print result
                    #         time.sleep(10)
                    # except:
                    #     pass
                    # self.tagsList.append([i.name,className,i])

# api = FindLocation()
# api.setParam()
# api.findAllTag()

