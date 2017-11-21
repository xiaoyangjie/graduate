# -*- coding:utf-8 -*-
import sys
sys.path.insert(0, '/home/server-cj/twitter/Django')
from TwitterTweetCapture.common.decorator import *
from TwitterTweetCapture.api.API import *
from TwitterTweetCapture.common.tools import createCollection
from TwitterTweetCapture.common.constants import *
from argparse import *

@setLogging()
def filterRealtimeTweet(tweetHost=DEFAULTHOST, tweetDatabase=None, tweetCollection=None,
                 proxyList=None,ids=None, keywords=None, locations=None,classificationName=None):
    """

    :param tweetHost:
    :param tweetDatabase:
    :param tweetCollection:
    :param proxyList:
    :param ids:
    :param keywords:
    :param locations:
    :return:
    """
    createCollection(tweetHost, tweetDatabase, tweetCollection,'tweet')
    mul_api = MultiProcessAPI(proxy_list=proxyList)
    mul_api.get_filter_tweet(tweet_collection={'host': tweetHost, 'db': tweetDatabase, 'cl': tweetCollection,
                                               'name': 'tweet'},
                             ids=ids, keywords=keywords, locations=locations, classificationName=classificationName
                             )  # ids

if __name__ == '__main__':
    # parser = ArgumentParser()
    # parser.add_argument('parameters', nargs='?', type=str, help='all parameters', default=None)
    # parser.add_argument(
    #     '-H', '--host', type=str, help='tweet mongo host', dest='host', default=None)
    # parser.add_argument(
    #     '-d', '--database', type=str, help='tweet database name', dest='database', default=None)
    # parser.add_argument(
    #     '-c', '--collection', type=str, help='tweet collection name', dest='collection', default=None)
    # parser.add_argument(
    #     '-p', '--proxy_list', nargs='+', type=str, help='proxy_list', dest='proxy_list', default=None)
    # parser.add_argument(
    #     '-nlh', '--nelocationhost', type=str, help='nelocation host', dest='nelocation_dest_host', default=None)
    # parser.add_argument(
    #     '-nld', '--nelocationport', type=int, help='nelocation port', dest='nelocation_dest_port', default=None)
    # parser.add_argument(
    #     '-dd', '--dd_cl_name', type=str, help='dandao collection name', dest='dd_cl_name', default='')
    # parser.add_argument(
    #     '-ids', '--ids', nargs='+', type=int, help='filter ids', dest='ids', default=None
    # )
    # parser.add_argument(
    #     '-kwds', '--keywords', nargs='+', type=str, help='filter keywords', dest='keywords', default=None
    # )
    # parser.add_argument(
    #     '-l', '--locations', nargs='+', type=float, help='filter locations', dest='locations', default=None
    # )
    # args = parser.parse_args()
    # if args.parameters:
    #     filterRealtimeTweet(*eval(args.parameters)[0], **eval(args.parameters)[1])
    # else:
    #     filterRealtimeTweet(tweetDatabase=args.database, tweetCollection=args.collection,
    #                         proxyList=args.proxy_list,keywords=args.keywords)
    # time.sleep(1)
    # exit(0)


    # tweetHost = 'mongodb://mongo:123456@121.49.99.14'        # 1
    tweetHost = 'localhost:27020'
    tweetDatabase = 'twitter'
    tweetCollection = 'filter_tweet'

    proxyList = ['192.168.1.148:8118']       # 本机ip
    # proxyList = ['127.0.0.1:59998']
    # keywords = ['shoot,shooting']
    # keywords = ['terrorism,terrorist']
    # keywords = ['dead,die,died']
    # keywords = ['kill,killed,bomb']
    keywords = ['terrorism,kill, dead, bomb, shoot,shooting,die,died,terrorist,attack,attacked']
    # classificationName = 'terrorism'
    filterRealtimeTweet(tweetHost=tweetHost, tweetDatabase=tweetDatabase, tweetCollection=tweetCollection,
                        proxyList=proxyList, keywords=keywords)

