# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

import psutil
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from program_code.TwitterCapture.TwitterUserCapture.UserInfo import userInfo as _userInfoCapture
from program_code.TwitterCapture.TwitterUserCapture.UserFriends import userFriends as _userFriendsCapture
from program_code.TwitterCapture.TwitterUserCapture.UserFollowers import userFollowers as _userFollowersCapture
from program_code.TwitterCapture.TwitterTweetCapture.FilterRealtimeTweet import filterRealtimeTweet as _filterTweetCapture
from program_code.TwitterCapture.TwitterTweetCapture.UserRealtimeTweet import realtimeTweet as _realtimeTweetCapture
from program_code.TwitterCapture.TwitterTweetCapture.HistoryTweet import historyTweet as _historyTweetCapture
from program_code.TwitterCapture.GetMongoData import GetMongoData
from multiprocessing import Process
from pymongo import MongoClient
from program_code.TwitterCapture.TwitterUserCapture.TwitterUserCapture.common.constants import MONGOHOST,PROCESS_DATABASE,PROCESS_COLLECTION,PROXY

def index(request):
    return render(request,'twitter/index.html')

def userInfo(request):
    return render(request, 'twitter/userInfo.html')

def userFriends(request):
    return render(request, 'twitter/userFriends.html')

def userFollowers(request):
    return render(request, 'twitter/userFollowers.html')

def realtimeTweet(request):
    return render(request, 'twitter/userRealtimeTweet.html')

def filterTweet(request):
    return render(request, 'twitter/filterTweet.html')

def historyTweet(request):
    return render(request, 'twitter/historyTweet.html')

def twitterCapture(request):
    """
    信息采集
    :param request: 包括type,userDatabase,userCollection,screenNameList,accountIdList,
    tweetDatabase,tweetCollection,keywords,description,creator,
    :return:
    """
    ########初始化参数#########################
    _type = None
    userDatabase = None
    userCollection = None
    screenNameList = None
    accountIdList = None
    tweetDatabase = None
    tweetCollection = None
    keywords = None
    proxyList = [PROXY]
    description = None
    creator = None
    requestNum = 0
    eachNum = 200
    processName = None
    kwargs = {}
    ################################################

    ###################获取参数#################################
    _type = request.GET['type']   #前面三个参数必须要有
    description = request.GET['description']
    creator = request.GET['creator']
    if _type is '':  #如果没有采集类型，直接返回报错
        return HttpResponse('没有选择采集类型，请重新选填')
    if description is '':
        return HttpResponse('请重新选填')
    if creator is '':
        return HttpResponse('请重新选填')
    try:
        userDatabase = request.GET['userDatabase']
    except:pass
    try:
        userCollection = request.GET['userCollection']
    except:pass
    try:
        screenNameList = request.GET['screenNameList'].split(',')
    except:pass
    try:
        accountIdList = request.GET['accountIdList'].split(',')
    except:pass
    try:
        tweetDatabase = request.GET['tweetDatabase']
    except:pass
    try:
        tweetCollection = request.GET['tweetCollection']
    except:pass
    try:
        keywords = request.GET['keywords']
    except:pass
    try:
        requestNum = int(request.GET['requestNum'])
    except:pass
    try:
        eachNum = int(request.GET['eachNum'])
    except:pass

    ###################对于每个采集功能，各自开始判断运行###########################
    if _type == 'userInfo':
        if userDatabase is '' or userCollection is '':
            return HttpResponse('没有填写用户数据库名字，请重新选填')
        else:
            kwargs['screenNameList'] = screenNameList
            kwargs['accountIdList'] = accountIdList
            kwargs['proxyList'] = proxyList
            kwargs['userDatabase'] = userDatabase
            kwargs['userCollection'] = userCollection
            api = Process(target=_userInfoCapture, kwargs=kwargs)
            api.start()
            processName = storeProcessInfo(pid=api.pid,_type=_type,description=description,creator=creator,userDatabase=userDatabase,
                             userCollection=userCollection,screenNameList=screenNameList,accountIdList=accountIdList)

    if _type == 'userFriends':
        if userDatabase is '' or userCollection is '':
            return HttpResponse('没有填写用户数据库名字，请重新选填')
        else:
            kwargs['screenNameList'] = screenNameList
            kwargs['accountIdList'] = accountIdList
            kwargs['proxyList'] = proxyList
            kwargs['userDatabase'] = userDatabase
            kwargs['userFriendsDatabase'] = userDatabase
            kwargs['userFriendsCollection'] = userCollection
            kwargs['userCollection'] = userCollection
            api = Process(target=_userFriendsCapture, kwargs=kwargs)
            api.start()
            processName = storeProcessInfo(pid=api.pid,_type=_type,description=description,creator=creator,userDatabase=userDatabase,
                             userCollection=userCollection,screenNameList=screenNameList,accountIdList=accountIdList)

    if _type == 'userFollowers':
        if userDatabase is '' or userCollection is '':
            return HttpResponse('没有填写用户数据库名字，请重新选填')
        else:
            kwargs['screenNameList'] = screenNameList
            kwargs['accountIdList'] = accountIdList
            kwargs['proxyList'] = proxyList
            kwargs['userFollowersDatabase'] = userDatabase
            kwargs['userFollowersCollection'] = userCollection
            kwargs['userDatabase'] = userDatabase
            kwargs['userCollection'] = userCollection
            api = Process(target=_userFollowersCapture, kwargs=kwargs)
            api.start()
            processName = storeProcessInfo(pid=api.pid,_type=_type,description=description,creator=creator,userDatabase=userDatabase,
                             userCollection=userCollection,screenNameList=screenNameList,accountIdList=accountIdList)

    if _type == 'userRealtimeTweet':
        if userDatabase is None or userCollection is None:
            return HttpResponse('没有填写用户数据库名字，请重新选填')
        if tweetDatabase is None or tweetCollection is None:
            return HttpResponse('没有填写推文数据库名字，请重新选填')
        else:
            kwargs['tweetDatabase'] = tweetDatabase
            kwargs['tweetCollection'] = tweetCollection
            kwargs['proxyList'] = proxyList
            kwargs['userDatabase'] = userDatabase
            kwargs['userCollection'] = userCollection
            api = Process(target=_realtimeTweetCapture, kwargs=kwargs)
            api.start()
            processName = storeProcessInfo(pid=api.pid,_type=_type,description=description,creator=creator,userDatabase=userDatabase,
                             userCollection=userCollection,tweetDatabase=tweetDatabase,tweetCollection=tweetCollection)

    if _type == 'historyTweet':
        if tweetDatabase is '' or tweetCollection is '':
            return HttpResponse('没有填写推文数据库名字，请重新选填')
        else:
            kwargs['tweetDatabase'] = tweetDatabase
            kwargs['tweetCollection'] = tweetCollection
            kwargs['screenNameList'] = screenNameList
            kwargs['userIdList'] = accountIdList
            kwargs['proxyList'] = proxyList
            kwargs['userDatabase'] = userDatabase
            kwargs['userCollection'] = userCollection
            api = Process(target=_historyTweetCapture, kwargs=kwargs)
            api.start()
            processName = storeProcessInfo(pid=api.pid,_type=_type,description=description,creator=creator,userDatabase=userDatabase,
                             userCollection=userCollection,tweetDatabase=tweetDatabase,tweetCollection=tweetCollection,
                             screenNameList=screenNameList, accountIdList=accountIdList,)

    if _type == 'filterTweet':
        if tweetDatabase is '' or tweetCollection is '':
            return HttpResponse('没有填写推文数据库名字，请重新选填')
        else:
            kwargs['proxyList'] = proxyList
            kwargs['tweetDatabase'] = tweetDatabase
            kwargs['tweetCollection'] = tweetCollection
            kwargs['keywords'] = [keywords]
            api = Process(target=_filterTweetCapture, kwargs=kwargs)
            api.start()
            processName = storeProcessInfo(pid=api.pid, _type=_type, description=description, creator=creator,
                             tweetDatabase=tweetDatabase,tweetCollection=tweetCollection,
                             keywords=keywords)

    return HttpResponse("采集开始，采集程序的唯一标识是：" + processName)

def infoGet(request):
    """
    用于获取数据
    :param request:
    :return:
    """
    ##############初始化参数#########################
    userDatabase = None
    userCollection = None
    screenNameList = None
    accountIdList = None
    tweetDatabase = None
    tweetCollection = None
    _type = None
    # keywords = None

    #################################################
    _type = request.GET['type']
    if _type is '':  # 如果没有采集类型，直接返回报错
        return JsonResponse({'level': 'error', 'content': '没有选择采集类型，请重新选填'})
    try:
        userDatabase = request.GET['userDatabase']
    except:pass
    try:
        userCollection = request.GET['userCollection']
    except:pass
    try:
        screenNameList = request.GET['screenNameList'].split(',')
    except:pass
    try:
        accountIdList = request.GET['accountIdList'].split(',')
    except:pass
    try:
        tweetDatabase = request.GET['tweetDatabase']
    except:pass
    try:
        tweetCollection = request.GET['tweetCollection']
    except:pass
    # try:
    #     keywords = request.GET['keywords']
    # except:pass

    #################获取所有的数据###############################
    result = []
    result = GetMongoData.infoGet(userDatabase=userDatabase,userCollection=userCollection,screenNameList=screenNameList,
                             accountIdList=accountIdList,tweetDatabase=tweetDatabase,tweetCollection=tweetCollection,_type=_type)

    return JsonResponse(result,safe=False)

def realtimeInfoGet(request):
    """

    :param request:
    :return:
    """
    ##############初始化参数#########################
    userDatabase = None
    userCollection = None
    screenNameList = None
    accountIdList = None
    tweetDatabase = None
    tweetCollection = None
    _type = None
    # keywords = None

    #################################################
    _type = request.GET['type']
    if _type is '':  # 如果没有采集类型，直接返回报错
        return JsonResponse({'level': 'error', 'content': '没有选择采集类型，请重新选填'})
    try:
        userDatabase = request.GET['userDatabase']
    except:pass
    try:
        userCollection = request.GET['userCollection']
    except:pass
    try:
        screenNameList = request.GET['screenNameList'].split(',')
    except:pass
    try:
        accountIdList = request.GET['accountIdList'].split(',')
    except:pass
    try:
        tweetDatabase = request.GET['tweetDatabase']
    except:pass
    try:
        tweetCollection = request.GET['tweetCollection']
    except:pass

##################获取实时数据(只用于显示filterTweet与realtimeTweet)#################################
    result = {}
    if _type not in ('userRealtimeTweet','filterTweet'):
        return JsonResponse({'level':'error','content':'类型错误，这个实时数据按钮只接受userRealtimeTweet与filterTweet'}, safe=False)

    result = GetMongoData.realtimeInfoGet(tweetDatabase=tweetDatabase,tweetCollection=tweetCollection)
    if result == {}:
        return JsonResponse({'level': 'error', 'content': '实时采集程序没有运行，请仔细检查'}, safe=False)
    return JsonResponse(result, safe=False)

def storeProcessInfo(pid=None,_type=None,creator=None,description=None,userDatabase=None,userCollection=None,
screenNameList=None,accountIdList=None,tweetDatabase=None,tweetCollection=None,keywords=None):
    """
    每次成功开启一个新的进程时，需要将一些必要的信息记录下来，包括进程ID，运行状态，功能描述，创建者，
    程序开始运行的时间，进程唯一标识，用户数据库，用户集合，推文数据库，推文集合,等
    :param pid:
    :param _type:
    :param creator:
    :param description:
    :return:
    """
    client = MongoClient(MONGOHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    content = {}
    content['pid'] = pid
    content['state'] = 'running'
    content['description'] = description
    content['creator'] = creator
    content['startDate'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    content['startUTC'] = int(time.time())
    content['processName'] = str(_type) + '_' + str(pid) + '_' + str(content['startUTC'])   #这个进程名是唯一标识，由采集类型+PID+创建进程时间构成
    content['userDatabase'] = userDatabase
    content['userCollection'] = userCollection
    content['screenNameList'] = screenNameList
    content['accountIdList'] = accountIdList
    content['tweetDatabase'] = tweetDatabase
    content['tweetCollection'] = tweetCollection
    content['keywords'] = keywords
    content['_type'] = _type

    client.insert(content)

    return content['processName']

def dataQuery(request):
    return render(request, 'twitter/dataQuery.html')

def processQuery(request):
    return render(request, 'twitter/processQuery.html')

def twitterTerminate(request):
    ##############初始化参数#########################
    processName = None

    ###############获取参数##############################
    processName = request.GET['processName']
    if processName is '':
        return HttpResponse('processName为空，请输入processName')

    processClient = MongoClient(MONGOHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    process = processClient.find_one({'processName':processName})
    if process is not None:
        if process['state'] == 'running':
            if psutil.pid_exists(process['pid']):
                #结束进程并更新数据库进程信息
                psutil.Process(process['pid']).terminate()
                endUTC = int(time.time())
                endDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                processClient.update({'processName':processName},{'$set':{'state':'terminate','endUTC':endUTC,'endDate':endDate}})
                return HttpResponse('结束采集程序完成')
            else:
                return HttpResponse('采集程序已经结束')
        else:
            return HttpResponse('采集程序已经结束')
    else:
        return HttpResponse('processName不存在，请输入正确的processName')

def twitterCheck(request):
    pass

def runningProcessInfo(request):
    pass

def searchProcess(request):
    pass