#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import *
from scawler import *
from interface import *
from controller import *
import threading

def main():

    controller = Controller()

    controller.start()

def run():
    for i in range(10):
        print("当前线程的名字是： " + threading.current_thread().name + "      "+str(i) + "\n")
def f():
    threads = []
    for i in  range(5):
        thread = threading.Thread(target=run)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()