#! /usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import random
import numpy as np
import json
import jieba
from gensim import corpora, models, similarities
from pprint import pprint
from collections import defaultdict
import time

class LSIEngine():

    def __init__(self, itemInfos):
        
        lastTime = time.time()
        # itemInfos : dict[(pid, description)]
        # train model
        jieba.load_userdict('./dict.txt.big.txt')
        stopWords = set([line.strip().decode("gbk").lower() for line in open("./stopWords.txt")])
        stopWords.add('\n')
        stopWords.add(' ')
        stopWords.add(u'\u2022')
        stopWords.add(u'\xa9')
        texts = []
        self.name2id = {}
        self.id2name = []
        for k, v in itemInfos.iteritems():
            seg_list = [w.lower() for w in jieba.cut(v, cut_all=False) if w.lower() not in stopWords]
            texts.append(list(seg_list))
            self.name2id[k] = len(self.id2name)
            self.id2name.append(k)

        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1

        texts = [[token for token in text if frequency[token] > 1] for text in texts]

        print  "start cast :", (time.time() - lastTime)

        lastTime = time.time()
        dictionary = corpora.Dictionary(texts)
        print  "dictionary cast :", (time.time() - lastTime)

        lastTime = time.time()
        corpus = [dictionary.doc2bow(text) for text in texts]
        print  "doc2bow cast :", (time.time() - lastTime)

        lastTime = time.time()
        tfidf = models.TfidfModel(corpus)
        print  "tfid model cast :", (time.time() - lastTime)
        lastTime = time.time()

        lastTime = time.time()
        corpus_tfidf = tfidf[corpus]
        print  "tfidf corpus cast :", (time.time() - lastTime)

        lastTime = time.time()
        self.lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=100) 
        print  "lsi model cast :", (time.time() - lastTime)
        lastTime = time.time()

        #corpus_lsi = lsi[corpus_tfidf] 
        self.index = similarities.MatrixSimilarity(self.lsi[corpus]) 
        self.corpus = corpus

        self.pidName = getPidName()
        print "init finish"

    def recommend(self, actions):
        # get cur vect
        localFactor = None
        for watchedPid, act in actions.iteritems():
            index = self.name2id[watchedPid]
            print "watch ", self.pidName[watchedPid]
            if act == 1:
                if localFactor is None:
                    localFactor = [(w1, w2 * -1) for (w1, w2) in self.lsi[self.corpus[index]]]
                else:
                    localFactor = [(w11, (w12 + w22*-1)) for ((w11, w12), (w21, w22)) in zip(localFactor, self.lsi[self.corpus[index]])]
            else:
                if localFactor is None:
                    localFactor = self.lsi[self.corpus[index]]
                else:
                    localFactor = [(w11, (w12 + w22)) for ((w11, w12), (w21, w22)) in zip(localFactor, self.lsi[self.corpus[index]])]
        if localFactor is None:
            return np.random.choice(self.name2id.keys())
        print localFactor 
        localFactor = [(v1, v2 / len(actions)) for (v1,v2) in localFactor]
        indexs = self.similar_items(localFactor, len(actions) + 1)
        for (index, value) in indexs:
            print self.pidName[self.id2name[index]], value
        # find first one which not in actions
        for (index, value) in indexs:
            pid = self.id2name[index] 
            if pid not in actions:
                return pid

    def similar_items(self, factor, N):
        """ Return the top N similar items for itemid. """
        sims = self.index[factor]
        return sorted(enumerate(sims), key=lambda item: -item[1])[:N]

def getPidName():
    import Config
    db = MySQLdb.connect(Config.host(), Config.user(), Config.passwd(), "reSystem", charset="utf8")
    cursor = db.cursor()      
    cursor.execute("SET NAMES 'utf8'")
    cursor.execute("select * from moviesJsonInfo")
    data = cursor.fetchall()
    print "data len ", len(data)
    db.close()

    r = {}
    for pid, info in data:
        try:
            pInfo = json.loads(info, strict=False)
            r[pid] = pInfo['title']
        except BaseException, e:
            print e

    return r

def readItemInfos(host, user, passwd):
    db = MySQLdb.connect(host, user, passwd, "reSystem", charset="utf8")
    cursor = db.cursor()      
    cursor.execute("SET NAMES 'utf8'")
    cursor.execute("select * from moviesJsonInfo")
    data = cursor.fetchall()
    print "db data len ", len(data)
    db.close()

    r = {}
    for pid, info in data:
        try:
            pInfo = json.loads(info, strict=False)
            if len(pInfo['summary']) > 50:
                r[pid] = pInfo['summary']
        except BaseException, e:
            print e

    print "return data len ", len(r)
    return r

if __name__ == "__main__":

    itemInfos = readItemInfos()
    b = LSIEngine(itemInfos)
    #uidInfo = dict([("a", (103, 105)),("b", (103, 104)),("c", (104))])
    #pidInfo = dict([(103, (set(["a", "b"]), set())),(104, (set(["c", "b"]), set(["a"]))),(105, (set(["a"]), set(["c"])))])

    print "for null"
    print b.recommend(dict())
    print "for key[1]"
    #print b.recommend(dict([(1296384L, 0)]))
    print b.recommend(dict([(1291546L, 0)]))
    #print recommendByAction([(103, 1)], uidInfo, pidInfo)
    #print recommendByAction(dict([(105, 0)]), uidInfo, pidInfo)
