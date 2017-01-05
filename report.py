# PYTHON script
import os
import ffmpy
import shutil
import time
from string import Template
import csv
import config as conf

def copyPic(dir, simN, itr, postName, picNameList, picRelPath, picExt):	
	dstDir = os.path.join(dir, picRelPath)
	srcDir = os.path.join(dir, postName)
	if not os.path.exists(dstDir):
		os.mkdir(dstDir)
	
	for i in range(1, itr+1):
		for sim in range(1, simN+1):
			for pic in picNameList:
				dirname = '.'.join((str(i), str(sim)))
				srcDir0 = os.path.join(srcDir, dirname)
				srcPic = os.path.join(srcDir, dirname, pic + picExt)
				dstPic = os.path.join(dstDir, pic + '_' + dirname + picExt)
				if os.path.exists(srcPic):
					shutil.copyfile(srcPic, dstPic)		
def copyData(dir, itr, postName, dataName, dataExt, dataRelPath)					:
	dataPath = os.path.join(dir, postName)
	dstDir = os.path.join(dir, dataRelPath)
	if not os.path.exists(dstDir):
		os.mkdir(dstDir)
	for i in range(1, itr+1):
		itrVar = '_' + str(i)
		fileName = dataName + itrVar + dataExt
		srcData = os.path.join(dataPath, fileName)
		dstData = os.path.join(dstDir, fileName)
		print(srcData)
		if os.path.exists(srcData):
			shutil.copyfile(srcData, dstData)
def readTemp(pathInput):
	with open(pathInput) as file:
		html = file.readlines()
		htmlStr = ''.join(html)
		
	template = Template(htmlStr)
	
	return(template)		
def saveHtml(html, htmlName, pathInput, opt):
	with open(os.path.join(pathInput , htmlName+'.html'), 'w') as file:
		file.write('%s' % html)
		
	if opt == 1:
		print('--------------------------------------------------------------\n'+
			'\t ' + htmlName + ' page is created in\n ' + pathInput +'\n' +
			'--------------------------------------------------------------\n')		
def reportData(dir, itr, temp, postName, dataRelPath, repRelPath, dataName, dataExt, variableNo, responseNo, headerChange, picName, picExt):
	reportDir = os.path.join(dir, repRelPath)
	if not os.path.exists(reportDir):
		os.mkdir(reportDir)
			
	tablePath = os.path.join(dir, dataRelPath)
	nameTag = dataName + '_' 
	navBar = itrNavBar(itr, nameTag)
			
	tbodyAll = ''
	thead = None	
	for i in range(1, itr+1):
		I = str(i)
		csvName = os.path.join(tablePath, nameTag + I + dataExt)
		if os.path.exists(csvName):
			tbody = ''
			thead = None
			with open(csvName) as csvFile:
				csvTable = csv.reader(csvFile, delimiter=',')
				trData = ''
				for r, row in enumerate(csvTable):		
					if r == 2 or r==0:
						continue				
					if r==1:
						trStat = 'head'
					else:
						trStat = 'body'
					rowId =  I + '.' + ('%02d' % (r-2)) 
					trData += '<tr class="collapsible" style="display:table-row;" id="' + rowId + '">'											
					for v,val in enumerate(row):
						if trStat == 'head':
							for opt in headerChange:
								if val == opt[0]:
									val = opt[1]
									break
							if v == 0:
								trData += ('<th></th>')
							if v <= variableNo:
								trData += ('<th class="alt1">' + val + '</th>')
							else:
								trData += ('<th class="alt3">' + val + '</th>')
						elif trStat == 'body':
							if v == 0:
								src = os.path.join( conf.picF, picName + '_' + I + '.' + str(r-2) + picExt)
								trData += ('<td><input type="checkbox" value="' + rowId + '"></input></td>')
								trData += ('<td class=""><a href="' + src + '">' + rowId  + '</a></td>')
							elif v <= variableNo:
								val = str(round(float(val),2))
								trData += ('<td class="" align="center">' + val + '</td>')
							else:
								val = str(round(float(val),2))
								trData += ('<td class="" align="center">' + val + '</td>')
								
					trData += ('</tr>')
					if trStat == 'head':
						thead =  trData
					elif trStat == 'body':
						tbody += trData
						tbodyAll += trData
					trData = ''
			pageName = nameTag + I
			tempHTML = temp.substitute(navigationBar = navBar, tableHead = thead, tableBody = tbody,
			itrVar =  '_' + I, ver = '', allType = dataName)
			saveHtml(tempHTML, pageName, reportDir, 1)	
	if thead:
		pageName = 'all' + dataName
		tempHTML = temp.substitute(navigationBar = navBar, tableHead = thead, tableBody = tbodyAll,
		itrVar = '', ver = 'all', allType = dataName)
		saveHtml(tempHTML, pageName, reportDir, 1)		
	return
def reportPic(dir, simN, itr, temp, Nrow, Ncol, postName, picNameList, repRelPath, picExt):	
	reportDir = os.path.join(dir, repRelPath)
	for picName in picNameList:
		navBar = itrNavBar(itr, picName + '_')
		allPic = ''	
		for i in range(1, itr+1): 
			I = str(i)
			r=0
			picTable = ''
			for sim in range(1, simN+1):
				name = '.'.join(( str(i), str(sim)))
				if r>Nrow:
					picTable += ('</tr>')
					r = 0
				elif r ==0:
					picTable += ('<tr>')
				
				picNameItr = picName + '_' +  '.'.join((str(i), str(sim)))
				picTable = picTableInp(picTable, picNameItr, name, picExt)
				r+=1
			picTable += ('</tr>')
			allPic += picTable
			
			pageName =  picName + '_' + I
			tempHTML = temp.substitute(navigationBar = navBar, tableBody = picTable, tableHead = '',
			itrVar = '_' + I, allType = picName, ver = '')
			saveHtml(tempHTML, pageName, reportDir, 1)
	
		pageName = 'all' + picName
		tempHTML = temp.substitute(navigationBar = navBar, tableBody = allPic, tableHead = '',
		itrVar = '', allType = picName, ver = 'all')
		saveHtml(tempHTML, pageName, reportDir, 1)				
def picTableInp(picTable, picName, var, picExt):
	src = os.path.join( conf.picF, picName + picExt)
	picTable += ('<td align="center"><a href="' + src + '" title=" '+ var + 
	'"><img style="width: 200px; height: 200px;" alt="" src="' + src + '"></td>')
		
	return(picTable)	
def itrNavBar(itr, pageTag):
	navBar = ''
	for i in range(1, itr+1):		
		I = str(i)	
		pageName = pageTag + I +'.html'
		navBar += ('<td><a href="' +  pageName + '"/><button type="button">iter ' + I +
			'</button></td>')
	return(navBar)
def setup(picNameList, picExt, dataName, dataExt, verRep, update):
	
	repRelPath = os.path.join(conf.RepF, verRep)
	picRelPath = os.path.join(repRelPath, conf.picF)
	dataRelPath = os.path.join(repRelPath, conf.dataF)
		
	RepDir = os.path.join(dir, conf.RepF)
	verRepDir = os.path.join(RepDir, verRep)
	# make dir
	if not os.path.exists(RepDir):
		os.mkdir(RepDir)
	if not os.path.exists(verRepDir):
		os.mkdir(verRepDir)
		
	# backup pic
	picDir = os.path.join(verRepDir, conf.picF)
	if update or not os.path.exists(picDir):
		copyPic(dir, simN, itr, 'META', picNameList, picRelPath, picExt)
	# backup data
	dataDir = os.path.join(verRepDir, conf.dataF)
	if  update or not os.path.exists(dataDir):
		copyData(dir, itr, 'ANSA', dataName, dataExt, dataRelPath)
		
	# copy css and js	
	scriptPath = os.path.join(os.path.dirname(__file__))
	scriptDst = os.path.join(dir, conf.RepF, 'script')
	scriptSrc = os.path.join(scriptPath, 'script')
	if not os.path.exists(scriptDst):
		shutil.copytree(scriptSrc, scriptDst)
	
	# read template
	menuTempPath = scriptPath + '/template.html'
	if os.path.exists(menuTempPath):
		temp = readTemp(menuTempPath)	
		return(repRelPath, picRelPath, dataRelPath, temp)
	
	
if __name__ == '__main__':
	dir = 'S:/nobackup/safety/s/cy11/3_upc/pedestrian/head_EN/runs/hood_opt_v3'
	simN = 22
	itr = 16
	
	variableNo = 13
	responseNo = 9
	
	# pic table format
	Nrow = 6
	Ncol = 8
	
	picNameList = ['pic_iso', 'pic_top', 'pic_cup']
	picExt = '.png'
	
	dataName = 'AnalysisResults'
	dataExt = '.csv'
	headerChange = [['inner_hood_thickness', 'thickness', 0]]
	
	verRep ='v4'
	update = True
	
	(repRelPath, picRelPath, dataRelPath, temp) = setup(picNameList, picExt, dataName, dataExt, verRep, update)
	
	if temp:
		reportPic(dir, simN, itr, temp, Nrow, Ncol, 'META', picNameList, repRelPath, picExt)
		reportData(dir, itr, temp, 'ANSA',dataRelPath, repRelPath, dataName, dataExt, variableNo, responseNo, headerChange, picNameList[1], picExt)
