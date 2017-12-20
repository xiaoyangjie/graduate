# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
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
    url = None
    url = request.GET['url']
    HtmlCapture().htmlCapture(url)
    print 1111111111111111

    return JsonResponse({'content': "获取网页成功", 'level': 'normal'})

def getTemplate(request):
    print os.getcwd()
    file_name = os.getcwd() + '/adaptionCapture/templates/adaptionCapture/template.html'
    response = StreamingHttpResponse(file_iterator(file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(file_name)
    return response

def file_iterator(file_name, chunk_size=512):
    with open(file_name) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
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