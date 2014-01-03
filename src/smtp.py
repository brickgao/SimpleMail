# -*- coding:utf8 -*-

import socket, logging

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
        print self.server


    def sendHelo(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.url, self.port))
        
        # Send HELO
        self.sock.sendall('HELO ' + self.server + '\r\n')
        self.logger.info('HELO ' + self.server)

        _ = self.sock.recv(1024)
        if not '220' in _:
            self.logger.error(_)
            return False, _
        else:
            self.logger.info(_)
            self.heloSucc = True
            return True, _


    def initMail(self, _from):
        
        if not self.heloSucc:
            self.logger.error('You should say HELO first')
            return False, 'You should say HELO first'

        # Init mail transfer
        self.sock.sendall('mail from: <' + _from + '>\r\n')
        self.logger.info('mail from: <' + _from + '>')

        _ = self.sock.recv(1024)
        print _
        



    def setRcpt(self, _to):

        if not self.heloSucc:
            self.logger.error('You should say HELO first')
            return False, 'You should say HELO first'

        self.sock.sendall('RCPT ' + _to + '\r\n')
        


