#记录开发的点点滴滴

##2017/12/7
初步实现了根据文本，自动生成采集代码，并全网站采集

遇到一个坑：在使用BeautifulSoup时，soup.find_all('body')[0].find_all('div')[2]这段代码本来想获取父节点下的第3个点，但是没用，需要加上soup.find_all('body')[0].find_all('div'，recursive=False)[2]才可以。而且，使用recursive=False时，不能使用attrs={}这个元素，即soup = soup.find_all(tag, attrs={'class': class_}，recursive=False)不行。无语。。主要是加了recursive=False后只会在子级找。

解决编码问题：r.content.decode(r.encoding).encode('utf-8')

##2017/12/12
r.content.decode(r.encoding).encode('utf-8')这种有问题，主要是r.encoding有时不一定对。。网页显示的是GB2312,但是r.encoding的是iso88591，这就尴尬了。使用chardet包，

import chardet

r = requests.get('https://www.weibo.com/2815081520/DvGP9pXPv?type=comment#_rnd1513063854649')

chardit1 = chardet.detect(r.content)

print chardit1['encoding']


数据可能不一致的问题。。主要是评论数之类的。很难。。