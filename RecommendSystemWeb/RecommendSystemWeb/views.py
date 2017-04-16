#!/usr/bin/python
# -*- coding: utf-8 -*-  

from flask import abort, request, session, escape, render_template, make_response
import os
import json
import MySQLdb
import random
import struct
import socket

host = "localhost"
user = "root"
passwd = "XW@mysql951.32"
port = 9998

from RecommendSystemWeb import app

@app.route('/')
def hello_world():
    if 'uniqueId' not in session:
        uniqueId = random.randint(0, 10000000)
        print "new user:", uniqueId
        session['uniqueId'] = uniqueId
    else: 
        print "old user:", session['uniqueId']
    return render_template('index.html')

def packResponseJson(item):
    '''
    根据节目id，查询节目信息，并生成json数据返回页面
    '''
    db = MySQLdb.connect(host, user, passwd, "reSystem", charset="utf8")
    cursor = db.cursor()      
    cursor.execute("select info from moviesJsonInfo where pid = %d" % item)
    data = cursor.fetchall()
    db.close()
    if len(data) == 0:
        return json.dumps({'name':u'也许您需要休息一下',
                'imgSrc':"", 
                'desc':u'也许您需要休息一下',
                'item': item})
    else:
        info = json.loads(data[0][0], strict=False)
        jsonData = {'name':info['title'],
                'imgSrc':info['images']['small'], 
                'desc':info['summary'],
                'item': item}
        return json.dumps(jsonData)

def communicationWithRSBackend(packet):
    '''
    和推荐后端通过socket交流，并获取推荐数据

    包格式：
        获取推荐：
         !I 2
         !I pid
    会得到一个节目id，或者状态码
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", port))
    r = 0
    try:
        sock.sendall(packet)
        response = sock.recv(1024)
        r = struct.unpack('!I', response[0:4])[0]
        print "Received: {}".format(r)
    finally:
        sock.close()
    return r

@app.route('/recommend')
def recommend():
    # 1 get session id
    if 'uniqueId' not in session:
        print " get recommend without uniqueId "
        abort(500)
    else: 
        #   if id in cache, get the context.
        #   if id no in cache, init a new context
        user = int(session['uniqueId'])
        packet = ""
        packet += struct.pack('!I', 2)
        packet += struct.pack('!I', user)

        #   get item from context
        item = communicationWithRSBackend(packet)
        print "recommedn for user:", user, " id:", item
        return packResponseJson(item)

@app.route('/feedback', methods=['POST'])
def feedback():
    '''
    反馈给推荐后端的包格式
        !I 0/1  0 代表喜欢，1代表不喜欢
        !I user 用户id
        !I pid  节目id
    ''' 
    # 1 get session id
    if 'uniqueId' not in session:
        print " feedback without uniqueId "
        abort(500)
    else: 
        print "feedback for user:", session['uniqueId']

        #   if id in cache, get the context.
        #   if id no in cache, init a new context
        user = int(session['uniqueId'])
        # get 
        value = int(request.form['value'])
        item = int(request.form['item'])
        packet = ""
        packet += struct.pack('!I', value)
        packet += struct.pack('!I', user)
        packet += struct.pack('!I', item)
        communicationWithRSBackend(packet)
        a = "value %d item %d" %( value, item )
        return a 

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
