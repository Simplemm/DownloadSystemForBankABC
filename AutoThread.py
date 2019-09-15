import threading
import datetime
import time

'''
这个程序无需更改，也不会出错
此程序扩展了 threading.Thread
使线程可以暂停和恢复
'''
class Thread(threading.Thread):

	def __init__(self, *args, **kwargs):
		super(Thread, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()     # 用于暂停线程的标识
		self.__flag.set()       # 设置为True
		self.__running = threading.Event()      # 用于停止线程的标识
		self.__running.set()      # 将running设置为True

	def run(self):
		date = ""
		while self.__running.isSet():
			self.__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
			print("old date is:", date)
			year = datetime.datetime.now().year
			month = datetime.datetime.now().month
			day = datetime.datetime.now().day
			hour = datetime.datetime.now().hour
			minute = datetime.datetime.now().minute
			second = datetime.datetime.now().second
			date = str(year) + "-" + str(month) + "-" + str(day) + "-" + str(hour) + "-" + str(minute) + "-" + str(second)
			print("new date is:", date)
			time.sleep(1)

	def pause(self):
		# 暂停线程调用此方法
		self.__flag.clear()     # 设置为False, 让线程阻塞

	def resume(self):
		# 恢复线程调用此方法
		self.__flag.set()    # 设置为True, 让线程停止阻塞

	def stop(self):
		self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
		self.__running.clear()        # 设置为False    

if __name__ == '__main__':
	## test codes here.
	a = Thread()
	a.start()
	time.sleep(3)
	a.pause()
	time.sleep(3)
	a.resume()
	time.sleep(3)
	a.pause()
	time.sleep(2)
	a.stop()