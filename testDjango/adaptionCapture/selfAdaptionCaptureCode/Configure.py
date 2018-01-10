# coding=utf-8

from urllib import quote_plus
MONGO_DEFAULT = "mongodb://%s:%s@%s" % (quote_plus('kb314'), quote_plus('fzdwxxcl.314'), '121.49.99.14:30011')
# MONGO_DEFAULT = "mongodb://localhost:27020"

MONGO_DB = 'yj'

MONGO_URL = 'Url'

MONGO_WEBSITE_CONTENT = 'WebsiteContent'

MONGO_CODE = 'Code'

MONGO_WEBSITE_PARSE = 'WebsiteParse'

# DEFAULT_URL = 'https://movie.douban.com/subject/25723583/'

DEFAULT_URL = 'https://movie.douban.com/subject/20495023'

ELEMENT_LIST = [
                 {'name':'url','content':['湄公河行动','战狼2'], 'type':'href'},
                # {'name' : 'title','content':'英伦对决 The Foreigner', 'type':'text'},
                {'name' : '评分', 'content' :'7.2', 'type':'text'},
                {'name' :'标题', 'content': '英伦对决 The Foreigner' , 'type':'text'}]
