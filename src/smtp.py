# -*- coding:utf8 -*-

import socket, logging, base64

class smtp:
    
    def __init__(self, url, port):
        
        self.url = url
        self.port = port
        self.logger = logging.Logger(__name__)
        self.heloSucc = False
        self.server = ''
        _ = url.split('.')
        for i in range(1, len(_)):
            if i == len(_) - 1: self.server += _[i]
            else:               self.server += _[i] + '.'


    def sendHelo(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.url, self.port))
        
        # Send HELO
        self.sock.sendall('EHLO ' + self.server + '\r\n')
        self.logger.info('EHLO ' + self.server)

        _ = self.sock.recv(1024)
        if not '220' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
            _ = self.sock.recv(1024)
            self.logger.info(_[:-2])
            self.heloSucc = True
            return True, _

    def login(self, username, passwd):

        if not self.heloSucc:
            self.logger.error('You should say HELO first')
            return False, 'You should say HELO first'

        self.username = username
        self.passwd = passwd

        # Authentication use LOGIN type
        
        self.sock.send('AUTH LOGIN\r\n')
        self.logger.info('AUTH LOGIN')

        _ = self.sock.recv(1024)
        if not '334' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])

        self.sock.send(base64.b64encode(self.username) + '\r\n')
        self.logger.info(base64.b64encode(self.username))

        _ = self.sock.recv(1024)
        if not '334' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])

        self.sock.send(base64.b64encode(self.passwd) + '\r\n')
        self.logger.info('***')

        _ = self.sock.recv(1024)
        if not '235' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
            return True, _


    def initMail(self, _from):
        
        if not self.heloSucc:
            self.logger.error('You should say HELO first')
            return False, 'You should say HELO first'

        # Init mail transfer
        self.sock.sendall('mail from: <' + _from + '>\r\n')
        self.logger.info('mail from: <' + _from + '>')

        _ = self.sock.recv(1024)
        if not '250' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
            return True, _


    def setRcpt(self, _to):

        if not self.heloSucc:
            self.logger.error('You should say HELO first')
            return False, 'You should say HELO first'

        # Set Rcpt of mail
        self.sock.sendall('rcpt to: <' + _to + '>\r\n')
        self.logger.info('rcpt to: <' + _to + '>')

        _ = self.sock.recv(1024)
        if not '250' in _:
            self.logger.error(_[:-2])
            return False, _
        else:
            self.logger.info(_[:-2])
            return True, _
        


