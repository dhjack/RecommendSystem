#! /usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import random

class BayesEngine():
    '''
    P (喜欢节目A|用户看过了节目a,b,c) = P (用户看过的节目a,b,c|喜欢节目A) * P (喜欢节目A) / P (用户看过节目a,b,c)
    P (用户看过的节目a,b,c|喜欢节目A) = P (用户看过节目a|喜欢节目A) * P (用户看过节目b|喜欢节目A) * P (用户看过节目c|喜欢节目A)
    P (用户看过节目a|喜欢节目A) = count(喜欢节目A的用户中，看过节目a的用户数) / count(喜欢节目A的用户数)
    P (喜欢节目A) = count(喜欢节目A的用户数) / count(总用户数)
    '''

    def __init__(self, behaviors):
        '''
        behaviors: (user, item, score)
        uidInfo: (user, set[watched])
        pidInfo: (pid, (set[favorite item], set[unfavorite item]))
        '''
        self.uidInfo, self.pidInfo = self.storeBehavior(behaviors)
        print "init finish"

    def storeBehavior(self, data):
        uidInfo = {}
        pidInfo = {}
        for uid, pid, rate in data:
            pid = long(pid)
            rate = int(rate)
            if uid not in uidInfo:
                uidInfo[uid] = set()
            uidInfo[uid].add(pid)

            if pid not in pidInfo:
                pidInfo[pid] = [set(), set()]
            if rate > 3:
                pidInfo[pid][0].add(uid)
            else:
                pidInfo[pid][1].add(uid)

        return (uidInfo, pidInfo)

    def recommend(self, actions):
        return self.recommendByAction(actions, self.uidInfo, self.pidInfo)

    def recommendByAction(self, actions, uidInfo, pidInfo):
        '''
        actions: like {pid:0, pid:1}, 0 is like and 1 is not like
        uidInfo: (user, set[watched])
        pidInfo: (pid, (set[favorite item], set[unfavorite item]))
        '''
        recommendPid = 0L
        oldProbability = -1
        # 遍历所有节目，计算对应的分值，取最大者
        for pid, info in pidInfo.iteritems():
            if pid in actions or len(info[0]) == 0:
                continue
            pm = len(info[0]) * 1.0 / len(uidInfo)
            pa = 1.0
            for watchedPid, act in actions.iteritems():
                paN = len(pidInfo.get(watchedPid, [set(), set()])[act] & info[0]) * 1.0 / len(info[0])

                #print "paN", paN
                # 如果没有数据，默认给一个初始值
                if paN == 0.0:
                    pa *= 0.001
                else:
                    pa *= paN
                
            newProbability = pm * pa
            if newProbability > oldProbability:
                oldProbability = newProbability
                recommendPid = pid

        return recommendPid


if __name__ == "__main__":
    def getUserBehavior():
        db = MySQLdb.connect(host, user, passwd, "reSystem", charset="utf8")
        cursor = db.cursor()      
        cursor.execute("SET NAMES 'utf8'")
        cursor.execute("select uid, pid, rate from userRates")
        data = cursor.fetchall()
        db.close()

        return data
    b = BayesEngine(getUserBehavior())
    #uidInfo = dict([("a", (103, 105)),("b", (103, 104)),("c", (104))])
    #pidInfo = dict([(103, (set(["a", "b"]), set())),(104, (set(["c", "b"]), set(["a"]))),(105, (set(["a"]), set(["c"])))])

    print b.recommend(dict([(1296384L, 0)]))
    #print recommendByAction([(103, 1)], uidInfo, pidInfo)
    #print recommendByAction(dict([(105, 0)]), uidInfo, pidInfo)
