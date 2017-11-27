from django.conf.urls import url
from twitter.views import index as twitterIndex
from twitter.views import *


urlpatterns = [
    url(r'^$', twitterIndex, name='twitterIndex'),
    url(r'userInfo/$',userInfo,name='userInfo'),
    url(r'userFriends/$',userFriends,name='userFriends'),
    url(r'userFollowers/$',userFollowers,name='userFollowers'),
    url(r'realtimeTweet/$',realtimeTweet,name='realtimeTweet'),
    url(r'keywordsTweet/$',keywordsTweet,name='keywordsTweet'),
    url(r'userTweet/$',userTweet,name='userTweet'),
    url(r'monitor/$',monitor,name='monitor'),
    url(r'search/$',search,name='search'),
    url(r'historyTweet/$',historyTweet,name='historyTweet'),
    ###################################################
    url(r'twitterCapture/$',twitterCapture,name='twitterCapture'),
    url(r'twitterTerminate/$',twitterTerminate,name='twitterTerminate'),
    url(r'twitterCheck/$',twitterCheck,name='twitterCheck'),
    url(r'infoGet/$', infoGet, name='infoGet'),
    url(r'realtimeInfoGet/$', realtimeInfoGet, name='realtimeInfoGet'),
    url(r'processQuery/$', processQuery, name='processQuery'),
    url(r'dataQuery/$', dataQuery, name='dataQuery'),
    url(r'runningProcessInfo/$', runningProcessInfo, name='runningProcessInfo'),
    url(r'getProcessIO/$', getProcessIO, name='getProcessIO'),
    url(r'searchProcess/$', searchProcess, name='searchProcess'),
]