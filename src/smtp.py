# -*- coding:utf8 -*-

import socket, logging

class smtp:
    
    def __init__(self, url, port):
        
        self.url = url
        self.port = port
        self.logger = logging.Logger(__name__)
        self.heloSucc = False


    def sendHelo(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.url, self.port))
        
        # Send HELO
        self.sock.sendall('HELO\r\n')
        self.logger.info('HELO')

        _ = self.sock.recv(1024)
        if not '220' in _:
            self.logger.error(_)
            return False, _
        else:
            self.logger.info(_)
            self.heloSucc = True
            return True, _


    def setRcpt(self, _to):
        
        pass


