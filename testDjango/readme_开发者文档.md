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

##2017/12/13
正则匹配的问题：24（中国）一直无法匹配，后来才发现。。re.compile("24（中国）")是将中国看成了一个组。。必须要re.compile("24\(中国\）")这样才行，转义。。

##2018/1/2
为什么需要使用扩展链接，首先我们要明白，毕设的题目是社交网络数据采集，用户针对的是大众用户（即对程序，DOM树不是太了解的用户）。对于社交网络扩展链接一般在访问的网页中，它与浏览器顶端的URL链接不一定一样（可能会跳转，如微博用户链接，扩展链接是https://weibo.com/1466554655,而浏览器上的链接是https://www.weibo.com/shelisun?is_hot=1）

##2018/1/3
论文的引用与目的：

1、国内网页去重技术研究:现状与总结。发现网页去重方法，找到满足自己的网页去重之完全去重，去重一模一样的网页的链接，目前在研究论文中的2.1.3的内容去重的基于最大正文块的网页去重，同时还可以利用这个方法达到寻找相似网页的目的。MD5

2、基于DOM树的网页相似度研究与应用。

3、Measuring Structural Similarity Among Web
Documents: Preliminary Results


1111、杂鱼论文：中文农业网页去重及相似度判断研究。


#论述

具体研究工作如下： (1)基于数据预提取的DOM树解析算法。解析DOM树是计算网页相似性的基础,也是提取网页信息的前提。本文主要提出了基于部分数据预提取的顺序DOM树解析算法,可以有效地提取绝大部分网页的DOM树结构。

基于标签统计判断相似性。增加class唯一性判定。