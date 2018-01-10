# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from urllib import quote_plus

import xlwt
from pymongo import MongoClient
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from selfAdaptionCaptureCode.HtmlCapture import htmlCaptureAPI
from selfAdaptionCaptureCode.HtmlCapture import HtmlCapture
from selfAdaptionCaptureCode.GenerateCode import generateCodeAPI

# Create your views here.

def index(request):
    return render(request, 'adaptionCapture/index.html')

def contentCapture(request):
    return render(request, 'adaptionCapture/contentCapture.html')

def urlCapture(request):
    return render(request, 'adaptionCapture/index.html')

def getHtml(request):
    htmlCaptureAPI.getDriver()
    return JsonResponse({'content': "获取网页成功", 'level': 'normal'})


def getPageSource(request):
    if htmlCaptureAPI.htmlCapture():
        return JsonResponse({'content': "获取网页成功", 'level': 'normal'})
    else:
        return JsonResponse({'content': "页面不存在，重新自定义采集", 'level': 'error'})

def specialCapture(request):
    pass

@csrf_exempt
def extendCapture(request):
    """
    扩展采集，即采集内容时，将同类的链接也采集了
    :param request:
    :return:
    """
    labelList = []
    print request.POST
    labelList = request.POST['labelList'].split(',')
    print labelList[0]
    selectUrlsDatabase = request.POST['selectUrlsDatabase']
    urlsHost = selectUrlsDatabase.split('|')[0]
    urlsDatabase = selectUrlsDatabase.split('|')[1]
    urlsCollection = selectUrlsDatabase.split('|')[2]
    urlsHost = "mongodb://%s:%s@%s" % (quote_plus('kb314'), quote_plus('fzdwxxcl.314'), urlsHost)

    selectContentDatabase = request.POST['selectContentDatabase']
    contentHost = selectContentDatabase.split('|')[0]
    contentDatabase = selectContentDatabase.split('|')[1]
    contentCollection = selectContentDatabase.split('|')[2]
    contentHost = "mongodb://%s:%s@%s" % (quote_plus('kb314'), quote_plus('fzdwxxcl.314'), contentHost)

    htmlCaptureAPI.extendCpature(labelList=labelList, urlsHost=urlsHost, urlsDatabase=urlsDatabase, urlsCollection=urlsCollection,
                                 contentHost=contentHost, contentDatabase=contentDatabase, contentCollection=contentCollection,)
    return JsonResponse({'content': "获取网页成功", 'level': 'normal'})

# def getTemplate(request):
#     print os.getcwd()
#     file_name = os.getcwd() + '/adaptionCapture/templates/adaptionCapture/template.html'
#     response = StreamingHttpResponse(file_iterator(file_name))
#     response['Content-Type'] = 'application/octet-stream'
#     response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
#     return response

# def file_iterator(file_name, chunk_size=512):
#     with open(file_name) as f:
#         while True:
#             c = f.read(chunk_size)
#             if c:
#                 yield c
#             else:
#                 break
@csrf_exempt
def getMaybeContent(request):
    """
    获取3个最有可能的内容，返回给用户
    :param request:
    :return:
    """
    name = None
    content = None
    name = request.POST['name']
    content = request.POST['content']
    print name
    print content
    contentList = generateCodeAPI.getMayContent(content)
    print len(contentList)
    if contentList != []:
        return JsonResponse({'content': contentList, 'level': 'normal'})
    else:
        return JsonResponse({'content': "匹配失败", 'level': 'error'})

@csrf_exempt
def generateLabel(request):
    num = None
    name = None
    _type = None
    num = request.POST['num']
    name = request.POST['name']
    _type = request.POST['type']

    generateCodeAPI.generateProcedure(name, num, _type)
    print 1111111
    return JsonResponse({'content': "ss", 'level': 'normal'})

def exportCSV(request):
    selectContentDatabase = request.POST['selectContentDatabase']
    contentHost = selectContentDatabase.split('|')[0]
    contentDatabase = selectContentDatabase.split('|')[1]
    contentCollection = selectContentDatabase.split('|')[2]
    savePath = request.POST['savePath']
    MONGO_DEFAULT = "mongodb://%s:%s@%s" % (quote_plus('kb314'), quote_plus('fzdwxxcl.314'), '121.49.99.14:30011')
    mongoClient = MongoClient(MONGO_DEFAULT)[contentDatabase][contentCollection]

    workbook = xlwt.Workbook(encoding='utf-8')
    EXCEL_ROWS = 65535
    EXCEL_COLS = 256
    nrows, total_rows, sheet_num = 0, 0, 0

    for data in mongoClient.find():
        data.pop('_id')
        if (nrows % EXCEL_ROWS == 0):
            wsheet = workbook.add_sheet('sheet' + str(sheet_num), cell_overwrite_ok=True)
            nrows = 0
            sheet_num = sheet_num + 1
        keys = data.keys()
        cols_num = EXCEL_COLS if len(keys) > EXCEL_COLS else len(keys)
        for ncol in xrange(cols_num):
            value = data[keys[ncol]]
            wsheet.write(nrows, ncol, value)
        nrows = nrows + 1
        total_rows = total_rows + 1
    workbook.save(savePath)

def showInfo(request):
    """
    返回采集完了的url
    :param request:
    :return:
    """
    if htmlCaptureAPI.showFinishUrlQueue.qsize() != 0:
        finishUrl = htmlCaptureAPI.showFinishUrlQueue.get()
        return JsonResponse({'level':'normal', 'data':finishUrl})
    else:
        return JsonResponse({'level':'error'})

