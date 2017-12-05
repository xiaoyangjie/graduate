
# from TwitterTweetCapture.api.API import API
# API().rest_find_one_tweet(841482821310980096)
import requests
import time

proxies = {'http':'http://127.0.0.1:10339'}
str = "Fri Nov 03 07:47:01 +0000 2017"
t = int(time.mktime(time.strptime(str, "%a %b %d %H:%M:%S +0000 %Y")))
print t
# result = requests.get('http://www.google.com',proxies=proxies)
r = requests.get('http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=P18OOmUjaf2MOs4ChcE&preferencesSaved=')
print r.content
#     result.raise_for_status()
#     print result.status_code
# except requests.RequestException as err:
#     print err.message

# import pymongo
# cli = pymongo.MongoClient('mongodb://mongo:123456@222.197.180.150')['twitter_user_tweet']['user']
# cli1 = pymongo.MongoClient('mongodb://mongo:123456@222.197.180.150')['twitter_user_tweet']['user_1']
# for i in cli.find():
#     i['id'] = i['account_id']
#     cli1.insert(i)