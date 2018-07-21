#!/usr/bin/python
# -*- coding: utf-8 -*-

# from Queue import Queue
import Queue
import threading
import urllib
import urlparse
import time
import json
import codecs
from bs4 import BeautifulSoup
from threading import Lock,Thread
from datetime import datetime

'''
演示一下程序：
该爬虫可以指定深度，指定线程数，指定主题三个功能 
第一步 爬取初始网页，也就是种子url
第二步 分析网页，抽取出相关链接，
第三步  分析抽取出来的链接是否满足爬取要求，
            比如深度，如果同时设定了主题，还需要判断网页上是否存在指定主题的内容
第四步  将满足爬取要求的链接放进爬取链接队列

下面运行一下做个基本演示

由于时间问题，我就把爬虫程序停下




效果就是这样
'''

# 指定初始URL

# _url = 'http://www.baidu.com/'
_url = 'http://news.sina.com.cn/'
# _url = 'http://www.pku.edu.cn/'

# 指定爬取深度
_depth = 2

# 指定线程数
_maxThread = 30

# 指定主题
_topic = []#'习近平'


import os, sys
from sys import exit
import codecs
import urllib2, urllib
    
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from time import sleep
from bs4 import BeautifulSoup


lock  = Lock()

# function to write file with add mode
def writeFileAdd(filename, content):
#     print "Writing into file:  %s\n" % filename
    with open(filename, "a+") as f:
        f.write(content) 

# function to write file with default mode
def writeFileDefault(filename, content):
#     print "Writing into file:  %s\n" % filename
    with open(filename, "w") as f:
        f.write(content)

def writeFileUTF8Default(filename, content):
    with codecs.open(filename,'w',encoding='utf8') as f:
        f.write(content)

def writeFileUTF8Add(filename, content):
    with codecs.open(filename,'a+',encoding='utf8') as f:
        f.write(content)

def exit():
    sys.exit()
            
def getFileNames(dir_path):        
    files = getFilesPath(dir_path)
    fileNames = []    
    for file in files:        
        file = os.path.split(file)[1]
        fileNames.append(file)
    return fileNames

def getFilesPath(dir_path):
    filesPath = []
    for parent, dirnames, filenames in os.walk(dir_path):    
        for filename in filenames[:]:                        
            full_filename =  os.path.join(parent, filename)
            filesPath.append(full_filename)
    return filesPath

def getContent(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    return lines    

def getContentUTF8(filename):
    with codecs.open(filename,'r',encoding='utf8') as f:
        lines = f.readlines()
    return lines 

def getContent2AString(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    return " ".join(lines)

def isAnscii(word):
    for elem in word:
        if ord(elem) >= 128 or ord(elem) < 48:
            return True
    return False
    
def deleteUnAnscii(sentence):
    tempList = []
    for elem in sentence.split():
        if not isAnscii(elem):
            tempList.append(elem)
    return " ".join(tempList) 

def getHtml(url):
    data = '' 
    while True:
        try:
            count = 1
            dcap = dict(DesiredCapabilities.PHANTOMJS)  
            dcap['phantomjs.page.settings.userAgent'] = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ') 
            driver = webdriver.PhantomJS(desired_capabilities=dcap)  
            driver.set_page_load_timeout(20)
            driver.set_script_timeout(20)
            driver.get(url)   
            data = driver.page_source   
            driver.save_screenshot('screenshot.png')  
            
#             file_path_html = './outer_data/' + url.replace('/', '###').replace('.', '+++').replace(':', '---').replace('htm', '').replace('html', '') + '.html'
#             writeFileUTF8Default(file_path_html, data)
            
            driver.quit()
            return data
        except :
            count += 1
            if count > 10:
                break
            
    
    return data
    
def cleanMe(html):
    soup = BeautifulSoup(html) # create a new bs4 object from the html data loaded
    for script in soup(["script", "style"]): # remove all javascript and stylesheet code
        script.extract()
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text
  
def parse_html(html):
    content = cleanMe(html)
    
    return content

count = 0
deadUrl = [] #存放死链
#crawledUrl = [] #存放全部爬取过的url，避免重复爬取
#多线程爬取类，获得多线程函数参数
#入口参数：url,depth,thread. depth = 0则无需进行爬虫
#返回：爬取的url列表
class CrawlThread(threading.Thread):
    def __init__(self,url,crawledUrl,topic_list,path):
        threading.Thread.__init__(self)
        self.url = url
        self.linklist = []
        self._running = True
        self.crawledUrl = crawledUrl
        self.topic_list = topic_list
        self.path = path
    # 目标url存活性判断:
    # 存活返回 True;否则返回False

    #判断结束标志位
    def terminate(self):
        self._running = False

    def urlStatus(self,url):
        try:
            response = urllib.urlopen(url)
            status = response.code
            if (status == 200 and  url not in self.crawledUrl):

                return True
            else:
                deadUrl.append(url)
                return False
        except:
            return False
    #判断url域名是否为当前域名
    def judgeDomain(self,testLink):
        domain = urlparse.urlparse(self.url).netloc #当前域名
        if domain == urlparse.urlparse(testLink).netloc:
            return True
        else:
            return False
    # 读取整个网页
    def getHtml(self,url):
        try:
            page = urllib.urlopen(url)
            htmlbody = page.read()
            return htmlbody
        except:
            print("访问错误！！！")
            return None

    def getfilepath(self,url):
        tempurl = url[7:len(url)].replace("/", "-")
        filepath = self.path  +"/"+ tempurl + ".html"
        filepath = filepath.replace("\\", "/")
        return filepath

    # 爬取url页面下的全部链接，多线程作用的函数
    def getLink(self,url):
        tmpLinks = []

        html = self.getHtml(url)
        if html is None:
            print("访问错误，请稍后再试")
            self._running = False
            return None

        soup = BeautifulSoup(html)
        links = soup.findAll('a')  # 返回一个列表
        ###获取<a>中href的值
        bad_links = {None, '', '#', ' '}  # 无用链接列表
        bad_protocol = {'javascript', 'mailto', 'tel', 'telnet'}  # 无用的头部协议，如javascript等
        right_protocol = {'http', 'https'}  # 存放正确的协议头部
        linklist = []  # 存放正常的链接
        for link in links:
            if link.get('href') in bad_links or link.get('href').split(':')[0] in bad_protocol:  #去除无用链接
                continue
            else:  # 列表中包含相对地址
                linklist.append(link.get('href'))
        # 将相对地址转换为绝对地址
        linklist_tmp = []
        for link in linklist:
            if link.split(':')[0] in right_protocol:
                if self.judgeDomain(link): #域名相同
                    linklist_tmp.append(link)
            else:
                link_temp = urlparse.urljoin(self.url, link) #相对变绝对
                linklist_tmp.append(link_temp)
        linklist = linklist_tmp
        # 去除重复链接 set()函数
        linklist = list(set(linklist))
        if linklist:
            for link in linklist:
                try:
                    response = urllib.urlopen(link)
                except:
                    print("访问错误，请稍后再试")
                    continue

                if response.code == 200 and link not in self.crawledUrl : #url存活性判断，去除死链
                    
                    if len(self.topic_list) == 0 :
#                         print 'nihao'
                        print("找到一个")
                        tmpLinks.append(link)
                        #上锁  保持只有一个线程访问crawledUrl
                        try:
                            page = response.read()
                        except:
                            print("被禁止访问，请稍后再试")
                            continue

                        filepath = self.getfilepath(link)
                        # 将网页保存在本地
                        writeFileDefault(filepath, page)

                        global lock
                        lock.acquire()
                        self.crawledUrl.append(link)
                        lock.release()

                        print(self.name)
                    else:
#                         print 'checking', link
                        content = self.getHtml(link)
                        if content is None:
                            continue
#                         content = cleanMe(content)
#                         if content.find(_topic.decode('utf8')) != -1:
                        for topic in self.topic_list:
                            topic = topic.encode("utf-8")
                            if content.find(topic) != -1:
                                print '找到了一个', link
                                tmpLinks.append(link)
                                try:
                                    page = response.read()
                                except:
                                    print("被禁止访问，请稍后再试！！！")
                                    break
                                filepath = self.getfilepath(link)
                                writeFileDefault(filepath, page)

                                lock.acquire()
                                self.crawledUrl.append(link)
                                lock.release()
                                #找到一个关键词就继续下一个
                                break
                else:
                    deadUrl.append(url)
#             for i in tmpLinks:
#                 print i
            self._running = False
            return tmpLinks
        else:#不再存在未爬取链接
            self._running = False
            return None


    def run(self): #线程创建后会直接运行run函数
        self.linklist = self.getLink(self.url)


    def getDatas(self):
        return self.linklist
    
# #广度遍历，爬取指定深度全部url
# def crawlDepth(url,depth,maxThread):
#     threadpool = [] #线程池
#     if depth == 0:
#         return url
#     else:
#         nowDepth = 1
#         print '爬虫深度：', nowDepth
#         th = CrawlThread(url)#获得深度为1时的全部url
#         th.setDaemon(True)
#         th.start()
#         th.join()
#         testLinks = Queue.deque(th.getDatas())
#         print 'testLinks:',testLinks
#         while nowDepth < depth and testLinks:
#             nowDepth = nowDepth + 1
#             print '爬虫深度：', nowDepth
#             tmpLinks = []
#             while testLinks:
#                 while len(threadpool) < maxThread:
#                     if testLinks:
#                         t = CrawlThread(testLinks.pop())
#                         t.setDaemon(True)
#                         threadpool.append(t)
#                         t.start()
#                     else:
#                         break
#                 for thread in threadpool:#等待线程结束
#                     thread.join()
#                     #取出线程数据
#                     tmp = thread.getDatas()
#                     if tmp:
#                         tmpLinks.extend(tmp)
#                 threadpool = []
#             if tmpLinks:
#                 testLinks = list(set(tmpLinks))
#             else:
#                 testLinks = Queue.deque([])
#         return crawledUrl
#

#start = time.time()


class Spider(object):

    def __init__(self,controller):
        self._thread_pool = []
        self._controller = controller


    def set_paramter(self,url,depth,maxThread,topic_list):
        self._url = url
        self._depth = depth
        self._maxThread = maxThread
        self._topic = topic_list
        self._crawledUrl = []

        self._crawledUrl_path = self.new_task_dir()



    #获取爬取到的链接
    def get_crawledUrls(self):
        return self._crawledUrl

    #得到存链接的路径
    def get_crawled_path(self):
        return self._crawledUrl_path

    def new_task_dir(self):
        dir_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S")


        now_path = os.getcwd().replace("\\", "/")
        path = now_path + "/crawledUrl/" + dir_name

        os.mkdir(path)
        self._log_file_path = path + "/log_" + dir_name + ".txt"
        self._log_file = open(self._log_file_path, mode="w")
        return path

    def get_log_path(self):
        return self._log_file_path

    def log(self,string):

        self._log_file.write(string)
        self._log_file.write("\n")

    #开始爬取
    def start_spider(self):
        self.crawlDepth(self._url, self._depth, self._maxThread)
        print(len(self._crawledUrl))


    #强制结束爬取
    def end_spider(self):
        if (len(self._thread_pool) > 0):
            for i in range(len(self._thread_pool)):
                self._thread_pool[i].terminate()


    #深度爬取
    def crawlDepth(self,urls, depth, maxThread):
        #self._threadpool = []  # 线程池
        if depth == 0:
            return urls
        else:
            nowDepth = 0
            # print '爬虫深度：', nowDepth
            # th = CrawlThread(url)  # 获得深度为1时的全部url
            # th.setDaemon(True)
            # th.start()
            # th.join()
            #testLinks = Queue.deque(th.getDatas())
            testLinks = Queue.deque(urls)
            print 'testLinks:', testLinks

            while nowDepth < depth and testLinks:
                nowDepth = nowDepth + 1
                print '爬虫深度：', nowDepth
                self.log("爬虫深度 : " + str(nowDepth))
                tmpLinks = []
                url_index = 0
                print("共%d个待爬取链接" % (len(testLinks)))
                self.log("共"+ str(len(testLinks)) + "个待爬取链接" )
                self._log_file.flush()
                while testLinks:

                    #如果线程池中的线程小于最大线程数   则创建线程
                    while len(self._thread_pool) < maxThread:
                        if testLinks:
                            t = CrawlThread(testLinks.pop(),self._crawledUrl,self._topic,self._crawledUrl_path)
                            t.setDaemon(True)
                            self._thread_pool.append(t)
                            url_index +=1
                            print("开始爬取第%d个待爬取连接" % (url_index) )
                            self.log("开始爬取第" + str(url_index) + "个待爬取连接"  )
                            self._log_file.flush()
                            t.start()
                        else:
                            break

                    for thread in self._thread_pool:
                        if not thread.is_alive():
                            tmp = thread.getDatas()
                            if tmp:
                                tmpLinks.extend(tmp)
                            self._thread_pool.remove(thread)

                    #如果待爬取的链接队列为空 循环主线程，等待线程池中的线程运行完毕
                    # if not testLinks:
                    #
                    #     while True:
                    #         #如果线程池中的线程个数为零则退出  否则进行一次判断：判断子线程是否运行完毕 每判断一次间隔一秒钟
                    #         if len(self._thread_pool) <= 0:
                    #             break
                    #         #说明线程正在运行，主线等待一秒钟
                    #         sleep(1)

                    # while(len(self._thread_pool) > 0):
                    #     count = 0
                    #     dead_flag_list = []
                    #     #判断线程池中的线程是否结束  并标记已经结束的线程
                    #     for thread in self._thread_pool:  # 等待线程结束
                    #         # thread.join(timeout=1)
                    #         # 取出线程数据
                    #         if not thread.is_alive():
                    #             tmp = thread.getDatas()
                    #             if tmp:
                    #                 tmpLinks.extend(tmp)
                    #             dead_flag_list.append(count)
                    #         count += 1

                        #根据标记flag 从线程池中删除每一个已经结束的线程
                        #for flag in dead_flag_list:
                        #    del self._thread_pool[flag]
                        #sleep(1)

                    #如果不为空，则说明线程池已满，需要等待，继续让主线程等待一秒

                #将剩余的线程执行完
                if len(self._thread_pool) > 0 :
                    for thread in self._thread_pool:
                        thread.join()

                    for thread in self._thread_pool:
                        tmp = thread.getDatas()
                        if tmp:
                            tmpLinks.extend(tmp)
                    self._thread_pool.remove(thread)

                if tmpLinks:
                    testLinks = list(set(tmpLinks))
                else:
                    testLinks = Queue.deque([])
            #设置爬取结束标志位 以便停止刷新
            self._controller.terminate_spider()
            return self._crawledUrl


def main():
    url, depth, maxThread = _url, _depth, _maxThread
    # crawlDepth(url,depth,maxThread)
    # for url in crawledUrl:
    #     print url



#main()
#print "Total time :%s"%(time.time()-start)



