# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.views.decorators.csrf import csrf_exempt
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
from program_code.TwitterCapture.TwitterTweetCapture.TwitterAPIKeywords import twitterAPIKeywords as _twitterAPIKeywordsCapture
from program_code.TwitterCapture.GetMongoData import GetMongoData
from multiprocessing import Process
from pymongo import MongoClient
from program_code.TwitterCapture.TwitterUserCapture.TwitterUserCapture.common.constants import \
    MONGOHOST,PROCESS_DATABASE,PROCESS_COLLECTION,PROXY,PROCESS_DB_COL_NAME
from django.template import RequestContext
from django.shortcuts import render_to_response
def index(request):
    return render(request,'twitter/index.html')

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
        kwargs['keywords'] = keywords
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
        if userDatabase == '':
            userDatabase = None
    except:pass
    try:
        userCollection = request.GET['userCollection']
        if userCollection == '':
            userCollection = None
    except:pass
    try:
        screenNameList = request.GET['screenNameList'].split(',')
        if screenNameList == ['']:
            screenNameList = None
    except:pass
    try:
        accountIdList = request.GET['accountIdList'].split(',')
        if accountIdList == ['']:
            accountIdList = None
    except:pass
    try:
        tweetDatabase = request.GET['tweetDatabase']
        if tweetDatabase == '':
            tweetDatabase = None
    except:pass
    try:
        tweetCollection = request.GET['tweetCollection']
        if tweetCollection == '':
            tweetCollection = None
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
        if userDatabase == '':
            userDatabase = None
    except:pass
    try:
        userCollection = request.GET['userCollection']
        if userCollection == '':
            userCollection = None
    except:pass
    try:
        screenNameList = request.GET['screenNameList'].split(',')
        if screenNameList == ['']:
            screenNameList = None
    except:pass
    try:
        accountIdList = request.GET['accountIdList'].split(',')
        if accountIdList == ['']:
            accountIdList = None
    except:pass
    try:
        tweetDatabase = request.GET['tweetDatabase']
        if tweetDatabase == '':
            tweetDatabase = None
    except:pass
    try:
        tweetCollection = request.GET['tweetCollection']
        if tweetCollection == '':
            tweetCollection = None
    except:pass
    #
    if tweetDatabase is None or tweetCollection is None:
        return JsonResponse({'level': 'error', 'content': '没有填写数据库，请填写'})
##################获取实时数据(只用于显示filterTweet与realtimeTweet)#################################
    result = {}
    if _type not in ('userRealtimeTweet','filterTweet'):
        return JsonResponse({'level':'error','content':'类型错误，这个实时数据按钮只接受关键词推文采集与实时用户推文采集'}, safe=False)

    result = GetMongoData.realtimeInfoGet(tweetDatabase=tweetDatabase,tweetCollection=tweetCollection)
    if result == {}:
        return JsonResponse({'level': 'error', 'content': '实时采集程序没有运行，请仔细检查'}, safe=False)
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
    client = MongoClient(MONGOHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    content = {}
    content['pid'] = pid
    content['state'] = 'running'
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
    client = MongoClient(MONGOHOST)[PROCESS_DATABASE][PROCESS_COLLECTION]
    for process in client.find({'state':'running'}):
        pass

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
    client = MongoClient(MONGOHOST)[PROCESS_DATABASE][PROCESS_DB_COL_NAME]
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
    pid = int(processName.split('_')[1])
    if psutil.pid_exists(pid):
        result = psutil.Process(pid).io_counters()
        return JsonResponse({'level':'normal','data':result.write_bytes})
    else:
        return JsonResponse({'level':'error'})
