import sys
import PyQt5
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from subprocess import Popen, PIPE
import signal
import heapq
#import roslaunch

import pics_rc
import cryptography
from cryptography.fernet import Fernet
import numpy as np
from datetime import datetime as dt
import subprocess
import os


addswitch_form = uic.loadUiType("adam-addswitch.ui")[0]
activatedep = {'roscore' : 0, 'ROSbridge' : 0}
runningprc = []

def kth_smallest(nums, k):
  heap = []
  for num in nums:
    heapq.heappush(heap, num)
  kth_min = None
  for _ in range(k):
    kth_min = heapq.heappop(heap)
  return kth_min[1]

class addswitchWindow(QDialog, addswitch_form):
	sig_btn = pyqtSignal(list)
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
		self.shprogram.setDisabled(True)
		self.disabledsh = True
		self.nodes.setDisabled(True)
		self.commidx = -1

		self.buttonBox.accepted.connect(self.addtoMain)
		self.checkBox_3.stateChanged.connect(self.activateshprogram)

	def activateshprogram(self):
		if self.disabledsh:
			self.shprogram.setDisabled(False)
			self.disabledsh = False
		else:
			self.shprogram.setDisabled(True)
			self.disabledsh = True

	def addtoMain(self):
		category = self.category.currentText()
		switchname = self.switchname.text()
		command = self.command.text()
		nodes = self.nodes.text()
		if (category == "") or (switchname == "") or (command == ""):
			reply = QMessageBox.warning(self, 'Warning', 'Fill the Blank(s)!',
				QMessageBox.Ok, QMessageBox.Ok)
		else:
			f = open("ADMS_switch_list.txt", 'a')
			f.write(str(category)+'|'+str(switchname)+'|'+str(command)+'|'+str(nodes)+'|')
			if self.checkBox.checkState() == 2: # 2 == checked!
				f.write("ROS1&")
			if self.checkBox_2.checkState() == 2: # 2 == checked!
				f.write("ROS2&")
			if self.checkBox_3.checkState() == 2: # 2 == checked!
				f.write("sh "+self.shprogram.text())
			f.write('|')
			if self.checkBox_4.checkState() == 2: # 2 == checked!
				f.write("roscore&")
			if self.checkBox_5.checkState() == 2: # 2 == checked!
				f.write("ROSbridge")
			f.write("\n")
			f.close()
			self.sig_btn.emit([category, switchname, command, nodes])
			print("add btn accepted!")

class QLabel_clickable(QLabel):
	clicked = pyqtSignal()
	def __init__(self, parent = None):
		QLabel.__init__(self, parent)
	def mousePressEvent(self, ev):
		self.clicked.emit()

class switchLayout(QHBoxLayout):
	def __init__(self, category, switchidx, switchname, nodes, switchNum, frame):
		super().__init__()
		self.category = category
		self.linenum = switchNum
		self.com = 0
		self.switchidx = switchidx
		self.switchon = False
		#self.frame = frame
		self.onimg = QPixmap('on.png')
		self.onimg = self.onimg.scaled(51, 51, Qt.KeepAspectRatio)
		self.offimg = QPixmap('off.png')
		self.offimg = self.offimg.scaled(51, 51, Qt.KeepAspectRatio)
		self.switch = QLabel_clickable()
		self.switch.resize(51, 51)
		self.switch.setPixmap(self.offimg)
		#self.switchlabel = QLabel(str(switchname))
		self.switchlabel = QLabel_clickable(str(switchname))
		self.switchlabel.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
		self.switchlabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
		self.switch.setObjectName('switch'+category+str(switchidx))
		self.switchlabel.setObjectName('switch'+category+str(switchidx)+'lbl')
		'''
		QApplication.setOverrideCursor(Qt.WaitCursor)
		QApplication.restoreOverrideCursor()
		'''
		self.addWidget(self.switch)
		self.addWidget(self.switchlabel)
		self.labelclicked = False
		self.switch.clicked.connect(self.onoff)
		self.switchlabel.clicked.connect(self.select)
	def onoff(self):
		if self.switchon: # on -> off
			self.activateutil(self.switchon)
			self.switch.setPixmap(self.offimg)
			self.switchon = False
		else:
			self.activateutil(self.switchon)
			self.switch.setPixmap(self.onimg)
			self.switchon = True
	def select(self):
		if not self.labelclicked:
			self.parentWidget().setStyleSheet("border : 2px solid blue")
			self.labelclicked = True
		else:
			self.parentWidget().setStyleSheet("border : transparent")
			self.labelclicked = False

	def activateutil(self, state):
		f = open("ADMS_switch_list.txt", 'r')
		print('linenum :', self.linenum)
		for i, line in enumerate(f):
			if i == self.linenum:
				linesplited = line.split('|')
				#env(ROS1&ROS2&sh)
				comms = ""
				env = linesplited[4].split('&')
				dep = linesplited[5].split('&')
				print('env :', env)
				if not self.switchon:
					for i in range(len(env)):
						if env[i] == 'ROS1':
							#ros1 activate
							comms = comms+". /opt/ros/melodic/setup.bash"
						if env[i] == 'ROS2':
							#ros2 activate
							if len(comms) != 0:
								comms = comms+" && "
							comms = comms+". /opt/ros/dashing/setup.bash"
						if env[i] == 'sh': #"(sh)
							if len(comms) != 0:
								comms = comms+" && "
							comms = comms+"sh "+self.shprogram
					#dependency(roscore&ROSbridge)
					for i in range(len(dep)):
						if (dep[i] == 'roscore') and (activatedep.get('roscore', -1) == 0):
							#ros1 activate
							commsdep = ". /opt/ros/melodic/setup.bash && roscore"
							subprocess.Popen(commsdep, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
							activatedep['roscore']+=1
						if (dep[i]=='ROSbridge') and (activatedep.get('ROSbridge', -1) == 0): #ROSbridge
							#ros2 activate
							commsdep = ". /opt/ros/melodic/setup.bash && . /opt/ros/dashing/setup.bash && ros2 run ros1_bridge dynamic_bridge --bridge-all-topics"
							subprocess.Popen(commsdep, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
							activatedep['ROSbridge']+=1
					# command
					if len(comms)!=0:
						comms = comms+" && "
					comms = comms+linesplited[2]
					self.com = subprocess.Popen(comms, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
					self.commidx = len(runningprc)+1
					runningprc.append((self.com, self.commidx))

				else: # switch on -> off
					self.com.send_signal(signal.SIGINT)
					for i in range(len(dep)):
						print(kth_smallest(runningprc, self.commidx, 'is killed!'))
						if dep[i] == 'roscore':
							activatedep['roscore']-=1
							if activatedep['roscore'] == 0:
								commsdep = "killall -9 roscore && killall -9 rosmaster"
								print(commsdep)
								subprocess.Popen(commsdep, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
						if dep[i] == 'ROSbridge':
							activatedep['ROSbridge']-=1
							if activate['ROSbridge'] == 0:
								commsdep = ". /opt/ros/melodic/setup.bash && rosnode kill /ros_bridge"
								print(commsdep)
								subprocess.Popen(commsdep, stdin = subprocess.PIPE, shell = True, executable = '/bin/bash')
		f.close()
