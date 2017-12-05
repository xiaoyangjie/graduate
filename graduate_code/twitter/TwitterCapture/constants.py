# -*- coding:utf-8 -*-
# python2.7
# constants.py
# 常量定义文件




INFINITE = -1  # 无采集上限

PROXYLIST = ['192.168.1.148:8118']
ES_HOST = '192.168.1.148:9200'
PROXY = 'localhost:9000'
# PROXY_HOST = '127.0.0.1'
# PROXY_PORT = 9000
# PROXY_LIST = [{'host':'222.197.180.171','port':8118,'state':'normal'}]

from urllib import quote_plus
DEFAULTHOST = "mongodb://%s:%s@%s" % (quote_plus('@kb111'), quote_plus('ylb@(*wiki*)'), '222.197.180.245:30011')

# DEFAULTHOST = 'mongodb://localhost:27020'

# HOST = 'mongodb://mongo:123456@222.197.180.150'  # mongo host
BASE_PATH = "/home/server-cj/twitter/"  # Linux图片存储路径
WIN_BASE_PATH = "D:/twitter/"  # Windows图片存储路径

COOKIES_COLLECTION = {'host': DEFAULTHOST, 'db': 'account', 'cl': 'cookies'}  # Twitter的cookie数据表

# friends/followers列表采集临时记录数据表
RECORD_COLLECTION = {'host': DEFAULTHOST, 'db': 'account', 'cl': 'temp_record', 'name': 'record'}

# Twitter API的token数据表
TOKEN_COLLECTION = {'host': DEFAULTHOST, 'db': 'account', 'cl': 'twitter_apis', 'name': 'token'}  # 'db': 'token'

PROCESS_DATABASE = 'Process'

PROCESS_COLLECTION = 'Process'

PROCESS_DB_COL_NAME = 'DbAndColName'


#log文件地址
LOG_PATH = './twitter/TwitterCapture/logs/'

# 爬虫程序的HTTP头部
HTTP_HEADER = {'Connection': 'Keep-Alive',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
                             '(KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
               }

API_FOLLOW_LIMIT = 5000  # friends/followers列表单次采集数量上限
API_FOLLOW_TIME_LIMIT = 15  # 每15分钟，同一个token的friends/followers列表采集次数上限
API_SEARCH_LIMIT = 20  # 单次查询数量上限
API_LOOKUP_LIMIT = 100  # 单次查询用户信息的用户数上限
API_LOOKUP_TIME_LIMIT = 180  # 每15分钟，同一个token的用户信息采集次数上限
MAX_FOLLOW = 5000  # 每个用户所需采集的friends/followers列表长度上限
PROCESS_COUNT = 8  # 启动的线程数

UPDATE_TIME = 1481422944  # 时间戳，位于该时间之前的用户需重新采集用户信息

#####################################tweet的配置################################################

# HOST = "mongodb://192.168.178.101:27017,192.168.178.104:27017/?replicaSet=twitter"

# TOKEN_COLLECTION = {'host': 'mongodb://mongo:123456@222.197.180.150', 'db': 'token', 'cl': 'twitter_apis', 'name': 'token'}
# TOKEN_COLLECTION = {'host': DEFAULTHOST, 'db': 'crawler_statues', 'cl': 'twitter_apis', 'name': 'token'}
# USER_COLLECTION = {'host': DEFAULTHOST, 'db': 'twitter_user_tweet', 'cl': 'user', 'name': 'user'}
USER_COLLECTION = {'host': DEFAULTHOST, 'db': 'twitter', 'cl': 'user', 'name': 'user'}
TWEET_COLLECTION = {'host': DEFAULTHOST, 'db': 'twitter', 'cl': 'tweet', 'name': 'tweet'}
LOCAL_ONLY_COLLECTIONS = ['token']

USER_TIMELINE_COUNT = 200  # max = 200
FILITER_IDS_LIMIT = 4800
FILITER_KEYWORDS_COUNT = 2
QUEUE_LIMIT = 200
SLEEP_SECOND = 5
THREAD_COUNT = 8  # 8
NEOLOCATION_HOST = '192.168.178.103'
NEOLOCATION_PORT = 10002
DEFAULT_TWITTER_TOKEN = {'consumer_key': "fO4lXV6LLz5e1Ew6uRDtvXpIQ",
                        'consumer_secret': "LivsS9DTKh4Xmfo2vOG2tpKmrj8lxsYqiDgZLamPBJahFqnjUo",
                        'access_token': "3502218016-5v49PSLUTrYZ0VSYCcFhgBxmzJccjcSZLJqxr5Y",
                        'access_token_secret': "jthqxcccNUNkQfprBcIDjXuqxW1JZvI7HC8ZPHOCry5Dr"}