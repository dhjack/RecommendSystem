#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from JServer import JRequestHandler, JServer 
import threading
import struct
from BayesEngine import BayesEngine
from ALSEngine import ALSEngine, read_data
from LSIEngine import LSIEngine, readItemInfos
import MySQLdb
import Config

class RSHandler(JRequestHandler):
    '''
    处理socket返回的数据。
    '''

    def process(self, data):
        global engine
        action = struct.unpack('!I', data[0:4])[0]
        user = struct.unpack('!I', data[4:8])[0]
        param = len(data) > 8 and struct.unpack('!I', data[8:])[0] or ""
        cur_thread = threading.current_thread()
        response = "rs: {}: {} {} {}".format(cur_thread.name, action, user, param)

        # 如果是获取推荐，那么应该会返回节目id；如果是反馈，那么返回0的状态
        response = ""
        if action == 2:
            pid = engine.recommend(getUserRealTimeAction(user))
            response += struct.pack('!I', pid)
        elif action == 1 or action == 0:
            saveUserRealTimeAction(action, user, param)
            response += struct.pack('!I', 0)
        else:
            print "unknow action", action
            response += struct.pack('!I', -1)

        return response

def getUserBehavior(host, user, passwd):
    db = MySQLdb.connect(host, user, passwd, "reSystem", charset="utf8")
    cursor = db.cursor()      
    cursor.execute("SET NAMES 'utf8'")
    cursor.execute("select uid, pid, rate from userRates")
    data = cursor.fetchall()
    db.close()
    return data

def getUserRealTimeAction(user):
    #print "get", user, "real time action"
    with lock:
        return realTimeActions.get(user, dict())

def saveUserRealTimeAction(action, user, pid):
    '''
    {user: set([pid, likeOrNot])}
    '''
    #print "set", user, "real time action", action, pid
    with lock:
        if user not in realTimeActions:
            realTimeActions[user] = {}
        realTimeActions[user][pid] = action
        #print realTimeActions[user]

if __name__ == "__main__":

    Config.init("./rs.conf")

    engine = None
    etype = Config.engineName()
    if etype == "bayes":
        engine = BayesEngine(getUserBehavior(Config.host(), Config.user(), Config.passwd()))
    elif etype == "als":
        df, plays = read_data(Config.host(), Config.user(), Config.passwd())
        engine = ALSEngine(df, plays)
    elif etype == "lsi":
        engine = LSIEngine(readItemInfos(Config.host(), Config.user(), Config.passwd()))
    else:
        print "unknow engine:", etype
        sys.exit(1)

    realTimeActions = {}
    lock = threading.Lock()

    JServer().start(Config.engineHost(), Config.enginePort(), RSHandler)
