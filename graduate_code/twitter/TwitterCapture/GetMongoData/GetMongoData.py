# coding=utf-8

"""
获取mongodb的数据，返回给前端，或者存入redis中，在从redis（缓存）中获取数据，返给前端。

"""
__author__ = 'YJ'
__version__ = '1.0'
__date__ = '2017/11/16'
from elasticsearch import Elasticsearch
from pymongo import MongoClient

from twitter.TwitterCapture.constants import *


# class GetMongoData(object):
#     def __init__(self):
#         pass
#         # self.mongoClient = MongoClient(MONGOHOST)[][]

def infoGet(userHost=None,userDatabase=None,userCollection=None,screenName=None,accountId=None,tweetId=None,
            tweetHost=None,tweetDatabase=None,tweetCollection=None,keywords=None,_type=None,page = 0,
            extend=None):
    """

    :param userHost:
    :param userDatabase:
    :param userCollection:
    :param screenName:
    :param accountId:
    :param tweetId:
    :param tweetHost:
    :param tweetDatabase:
    :param tweetCollection:
    :param keywords:
    :param _type:
    :param page:
    :return:
    """
    result = []
    num = 5  #每次返回的条数
    if _type == 'userInfoSearch':
        _assert() #判断数据库是否存在
        userClient = MongoClient(userHost)[userDatabase][userCollection]
        if screenName:
            user = userClient.find_one({'screen_name': screenName})
            user.pop('_id')
            result.append(user)
        elif accountId:
            user = userClient.find_one({'id':accountId})
            user.pop('_id')
            result.append(user)

    if _type == 'tweetInfoSearch':
        _assert()  # 判断数据库是否存在
        tweetClient = MongoClient(tweetHost)[tweetDatabase][tweetCollection]
        if tweetId:
            tweet = tweetClient.find_one({'id': tweetId})
            tweet.pop('_id')
            result.append(tweet)

    if _type == 'userFilterSearch':
        esClient = Elasticsearch(ES_HOST)
        queryAll = {
            "query": {
                "regexp": {
                    "description": keywords
                }
            }
        }
        index = userDatabase.lower()
        searched = esClient.search(index=index, doc_type=userCollection, body=queryAll)
        totalNum = searched['hits']['total']
        startLoc = page * num
        endLoc = (page + 1)* num
        for hit in searched['hits']['hits']:
            if startLoc < endLoc:
                result.append(hit['_source'])
                startLoc += 1

    if _type == 'tweetFilterSearch':
        esClient = Elasticsearch(ES_HOST)
        queryAll = {
            "query": {
                "regexp": {
                    "text": keywords
                }
            }
        }
        print tweetCollection
        searched = esClient.search(index=tweetDatabase.lower(), doc_type=tweetCollection, body=queryAll)
        totalNum = searched['hits']['total']
        startLoc = page * num
        endLoc = (page + 1) * num
        for hit in searched['hits']['hits']:
            if startLoc < endLoc:
                result.append(hit['_source'])
                startLoc += 1
        # else:
        #     for user in userClient.find().skip(page).limit(num):
        #         user.pop('_id')
        #         result.append(user)

    # if _type in ('filterTweet','historyTweet','userRealtimeTweet'):
    #     _assert()  # 判断数据库是否存在
    #     tweetClient = MongoClient(MONGOHOST)[tweetDatabase][tweetCollection]
    #     for tweet in tweetClient.find().skip(page).limit(num):
    #         tweet.pop('_id')
    #         result.append(tweet)

    return result

def realtimeInfoGet(processName=None):
    """
    现在先从mongo中取，以后从redis中取数据吧
    :return:
    """
    process = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_COLLECTION].find_one({'processName':processName})
    result = {}

    if process['_type'] in ['filterTweet','userRealtimeTweet']:
        for tweet in MongoClient(process['tweetHost'])[process['tweetDatabase']][process['tweetCollection']].find().sort('id',-1).limit(1):
            tweet.pop('_id')
            result = tweet
    return result

#func1:判断数据库是否存在
#func2:从数据库中获取信息
# def userInfoGet():
def _assert():
    pass