#encoding=utf8
import requests
import random
import sys, socket, time, threading

HOST = '192.168.1.148'
PORT = 8111
#代理IP
# PROXYLIST = [{'host':'192.168.1.108','port':8111},
#              {'host':'192.168.1.36','port':8111},
#              {'host':'192.168.1.66','port':8111}]
PROXYLIST = [{'host':'127.0.0.1','port':59998}]

#####################################################
#
# Proxy模块，用于定时检测代理是否有效
#
#######################################################
class Proxy(object):
    def __init__(self,proxyList):
        self.proxyList = []  #用于存储可以使用的代理
        self.PROXYLIST = proxyList

    def proxyStatus(self):
        """
        监控代理，将可以使用的代理放入self.proxyList中
        :return:
        """
        TESTURL = 'https://www.google.com'
        num = 0
        for i in range(len(self.PROXYLIST)):
            ########代理格式##################
            proxies = {'http':'http://%s' %(self.PROXYLIST[i].get('host')+':'+str(self.PROXYLIST[i].get('port'))),
                        'https':'http://%s' %(self.PROXYLIST[i].get('host')+':'+str(self.PROXYLIST[i].get('port')))}
            try:
                r = requests.get(TESTURL, proxies=proxies)  #访问GOOGLE
                if r.status_code == 200:###########说明这个代理是好的######################
                    self.PROXYLIST[i]['state'] = 'normal'
                    if self.PROXYLIST[i] not in self.proxyList:
                        self.proxyList.append(self.PROXYLIST[i])#############添加代理############
                else:
                    self.PROXYLIST[i]['state'] = 'breakdown'
                    num += 1
                    if self.PROXYLIST[i] in self.proxyList:###########说明这个代理是不能使用的######################
                        self.proxyList.remove(self.PROXYLIST[i])  ##########删除代理################
            except requests.exceptions.ConnectionError: #连接错误，说明代理端口没有打开:
                num += 1
                self.PROXYLIST[i]['state'] = 'breakdown'
            except TypeError:
                pass

        if num == len(self.PROXYLIST):
            from twitter.TwitterCapture import ProxyConstant
            print ProxyConstant.PROXY_LIST
            reload(ProxyConstant)
            self.PROXYLIST = ProxyConstant.PROXY_LIST
            print 33333333333
            print self.PROXYLIST
        ###########每过30秒重新检测一次，使用的是异步#######################
        threading.Timer(60, self.proxyStatus).start()

    def getProxyStatus(self):
        pass


LOGGING = True
loglock = threading.Lock()
#打印日志到标准输出
def log(s, *a):
    if LOGGING:
      loglock.acquire()
    try:
        print('%s:%s' % (time.ctime(), (s % a)))
        sys.stdout.flush()
    finally:
        loglock.release()
###########################################
#
#  实现端口转发
#
##############################################

class PipeThread(threading.Thread):

    pipes = []   #静态成员变量，存储通讯的线程编号
    pipeslock = threading.Lock()  #线程锁，用于建立多个线程，且不会冲突
    def __init__(self, source, sink):
        super(PipeThread, self).__init__()
        self.source = source   #发送数据端
        self.sink = sink       #接收数据端
        log('Creating new pipe thread %s (%s -> %s)',
            self, source.getpeername(), sink.getpeername())
        self.pipeslock.acquire()  #锁住线程
        try:
            self.pipes.append(self)  #记录线程
        finally:
            self.pipeslock.release()  #释放锁
        self.pipeslock.acquire()  #锁住线程
        try:
            pipes_now = len(self.pipes)     #记录当前还有多少线程
        finally:
            self.pipeslock.release()  #释放锁
        log('%s pipes now active', pipes_now)

    def run(self):
        """
        接收数据，数据接收完毕，关闭连接
        :return:
        """
        while True:
            try:
                data = self.source.recv(1024)   #source接收数据后，自动发往sink端
                if not data:
                    break
                self.sink.send(data)     #sink接收完source的数据后，发往目的地址，如twitterAPI
            except:
                break



        log('%s terminating', self)
        self.pipeslock.acquire()   #锁住线程
        try:
            self.pipes.remove(self)  #移除线程
        finally:
            self.pipeslock.release() #释放锁
        self.pipeslock.acquire() #锁住线程
        try:
            pipes_left = len(self.pipes)   #记录当前还有多少线程
        finally:
            self.pipeslock.release() #释放锁
        log('%s pipes still active', pipes_left)

#####################################
#
#  打一个洞，每一个请求生成一个新的socket。
#
####################################
class Pinhole(threading.Thread):
    def __init__(self, host , port, proxyList):
        self.PROXYLIST = proxyList
        self.proxy = Proxy(proxyList)
        self.proxyList = self.proxy.proxyList
        self.proxy.proxyStatus()  #异步运行代理模块，将可以使用的代理放入self.proxy中
        self.getProxyInfo()
        super(Pinhole, self).__init__()
        log('Redirecting: %s: %s->%s',host, port, proxyList)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #在本机上开一个端口，用于接收用户的请求
        self.sock.bind((host, port))    #监听这个端口
        self.sock.listen(10000)          #同时监听数量最大为100

    def run(self):
        """
        一直监听本机socket端口，每来一次请求，就打开一个新的socket端口，建立一个链接。
        :return:
        """
        while True:
            self.proxyList = self.proxy.proxyList #每次读取可使用的代理
            print self.proxyList
            if self.proxyList == []:
                self.proxyList = self.PROXYLIST   #如果没有可使用的代理，则给出全部代理（主要是怕代理使用过多，而不是真正的没有代理了）
            try:
                newsock, address = self.sock.accept()  #####监听端口，建立新的连接（这里是用户和socket的新连接）
                log('Creating new session for %s:%s', *address)
                fwd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ##建立连接
                rNum = random.randint(0,len(self.proxyList) - 1) #随机取出一个代理
                print rNum
                fwd.connect((self.proxyList[rNum].get('host'), self.proxyList[rNum].get('port')))  #这里是将新的socket与代理地址建立连接

                PipeThread(newsock, fwd).start() #正向传送，数据发往代理
                PipeThread(fwd, newsock).start() #逆向传送，从代理接收数据
            except:pass

    def getProxyInfo(self):
        self.PROXYLIST = self.proxy.PROXYLIST
        threading.Timer(30, self.getProxyInfo).start()

if __name__ == '__main__':

    print('Starting Pinhole port fowarder/redirector')
    try:
    # port = int(sys.argv[1])
        host = HOST    #本机的ip
        port = PORT    #本机的端口号
        proxyList = PROXYLIST   #IP代理

    # try:
    #   newport = int(sys.argv[3])
    # except IndexError:
    #   newport = port
    except (ValueError, IndexError):
    # print('Usage: %s port newhost [newport]' % sys.argv[0])
        sys.exit(1)
    #sys.stdout = open('pinhole.log', 'w') #将日志写入文件
    Pinhole(host, port, proxyList).start()