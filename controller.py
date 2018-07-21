#!/usr/bin/python
# -*- coding: utf-8 -*-


from interface import *
from scawler import Spider
import threading
from datetime import datetime
import time

class SpiderThread(threading.Thread):

    def __init__(self,fn):
        threading.Thread.__init__(self)
        self._running = True
        self.fn = fn
    #判断结束标志位
    def terminate(self):
        self._running = False

    def run(self):
        self.fn()




class Controller(object):

    def __init__(self):

        self._app = App(self)
        self._spider = Spider(self)
        self._spider_running = False
        self._timer = None

    def get_crawled_path(self):
        return self._spider.get_crawled_path()

    def start(self):
        self._app.start()

    #在界面中获取数据后先设置爬虫的参数然后调用start
    def set_spider_paramter(self,url,depth,maxThread,topic_list):
        self._spider.set_paramter(url,depth,maxThread,topic_list)

    def start_spider(self):
        #self._spider_thread = threading.Thread(target=self._spider.start_spider)
        #创建爬虫线程
        self._spider_thread = SpiderThread(self._spider.start_spider)
        self._spider_running = True
        #开启爬虫与刷新线程
        self._timer = threading.Timer(2,self.refresh_crawled_urls)
        self._spider_thread.start()
        self._timer.start()

    def terminate_spider(self):
        self._spider_running = False
        self._spider_thread.terminate()

    def refresh_crawled_urls(self):
        if self._spider_running:
            #只要爬虫还在运行就每一秒刷新一次爬取结果
            self._timer = threading.Timer(1,self.refresh_crawled_urls)
            self._app.refresh_crawled_urls_list(self._spider.get_crawledUrls())
            self._app.refresh_log(self._spider.get_log_path())
            self._timer.start()