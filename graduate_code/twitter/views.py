# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
from multiprocessing import Process

import psutil
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient

from BeforeDjangoOperation import info
from TwitterCapture.GetMongoData import GetMongoData
from TwitterCapture.TwitterTweetCapture.FilterRealtimeTweet import filterRealtimeTweet as _filterTweetCapture
from TwitterCapture.TwitterTweetCapture.HistoryTweet import historyTweet as _historyTweetCapture
from TwitterCapture.TwitterTweetCapture.TwitterAPIKeywords import twitterAPIKeywords as _twitterAPIKeywordsCapture
from TwitterCapture.TwitterTweetCapture.UserRealtimeTweet import realtimeTweet as _realtimeTweetCapture
from TwitterCapture.TwitterUserCapture.UserFriends import userFriends as _userFriendsCapture
from TwitterCapture.TwitterUserCapture.UserInfo import userInfo as _userInfoCapture
from twitter.TwitterCapture.TwitterUserCapture.UserFollowers import userFollowers as _userFollowersCapture
from twitter.TwitterCapture.constants import \
    DEFAULTHOST,PROCESS_DATABASE,PROCESS_COLLECTION,PROXY,PROCESS_DB_COL_NAME
from twitter.TwitterCapture.ProxyConstant import PROXY_LIST


def index(request):
    return render(request,'twitter/index.html')

def infoCapture(request):
    return render(request, 'twitter/infoCapture.html')

def userInfo(request):
    result = getDataAndColInfo()
    return render(request,'twitter/userInfo.html',{'user':result['user']})

def userFriends(request):
    return render(request, 'twitter/userFriends.html')

def userFollowers(request):
    return render(request, 'twitter/userFollowers.html')

def realtimeTweet(request):
    return render(request, 'twitter/userRealtimeTweet.html')

def keywordsTweet(request):
    result = getDataAndColInfo()
    return render(request, 'twitter/filterTweet.html',{'tweet':result['tweet']})

def userTweet(request):
    result = getDataAndColInfo()
    return render(request, 'twitter/userTweet.html', {'tweet': result['tweet'],'user':result['user']})

def monitor(request):
    result = getDataAndColInfo()
    return render(request, 'twitter/monitor.html', {'tweet': result['tweet'],'user':result['user']})

def search(request):
    result = getDataAndColInfo()
    return render(request, 'twitter/search.html', {'tweet': result['tweet'],'user':result['user']})

def historyTweet(request):
    return render(request, 'twitter/historyTweet.html')

@csrf_exempt
def twitterCapture(request):
    """
    信息采集
    :param request: 包括type,userDatabase,userCollection,screenNameList,accountIdList,
    tweetDatabase,tweetCollection,keywords,description,creator,
    :return:
    """
    ########初始化参数#########################
    _type = None
    userHost = None
    userDatabase = None
    userCollection = None
    screenNameList = None
    accountIdList = None
    tweetHost = None
    tweetDatabase = None
    tweetCollection = None
    keywords = None
    proxyList = [PROXY]
    description = None
    creator = None
    captureNum = 100
    processName = None
    processNameMap = {}
    myFile = None
    kwargs = {}
    ################################################

    ###################获取参数#################################
    print request.POST
    _type = request.POST['type'].split(',')
    try:
        selectUserDatabase = request.POST['selectUserDatabase']
        userHost = selectUserDatabase.split('|')[0]
        userDatabase = selectUserDatabase.split('|')[1]
        userCollection = selectUserDatabase.split('|')[2]
    except:pass
    try:
        screenNameList = request.POST['screenNameList'].split(',')
        if screenNameList == ['']:
            screenNameList = None
    except:pass
    try:
        accountIdList = request.POST['accountIdList'].split(',')
        if accountIdList == ['']:
            accountIdList = None
    except:pass

    myFile = request.FILES.get("myfile", None)  # 获取上传的文件，如果没有文件，则默认为None
    if myFile:
        cnt = myFile.read().split(':')
        if cnt[0] == 'screenNameList':
            if screenNameList :
                screenNameList += cnt[1].split(',')
            else:
                screenNameList = cnt[1].split(',')
    try:
        selectTweetDatabase = request.POST['selectTweetDatabase']
        tweetHost = selectTweetDatabase.split('|')[0]
        tweetDatabase = selectTweetDatabase.split('|')[1]
        tweetCollection = selectTweetDatabase.split('|')[2]
    except:pass
    try:
        keywords = request.POST['keywords']
        if keywords == '':
            keywords = None
    except:pass
    try:
        captureNum = int(request.POST['captureNum'])
    except:pass

    # try:
    #     userDatabase = request.GET['userDatabase']
    #     if userDatabase == '':
    #         userDatabase = None
    # except:pass
    # try:
    #     userCollection = request.GET['userCollection']
    #     if userCollection == '':
    #         userCollection = None
    # except:pass
    # try:
    #     screenNameList = request.GET['screenNameList'].split(',')
    #     if screenNameList == ['']:
    #         screenNameList = None
    # except:pass
    # try:
    #     accountIdList = request.GET['accountIdList'].split(',')
    #     if accountIdList == ['']:
    #         accountIdList = None
    # except:pass
    # try:
    #     tweetDatabase = request.GET['tweetDatabase']
    #     if tweetDatabase == '':
    #         tweetDatabase = None
    # except:pass
    # try:
    #     tweetCollection = request.GET['tweetCollection']
    #     if tweetCollection == '':
    #         tweetCollection = None
    # except:pass
    # try:
    #     keywords = request.GET['keywords']
    #     if keywords == '':
    #         keywords = None
    # except:pass
    # try:
    #     requestNum = int(request.GET['requestNum'])
    # except:pass
    # try:
    #     eachNum = int(request.GET['eachNum'])
    # except:pass
    #
    ###################对于每个采集功能，各自开始判断运行###########################
    if 'userInfo' in _type:
        kwargs = {}
        kwargs['screenNameList'] = screenNameList
        kwargs['accountIdList'] = accountIdList
        kwargs['proxyList'] = proxyList
        kwargs['userHost'] = userHost
        kwargs['userDatabase'] = userDatabase
        kwargs['userCollection'] = userCollection
        api = Process(target=_userInfoCapture, kwargs=kwargs)
        api.start()
        processName = storeProcessInfo(pid=api.pid,_type='userInfo',userHost=userHost,userDatabase=userDatabase,
                         userCollection=userCollection,screenNameList=screenNameList,accountIdList=accountIdList)
        processNameMap['userInfo'] = processName

    if 'userFriends' in _type:
        kwargs = {}
        kwargs['screenNameList'] = screenNameList
        kwargs['accountIdList'] = accountIdList
        kwargs['proxyList'] = proxyList
        kwargs['userHost'] = userHost
        kwargs['userDatabase'] = userDatabase
        kwargs['userFriendsDatabase'] = userDatabase
        kwargs['userFriendsCollection'] = userCollection
        kwargs['userCollection'] = userCollection
        api = Process(target=_userFriendsCapture, kwargs=kwargs)
        api.start()
        processName = storeProcessInfo(pid=api.pid,_type='userFriends',userHost=userHost,userDatabase=userDatabase,
                         userCollection=userCollection,screenNameList=screenNameList,accountIdList=accountIdList)
        processNameMap['userFriends'] = processName

    if 'userFollowers' in _type:
        kwargs = {}
        kwargs['screenNameList'] = screenNameList
        kwargs['accountIdList'] = accountIdList
        kwargs['proxyList'] = proxyList
        kwargs['userHost'] = userHost
        kwargs['userFollowersDatabase'] = userDatabase
        kwargs['userFollowersCollection'] = userCollection
        kwargs['userDatabase'] = userDatabase
        kwargs['userCollection'] = userCollection
        api = Process(target=_userFollowersCapture, kwargs=kwargs)
        api.start()
        processName = storeProcessInfo(pid=api.pid,_type='userFollowers',userHost=userHost,userDatabase=userDatabase,
                         userCollection=userCollection,screenNameList=screenNameList,accountIdList=accountIdList)
        processNameMap['userFollowers'] = processName

    if 'userRealtimeTweet'in _type:
        if accountIdList:
            kwargs['tweetHost'] = tweetHost
            kwargs['tweetDatabase'] = tweetDatabase
            kwargs['tweetCollection'] = tweetCollection
            kwargs['ids'] = accountIdList
            kwargs['proxyList'] = proxyList
            api = Process(target=_filterTweetCapture, kwargs=kwargs)
        else:
            kwargs['tweetHost'] = tweetHost
            kwargs['tweetDatabase'] = tweetDatabase
            kwargs['tweetCollection'] = tweetCollection
            kwargs['proxyList'] = proxyList
            kwargs['userHost'] = userHost
            kwargs['userDatabase'] = userDatabase
            kwargs['userCollection'] = userCollection
            api = Process(target=_realtimeTweetCapture, kwargs=kwargs)
        api.start()
        processName = storeProcessInfo(pid=api.pid,_type='userRealtimeTweet',tweetHost=tweetHost,userHost=userHost,userDatabase=userDatabase,
                         userCollection=userCollection,tweetDatabase=tweetDatabase,tweetCollection=tweetCollection,
                                       accountIdList=accountIdList)

    if 'historyTweet'in _type:
        kwargs['tweetHost'] = tweetHost
        kwargs['tweetDatabase'] = tweetDatabase
        kwargs['tweetCollection'] = tweetCollection
        kwargs['screenNameList'] = screenNameList
        kwargs['userIdList'] = accountIdList
        kwargs['proxyList'] = proxyList
        kwargs['userHost'] = userHost
        kwargs['userDatabase'] = userDatabase
        kwargs['userCollection'] = userCollection
        kwargs['count'] = 100
        kwargs['requestNum'] = captureNum / 100
        api = Process(target=_historyTweetCapture, kwargs=kwargs)
        api.start()
        processName = storeProcessInfo(pid=api.pid,_type='historyTweet',tweetHost=tweetHost,userHost=userHost,userDatabase=userDatabase,
                         userCollection=userCollection,tweetDatabase=tweetDatabase,tweetCollection=tweetCollection,
                         screenNameList=screenNameList, accountIdList=accountIdList,)

    if 'filterTweet'in _type:
        kwargs['proxyList'] = proxyList
        kwargs['tweetHost'] = tweetHost
        kwargs['tweetDatabase'] = tweetDatabase
        kwargs['tweetCollection'] = tweetCollection
        kwargs['keywords'] = [keywords]
        api = Process(target=_filterTweetCapture, kwargs=kwargs)
        api.start()
        processName = storeProcessInfo(pid=api.pid, _type='filterTweet', tweetHost=tweetHost,
                         tweetDatabase=tweetDatabase,tweetCollection=tweetCollection,
                         keywords=keywords)

    if 'filterHistoryTweet'in _type:
        kwargs['proxy'] = PROXY
        kwargs['mongodb'] = tweetHost
        kwargs['mongoDataName'] = tweetDatabase
        kwargs['mongoColName'] = tweetCollection
        kwargs['keyword'] = keywords
        api = Process(target=_twitterAPIKeywordsCapture, kwargs=kwargs)
        api.start()
        processName = storeProcessInfo(pid=api.pid, _type='filterHistoryTweet', tweetHost=tweetHost,
                         tweetDatabase=tweetDatabase,tweetCollection=tweetCollection,
                         keywords=keywords)
    print processName
    if 'userInfo' in _type or 'userFollowers' in _type or 'userFriends' in _type:
        return JsonResponse({'content': "采集开始", 'processName': processNameMap, 'level': 'normal'})
    else:
        return JsonResponse({'content':"采集开始" , 'processName': processName , 'level':'normal'})

@csrf_exempt
def infoGet(request):
    """
    用于获取数据
    :param request:
    :return:
    """
    ##############初始化参数#########################
    userHost = None
    userDatabase = None
    userCollection = None
    screenName = None
    accountId = None
    tweetId = None
    tweetHost = None
    tweetDatabase = None
    tweetCollection = None
    _type = None
    keywords = None
    extend = None

    #################################################
    _type = request.POST['type']
    print request.POST

    try:
        selectUserDatabase = request.POST['selectUserDatabase']
        userHost = selectUserDatabase.split('|')[0]
        userDatabase = selectUserDatabase.split('|')[1]
        userCollection = selectUserDatabase.split('|')[2]
    except:pass

    try:
        screenName = request.POST['screenName']
        if screenName == '':
            screenName = None
    except:pass
    try:
        accountId = request.POST['accountId']
        if accountId == '':
            accountId = None
        else:
            accountId = int(accountId)
    except:pass
    try:
        tweetId = request.POST['tweetId']
        if tweetId == '':
            tweetId = None
        else:
            tweetId = int(tweetId)
    except:pass
    try:
        selectTweetDatabase = request.POST['selectTweetDatabase']
        tweetHost = selectTweetDatabase.split('|')[0]
        tweetDatabase = selectTweetDatabase.split('|')[1]
        tweetCollection = selectTweetDatabase.split('|')[2]
    except:pass
    try:
        keywords = request.POST['keywords']
        if keywords == '':
            keywords = None
    except:pass
    try:
        extend = request.POST['extend']
        if extend == '':
            extend = None
    except:pass

    #################获取所有的数据###############################
    result = []
    result = GetMongoData.infoGet(userHost=userHost, userDatabase=userDatabase, userCollection=userCollection, screenName=screenName, tweetId=tweetId,
                                  accountId=accountId, tweetHost=tweetHost, tweetDatabase=tweetDatabase, tweetCollection=tweetCollection, _type=_type,
                                  keywords=keywords, extend=extend)
    return JsonResponse(result,safe=False)

def realtimeInfoGet(request):
    """

    :param request:
    :return:
    """
    ##############初始化参数#########################
    processName = None

    #################################################
    processName = request.GET['processName']

    result = GetMongoData.realtimeInfoGet(processName=processName)

    return JsonResponse(result, safe=False)

def storeProcessInfo(pid=None,_type=None,userHost=None,userDatabase=None,userCollection=None,
screenNameList=None,accountIdList=None,tweetHost=None,tweetDatabase=None,tweetCollection=None,keywords=None):
    """
    每次成功开启一个新的进程时，需要将一些必要的信息记录下来，包括进程ID，运行状态，功能描述，创建者，
    程序开始运行的时间，进程唯一标识，用户数据库，用户集合，推文数据库，推文集合,等
    :param pid:
    :param _type:
    :param creator:
    :param description:
    :return:
    """
    client = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    content = {}
    content['pid'] = pid
    content['state'] = 'running'
    content['startDate'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    content['startUTC'] = int(time.time())
    content['processName'] = str(_type) + '_' + str(pid) + '_' + str(content['startUTC'])   #这个进程名是唯一标识，由采集类型+PID+创建进程时间构成
    content['userHost'] = userHost
    content['userDatabase'] = userDatabase
    content['userCollection'] = userCollection
    content['screenNameList'] = screenNameList
    content['accountIdList'] = accountIdList
    content['tweetHost'] = tweetHost
    content['tweetDatabase'] = tweetDatabase
    content['tweetCollection'] = tweetCollection
    content['keywords'] = keywords
    content['_type'] = _type
    content['isES'] = False
    if tweetHost == None:
        count = MongoClient(userHost)[userDatabase][userCollection].count()
    else:
        count = MongoClient(tweetHost)[tweetDatabase][tweetCollection].count()
    content['count'] = count
    content['countBefore'] = count

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

    processClient = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
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
    """
    判断采集进程采集进度
    :param request:
    :return:
    """
    pass

def runningProcessInfo(request):
    """
    返回正在运行的进程的信息
    :param request:
    :return:
    """
    client = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    for process in client.find({'state':'running'}):
        pass


def getBasicInfo(request):
    """
    获取基本信息，包括正在运行的进程、代理情况、服务器资源使用情况等
    :param request:
    :return:
    """


    client = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    processList = []
    for process in client.find({'state': 'running'}):
        process.pop('_id')
        process['_processName'] = process['processName'].split('_')[0] + '_' + process['processName'].split('_')[1] + '_*'
        processList.append(process)
    return JsonResponse({'proxyResult':info['proxyList'],'serverInfo':info,'process':processList})


def searchProcess(request):
    """
    搜索进程，并将满足条件的进程信息返回
    :param request:
    :return:
    """
    pass

def getDataAndColInfo():
    """
    获取数据库与集合名称
    :return: {'user':[],'tweet':[]}
    """
    client = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_DB_COL_NAME]
    userList = []
    tweetList = []
    for i in client.find({'type':'user'}):
        userList.append(i['HostName'] + '|' + i['DBName'] + '|' + i['COLName'])
    for i in client.find({'type':'tweet'}):
        tweetList.append(i['HostName'] + '|' + i['DBName'] + '|' + i['COLName'])
    result = {}
    result['user'] = userList
    result['tweet'] = tweetList
    return result


def getProcessIO(request):
    processName = request.GET['processName']
    client = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    process = client.find_one({'processName':processName})
    pid = process['pid']
    if psutil.pid_exists(pid):
        result = process['count'] - process['countBefore']
        return JsonResponse({'level':'normal','data':result})
    else:
        str = "采集完成"
        if process['_type'] == 'userFollowers':
            str = "粉丝ID" + str
        if process['_type'] == 'userFriends':
            str = "朋友ID" + str
        if process['_type'] == 'userInfo':
            str = "用户信息" + str
        return JsonResponse({'level':'error','data':str})

def createColHtml(request):

    result = getDataAndColInfo()
    return render(request, 'twitter/createCol.html', {'tweet': result['tweet'],'user':result['user']})

def createCol(request):
    """

    :param request:
    :return:
    """
    _type = None
    userDatabase = None
    userCollection = None
    userHost = None
    tweetHost = None
    tweetDatabase = None
    tweetCollection = None

    client = MongoClient(DEFAULTHOST)[PROCESS_DATABASE][PROCESS_DB_COL_NAME]
    _type = request.GET['type']
    if _type == 'user':
        userHost = request.GET['userHost']
        userDatabase = request.GET['userDatabase']
        userCollection = request.GET['userCollection']
        if userCollection in MongoClient(userHost)[userDatabase].collection_names():
            return HttpResponse("集合已经存在，请重新输入")
        else:
            MongoClient(userHost)[userDatabase][userCollection].ensure_index('id', unique=True)
            MongoClient(userHost)[userDatabase][userCollection].ensure_index('screen_name', unique=True)
            MongoClient(userHost)[userDatabase][userCollection].ensure_index('captured_friends_count')
            MongoClient(userHost)[userDatabase][userCollection].ensure_index('captured_followers_count')
            client.insert({'type':'user','HostName':userHost,'DBName':userDatabase,'COLName':userCollection})
            return HttpResponse("创建集合成功")
    elif _type == 'tweet':
        tweetHost = request.GET['tweetHost']
        tweetDatabase = request.GET['tweetDatabase']
        tweetCollection = request.GET['tweetCollection']
        if tweetCollection in MongoClient(tweetHost)[tweetDatabase].collection_names():
            return HttpResponse("集合已经存在，请重新输入")
        else:
            MongoClient(tweetHost)[tweetDatabase][tweetCollection].ensure_index('id', unique=True)
            client.insert({'type':'tweet','HostName':tweetHost,'DBName':tweetDatabase,'COLName':tweetCollection})
            return HttpResponse("创建集合成功")
    #删除集合
    else:
        try:
            selectUserDatabase = request.GET['selectUserDatabase']
            userHost = selectUserDatabase.split('|')[0]
            userDatabase = selectUserDatabase.split('|')[1]
            userCollection = selectUserDatabase.split('|')[2]
        except:
            pass
        try:
            selectTweetDatabase = request.GET['selectTweetDatabase']
            tweetHost = selectTweetDatabase.split('|')[0]
            tweetDatabase = selectTweetDatabase.split('|')[1]
            tweetCollection = selectTweetDatabase.split('|')[2]
        except:
            pass

        print userHost,tweetHost
        if tweetHost != '已存在的数据库':
            if tweetCollection in MongoClient(tweetHost)[tweetDatabase].collection_names():
                MongoClient(tweetHost)[tweetDatabase].drop_collection(tweetCollection)
            client.delete_one({'type':'tweet','HostName':tweetHost,'DBName':tweetDatabase,'COLName':tweetCollection})
        if userHost != '已存在的数据库':
            if userCollection in MongoClient(userHost)[userDatabase].collection_names():
                MongoClient(userHost)[userDatabase].drop_collection(userCollection)
            client.delete_one(
                {'type': 'user', 'HostName': userHost, 'DBName': userDatabase, 'COLName': userCollection})

        return HttpResponse("删除集合成功")

def getProxyIP(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        regip = real_ip.split(",")[0]
    except:
        try:
            regip = request.META['REMOTE_ADDR']
        except:
            regip = ""
    if regip != PROXY_LIST[0]['host']:
        fp = open('./TwitterCapture/ProxyConstant.py','w')
        ProxyList = []
        _proxy = {}
        _proxy['host'] = regip
        _proxy['port'] = 8118
        _proxy['state'] = 'breakdown'
        ProxyList.append(_proxy)
        _str = "# coding=utf-8 \n" \
               "" \
               "# 专门用于代理常量\n" \
               "" \
               "PROXY_LIST=" + str(ProxyList)
        print _str
        fp.write(_str.encode('utf-8'))
        print 2222222222222
        fp.close()

    return HttpResponse(regip)