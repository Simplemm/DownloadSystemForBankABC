import requests
import requests, re, base64, zlib, xmltodict, json
from datetime import datetime, date, timedelta
import os
# import parse
import urllib.request as request
import sys
import urllib
import gzip
from io import StringIO, BytesIO
import datetime
import base64
import parse
import threading

def excel2txt(excel_path, txt_path):
	try:
		excel = pd.read_excel(excel_path)
		data = excel.to_csv(txt_path, index=False)
		with open(txt_path,'w') as f:
			f.write(data)
			f.close()
		return True
	except:
		return False
#解析chunked格式数据
def decode_chunked(content):
    content = content.lstrip(b'\r') 
    content = content.lstrip(b'\n')
    temp = content.find(b'\r\n')
    print(temp)
    strtemp = content[0:temp]
    readbytes = int(strtemp, 16)
    print(readbytes)
    start = 2
    offset = temp + 2
    newcont = b''
    while(readbytes > 0):
        newcont = newcont + content[offset:readbytes + offset]
        offset += readbytes
        endtemp = content.find(b'\r\n', offset + 2)
        if(endtemp > -1):
            strtemp = content[offset + 2:endtemp]
            readbytes = int(strtemp, 16)
            if(readbytes == 0): 
                break
            else:
                offset = endtemp + 2
    content = newcont
    return content

#转化字符串为字典(&格式)
def praseDataTodict_iReport(PostData):
	datalist = PostData.split('&')
	dict  = {}
	for e in datalist:
		key,value = e.split("=",1)
		dict[key] = value
	return dict
#下载iReport报表
def downloadTable_iReport(postdata,cookie,path,type,date,special):   #iReport系统
	print(cookie)
	url = "http://10.233.66.58/rsp/appReport/ReportQueryAction_query.action"
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
		"Cookie": cookie,
		"Referer": "http://ireport.abc/ClientBin/ABC.UDesk.Main.xap",
		"Accept-Encoding": "gzip",

		#"Host": "10.233.66.58",
		"SOAPAction": ""
	}
	print(headers)
	#proxy = {'http':'http://127.0.0.1:8888'}
	if type != 'xml':
		if special == False:
			postdata['rvo.date'] = date
			resp = requests.post(url, headers=headers, data=postdata, timeout=5)
			data = resp.content
			print(data)
		else:
			postdata['rvo.date'] = date
			postdata_1 = urllib.parse.urlencode(postdata)
			req = request.Request(url, headers=headers, data=postdata_1.encode())
			resp = request.urlopen(req,timeout=5)
			data_orgin = resp.read()
			data = decode_chunked(data_orgin)
			data = gzip.decompress(data)
	else:
		url = 'http://10.233.66.58/rsp/webservices/AhcService'
		headers = {
		'Referer': 'http://ireport.abc/ClientBin/ABC.UDesk.Main.xap',
		'Accept-Language': 'zh-CN',
		'Content-Type': 'text/xml; charset=utf-8',
		'SOAPAction': '',
		'Accept-Encoding': 'gzip, deflate',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
		'Host': '10.233.66.58',
		'Connection': 'Keep-Alive',
		"Cookie": cookie
		}
		print(headers)
		dic = xmltodict.parse(postdata)
		print(dic)
		parameter = base64.b64decode(dic['s:Envelope']['s:Body']['downloadAdhocData']['in3'])
		#bs = base64.b64encode(parameter)
		js = json.loads(parameter)
		js['DTE'] = date
		PostData_m = json.dumps(js).replace(' ','')
		strb = bytes(PostData_m,encoding='utf-8')
		strb = base64.b64encode(strb)
		dic['s:Envelope']['s:Body']['downloadAdhocData']['in3'] = str(strb,encoding='utf-8')
		postdata = xmltodict.unparse(dic)
		print(postdata)
		#print(postdata)
		resp = requests.post(url, headers=headers, data=postdata,timeout=5)
		data = resp.content
		#print(data)
		xmlfile = xmltodict.parse(data)
		filedata = xmlfile['soap:Envelope']['soap:Body']['ns1:downloadAdhocDataResponse']['ns1:out']['fileByte']['#text']
		data = base64.b64decode(filedata)[1:]
	f_excel = open(path + date + ".et", "wb")
	f_excel.write(data)
	#excel2txt(path + date + ".et", path + date + ".txt")

# 登陆ireport获取cookie
def Login_iReport():
	print('login in ')
	url = "http://10.233.66.58/rsp/webservices/CmnService"
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
	"Cookie":"",
	"Referer": "http://ireport.abc/ClientBin/ABC.UDesk.Main.xap",
	"Accept-Encoding": "gzip, deflate",
	"Host": "10.233.66.58",
	"SOAPAction": "",
	"Content-Type": "text/xml; charset=utf-8"
	}
	postdata = '''<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><getST xmlns="http://service.app.rsp.abchina.com"><in0>660015812</in0><in1>a2FlOXQzYTM=</in1><in2>1</in2><in3>-1</in3><in4>1</in4></getST></s:Body></s:Envelope>'''
	response = requests.post(url,headers = headers ,data = postdata ,timeout=3)
	bigdata = xmltodict.parse(response.text)["soap:Envelope"]["soap:Body"]["ns1:getSTResponse"]["ns1:out"]
	loginCookies = response.cookies
	New_cookies = "JSESSIONID=" + loginCookies["JSESSIONID"] +"," + "BIGipServerpool-IRP-01="+loginCookies["BIGipServerpool-IRP-01"]
	headers = {
	"Cookie":New_cookies,
	"Content-Type": "application/x-www-form-urlencoded",
	"Referer": "http://ireport.abc/login.aspx",
	"Host": "ireport.abc"}
	url = "http://ireport.abc/index.aspx"
	pstdata = "SSOToken=" + bigdata;
	loginresponse = requests.post(url,data =pstdata,headers =headers)
	print("login out")

	return New_cookies;

 #下载udesk系统报表
def downloadTable_udesk(path,date):
	print("hesdaaaaaaaaaaa"+path)
	url = 'http://10.237.205.3/ccms/webservice.xml/ReportService?wsdl '
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
		#"Cookie": "JSESSIONID=0000qIOszAmTYBj6x31X1o4IoiP:1ajjhr2n8; BIGipServerpool-IRP-01=3599557898.31011.0000",
		"Referer": "http://ireport.abc/ClientBin/ABC.UDesk.Main.xap",
		"Accept-Encoding": "gzip, deflate",
		"Host": "10.237.205.3",
		"Content-Type": "text/xml; charset=utf-8",
		"SOAPAction": "",
	}
	date = date
	postdata = '''<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><findTagMktSumByWhereDown xmlns="http://service.report.ccms.abchina.com/"><arg0 xmlns=""><applysrc>'#'</applysrc><custyp>#</custyp><idntflg>1</idntflg><idntfytyp>#</idntfytyp><mkterflg>0</mkterflg><orgcode>319999</orgcode><prccode>#</prccode><querylevel>2</querylevel><querytype>1</querytype><resrv1>全部</resrv1><rptdte>'''+date+'''</rptdte><rptyp>1</rptyp></arg0><arg1 xmlns=""><orgcode>319999</orgcode><orgname>重庆分行</orgname><roleids>R1FA000001</roleids><roleids>R1KM000001</roleids><userid>chengyonhui1</userid><username>陈詠晖</username></arg1></findTagMktSumByWhereDown></s:Body></s:Envelope>'''
	response = requests.post(url, headers = headers, data =postdata.encode("utf-8"))
	parse.XmlToExcel(response.content,path+date+".et",date)
	excel2txt(path + date + ".et", path + date + ".txt")
	return 0
#下载信用卡报表查询平台报表
def downloadTable_31h999(path):   #31H999系统
	url = 'http://10.234.73.51/login.php'
	headers={
	'Host': '10.234.73.51',
	'Connection': 'keep-alive',
	'Referer': 'http://10.234.73.51/',
	'Cookie': 'PHPSESSID=otjp0qa11rr0l6gg5ifvs803fa0sbknm4q2bmpild6btl3v0to60',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
	}
	data = {
	'uid':'31H999',
	'password':'abcd1234',
	'signInBtn':'登陆'
	}
	proxy = {'http':'http://localhost:8888'}
	session = requests.session()
	res0 = session.post(url,data = data)
	headers = {
	'Referer': 'http://10.234.73.51/app/reportSchModel/schReportDataUI.php?reportID=hW2yjPTNT48%3D',
	'Accept-Encoding': 'gzip, deflate',
   'Accept-Language': 'zh-CN,zh;q=0.9',
   'Content-Type': 'application/x-www-form-urlencoded'
	}
	url2 = 'http://10.234.73.51/app/reportSchModel/exptReportData.php'
	data = '''reportIDHidden=1016&acBatchNameIDTemp=20190630（导入日期：20190703）&acBatchNameID=MTczODUxMjY1MQ==&schRangeID=b&orgCode=&orgName=&exptBtn=导出'''.encode('utf-8')
	#data_table = praseDataTodict_iReport(data)

	#ajax 请求1016 表，非目标表，可改，方法相同
	res = session.get('http://10.234.73.51/app/ajax/acAjaxReportBatchName.php?reportIDEncode=lK2hZKqFQp4=&term=0') 
	js = json.loads(res.text)
	#可根据返回值设定选项
	value = js[0]['value']
	name = js[0]['label']
	print(name,value)
	'''reportIDHidden=1021&acBatchNameIDTemp=20190728%EF%BC%88%E5%AF%BC%E5%85%A5%E6%97%A5%E6%9C%9F%EF%BC%9A20190730%EF%BC%89&acBatchNameID=OTUyMTc0NDY1MQ%3D%3D&schRangeID=b&orgCode=&orgName=&exptBtn=%E5%AF%BC%E5%87%BA'''
	data = 'reportIDHidden=1021&acBatchNameIDTemp='+ name + '&acBatchNameID='+value+'&schRangeID=b&orgCode=&orgName=&exptBtn=导出'
	dict1 = praseDataTodict_iReport(data)
	res = session.post(url2,data=dict1,headers=headers)
	tidname = ''
	with open(path + name[0:7]+ '.csv','wb') as file:
		file.write(res.content)
		file.close()
	#excel2txt(path + name[0:7] + ".et", path + name[0:7] + ".txt")
	return 0


def download_api(tableList, chooseDate):
	print(tableList)
	with open('config.json', "r+", encoding='UTF-8') as f:
		conf = json.load(f)
		f.close()
	defaultPath = conf["download"]['filepath']
	date = ''
	for e in str(datetime.datetime.now().date()).split('-'):
		date += e
	print(defaultPath)
	path = defaultPath + "/" + chooseDate
	# chooseDate = datetime.datetime.today() + datetime.timedelta(-5)
	# chooseDate = chooseDate.strftime('%Y%m%d')
	print(chooseDate)
	print(path)
	if not os.path.exists(path):
		os.mkdir(path)
	print(path)
	cookie = ''
	#cookie = Login_iReport()
	isLogined = 0
	for e in tableList:
		print("in")
		newpath = path + '/' + conf['tables'][e]['tid']+'_'
		if conf["tables"][e]['platform'] == 'ireport':
			if isLogined != 1:
				for i in range(5):
					try:
						cookie = Login_iReport()
						isLogined = 1
						break
					except:
						continue
			print('-----------------------------------')
			if conf["tables"][e]['isXML']:
				#cookie = Login_iReport()
				PostData = conf["tables"][e]['parameter']
				print("adsadsaaaaaaaaaaaa")
				for i in range(5):
					try:
						downloadTable_iReport(PostData,cookie,newpath,'xml',chooseDate,False)
						break;
					except:
						continue
				# t = threading.Thread(target=downloadTable_iReport,args=(PostData,cookie,newpath,'xml',chooseDate,False,textbox,e,))
				# t.start()
				
			else:
				if e =='sd03_NEW':
					special = True
				else:
					special = False
				postdata = praseDataTodict_iReport(conf["tables"][e]['parameter'])
				print(newpath)
				for i in range(5):
					try:
						downloadTable_iReport(postdata,cookie, newpath,'normal',chooseDate,special)
						break;
					except:
						continue
				
				# t = threading.Thread(target=downloadTable_iReport,args=(postdata,cookie, newpath,'normal',chooseDate,special,textbox,e,))
				# t.start()
				
		elif conf["tables"][e]['platform'] == '信用卡报表查询平台':
			downloadTable_31h999(newpath)
			# t = threading.Thread(target = downloadTable_31h999,args=(newpath,textbox,e,))
			# t.start()
		elif conf["tables"][e]['platform'] == '发卡营销系统':
			downloadTable_udesk(newpath,chooseDate)
			# t = threading.Thread(target = downloadTable_udesk,args=(newpath,chooseDate,textbox,e,))
			# t.start()
