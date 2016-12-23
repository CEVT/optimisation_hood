# PYTHON script
import os
import ffmpy
import shutil
import time
from string import Template

def copyPic(dir):
	
	picDir = os.path.join(dir, 'pic')
	if os.path.exists(picDir):
		shutil.rmtree(picDir)
		while os.path.exists(picDir):
			time.sleep(5)
			print('wait')
	os.mkdir(picDir)
	listDir = os.listdir(dir)
	
	i = 1
	for item in listDir:
		isoPic = os.path.join(dir, item, 'pic_iso.png')
		topPic = os.path.join(dir, item, 'pic_top.png')
		cupPic = os.path.join(dir, item, 'pic_cup.png')
		
		picList = [isoPic, topPic, cupPic]
		for p,pic in enumerate(picList):
			if os.path.exists(pic):
				fileName = 'pic' + ('%03d' % i) + '.png'
				shutil.copyfile(pic, os.path.join(picDir, fileName))
				i+=1
				
	return(True)
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
	
def report(dir, simN, itr, temp, row, col, postName):
	reportDir = os.path.join(dir, 'Rep')
	if not os.path.exists(reportDir):
		os.mkdir(reportDir)
	
			
	picNameList = ['pic_iso', 'pic_top', 'pic_cup']
	
	for picName in picNameList:
		navBar = ''
		for i in range(1, itr+1):
			I = str(i)
			navBar += ('<td><a href="iter' + I + picName + '.html"/><button type="button">iter ' + I +
				'</button></td>') 
		for i in range(1, itr+1): 
			I = str(i)
			r=0
			picTable = ''
			for sim in range(1, simN+1):
				name = '.'.join(( str(i), str(sim)))
				dirPath = os.path.join(dir, postName, name)
				if os.path.exists(dirPath):
					if r>row:
						picTable += ('</tr>')
						r = 0
					elif r ==0:
						picTable += ('<tr>')
					
					picTable = picTableInp(picTable, picName, name, postName)
					r+=1
			picTable += ('</tr>')
			iso = 'iter'+ I + 'pic_iso.html'
			top = 'iter'+ I + 'pic_top.html'
			cup = 'iter'+ I + 'pic_cup.html'
			# print(picTable)
			pageName = 'iter' + I + picName
			tempHTML = temp.substitute(navigationBar = navBar, Picturetable = picTable, isoPath = iso,
			topPath = top, cupPath = cup)
			saveHtml(tempHTML, pageName, reportDir, 1)
				
			
			
		
		
def picTableInp(picTable, picName, var, postName):
	src = os.path.join(os.pardir, postName, var, picName + '.png')
	picTable += ('<td align="center"><a href="' + src + '" title=" '+ var + 
	'"><img style="width: 200px; height: 200px;" alt="" src="' + src + '"></td>')
		
	return(picTable)
	


if __name__ == '__main__':
#---------------------------------------------------------------------------------------------------
#				menu
# --------------------------------------------
	scriptPath = os.path.join(os.path.dirname(__file__))
	menuTempPath = scriptPath + '/template.html'
	menuPath = 'Rep/'
	print(menuTempPath)
	if os.path.exists(menuTempPath):
		temp = readTemp(menuTempPath)
		# (mapTag, name) = mapLink('Rep/')
		# menuHtml = menuTemp.substitute(map = mapTag, jobName = name)
		# saveHtml(menuHtml, 'menu', menuPath, 0)

	

		dir = 'S:/nobackup/safety/s/cy11/3_upc/pedestrian/head_EN/runs/hood_opt_v3'
		simN = 22
		itr = 15
		
		row = 6
		col = 8
		
		report(dir, simN, itr, temp, row, col, 'META')
	# copyPic(dir+ '/META')
	# aniPic(dir)
