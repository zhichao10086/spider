#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk
from Tkinter import *
from CONSTANT import *
from ttk import *
import tkFileDialog
import os
import tkMessageBox
import webbrowser
from itertools import islice

class App(object):

    def __init__(self,controller):
        self._controller = controller
        self._maxThread = 0
        self._depth = 0
        self._urls = []
        self._key_words = []
        self._crawled_list_index = 0
        self._log_index = 0
        self._master = Tk()
        self.init_widget_layout(self._master)

    def init_widget_layout(self,master):

        master.title(APP_NAME)
        #总体布局分为上下两个容器
        self._frame_top = Frame(master).grid(row = 0)
        #self._frame_down = Frame(master).grid(row = 1)

        #self._frame_down_left = Frame(self._frame_down).grid(row = 0,column = 0)
        #self._frame_down_right = Frame(self._frame_down).grid(row = 0,column = 1)

        #第一排控件

        self._btn_start = Button(self._frame_top,text = BTN_START)
        self._btn_end = Button(self._frame_top,text = BTN_END)
        self._label_thread = Label(self._frame_top,text = LABEL_THREAD)
        self._cbx_thread = Combobox(self._frame_top)
        self._cbx_thread["values"] = range(1,MAX_THREAD+1)
        self._label_depth = Label(self._frame_top,text = LABEL_DEPTH)
        self._cbx_depth = Combobox(self._frame_top)
        self._cbx_depth["values"] = range(1,MAX_DEPTH+1)
        self._cbx_thread.current(5)
        self._cbx_depth.current(3)

        #上层的第二排控件
        self._label_keywords = Label(self._frame_top,text = LABEL_KEYWORDS)
        self._entry_keywords = Entry(self._frame_top)
        #打开地址文件按钮
        self._btn_openurls = Button(self._frame_top,text = BTN_OPEN_URLS_FILE)
        self._entry_urls = Entry(self._frame_top)

        self._btn_start.grid(row = 0, column = 0)
        self._btn_end.grid(row = 0, column = 1)
        self._label_thread.grid(row = 0, column = 2)
        self._cbx_thread.grid(row = 0, column = 3)
        self._label_depth.grid(row = 0, column = 4)
        self._cbx_depth.grid(row = 0, column = 5)

        self._label_keywords.grid(row = 1, column = 0)
        self._entry_keywords.grid(row = 1, column = 1)
        self._btn_openurls.grid(row = 1, column = 2)
        self._entry_urls.grid(row = 1, column = 3)


        #下方控件  包括 urllist

        self._list_url = Listbox(self._frame_top)
        self._list_url.grid(row=2,column = 0,columnspan = 3,sticky = tk.N +tk.E+tk.W)

        self._list_log = Listbox(self._frame_top)
        self._list_log.grid(row = 2,column = 3,columnspan = 3,sticky = tk.N +tk.E+tk.W)

        #绑定事件
        self.bind_all_event()


    def bind_all_event(self):
        self._btn_start.bind("<Button-1>",self.btn_start_event)
        self._btn_end.bind("<Button-1>",self.btn_start_event)
        self._btn_openurls.bind("<Button-1>",self.open_urlfile_event)
        self._list_url.bind("<Double-Button-1>",self.openurl)


    def open_urlfile_event(self,event):
        filename = tkFileDialog.askopenfilename(initialdir=os.getcwd())
        file = open(filename)

        urls = file.readlines()

        for url in urls:
            self._urls.append(url.split("\n")[0])
        temp = self._entry_urls.get()

        self._entry_urls.delete(0,len(temp))
        self._entry_urls.insert(0,filename)


    #开始按钮的事件
    def btn_start_event(self,event):
        #获得所有参数

        #获得所有的值
        maxThread = self._cbx_thread.get()
        depth = self._cbx_depth.get()
        keywords = self._entry_keywords.get()
        self._key_words = keywords.split(" ")

        if(maxThread ==""):
            tkMessageBox.showinfo(title=WARNING,message=thread_warning)
            return
        if (depth == ""):
            tkMessageBox.showinfo(title=WARNING, message=depth_warning)
            return

        if len(self._urls)<=0:
            tkMessageBox.showinfo(title=WARNING, message=url_warning)
            return

        self._maxThread = int(maxThread)
        self._depth = int(depth)
        self._log_index = 0
        self._crawled_list_index = 0


        self._controller.set_spider_paramter(self._urls,self._depth,self._maxThread,self._key_words)
        self._controller.start_spider()

    def clear_log(self):
        #清空LIST
        self._list_url.delete(0,END)



    #结束按钮的事件
    def btn_end_event(self,event):
        self._controller.start_spider()


    #刷新爬取到的urllist
    def refresh_crawled_urls_list(self,crawled_urls):
        for i in range(self._crawled_list_index ,len(crawled_urls)):
            self._list_url.insert(END,crawled_urls[i])

        #将每一次的位置记录下来
        self._crawled_list_index = len(crawled_urls)

    def refresh_log(self,filepath):
        f = open(filepath,"r")
        for line in islice(f, self._log_index, None):
            self._list_log.insert(END,line)
            self._log_index +=1
        f.close()

    def openurl(self,event):

        selected = self._list_url.curselection()[0]
        url = self._list_url.get(selected,selected)[0]

        tempurl = url[7:len(url)].replace("/", "-")
        crawled_path = self._controller.get_crawled_path()
        filepath = crawled_path+"/" +tempurl +".html"
        webbrowser.open(filepath)

    def start(self):
        self._master.mainloop()




