#!/usr/bin/python
# -*- coding:utf8 -*-

import ConfigParser

localHost = "localhost"
localUser = "root"
localPasswd = "123456"

localEngineName = "bayes"
localEnginePort = 9998
localEngineHost = "localhost"

def init(path):

    global localHost, localUser, localPasswd, localEngineName, localEnginePort, localEngineHost

    configEntity = ConfigParser.ConfigParser()
    configEntity.read(path)

    localHost = configEntity.get("dbConfig", "host")
    localUser = configEntity.get("dbConfig", "user")
    localPasswd = configEntity.get("dbConfig", "passwd")

    localEngineName = configEntity.get("engine", "name")
    localEngineHost = configEntity.get("engine", "host")
    localEnginePort = configEntity.getint("engine", "port")

    print "dbConfig host:", localHost
    print "dbConfig user:", localUser
    print "dbConfig passwd:", localPasswd

    print "engine name:", localEngineName
    print "engine host:", localEnginePort
    print "engine port:", localEnginePort


def host():
    return localHost

def user():
    return localUser

def passwd():
    return localPasswd

def engineName():
    return localEngineName

def enginePort():
    return localEnginePort

def engineHost():
    return localEngineHost


