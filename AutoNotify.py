#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   AutoNotify.py    
@Desc    :   
@Project :   AutoNotifyApp
@Contact :   thefreer@outlook.com
@License :   (C)Copyright 2018-2019, TheFreer.NET
@WebSite :   www.thefreer.net
@Modify Time           @Author        @Version
------------           -------        --------
2019/07/25 16:43       the freer      1.0         
'''
import win32gui
import win32con
import winsound
import argparse
import os

from AutoThread import Thread

'''
此程序为调用 Windows API 实现发送通知的功能
以下代码无需更改
'''

class AutoNotifyApp():
	def __init__(self):
		# 注册一个窗口类
		wc = win32gui.WNDCLASS()
		hinst = wc.hInstance = win32gui.GetModuleHandle(None)
		self.hover_text = "AutoNotifyApp"
		wc.lpszClassName = self.hover_text
		wc.lpfnWndProc = {win32con.WM_DESTROY: self.OnDestroy,}
		classAtom = win32gui.RegisterClass(wc)
		style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
		self.hwnd = win32gui.CreateWindow( classAtom, self.hover_text, style,
				0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
				0, 0, hinst, None)
		hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
		self.nid = (self.hwnd, 0, win32gui.NIF_ICON, win32con.WM_USER+20, hicon, self.hover_text)
		win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, self.nid)

	def showMsg(self, msg, title, length, icon_path, ring, hover_text):
		self.hover_text = hover_text
		hinst = win32gui.GetModuleHandle(None)
		if os.path.isfile(icon_path):
			icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
			hicon = win32gui.LoadImage(hinst,
						icon_path,
						win32con.IMAGE_ICON,
						0,
						0,
						icon_flags)
		else:
			print("Can't find icon file - using default.")
			hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

		if self.nid: message = win32gui.NIM_MODIFY
		else: message = win32gui.NIM_ADD
		win_tag = win32gui.NIF_INFO | win32gui.NIF_ICON | win32gui.NIF_TIP | win32gui.NIF_MESSAGE
		self.nid = (self.hwnd,
					0,
					win_tag,
					win32con.WM_USER+20,
					hicon,
					self.hover_text,
					msg,
					length,
					title
					# hicon
					)
		win32gui.Shell_NotifyIcon(message, self.nid) 
		# 此处可根据hover_text播放不同的铃声
		self.playSound(ring)


	def playSound(self, ring):
		try:
			winsound.PlaySound(ring, winsound.SND_ASYNC)
		except:
			pass

	def OnDestroy(self, hwnd, msg, wparam, lparam):
		nid = (self.hwnd, 0)
		win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
		win32gui.PostQuitMessage(0) # Terminate the app.
	    
class AutoNotifyThread(Thread):
	def __init__(self, notify, msg, title, length, icon_path, ring, hover_text):
		super(AutoNotifyThread, self).__init__()
		self.notify = notify
		self.msg = msg
		self.title = title
		self.length = length
		self.icon_path = icon_path
		self.ring = ring
		self.hover_text = hover_text
	
	def run(self):
		self.notify.showMsg(self.msg, self.title, self.length, self.icon_path, self.ring, self.hover_text)


if __name__ == "__main__":
	### 此程序无需更改，下面只介绍说明此函数可以接受的参数
	# 初始化解析器对象，接收传入程序的参数
	parser = argparse.ArgumentParser(description='请输入你的参数...', add_help=True)
	# 添加参数 title，通知标题，default 为参数为空时的默认值
	# type 为输入参数值的数据类型，help 为关于此参数的帮助信息
	# 下面的其他参数类似
	parser.add_argument('-title', default="表格自动下载结果", type=str,
						help='通知标题')
	parser.add_argument('-msg', default="默认消息", type=str,
						help='通知消息')
	## 以下略，可以查看 help='*'
	parser.add_argument('-length', default=200, type=int,
	                    help='通知持续时长，不用改')
	parser.add_argument('-icon', default="./res/custom.ico", type=str,
	                    help='通知图标，相对路径和绝对路径都可以')
	parser.add_argument('-ring', default="./res/custom.mp3", type=str,
	                    help='通知铃声，相对路径和绝对路径都可以')
	parser.add_argument('-hover', default="AutoNotifyApp", type=str,
	                    help='用于区分是哪一个应用调用的此通知应用，\
	                    可以根据hover text的不同定制通知')

	args = parser.parse_args()

	notify = AutoNotifyApp()
	ant = AutoNotifyThread(notify, args.msg, args.title, args.length, args.icon, args.ring, args.hover)
	ant.start()

