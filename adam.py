import sys
from PyQt5.QtWidgets import * #PyQt import
from PyQt5.QtGui import *
from PyQt5 import uic
import PyQt5
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui
import pics_rc
import cryptography
from cryptography.fernet import Fernet
import rclpy
from std_msgs.msg import String
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
from sensor_msgs.msg import Image
import numpy as np
import time
from datetime import datetime as dt
import subprocess
from subprocess import Popen, PIPE
import os
from authManager import authentication_server
import queue
from queue import PriorityQueue
import signal

import adam_addswitch
from adam_addswitch import *


login_form = uic.loadUiType("adam-login2.ui")[0]
main_form = uic.loadUiType("adam-main-dark.ui")[0]

categorynum = 5

class loginWindow(QMainWindow, login_form):

	def center(self): #for load ui at center of screen
		frameGm = self.frameGeometry()
		screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

	def __init__(self):

		super().__init__()
		self.setupUi(self)
		self.center()
		self.setWindowFlags(Qt.WindowStaysOnTopHint)

		self.commandLinkButton.clicked.connect(self.loginBtn)
		self.lineEdit_2.returnPressed.connect(self.credentialCheck)
		self.lineEdit_2.textChanged.connect(self.autoCheck)

		self.update_auth.clicked.connect(self.updateAuth)
		self.authManager = authentication_server()

		self.pushButton_1.clicked.connect(self.btn_1)
		self.pushButton_2.clicked.connect(self.btn_2)
		self.pushButton_3.clicked.connect(self.btn_3)
		self.pushButton_4.clicked.connect(self.btn_4)
		self.pushButton_5.clicked.connect(self.btn_5)
		self.pushButton_6.clicked.connect(self.btn_6)
		self.pushButton_7.clicked.connect(self.btn_7)
		self.pushButton_8.clicked.connect(self.btn_8)
		self.pushButton_9.clicked.connect(self.btn_9)
		self.pushButton_0.clicked.connect(self.btn_0)
		self.pushButton_10.clicked.connect(self.btn_b)


		try:
			temp = np.load('./adms_user_db.npz', allow_pickle=True)
			self.userDB = temp['db'].item()

		except Exception:
			QMessageBox.warning(self, "인증 DB 가져오기 실패", "로그인을 하기위해서는 인증DB 갱신을 꼭 해주세요.", QMessageBox.Ok)


	def loginBtn(self):
		self.credentialCheck()

	def btn_1(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '1')
	def btn_2(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '2')
	def btn_3(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '3')
	def btn_4(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '4')
	def btn_5(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '5')
	def btn_6(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '6')
	def btn_7(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '7')
	def btn_8(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '8')
	def btn_9(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '9')
	def btn_0(self):
		self.lineEdit_2.setText(self.lineEdit_2.text() + '0')
	def btn_b(self):
		self.lineEdit_2.setText(self.lineEdit_2.text()[:-1])
	def autoCheck(self):
		if len(self.lineEdit_2.text())>2:
			self.credentialCheck()

	#test 용 0Vyk090ARPaeXe20mRvv
	def updateAuth(self):
		buttonReply=QMessageBox.question(self, '인증 서버 DB 갱신', "이 작업은 되돌릴 수 없습니다. \n1. KeyPair를 제대로 확인해주세요\n2. 조회 후 업데이트된 DB 적용까지 시간이 걸릴 수 있습니다.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if buttonReply == QMessageBox.Yes:
			keyPair = self.lineEdit_3.text()
			try:
				self.authManager.update(keyPair)
			except Exception as ex:
				buttonReply=QMessageBox.warning(self, "서버에서 가져오기 실패", "서버에서 조회를 실패하였습니다.\nKey Pair를 확인해주세요", QMessageBox.Ok)
				return;

			temp = np.load('./adms_user_db.npz', allow_pickle=True)
			self.userDB = temp['db'].item()
			QMessageBox.information(self, "인증 DB 갱신 성공", "프로그램 재시작 후 로그인 해주세요.", QMessageBox.Ok)
		else:
			return;

	def credentialCheck(self, id=None, pwd=None):
		self.pwd = pws if pwd else self.lineEdit_2.text()
		try:
			returnVal = self.userDB.idValidation(self.lineEdit_2.text())
			print(returnVal)
			if returnVal:
				self.mW = mainWidnow(self.userDB.retrieve(returnVal, 'all'))
				self.mW.show()
				self.hide()
				return 1
			else:
				self.label_7.setText("Wrong Passwords")
				return 0
			pass
		except Exception as ex:
			raise Exception(ex)
			self.label_7.setText(f"Invalid Input\n{ex}")
			return 0


class rosbagRecord():
	# https://gist.github.com/marco-tranzatto/8be49b81b1ab371dcb5d4e350365398a
	def __init__(self, comms, parent = None):

		self.main = parent
		self.working = True
		#self.commands = comms
		self.pipe = subprocess.Popen(comms, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')

	def stop_recording(self, s):
		#list_cmd = subprocess.Popen("rosnode list", shell=True, stdout=subprocess.PIPE)
		#list_output = list_cmd.stdout.read()
		#retcode = list_cmd.wait()
		#for strs in list_output.split("\n"):
		#	if(strs.startswith(s)):
		#		os.system("source /opt/ros/melodic/setup.bash && rosnode kill " + strs)
		#os.system(". /opt/ros/melodic/setup.bash && rosnode kill " + s)

		killComms = ". /opt/ros/melodic/setup.bash && rosnode kill " + s
		subprocess.Popen(killComms, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
		'''
		global pipe
		print("Record End")
		os.killpg(os.getpid(pipe.pid), signal.SIGTERM)
		'''

	def stop_recording_handler(self):
		self.stop_recording("/adam_record")


class mainWidnow(QMainWindow, main_form):
	def center(self): #for load ui at center of screen
		frameGm = self.frameGeometry()
		screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
		centerPoint = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())

	def __init__(self, userInfo):
		super().__init__()
		self.setupUi(self)
		self.center()
		self.saveDialog.clicked.connect(self.saveFileDialog)
		self.logout.clicked.connect(self.logoutBtn)

		self.name = userInfo[0]
		self.sid = userInfo[3]

		self.label.setText(self.label.text() + self.name)
		self.label_5.setText(self.label_5.text() + self.sid)

		self.adms_subscriber_class = adms_subscriber()
		self.adms_subscriber_class.start()
		self.adms_subscriber_class.sig_wheel.connect(self.wheel_speed)
		self.adms_subscriber_class.sig_apsbps.connect(self.apsbpsFeed)
		self.adms_subscriber_class.sig_gear.connect(self.gearPosition)
		self.adms_subscriber_class.sig_steer.connect(self.steeringHandle)
		self.adms_subscriber_class.sig_estop.connect(self.estopVisual)
		self.adms_subscriber_class.sig_auto.connect(self.autostandby)
		self.adms_subscriber_class.sig_override.connect(self.overRide)
		self.adms_subscriber_class.sig_turn.connect(self.turnSig)
		self.adms_subscriber_class.sig_belt.connect(self.driverBelt)
		self.adms_subscriber_class.sig_trunk.connect(self.trunkOpen)
		self.adms_subscriber_class.sig_door.connect(self.doorOpen)

		self.turnleft.close()
		self.turnright.close()
		self.harzardLamp.close()
		self.beltno.close()
		self.trunkopen.close()
		self.doorfl.close()
		self.doorfr.close()
		self.doorrl.close()
		self.doorrr.close()

		self.topicnode = rclpy.create_node('list_all_topics')

		self.reload.clicked.connect(self.reloadTopics)
		self.selectAll.clicked.connect(self.checkAll)
		self.recordBtn.clicked.connect(self.recordBagbyBtn)
		self.recordFlag = False
		self.cantime = time.time()
		self.visualtime = time.time()

		self.setupBtn.clicked.connect(self.setupCar)

		self.lightmode = False
		self.modeChange.clicked.connect(self.changeWinMode)

		#######Switch Part#######
		self.amw = addswitchWindow()
		self.switchNum = 0 # shows how many switch 'now'
		self.switchnumarr = {'Vision' : 0, 'LIDAR' : 0, 'GPS' : 0, 'Driving' : 0, 'HW' : 0, 'Page' : 0}
		try:
			f = open("ADMS_switch_list.txt", 'r')
			while True:
				line = f.readline()
				if not line:
					break
				else:
					category, switchname, command, node, _, _ = line.split('|')
					self.btnVisualization([category, switchname, command, node])
		except:
			f = open("ADMS_switch_list.txt", 'w')
		self.onimg = QPixmap('on.png')
		self.onimg = self.onimg.scaled(51, 51, Qt.KeepAspectRatio)
		self.offimg = QPixmap('off.png')
		self.offimg = self.offimg.scaled(51, 51, Qt.KeepAspectRatio)
		f.close()

		self.addSwitchBtn.clicked.connect(self.popAddSwitch)
		self.delSwitchBtn.clicked.connect(self.deleteSwitch)
		self.amw.sig_btn.connect(self.btnVisualization)

		#######Switch Part#######

	def changeWinMode(self):
		if not self.lightmode:
			self.setStyleSheet("background-color : rgb(236, 232, 228)")
			self.modeChange.setText("Dark Mode")
			widgetlist = self.centralwidget.findChildren(QWidget)
			for qwdg in widgetlist:
				qwdg.setStyleSheet("color : black;")
				if qwdg.objectName() in ['closeddoors', 'turnleft', 'turnright', 'doorfl', 'doorfr', 'doorrl', 'doorrr']:
					qwdg.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: rgba(255, 255, 0);")
					if qwdg.objectName() == 'closeddoors':
						qwdg.setPixmap(QPixmap("./closeddoors.png"))
					elif qwdg.objectName() == 'doorfl' or qwdg.objectName() == 'doorrl':
						qwdg.setPixmap(QPixmap("./ldoor.png"))
					elif qwdg.objectName() == 'doorfr' or qwdg.objectName() == 'doorrr':
						qwdg.setPixmap(QPixmap("./rdoor.png"))
				elif qwdg.objectName() == 'beltok':
					qwdg.setPixmap(QPixmap("./beltOK.png"))
				elif qwdg.objectName() == 'trunkclosed':
					qwdg.setPixmap(QPixmap("./trunk.png"))
			#print(widgetlist)
			self.lightmode = True
		else:
			self.setStyleSheet("background-color : rgb(46, 52, 54);")
			self.modeChange.setText("Light Mode")
			widgetlist = self.centralwidget.findChildren(QWidget)
			for qwdg in widgetlist:
				qwdg.setStyleSheet("color : white;")
				if qwdg.objectName() in ['closeddoors', 'turnleft', 'turnright', 'doorfl', 'doorfr', 'doorrl', 'doorrr']:
					qwdg.setStyleSheet("background-color: rgba(255, 255, 255, 0); border: rgba(255, 255, 0);")
					if qwdg.objectName() == 'closeddoors':
						qwdg.setPixmap(QPixmap("./closeddoorswhite.png"))
					elif qwdg.objectName() == 'doorfl' or qwdg.objectName() == 'doorrl':
						qwdg.setPixmap(QPixmap("./ldoorwhite.png"))
					elif qwdg.objectName() == 'doorfr' or qwdg.objectName() == 'doorrr':
						qwdg.setPixmap(QPixmap("./rdoorwhite.png"))
				elif qwdg.objectName() == 'beltok':
					qwdg.setPixmap(QPixmap("./beltOKwhite.png"))
				elif qwdg.objectName() == 'trunkclosed':
					qwdg.setPixmap(QPixmap("./trunkwhite.png"))
			self.lightmode = False

	def deleteSwitch(self):
		idx = self.switchTabBox.currentIndex()
		category = self.switchTabBox.tabText(idx)
		q = PriorityQueue()
		deletenum = 0
		for i in range(self.switchnumarr.get(category)):
			if eval('self.frame'+str(category)+str(i)).styleSheet() == 'border : 2px solid blue':
				frame = eval('self.frame'+str(category)+str(i))
				frame.setStyleSheet("border : transparent")
				#print('layout item :', frame.layout().itemAt(0).layout())
				frame.layout().itemAt(0).layout().labelclicked = False
				print(i, 'th child :', eval('self.frame'+str(category)+str(i)).findChildren(QLabel))
				childrenwidget = eval('self.frame'+str(category)+str(i)).findChildren(QLabel)
				row = i//5
				col = i-5*row
				q.put((row, col))
				#eval('self.frame'+str(category)+str(i)).styleSheet()
				delswitchname = childrenwidget[1].text()
				for j in range(len(childrenwidget)):
					print(i, 'th', j, 'child objectname :', childrenwidget[j].objectName())
					dellayout = childrenwidget[j].parent().layout().itemAt(0).layout()
					print(dellayout, dellayout.layout())
					delwidget = dellayout.takeAt(0)
					print('delwidget :', delwidget.widget())
					delwidget.widget().setParent(None)
				f = open("ADMS_switch_list.txt", "r")
				lines = f.readlines()
				f.close()
				new_f = open("ADMS_switch_list.txt", "w")
				print("category :", category, "delswitchname :", delswitchname)
				for line in lines:
					check = line.strip("\n").split('|')
					print('check :', check)
					if check[0] != category or check[1] != delswitchname:
						new_f.write(line)
				new_f.close()
				deletenum+=1
		print('switchnumarr :', self.switchnumarr.get(category))

		for i in range(self.switchnumarr.get(category)):
			if eval('self.frame'+str(category)+str(i)).findChild(QLabel) != None:
				print(eval('self.frame'+str(category)+str(i)).findChildren(QLabel), 'are exist!')
				r, c = q.get()
				print(r, c)
				print('lala')
				cr = i//5
				cc = i-5*cr
				cframe = eval('self.frame'+str(category)+str(i))
				clayout = eval('self.frame'+str(category)+str(i)).layout().itemAt(0).layout()
				#print(clayout.parentWidget().parent().layout())
				fframe = eval('self.frame'+str(category)+str(5*r+c))
				cframe.layout().takeAt(0)
				fframe.layout().takeAt(0)
				fframe.layout().addLayout(clayout)
				print('r, c :', r, c, 'cr, cc :', cr, cc)
				q.put((cr, cc))
		self.switchnumarr[category] -= deletenum
		self.switchNum -= deletenum

	def btnVisualization(self, btninfo):
		category, switchname, command, nodes = btninfo
		self.switchTabBox.setCurrentWidget(self.switchTabBox.findChild(QWidget, category))
		switchidx = self.switchnumarr.get(category)
		row = switchidx//5
		col = switchidx-5*row
		grid = self.gridLayoutVision
		frame = eval('self.frame'+str(category)+str(self.switchnumarr[category]))
		layoutcontainer = QHBoxLayout()
		frame.setLayout(layoutcontainer)
		framelbx = switchLayout(category, switchidx, switchname, nodes, self.switchNum, frame)
		frame.layout().addLayout(framelbx)
		self.switchNum += 1
		self.switchnumarr[category] += 1

	def popAddSwitch(self):
		print('switch # :', self.switchNum)
		self.amw.show()

	def setupCar(self):
		### SetupCar (v0.1 for LatteAlpha Environ)
		os.system("sh dbw_start")
	def closeEvent(self, event):
		reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?',
				QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			if self.recordFlag:
				killComms = ". /opt/ros/melodic/setup.bash && rosnode kill /adam_record"
				print(killComms)
				subprocess.Popen(killComms, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
			for i in range(len(adam_addswitch.runningprc)):
				print('try to shut down ', adam_addswitch.runningprc[i][0])
				adam_addswitch.runningprc[i][0].send_signal(signal.SIGINT)
			killROS = "killall -9 roscore && killall -9 rosmaster"
			subprocess.Popen(killROS, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
			killbridge = "killall -9 ros2"
			subprocess.Popen(killbridge, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
			event.accept()
			print('Window closed')
		else:
			event.ignore()


	def recordBagbyBtn(self):
		if self.recordFlag:	# Now recording... should shut down
			## Shut down thread, and delete process.
			self.recorder.stop_recording_handler()
			self.recordFlag = False
			self.recordBtn.setText('운행 기록 시작 (10km/h 이상 주행시 자동 시작)')
		else:   # Now not recording.... should start recording
			command = "source /opt/ros/melodic/setup.bash && rosbag record"
			# Save directory
			# base directory is ~/rosbagAdam
			dir_ = self.saveDir.text()
			if not dir_: #if dir_ is unset, set dir_ current working directory
				dir_ = os.getcwd()

			print("dir : ", dir_)
			now = time.localtime()
			now = str(now.tm_year)[2:]+str(now.tm_mon)+str(now.tm_mday)+str(now.tm_hour)+str(now.tm_min)+str(now.tm_sec)
			command = command + ' -O ' + dir_ + "/" + self.sid + "_" +str(now)

			numofTopic = 0
			for i in range(self.topicList.count()):
				if self.topicList.item(i).checkState() == Qt.Checked:
					command = command + ' ' + str(self.topicList.item(i).text())
					numofTopic += 1
			if not numofTopic:
				buttonReply=QMessageBox.warning(self, "ROSBAG Record Fail", "Make sure the Topic is checked at least one!", QMessageBox.Ok)
				return


			print(command)
			#try:

			command = command + str(" __name:=adam_record")
			self.recorder = rosbagRecord(command)

			self.recordBtn.setText('녹화 중... 클릭하여 중지 및 녹화파일 저장')
			self.recordFlag = True
			#except:
			#	print("Can't Start Recording : Topic ERROR!!!!")


	def doorOpen(self, msg):
		self.timetable.setItem(0, 0, QTableWidgetItem(str(self.cantime)))
		# 0: fl, 1: fr
		# 2: rl, 3: rr
		if msg[0]:
			self.doorfl.show()
		else:
			self.doorfl.close()
		if msg[1]:
			self.doorfr.show()
		else:
			self.doorfr.close()
		if msg[2]:
			self.doorrl.show()
		else:
			self.doorrl.close()
		if msg[3]:
			self.doorrr.show()
		else:
			self.doorrr.close()
		self.visualtime = time.time()
		self.timetable.setItem(1, 0, QTableWidgetItem(str(self.visualtime)))
		delaytime = self.visualtime - self.cantime
		self.timetable.setItem(2, 0, QTableWidgetItem(str(delaytime)))

	def trunkOpen(self, msg):
		if msg:
			self.trunkopen.show()
		else:
			self.trunkopen.close()

	def driverBelt(self, msg):
		if msg:
			self.beltno.close()
		else:
			self.beltno.show()

	def turnSig(self, msg):
		if msg == 0:
			self.turnleft.close()
			self.turnright.close()
			self.harzardLamp.close()
		elif msg == 1:
			self.turnleft.show()
			self.turnright.close()
			self.harzardLamp.close()
		elif msg == 2:
			self.turnleft.close()
			self.turnright.show()
			self.harzardLamp.close()
		elif msg == 7:
			self.turnleft.close()
			self.turnright.close()
			self.harzardLamp.show()

	def overRide(self, msg):
		if msg == 0:
			self.override.setText('Driving Mode: Manual')
			self.override.setStyleSheet("font-weight: normal; color: black")
		elif msg == 1:
			self.override.setText('Driving Mode: Auto')
			self.override.setStyleSheet("font-weight: normal; color: black")
		elif msg == 2:
			self.override.setText('Manual Mode by "Steer"')
			self.override.setStyleSheet("font-weight: normal; color: black")
		elif msg == 3:
			self.override.setText('Manual Mode Mode by "Accel"')
			self.override.setStyleSheet("font-weight: normal; color: black")
		elif msg == 4:
			self.override.setText('Manual Mode by "Brake"')
			self.override.setStyleSheet("font-weight: normal; color: black")
		elif msg == 6:
			self.override.setText('Manual Mode by "ESTOP"')
			self.override.setStyleSheet("font-weight: bold; color: red")
		else:
			print("WRONG VALUE!!!!!")

	def autostandby(self, msg):
		# 0: Auto Standby Switch
		# 1: APM
		# 2: ASM
		# 3: AGM
		if msg[0]:   # Auto Standby Switch ON
			self.autoStandbyMode.setText('ON')
			self.autoStandbyMode.setStyleSheet("font-weight: bold; color: green")
			if msg[1]:
				self.apm.setStyleSheet("font-weight: bold; color: green")
			else:
				self.apm.setStyleSheet("font-weight: normal; color: black")
			if msg[2]:
				self.asm_2.setStyleSheet("font-weight: bold; color: green")
			else:
				self.asm_2.setStyleSheet("font-weight: normal; color: black")
			if msg[3]:
				self.agm.setStyleSheet("font-weight: bold; color: green")
			else:
				self.agm.setStyleSheet("font-weight: normal; color: black")
		else:   # Auto Standby Switch OFF
			self.autoStandbyMode.setText('OFF')
			self.autoStandbyMode.setStyleSheet("font-weight: bold; color: black")
			self.apm.setStyleSheet("font-weight: normal; color: black")
			self.asm_2.setStyleSheet("font-weight: normal; color: black")
			self.agm.setStyleSheet("font-weight: normal; color: black")

	def estopVisual(self, msg):
		if msg:
			self.estopBox.setStyleSheet("background-color: red")
		else:
			self.estopBox.setStyleSheet("background-color: rgba(255, 255, 255, 10)")

	def steeringHandle(self, msg):
		self.steerVal.setText('Steering :' + str(msg))
		self.steerbar.setValue(msg)

	def gearPosition(self, msg):
		if msg == 0:   # Parking
			self.gearSlider.setValue(99)
		elif msg == 5:   # Driving
			self.gearSlider.setValue(0)
		elif msg == 6:   # Neutral
			self.gearSlider.setValue(25)
		elif msg == 7:   # Reverse
			self.gearSlider.setValue(50)
		else:
			self.print("Gear ValueError!!!!", msg)

	def apsbpsFeed(self, msg):
		self.feedbacktable.setItem(1, 1, QTableWidgetItem(str(msg[0])))
		self.feedbacktable.setItem(1, 2, QTableWidgetItem(str(msg[12])))
		self.feedbacktable.setItem(2, 1, QTableWidgetItem(str(msg[1])))
		self.feedbacktable.setItem(2, 2, QTableWidgetItem(str(msg[11])))


	def checkAll(self):
		#Fuck dataChanged
		checkeditem = 0
		for i in range(self.topicList.count()):
			if self.topicList.item(i).checkState() == Qt.Checked:
				checkeditem += 1
		if checkeditem != self.topicList.count():   ## Select All Items
			#print(checkeditem, self.topicList.count(), "check all item!")
			for i in range(self.topicList.count()):
				self.topicList.item(i).setCheckState(Qt.Checked)
				checkeditem = self.topicList.count()
		else:   ## Uncheck All Items
			#print("uncheck all item!")
			for i in range(self.topicList.count()):
				self.topicList.item(i).setCheckState(Qt.Unchecked)
				checkeditem = 0

	def reloadTopics(self):
		topics = self.topicnode.get_topic_names_and_types()
		self.topicList.clear()
		for topic in topics:
			newitem = topic[0]
			print(newitem)
			#+' '+topic[1]
			newitem = QListWidgetItem(newitem)
			newitem.setFlags(newitem.flags() | Qt.ItemIsUserCheckable)
			newitem.setCheckState(Qt.Unchecked)
			self.topicList.addItem(newitem)

	def saveFileDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		filedir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		if filedir:
			self.saveDir.setText(filedir)

	def logoutBtn(self):
		'''
		TODO
		1. is it recording? (is it driving?)
		'''
		self.logWin = loginWindow()
		self.logWin.show()
		self.adms_subscriber_class.quit()

		self.hide()

	@pyqtSlot(list)
	def wheel_speed(self, msg):
		self.cantime = time.time()
		tot_speed = msg[0]
		if tot_speed >= 10:   ## if car is faster than 10km/h, start recording
			if not self.recordFlag:
				pass
				#self.recordFlag = True
				##start Thread
				#emit signal of pressing btn
		fl, fr, rl, rr = msg[1:]
		self.rl_speed.setText("RL :" + str(round(rl, 2)))
		self.fl_speed.setText("FL :" + str(round(fl, 2)))
		self.fr_speed.setText("FR :" + str(round(fr, 2)))
		self.rr_speed.setText("RR :" + str(round(rr, 2)))
		self.velocityLcd.display(int(tot_speed))

class adms_subscriber(QThread):
	sig_wheel = pyqtSignal(list)   # Wheel & Average Speed
	sig_apsbps = pyqtSignal(list)   # APS/BPS ACT/NONACT FEEDBACK
	sig_gear = pyqtSignal(int)   # GearPosition
	sig_steer = pyqtSignal(int)   # Steering Angle
	sig_estop = pyqtSignal(bool)   # ESTOP Switch
	sig_auto = pyqtSignal(list)   # Auto Stnadby Switch
	sig_override = pyqtSignal(int)   # Override Feedback
	sig_turn = pyqtSignal(int)   # Turn Signal
	sig_belt = pyqtSignal(bool)   # Driver Belt
	sig_trunk = pyqtSignal(bool)   # Trunk
	sig_door = pyqtSignal(list)   # Door
	def __init__(self):
		super().__init__()
		try:
			rclpy.init(args=None)
		except:
			raise Exception("Init 실패, 다시시도 해주세요")
		self.node = rclpy.create_node("ADMS")
		self.node.get_logger().info("ADMS : ADMS Initialize")
	def __del__(self):
		print("Command Job Done")
		#commsdel = ". /opt/ros/dashing/setup.bash"
		#subprocess.Popen(commsdel, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
		#rclpy.shutdown()
		self.wait()
		self.quit()
	def run(self):
			sub2 = self.node.create_subscription(
				Float32MultiArray,
				'/Ioniq_info',
				self.joint_callback)
			rclpy.spin(self.node)
	def joint_callback(self, msg : Float32MultiArray):
		self.sig_wheel.emit(list(msg.data[19:]))
		self.sig_apsbps.emit(list(msg.data))
		self.sig_gear.emit(int(list(msg.data)[2]))
		self.sig_steer.emit(int(list(msg.data)[3]))
		self.sig_estop.emit(bool(list(msg.data)[4]))
		self.sig_auto.emit(list(msg.data)[5:9])
		self.sig_override.emit(int(list(msg.data)[9]))
		self.sig_turn.emit(int(list(msg.data)[10]))
		self.sig_belt.emit(bool(list(msg.data)[13]))
		self.sig_trunk.emit(bool(list(msg.data)[14]))
		self.sig_door.emit(list(msg.data)[15:19])


if __name__ == "__main__":
	app = QApplication(sys.argv)
	logWin = loginWindow()
	logWin.show()
	app.exec_()
