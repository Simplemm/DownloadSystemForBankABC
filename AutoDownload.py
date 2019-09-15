#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   AutoDownload.py    
@Desc    :   
@Project :   AutoDownloadApp
@Contact :   thefreer@outlook.com
@License :   (C)Copyright 2018-2019, TheFreer.NET
@WebSite :   www.thefreer.net
@Modify Time           @Author        @Version
------------           -------        --------
2019/07/26 16:03       the freer      1.0         
'''
import os
import time
import json
# argparse 模块用来给 Python 程序传递参数
import argparse
import subprocess
# apscheduler 这个模块用来自动下载调度
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date, timedelta
# 这个 AutoThread 继承自 threading.Thread，在此基础上实现了暂停线程和恢复线程功能
from AutoThread import Thread
import DownloadSystem


## 此程序每次更新和自动下载程序相关的配置需要重启此程序

def open_exe(exe_path, args=[], inps=[]):
	'''
	这个函数用于运行指定的 exe 可执行程序
	:param exe_path: 可执行程序的绝对路径或者相对路径
	:param args: 在命令行执行程序时输入的参数名，形式为列表
	:param inps: 在命令行执行程序时输入的参数值，形式为列表
	:return: 返回此可执行程序的在命令行运行结果的第一行输出
	:usage:
		以相对路径为例：
			open_exe("./notify.exe", ["msg", "title"], ["下载完成……", "自动下载通知！"])
			- 可执行文件路径为："./notify.exe"
			- 运行时传入的第一个参数名为："msg"，参数值为："下载完成……"；
			- 运行时传入的第二个参数名为："title"，参数值为："自动下载通知！"；
		则此函数运行等价于在当前目录打开命令行执行命令：
			./notify.exe -msg 下载完成…… -title 自动下载通知！
		
	'''
	# 使用可执行文件路径初始化命令字符串
	cmd = f"{exe_path}"
	# 下面这个循环是拼接命令的过程
	for arg,inp in zip(args, inps):
		cmd += f" -{arg} {inp}"
	# 实例化一个 Popen对象，这个对象保存了上面命令在命令行运行的信息
	s = subprocess.Popen(cmd,bufsize=0,stdout=subprocess.PIPE,universal_newlines=True)
	# nextline 是可执行文件运行的结果
	nextline = s.stdout.readline()
	return nextline
	

class AutoDownApp():
	'''
	这个类是一个自动运行下载程序的类
	本程序的自动下载表格就是基于这个类实现的
	它实现了自动下载表格需要的方法
	'''
	def download(self, exe):									# lihai
		with open("config.json", encoding="UTF-8") as conf:		# 打开配置文件
			config = json.load(conf)
		tables = config["tables"]								# 获取所有表信息
		table_list = []
		for t in tables:
			# 遍历所有表
			table_list.append(t)
		yes_date = datetime.today() + timedelta(-1)				# 获取前一天的日期
		yes_date = yes_date.strftime('%Y%m%d')					# 格式化日期：20190906
		DownloadSystem.download_api(table_list, yes_date)		# 调用下载函数
		open_exe("./notify.exe", ["msg", "title"], ["下载完成……", "自动下载通知！"])	# 调用通知程序


class AutoDownThread(Thread):
	'''
	这个类是一个自 动运行下载程序的线程类，继承自 AutoThread.Thread
	此线程类的 run 方法用于运行上面的 AutoDownApp 对象
	'''
	def __init__(self, down, trigger_config, args=None):
		super(AutoDownThread, self).__init__()
		# 初始化一个调度器对象
		self.scheduler = BackgroundScheduler()
		# 初始化一个触发器对象，其中 trigger_config 为触发器的配置，用于配置何时触发行为
		self.trigger = CronTrigger(**trigger_config)
		# 初始化一个 AutoDownApp 对象
		self.down = down
		# 初始化调度器的配置
		self.config = {
			"func": down.download, # 运行的函数，AutoDownApp.download，即自动下载
			"args": args, # 运行函数时需传入的参数，形式为列表
			"trigger": self.trigger, # 触发器对象
		}
	
	def run(self):
		'''
		此 run 方法为运行线程时执行的过程
		此方法无需显式的调用，如声明了一个线程：
			t = AutoDownThread(**config)
		那么只需：
			t.start()
		线程就会执行这个 run 函数
		:return: 无
		'''
		# 根据调度器配置添加一个调度任务，用于执行一些动作
		# 一个调度器可以添加多个任务
		self.scheduler.add_job(**self.config)
		# 执行调度器
		self.scheduler.start()
		# 下面这个 while 循环保证调度器永远运行
		while True:
			time.sleep(600)


if __name__ == '__main__':
	# 读取配置文件，存入一个字典
	with open("config.json", encoding="UTF-8") as conf:
		config = json.load(conf)
	# 读入配置中的触发器配置
	trigger_config = config["trigger_config"]
	# 初始化一个 解析器对象，用于程序运行时接收传入的参数
	parser = argparse.ArgumentParser(description='Process some integers.')
	# 为此解析器添加了一个参数：exe
	parser.add_argument('-exe', default="./test.exe", type=str,
						help='下载程序路径')
	# 从解析器读入接收到的参数，如 args.exe 即为输入的 exe参数的参数值
	args = parser.parse_args()
	# 初始化一个自动下载对象
	down = AutoDownApp()
	# 初始化自动下载线程对象
	adt = AutoDownThread(down, trigger_config, [args.exe])
	# 运行线程
	adt.start()