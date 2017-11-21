# coding=utf-8

from multiprocessing import Process
import psutil
from pymongo.errors import PyMongoError
import time
from pymongo import MongoClient
from program_code.TwitterCapture.TwitterUserCapture.TwitterUserCapture.common.constants import MONGOHOST,\
    PROCESS_DATABASE,PROCESS_COLLECTION,PROXY
from program_code.TwitterCapture.TwitterUserCapture.UserInfo import userInfo
from program_code.TwitterCapture.TwitterUserCapture.UserFriends import userFriends
from program_code.TwitterCapture.TwitterUserCapture.UserFollowers import userFollowers
from program_code.TwitterCapture.TwitterTweetCapture.FilterRealtimeTweet import filterRealtimeTweet
from program_code.TwitterCapture.TwitterTweetCapture.HistoryTweet import historyTweet
from program_code.TwitterCapture.TwitterTweetCapture.UserRealtimeTweet import realtimeTweet

def operation():
    """
    1、当Django重启时，重新启动任务集合中的所有正在运行程序。
    一般来说Django程序稳定后，是不会重启的，除非改版。
    2、启动一个守护进程（依赖于Django），用于观测程序是否在运行。
    :return:
    """
    #重启那些正在运行的程序
    restartProcess()

    #开启守护进程
    api = Process(target=daemon)
    api.start()

def restartProcess():
    processClient = MongoClient(MONGOHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    for process in processClient.find({'state':'running'}):
        kwargs = {}
        ###################对于每个采集功能，各自开始判断运行###########################
        if process['_type'] == 'userInfo':
            kwargs['screenNameList'] = process['screenNameList']
            kwargs['accountIdList'] = process['accountIdList']
            kwargs['proxyList'] = [PROXY]
            kwargs['userDatabase'] = process['userDatabase']
            kwargs['userCollection'] = process['userCollection']
            api = Process(target=userInfo, kwargs=kwargs)
            api.start()
            processClient.update({'processName':process['processName']},{'$set':{'pid':api.pid}})

        if process['_type'] == 'userFriends':
            kwargs['screenNameList'] = process['screenNameList']
            kwargs['accountIdList'] = process['accountIdList']
            kwargs['proxyList'] = [PROXY]
            kwargs['userDatabase'] = process['userDatabase']
            kwargs['userFriendsDatabase'] = process['userDatabase']
            kwargs['userFriendsCollection'] = process['userCollection']
            kwargs['userCollection'] = process['userCollection']
            api = Process(target=userFriends, kwargs=kwargs)
            api.start()
            processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'userFollowers':
            kwargs['screenNameList'] = process['screenNameList']
            kwargs['accountIdList'] = process['accountIdList']
            kwargs['proxyList'] = [PROXY]
            kwargs['userFollowersDatabase'] = process['userDatabase']
            kwargs['userFollowersCollection'] = process['userCollection']
            kwargs['userDatabase'] = process['userDatabase']
            kwargs['userCollection'] = process['userCollection']
            api = Process(target=userFollowers, kwargs=kwargs)
            api.start()
            processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'userRealtimeTweet':
            kwargs['tweetDatabase'] = process['tweetDatabase']
            kwargs['tweetCollection'] = process['tweetCollection']
            kwargs['proxyList'] = [PROXY]
            kwargs['userDatabase'] = kwargs['userDatabase']
            kwargs['userCollection'] = kwargs['userCollection']
            api = Process(target=realtimeTweet, kwargs=kwargs)
            api.start()
            processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'historyTweet':
                kwargs['tweetDatabase'] = process['tweetDatabase']
                kwargs['tweetCollection'] = process['tweetCollection']
                kwargs['screenNameList'] = process['screenNameList']
                kwargs['userIdList'] = process['accountIdList']
                kwargs['proxyList'] = [PROXY]
                kwargs['userDatabase'] = process['userDatabase']
                kwargs['userCollection'] = process['userCollection']
                api = Process(target=historyTweet, kwargs=kwargs)
                api.start()
                processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'filterTweet':
                kwargs['proxyList'] = [PROXY]
                kwargs['tweetDatabase'] = process['tweetDatabase']
                kwargs['tweetCollection'] = process['tweetCollection']
                kwargs['keywords'] = [process['keywords']]
                api = Process(target=filterRealtimeTweet, kwargs=kwargs)
                api.start()
                processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})


def daemon():
    """
    用于判断程序是否在运行。
    :return:
    """
    print u"启动观测程序"
    sleepTime = 60  #每隔60秒运行一次
    while True:
        try:
            collection = MongoClient(MONGOHOST).get_database(PROCESS_DATABASE).get_collection(PROCESS_COLLECTION)
        except PyMongoError as err:
            print err.message
            time.sleep(sleepTime)
        else:
            try:
                while True:
                    cursor = collection.find({'state': 'running'}, {'_id': 0, 'pid': 1, 'processName': 1})
                    for process in cursor:
                        if not psutil.pid_exists(process.get('pid')):
                            endUTC = int(time.time())
                            endDate = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                            collection.update({'processName': process.get('processName'), 'state': 'running'},
                                              {'$set': {'state': 'terminate', 'endUTC': endUTC,
                                                        'endDate': endDate}})
                    time.sleep(sleepTime)
            except Exception as err:
                print err.message
                time.sleep(sleepTime)