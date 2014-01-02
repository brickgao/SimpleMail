# -*- coding:utf8 -*-

import socket, logging

class pop3:
    
    def __init__(self, url, port):
        
        self.url = url
        self.port = port
        self.loginSucc = False
        self.totalMail = 0
        self.totalSize = 0
        self.simpleMailList = []
        self.logger = logging.Logger(__name__)


    def login(self, username, passwd):

        self.username = str(username)
        self.passwd = str(passwd)

        # Connect to server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.url, self.port))

        _ = self.sock.recv(1024)
        if not '+OK' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])

        # Send username
        self.sock.sendall('USER ' + self.username + '\r\n')
        self.logger.info('USER ' + self.username)

        _ = self.sock.recv(1024)
        if not '+OK' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
        
        self.sock.sendall('PASS ' + self.passwd + '\r\n')
        self.logger.info('PASS ***')
        
        _ = self.sock.recv(1024)
        if not '+OK' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
            self.loginSucc = True
            return True, _

    def getList(self):

        if not self.loginSucc:
            self.logger.error('You should login first')
            return False, 'You should login first'

        # Send LIST
        self.sock.sendall('LIST\r\n')
        self.logger.info('LIST')

        _ = self.sock.recv(1024)
        if not '+OK' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
            _list = _[4:-2].split('\r\n')[1:-1]
            self.simpleMailList = []
            # Format list information
            for _t in _list:
                _d = {}
                _d['id'] = _t.split(' ')[0]
                _d['size'] = _t.split(' ')[1]
                self.simpleMailList.append(_d)
            return True, _

    def getStat(self):

        if not self.loginSucc:
            self.logger.error('You should login first')
            return False, 'You should login first'

        # Send STAT
        self.sock.sendall('STAT\r\n')
        self.logger.info('STAT')

        _ = self.sock.recv(1024)
        if not '+OK' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
            # Format stat information
            self.totalMail = int(_[:-2].split(' ')[1])
            self.totalSize = int(_[:-2].split(' ')[2])
            return True, _

if __name__ == '__main__':

    pop = pop3('pop.163.com', 110)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') 
    ch.setFormatter(formatter)
    pop.logger.addHandler(ch)
    _user, _pass = raw_input().split(' ')
    pop.login(_user, _pass)
    pop.getList()
    pop.getStat()
