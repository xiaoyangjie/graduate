# coding=utf-8

"""
获取mongodb的数据，返回给前端，或者存入redis中，在从redis（缓存）中获取数据，返给前端。

"""
__author__ = 'YJ'
__version__ = '1.0'
__date__ = '2017/11/16'
from ..TwitterUserCapture.TwitterUserCapture.common.constants import *
from pymongo import MongoClient

# class GetMongoData(object):
#     def __init__(self):
#         pass
#         # self.mongoClient = MongoClient(MONGOHOST)[][]

def infoGet(userDatabase=None,userCollection=None,screenNameList=None,accountIdList=None,tweetDatabase=None,
            tweetCollection=None,keywords=None,_type=None,page = 0):
    """
    只有两种类型，user与tweet
    :param userDatabase:
    :param userCollection:
    :param screenNameList:
    :param accountIdList:
    :param tweetDatabase:
    :param tweetCollection:
    :param keywords:
    :param _type:
    :return:
    """
    result = []
    num = 5  #每次返回的条数
    if _type in ('userInfo','userFriends','userFollowers'):
        _assert() #判断数据库是否存在
        userClient = MongoClient(MONGOHOST)[userDatabase][userCollection]
        if screenNameList is not None:
            for screenName in screenNameList:
                user = userClient.find_one({'screen_name': screenName})
                user.pop('_id')
                result.append(user)
        elif accountIdList is not None:
            for accountId in accountIdList:
                user = userClient.find_one({'id':accountId})
                user.pop('_id')
                result.append(user)
        else:
            for user in userClient.find().skip(page).limit(num):
                user.pop('_id')
                result.append(user)

    if _type in ('filterTweet','historyTweet','userRealtimeTweet'):
        _assert()  # 判断数据库是否存在
        tweetClient = MongoClient(MONGOHOST)[tweetDatabase][tweetCollection]
        for tweet in tweetClient.find().skip(page).limit(num):
            tweet.pop('_id')
            result.append(tweet)

    return result

def realtimeInfoGet(tweetDatabase=None,tweetCollection=None):
    """
    现在先从mongo中取，以后从redis中取数据吧
    :param tweetDatabase:
    :param tweetCollection:
    :return:
    """
    ################判断实时数据采集是否在运行#######################
    flag = False
    result = {}
    processClient = MongoClient(MONGOHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    for process in processClient.find({'state':'running'}):
        if process['tweetDatabase'] == tweetDatabase and process['tweetCollection'] == tweetCollection:
            flag = True
            break
    if flag:
        for tweet in MongoClient(MONGOHOST)[tweetDatabase][tweetCollection].find().sort('id',-1).limit(1):
            tweet.pop('_id')
            result = tweet
    return result

#func1:判断数据库是否存在
#func2:从数据库中获取信息
# def userInfoGet():
def _assert():
    pass