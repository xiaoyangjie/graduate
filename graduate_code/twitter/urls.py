from django.conf.urls import url
from twitter.views import index as twitterIndex
from twitter.views import *


urlpatterns = [
    url(r'$', twitterIndex, name='twitterIndex'),
    url(r'userInfo/$',userInfo,name='userInfo'),
    url(r'userFriends/$',userFriends,name='userFriends'),
    url(r'userFollowers/$',userFollowers,name='userFollowers'),
    url(r'realtimeTweet/$',realtimeTweet,name='realtimeTweet'),
    url(r'filterTweet/$',filterTweet,name='filterTweet'),
    url(r'historyTweet/$',historyTweet,name='historyTweet'),
]