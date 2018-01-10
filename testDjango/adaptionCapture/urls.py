# coding=utf-8
from django.conf.urls import url
from adaptionCapture.views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'contentCapture/$', contentCapture, name='contentCapture'),
    url(r'urlCapture/$', urlCapture, name='urlCapture'),
    url(r'getHtml/$', getHtml, name='getHtml'),
    url(r'getPageSource/$', getPageSource, name='getPageSource'),
    url(r'getMaybeContent/$', getMaybeContent, name='getMaybeContent'),
    url(r'generateLabel/$', generateLabel, name='generateLabel'),
    url(r'specialCapture/$', specialCapture, name='specialCapture'),
    url(r'extendCapture/$', extendCapture, name='extendCapture'),
]