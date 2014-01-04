# -*- coding:utf8 -*-

import sys, threading, time, os
from PyQt4 import QtGui, QtCore
from smtp import smtp
from pop3 import pop3
from logging import Logger, Handler, getLogger, Formatter

mutex = threading.Lock()

def append_to_widget(widget, s):
    widget.append(s)

    
class loggerHandler(Handler):

    def __init__(self, loggerWidget):
        
        self.loggerWidget = loggerWidget
        super(loggerHandler, self).__init__()

    def emit(self, record):

        self.loggerWidget.emit(QtCore.SIGNAL('newLog(QString)'), 
                                             QtCore.QString(self.format(record).decode('gbk')))

  

class QMainArea(QtGui.QWidget):
    
    def __init__(self):

        super(QMainArea, self).__init__()
        self.initLayout()


    def initLayout(self):

        self.pop3AddressLable = QtGui.QLabel(u'POP3服务器地址')
        self.pop3AddressText = QtGui.QLineEdit(self)

        self.smtpAddressLable = QtGui.QLabel(u'SMTP服务器地址')
        self.smtpAddressText = QtGui.QLineEdit(self)

        self.accountLable = QtGui.QLabel(u'用户名')
        self.accountText = QtGui.QLineEdit(self)

        self.passwdLable = QtGui.QLabel(u'密码')
        self.passwdText = QtGui.QLineEdit(self)
        self.passwdText.setEchoMode(QtGui.QLineEdit.Password)

        self.logLable = QtGui.QLabel(u'日志')
        self.logView = QtGui.QTextBrowser()

        self.mailList = QtGui.QTreeWidget()
        self.mailList.setHeaderLabels([u'时间', 
                                       u'发件人', 
                                       u'收件人', 
                                       u'主题'])

        self.loginBtn = QtGui.QPushButton(u'登录')

        self.logoutBtn = QtGui.QPushButton(u'断开')

        self.sendBtn = QtGui.QPushButton(u'发信')

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(self.pop3AddressLable, 1, 1, 1, 1)
        grid.addWidget(self.pop3AddressText, 1, 2, 1, 2)
        grid.addWidget(self.smtpAddressLable, 2, 1, 1, 1)
        grid.addWidget(self.smtpAddressText, 2, 2, 1, 2)
        grid.addWidget(self.accountLable, 3, 1, 1, 1)
        grid.addWidget(self.accountText, 3, 2, 1, 2)
        grid.addWidget(self.passwdLable, 4, 1, 1, 1)
        grid.addWidget(self.passwdText, 4, 2, 1, 2)
        grid.addWidget(self.loginBtn, 5, 1, 1, 1)
        grid.addWidget(self.logoutBtn, 5, 2, 1, 1)
        grid.addWidget(self.sendBtn, 5, 3, 1, 1)
        grid.addWidget(self.logLable, 6, 1, 1, 1)
        grid.addWidget(self.logView, 7, 1, 1, 3)
        grid.addWidget(self.mailList, 1, 4, 7, 3)

        self.setLayout(grid)

        

class mainWindow(QtGui.QMainWindow):

    def __init__(self):
        
        super(mainWindow, self).__init__()
        self.initLayout()


    def initLayout(self):

        self.statusBar()
        menuBar = self.menuBar()

        exitAction = QtGui.QAction(u'退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip(u'退出 SimpleMail')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.fileMenu = menuBar.addMenu(u'菜单')
        self.fileMenu.addAction(exitAction)

        self.mainArea = QMainArea()

        self.setCentralWidget(self.mainArea)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle(u'SimpleMail')
        self.show()
