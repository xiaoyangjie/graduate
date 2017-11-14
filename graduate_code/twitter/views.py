# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

def index(request):
    return render(request,'twitter/index.html')

def userInfo(request):
    return render(request, 'twitter/index.html')

def userFriends(request):
    return render(request, 'twitter/index.html')

def userFollowers(request):
    return render(request, 'twitter/index.html')

def realtimeTweet(request):
    return render(request, 'twitter/index.html')

def filterTweet(request):
    return render(request, 'twitter/index.html')

def historyTweet(request):
    return render(request, 'twitter/index.html')
