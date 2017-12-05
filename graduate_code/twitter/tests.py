# -*- coding: utf-8 -*-
import requests

r = requests.get('https://www.baidu.com')
print r
from urllib import quote_plus
DEFAULTHOST = "mongodb://%s:%s@%s" % (quote_plus('@kb111'), quote_plus('ylb@(*wiki*)'), '222.197.180.245:30011')
print DEFAULTHOST