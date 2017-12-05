# coding=utf-8
import threading
import time
from multiprocessing import Process

import psutil
import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from TwitterCapture.TwitterTweetCapture.FilterRealtimeTweet import filterRealtimeTweet
from TwitterCapture.TwitterTweetCapture.HistoryTweet import historyTweet
from TwitterCapture.TwitterTweetCapture.UserRealtimeTweet import realtimeTweet
from TwitterCapture.TwitterUserCapture.UserFriends import userFriends
from TwitterCapture.TwitterUserCapture.UserInfo import userInfo
from twitter.TwitterCapture.TwitterUserCapture.UserFollowers import userFollowers
from twitter.TwitterCapture.constants import DEFAULTHOST,\
    PROCESS_DATABASE,PROCESS_COLLECTION,PROXY
from twitter.TwitterCapture.ProxyConstant import PROXY_LIST
from twitter.TwitterCapture.SocketProxy import Pinhole


info = {}
info['CPU'] = 0
info['memory'] = {}
info['memory']['total'] = 0
info['memory']['used'] = 0
info['memory']['free'] = 0
info['memory']['percent'] = 0
info['netIORecv'] = 0
info['netIOSend'] = 0
info['disk'] = {}

def operation():
    """
    1、当Django重启时，重新启动任务集合中的所有正在运行程序。
    一般来说Django程序稳定后，是不会重启的，除非改版。
    2、启动一个守护进程（依赖于Django），用于观测程序是否在运行。
    3、代理监控，用于查看每个代理的状态，normal或者breakdown
    :return:
    """
    #重启那些正在运行的程序
    restartProcess()

    #代理监控
    proxyAPI = Pinhole(PROXY.split(':')[0], int(PROXY.split(':')[1]), PROXY_LIST)
    proxyAPI.start()

    # 服务器资源监控
    serverMonitor(proxyAPI)

    #开启检测进程
    api = Process(target=daemon)
    api.start()

def serverMonitor(proxyAPI):
    info['proxyList'] = proxyAPI.PROXYLIST
    info['netIORecv'] = (psutil.net_io_counters().bytes_recv - info['netIORecv']) / 1024 / 1024 / 1024
    info['netIOSend'] = (psutil.net_io_counters().bytes_sent - info['netIOSend']) / 1024 / 1024 / 1024
    info['memory']['total'] = psutil.virtual_memory().total / 1024 / 1024
    info['memory']['used'] = psutil.virtual_memory().used / 1024 / 1024
    info['memory']['free'] = psutil.virtual_memory().free / 1024 / 1024
    info['memory']['percent'] = psutil.virtual_memory().percent
    info['CPU'] = psutil.cpu_percent(1)
    info['disk']['total'] = psutil.disk_usage('/').total / 1024 / 1024 / 1024
    info['disk']['used'] = psutil.disk_usage('/').used / 1024 / 1024 / 1024
    info['disk']['free'] = psutil.disk_usage('/').free / 1024 / 1024 / 1024
    info['disk']['percent'] = psutil.disk_usage('/').percent

    # ###########每过30秒重新检测一次，使用的是异步#######################
    threading.Timer(60, serverMonitor,args=(proxyAPI,)).start()

# def proxyMonitor():
#     TESTURL = 'https://www.google.com'
#     for i in range(len(PROXY_LIST)):
#         ########代理格式##################
#         proxies = {'http': 'http://%s' % (PROXY_LIST[i].get('host') + ':' + str(PROXY_LIST[i].get('port'))),
#                    'https': 'http://%s' % (PROXY_LIST[i].get('host') + ':' + str(PROXY_LIST[i].get('port')))}
#         try:
#             r = requests.get(TESTURL, proxies=proxies)  # 访问GOOGLE
#
#             if r.status_code == 200:
#                 proxyList[i]['state'] = 'normal'
#             else:
#                 proxyList[i]['state'] = 'breakdown'
#         except requests.exceptions.ConnectionError: #连接错误，说明代理端口没有打开
#             proxyList[i]['state'] = 'breakdown'
#
#     # ###########每过30秒重新检测一次，使用的是异步#######################
#     threading.Timer(60, proxyMonitor).start()

def restartProcess():
    processClient = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    for process in processClient.find({'state':'running'}):
        kwargs = {}
        ###################对于每个采集功能，各自开始判断运行###########################
        if process['_type'] == 'userInfo':
            kwargs['screenNameList'] = process['screenNameList']
            kwargs['accountIdList'] = process['accountIdList']
            kwargs['proxyList'] = [PROXY]
            kwargs['userHost'] = process['userHost']
            kwargs['userDatabase'] = process['userDatabase']
            kwargs['userCollection'] = process['userCollection']
            api = Process(target=userInfo, kwargs=kwargs)
            api.start()
            processClient.update({'processName':process['processName']},{'$set':{'pid':api.pid}})

        if process['_type'] == 'userFriends':
            kwargs['screenNameList'] = process['screenNameList']
            kwargs['accountIdList'] = process['accountIdList']
            kwargs['proxyList'] = [PROXY]
            kwargs['userHost'] = process['userHost']
            kwargs['userDatabase'] = process['userDatabase']
            kwargs['userCollection'] = process['userCollection']
            kwargs['userFriendsHost'] = process['userHost']
            kwargs['userFriendsDatabase'] = process['userDatabase']
            kwargs['userFriendsCollection'] = process['userCollection']

            api = Process(target=userFriends, kwargs=kwargs)
            api.start()
            processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'userFollowers':
            kwargs['screenNameList'] = process['screenNameList']
            kwargs['accountIdList'] = process['accountIdList']
            kwargs['proxyList'] = [PROXY]
            kwargs['userFriendsDatabase'] = process['userHost']
            kwargs['userFollowersDatabase'] = process['userDatabase']
            kwargs['userFollowersCollection'] = process['userCollection']
            kwargs['userHost'] = process['userHost']
            kwargs['userDatabase'] = process['userDatabase']
            kwargs['userCollection'] = process['userCollection']
            api = Process(target=userFollowers, kwargs=kwargs)
            api.start()
            processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'userRealtimeTweet':
            kwargs['tweetHost'] = process['tweetHost']
            kwargs['tweetDatabase'] = process['tweetDatabase']
            kwargs['tweetCollection'] = process['tweetCollection']
            kwargs['proxyList'] = [PROXY]
            kwargs['userHost'] = process['userHost']
            kwargs['userDatabase'] = kwargs['userDatabase']
            kwargs['userCollection'] = kwargs['userCollection']
            api = Process(target=realtimeTweet, kwargs=kwargs)
            api.start()
            processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'historyTweet':
            kwargs['tweetHost'] = process['tweetHost']
            kwargs['tweetDatabase'] = process['tweetDatabase']
            kwargs['tweetCollection'] = process['tweetCollection']
            kwargs['screenNameList'] = process['screenNameList']
            kwargs['userIdList'] = process['accountIdList']
            kwargs['proxyList'] = [PROXY]
            kwargs['userHost'] = process['userHost']
            kwargs['userDatabase'] = process['userDatabase']
            kwargs['userCollection'] = process['userCollection']
            api = Process(target=historyTweet, kwargs=kwargs)
            api.start()
            processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'filterTweet':
                kwargs['proxyList'] = [PROXY]
                kwargs['tweetHost'] = process['tweetHost']
                kwargs['tweetDatabase'] = process['tweetDatabase']
                kwargs['tweetCollection'] = process['tweetCollection']
                kwargs['keywords'] = [process['keywords']]
                api = Process(target=filterRealtimeTweet, kwargs=kwargs)
                api.start()
                processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})

        if process['_type'] == 'filterHistoryTweet':
                kwargs['proxyList'] = [PROXY]
                kwargs['tweetHost'] = process['tweetHost']
                kwargs['tweetDatabase'] = process['tweetDatabase']
                kwargs['tweetCollection'] = process['tweetCollection']
                kwargs['keywords'] = [process['keywords']]
                api = Process(target=filterRealtimeTweet, kwargs=kwargs)
                api.start()
                processClient.update({'processName': process['processName']}, {'$set': {'pid': api.pid}})


def daemon():
    """
    用于判断程序是否在运行，并且将所有数据库同步ES。
    :return:
    """
    print "启动观测程序"
    sleepTime = 60  #每隔60秒运行一次

    #同步ES以后再说
    # client = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_DB_COL_NAME]
    # for i in client.find():
    #     if i['type'] == 'user':
    #         cmd = "start mongo-connector -m " + i['HostName'] + " -t " + ES_HOST + \
    #               " -d elastic2_doc_manager -n " + i['DBName'] + "." + i['COLName'] + " -i id,screen_name,description,created_at"
    #         print cmd
    #         os.system(cmd)
    #     else:
    #         cmd = "start mongo-connector -m " + i['HostName'] + " -t " + ES_HOST + \
    #               " -d elastic2_doc_manager -n " + i['DBName'] + "." + i[
    #                   'COLName'] + " -i id,user.id,user.screen_name,text,created_at"
    #         print cmd
    #         os.system(cmd)


    while True:
        try:
            collection = MongoClient(DEFAULTHOST).get_database(PROCESS_DATABASE).get_collection(PROCESS_COLLECTION)
        except PyMongoError as err:
            print err.message
            time.sleep(sleepTime)
        else:
            try:
                ########对于正在运行的进程检测是否运行，并查看对应数据库中采集的条数########
                while True:
                    cursor = collection.find({'state': 'running'})
                    for process in cursor:
                        if not psutil.pid_exists(process.get('pid')):
                            endUTC = int(time.time())
                            endDate = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                            collection.update({'processName': process.get('processName'), 'state': 'running'},
                                              {'$set': {'state': 'terminate', 'endUTC': endUTC,
                                                        'endDate': endDate}})
                        result = 0
                        if process['tweetHost'] == None:
                            if process['_type'] == 'userFollowers':
                                result = MongoClient(process['userHost'])[process['userDatabase']][process['userCollection']].find({'captured_followers_count':{'$exists':True}}).count()
                            if process['_type'] == 'userFriends':
                                result = MongoClient(process['userHost'])[process['userDatabase']][process['userCollection']].find({'captured_friends_count':{'$exists':True}}).count()
                            if process['_type'] == 'userInfo':
                                result = MongoClient(process['userHost'])[process['userDatabase']][process['userCollection']].find({'screen_name':{'$exists':True}}).count()
                        else:
                            result = MongoClient(process['tweetHost'])[process['tweetDatabase']][process['tweetCollection']].count()
                        collection.update({'processName': process.get('processName')},{'$set': {'count':result,'countBefore':process['count']}})

                    time.sleep(sleepTime)
            except Exception as err:
                print err.message
                time.sleep(sleepTime)

