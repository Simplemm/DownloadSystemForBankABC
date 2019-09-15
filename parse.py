from xml.dom import minidom
import xml
import xlwt
def XmlToExcel(xml,name,date):
	dom = minidom.parseString(xml)
	datas = dom.getElementsByTagName("data")
	count = 0
	f = xlwt.Workbook()
	sheet = f.add_sheet(u'sheet1',cell_overwrite_ok=True)
	row0 = u'识别客户营销情况统计-识别客户营销统计表'
	row1 = u'日期：' + date
	row2 = u'客户类型：全部'
	row3 = u'机构：319999'
	col = ['序号','机构号','机构名称','客户类别','进件渠道','产品','进件数','进件客户数','开卡数','开卡客户数',
		'识别次数','识别客户数','识别渠道'	,'识别客户进件率','识别客户渗透率']
	sheet.write(0,0,row0)
	sheet.write(1,0,row1)
	sheet.write(2,0,row2)
	sheet.write(3,0,row3)
	for i in range(len(col)):
		sheet.write(3,i,col[i])
	rowcount = 3
	for e in datas:
		rowcount += 1
		count += 1
		#applysrc = e.getElementsByTagName("applysrc")[0].childNodes[0].data
		try:
			custyp = e.getElementsByTagName("custyp")[0].childNodes[0].data #客户类别
		except:
			custyp = " "
		idntcustcnt = e.getElementsByTagName("idntcustcnt")[0].childNodes[0].data#识别客户数
		idntcustmktprcnt = e.getElementsByTagName("idntcustmktprcnt")[0].childNodes[0].data#识别客户进件率
		idntcustprmbity = e.getElementsByTagName("idntcustprmbity")[0].childNodes[0].data#识别客户渗透率
		idntfycnt = e.getElementsByTagName("idntfycnt")[0].childNodes[0].data#识别次数
		idntfytyp = e.getElementsByTagName("idntfytyp")[0].childNodes[0].data#
		mktcnt = e.getElementsByTagName("mktcnt")[0].childNodes[0].data#进件数
		mktcustcnt = e.getElementsByTagName("mktcustcnt")[0].childNodes[0].data#进件客户数
		opencnt = e.getElementsByTagName("opencnt")[0].childNodes[0].data#开卡用户数
		opencustcnt = e.getElementsByTagName("opencustcnt")[0].childNodes[0].data#开卡客户数
		orgcode = e.getElementsByTagName("orgcode")[0].childNodes[0].data#机构编号
		orgname = e.getElementsByTagName("orgname")[0].childNodes[0].data#机构名
		data = [count,orgname,orgcode,custyp,"全部","全部",int(mktcnt),int(mktcustcnt),int(opencnt),int(opencustcnt),int(idntfycnt),int(idntcustcnt),"全部",float(idntcustmktprcnt),float(idntcustprmbity)]
		for i in range(15):
			sheet.write(rowcount,i,data[i])
	f.save(name)


	