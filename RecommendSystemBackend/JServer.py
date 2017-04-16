#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import threading
import SocketServer
import struct

class JRequestHandler(SocketServer.BaseRequestHandler):
    '''
    提供一个基类，需要重写process，做实际的解析包, 并处理的动作
    '''

    def process(self, data):
        action = struct.unpack('!I', data[0:4])[0]
        user = struct.unpack('!I', data[4:8])[0]
        param = len(data) > 8 and struct.unpack('!I', data[8:])[0] or ""
        cur_thread = threading.current_thread()
        response = "{}: {} {} {}".format(cur_thread.name, action, user, param)
        return response

    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        self.request.sendall(self.process(data))

class JServer():
    '''
    封装了server的开启的动作。不会停止。应该需要作为daemon进程使用
    '''

    def start(self, host, port, handerClass):
        self.server = ThreadedTCPServer((host, port), handerClass)
        ip, port = self.server.server_address    # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()
        print "Server loop running in thread:", server_thread.name

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass

def client(ip, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    r = ''
    try:
        packet = ""
        packet += struct.pack('!I', data[0])
        packet += struct.pack('!I', data[1])
        if len(data) > 2:
            packet += struct.pack('!I', data[2])

        sock.sendall(packet)
        response = sock.recv(1024)
        print len(response)
        r = struct.unpack('!I', response[0:4])[0]
        print "Received: {}".format(r)
    finally:
        sock.close()
    return r

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 9998

    #s = JServer()
    #s.start(HOST, PORT, JRequestHandler)

    pid = client(HOST, PORT, (2, 3872343))
    client(HOST, PORT, (0, 3872343, pid))
    client(HOST, PORT, (2, 3872343))
    #s.stop()
