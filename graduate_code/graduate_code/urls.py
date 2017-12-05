# coding=utf-8
"""graduate_code URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin



urlpatterns = [
    ###############twiiter########################
    url(r'^twitter/', include('twitter.urls')),
    ###############管理账户##########################
    url(r'^admin/', admin.site.urls),
    # ############首页########################
    # url(r'^$', totalIndex, name="totalIndex"),
    # #############测试###############
    # url(r'^add/$', add, name="add"),
    # ##############ES查找#################
    # url(r'^search/$', searchIndex, name="searchIndex"),
    # url(r'^search/create/$', searchCreate, name="searchCreate"),
    # url(r'^search/finish_creart/$', finishCreart, name="finishCreart"),
]
