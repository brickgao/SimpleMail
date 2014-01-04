# -*- coding:utf8 -*-

import sys, threading, time, os, email
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
        self.pop3 = pop3('')
        self.smtp = smtp('')
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

        FORMAT = Formatter('%(asctime)s %(levelname)s: %(message)s')
        self.handler = loggerHandler(self.logView)
        self.handler.setFormatter(FORMAT)
        self.pop3.logger.addHandler(self.handler)
        self.smtp.logger.addHandler(self.handler)
        self.logView.connect(self.logView,
                             QtCore.SIGNAL('newLog(QString)'), 
                             lambda log: append_to_widget(self.logView, log))
        

        self.mailListView = QtGui.QTreeWidget()
        self.mailListView.setHeaderLabels([u'#', 
                                           u'时间', 
                                           u'发件人', 
                                           u'收件人', 
                                           u'主题'])
        self.mailListView.setColumnWidth(0, 60)
        self.connect(self,
                     QtCore.SIGNAL('needRefresh'),
                     self.refreshMailList)
        

        self.loginBtn = QtGui.QPushButton(u'登录')
        self.loginBtn.clicked.connect(self.login)

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
        grid.addWidget(self.mailListView, 1, 4, 7, 5)

        self.setLayout(grid)


    def login(self):

        if self.pop3AddressText.text() == '':
            return self.errorAlert(u'请填写 POP3 服务器地址')
        if self.smtpAddressText.text() == '':
            return self.errorAlert(u'请填写 SMTP 服务器地址')
        if self.accountText.text() == '':
            return self.errorAlert(u'请填写用户名')
        if self.passwdText.text() == '':
            return self.errorAlert(u'请填写密码')

        t = threading.Thread(target=self.loginRun)
        t.start()

        
    def loginRun(self):

        global mutex

        mutex.acquire()

        self.pop3.url = str(self.pop3AddressText.text())
        self.smtp.url = str(self.smtpAddressText.text())

        self.pop3.login(self.accountText.text(),
                        self.passwdText.text())
        self.pop3.getList()
        self.pop3.getStat()
        self.pop3.getAllMail()
        self.emit(QtCore.SIGNAL('needRefresh'))

        mutex.release()

    
    def refreshMailList(self):
        
        self.mailList = self.pop3.mailList
        self.mailListView.clear()
        for i in range(len(self.mailList)):
            _ = self.mailList[i]
            mailInfo = QtGui.QTreeWidgetItem()
            _sj = email.Header.decode_header(_.get('subject'))[0][0]
            _code = email.Header.decode_header(_.get('subject'))[0][1]
            _sj = _sj.decode(_code)
            mailInfo.setText(0, str(i))
            mailInfo.setText(1, _.get('date').split(',')[1][1:])
            mailInfo.setText(2, email.utils.parseaddr(_.get('from'))[1])
            mailInfo.setText(3, email.utils.parseaddr(_.get('to'))[1])
            mailInfo.setText(4, _sj)
            self.mailListView.addTopLevelItem(mailInfo)

    
    def errorAlert(self, s):

        QtGui.QMessageBox.critical(self, u'错误', s)

        

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
