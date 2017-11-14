# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse
from django.http import JsonResponse

from django.shortcuts import render

def index(request):
    return render(request, 'total_index/index.html')

def test(request):
    return render(request, 'total_index/test.html')

def add(request):
    a = request.GET['a']
    b = request.GET['b']
    a = int(a)
    b = int(b)
    return HttpResponse(str(a+b))