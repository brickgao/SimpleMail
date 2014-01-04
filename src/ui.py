# -*- coding:utf8 -*-

import sys, threading, time, os, email
from PyQt4 import QtGui, QtCore, QtWebKit
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


        
class QSendMailView(QtGui.QDialog):

    def __init__(self, parent=None):
        
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.initLayout()

    def initLayout(self):
        
        self.toLable = QtGui.QLabel(u'发件人')
        self.toText = QtGui.QLineEdit(self)

        self.subjectLable = QtGui.QLabel(u'标题')
        self.subjectText = QtGui.QLineEdit(self)

        self.contentLable = QtGui.QLabel(u'正文')
        self.contentText = QtGui.QTextEdit(self)

        self.sendBtn = QtGui.QPushButton(u'发送')
        self.sendBtn.clicked.connect(self.send)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.toLable, 1, 1, 1, 1)
        grid.addWidget(self.toText, 1, 2, 1, 1)
        grid.addWidget(self.subjectLable, 2, 1, 1, 1)
        grid.addWidget(self.subjectText, 2, 2, 1, 1)
        grid.addWidget(self.contentLable, 3, 1, 1, 1)
        grid.addWidget(self.contentText, 3, 2, 5, 1)
        grid.addWidget(self.sendBtn, 8, 1, 1, 2)

        self.setLayout(grid)
        
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle(u'发送邮件')

        self.show()


    def send(self):
        
        if self.toText.text() == '':
            return self.errorAlert(u'请输入收件人')
        if self.subjectText.text() == '':
            return self.errorAlert(u'请输入标题')
        if self.contentText.toPlainText() == '':
            return self.errorAlert(u'请输入正文')

        _d = {}
        _d['to'] = str(self.toText.text())
        _d['subject'] = str(self.subjectText.text())
        _d['content'] = str(self.contentText.toPlainText())
        
        self.parent._e.emit(_d)
        
        self.close()


    def errorAlert(self, s):

        QtGui.QMessageBox.critical(self, u'错误', s)

        
        
class QMailInfo(QtGui.QDialog):
    
    def __init__(self, mailInfo, parent=None):
        
        self.mailInfo = mailInfo
        QtGui.QDialog.__init__(self, parent)
        self.initLayout()

    
    def initLayout(self):

        _ = self.mailInfo

        self.fromLable = QtGui.QLabel(u'发件人')
        self._from = QtGui.QLabel(email.utils.parseaddr(_.get('from'))[1])

        self.toLable = QtGui.QLabel(u'收件人')
        self._to = QtGui.QLabel(email.utils.parseaddr(_.get('to'))[1])


        _sj = email.Header.decode_header(_.get('subject'))[0][0]
        _code = email.Header.decode_header(_.get('subject'))[0][1]
        _sj = _sj.decode(_code)

        self.subjectLable = QtGui.QLabel(u'主题')
        self._subject = QtGui.QLabel(_sj)

        self.sendTimeLable = QtGui.QLabel(u'时间')
        self.sendTime = QtGui.QLabel(_.get('date'))

        self.contentLable = QtGui.QLabel(u'邮件正文')
        self.contentView = QtWebKit.QWebView()

        content = u''
        _type = _.get_content_charset()
        if _type:   _c = _.get_payload(decode='base64')
        else:       _c = _.get_payload()
        if _.is_multipart():
            for _e in _c:
                content += unicode(_e, _type)
        else:   
            content = unicode(_c, _type)
        self.contentView.setHtml(content, 
                                 QtCore.QUrl(''))

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.fromLable, 1, 1, 1, 1)
        grid.addWidget(self._from, 1, 2, 1, 3)
        grid.addWidget(self.toLable, 2, 1, 1, 1)
        grid.addWidget(self._to, 2, 2, 1, 3)
        grid.addWidget(self.subjectLable, 3, 1, 1, 1)
        grid.addWidget(self._subject, 3, 2, 1, 3)
        grid.addWidget(self.sendTimeLable, 4, 1, 1, 1)
        grid.addWidget(self.sendTime, 4, 2, 1, 3)
        grid.addWidget(self.contentLable, 5, 1, 1, 1)
        grid.addWidget(self.contentView, 6, 1, 1, 4)
    
        self.setLayout(grid)

        self.setGeometry(120, 120, 800, 500)
        self.setWindowTitle(u'查看邮件' + _sj)
        self.show()
        

        

class QMainArea(QtGui.QWidget):
    
    _e = QtCore.pyqtSignal(dict, name='sendMail')

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
        self.mailListView.itemDoubleClicked.connect(self.getCurrentMail)

        self._e.connect(self.sendMailNow)

        self.loginBtn = QtGui.QPushButton(u'登录')
        self.loginBtn.clicked.connect(self.login)

        self.logoutBtn = QtGui.QPushButton(u'断开')
        self.logoutBtn.clicked.connect(self.logout)

        self.sendBtn = QtGui.QPushButton(u'发信')
        self.sendBtn.clicked.connect(self.sendMail)

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


    def logout(self):
        
        t = threading.Thread(target=self.logoutRun)
        t.start()


    def logoutRun(self):
        
        global mutex

        mutex.acquire()

        self.pop3.quit()
        self.emit(QtCore.SIGNAL('needRefresh'))

        mutex.release()


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

            
    def getCurrentMail(self):
        
        _id = int(self.mailListView.currentItem().text(0))
        mailView = QMailInfo(self.mailList[_id], parent=self)
        mailView.exec_()
        mailView.destroy()


    def sendMail(self):

        if self.pop3AddressText.text() == '':
            return self.errorAlert(u'请填写 POP3 服务器地址')
        if self.smtpAddressText.text() == '':
            return self.errorAlert(u'请填写 SMTP 服务器地址')
        if self.accountText.text() == '':
            return self.errorAlert(u'请填写用户名')
        if self.passwdText.text() == '':
            return self.errorAlert(u'请填写密码')

        sendMailView = QSendMailView(parent=self)
        sendMailView.exec_()
        sendMailView.destroy()

    def sendMailNow(self, _d):
        
        t = threading.Thread(target=self.sendMailRun, args=(_d, ))
        t.start()

    
    def sendMailRun(self, _d):
        
        global mutex

        mutex.acquire()

        self.smtp.url = str(self.smtpAddressText.text())
        self.smtp.server = ''
        _ = self.smtp.url.split('.')
        for i in range(1, len(_)):
            if i == len(_) - 1: self.smtp.server += _[i]
            else:               self.smtp.server += _[i] + '.'

        self.smtp.sendHelo()
        self.smtp.login(self.accountText.text(), self.passwdText.text())
        self.smtp.initMail(str(self.accountText.text()))
        self.smtp.setRcpt(_d['to'])
        self.smtp.setData(_d)
        self.smtp.quit()
        
        mutex.release()

    
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
