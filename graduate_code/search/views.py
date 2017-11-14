# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'search/index.html')

def create(request):
    return render(request, 'search/create.html')

def finishCreart(request):
    _type = request.GET['type']
    mongoDatabase = request.GET['mongo_database']
    mongoCollection = request.GET['mongo_collection']
    if mongoDatabase == '' or mongoCollection == '':
        return HttpResponse("请检查mongoDatabase或者mongoCollection")
    mongo = mongoDatabase + '.' + mongoCollection
    if _type not in ('user','tweet'):
        return HttpResponse("请检查type是否输入正确")
    else :
        cmd_str = None
        if _type == 'user':
            cmd_str = "start mongo-connector -m localhost:27020 -t localhost:9200 -d elastic2_doc_manager -n "+ mongo +" -i id,description,created_at"
        if _type == 'tweet':
            cmd_str = "start mongo-connector -m localhost:27020 -t localhost:9200 -d elastic2_doc_manager -n "+ mongo +" -i id,text,user.id,created_at"
        print cmd_str
        os.system(cmd_str)
        return HttpResponse("完成创建")