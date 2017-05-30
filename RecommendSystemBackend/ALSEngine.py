#! /usr/bin/env python
# -*- coding: utf-8 -*-

from scipy.sparse import coo_matrix
import pandas
import numpy as np
from implicit.als import AlternatingLeastSquares
import MySQLdb

class ALSEngine():

    def __init__(self, df, behaviors, factors=50, regularization=0.01,
                              iterations=15,
                              exact=False, trees=20,
                              use_native=True,
                              dtype=np.float64,
                              cg=False):

        self.model = AlternatingLeastSquares(factors=factors, regularization=regularization,
                                        use_native=use_native, use_cg=cg,
                                        dtype=dtype)
        self.model.fit(behaviors)
        self.indexToRealId = dict(enumerate(df['artist'].cat.categories))
        self.realIdToIndex = dict((v,k) for k,v in self.indexToRealId.iteritems())
        self._item_norms = None
        print "init finish"

    @property
    def item_norms(self):
        if self._item_norms is None:
            self._item_norms = np.linalg.norm(self.model.item_factors, axis=-1)
        return self._item_norms

    def recommend(self, actions):
        localFactor = None
        for watchedPid, act in actions.iteritems():
            index = self.realIdToIndex[watchedPid]
            if act == 1:
                if localFactor is None:
                    localFactor = self.model.item_factors[index] * -1
                else:
                    localFactor += self.model.item_factors[index] * -1
            else:
                if localFactor is None:
                    localFactor = self.model.item_factors[index]
                else:
                    localFactor += self.model.item_factors[index]
        if localFactor is None:
            return np.random.choice(self.realIdToIndex.keys())
        localFactor /= len(actions)
        indexs = self.similar_items(localFactor, len(actions) + 1)
        # find first one which not in actions
        for index in indexs:
            pid = self.indexToRealId[index] 
            if pid not in actions:
                return pid

    def similar_items(self, factor, N):
        """ Return the top N similar items for itemid. """
        scores = self.model.item_factors.dot(factor) / self.item_norms / np.linalg.norm(factor, axis = -1)
        best = np.argpartition(scores, -N)[-N:]
        return sorted(best, key=lambda x: -scores[x])

def read_data(host, user, passwd):
    db = MySQLdb.connect(host, user, passwd, "reSystem", charset="utf8")

    sql="select uid as user, pid as artist, rate * 30 as plays from userRates"
    data=pandas.read_sql(sql, db)  

    # map each artist and user to a unique numeric value
    data['user'] = data['user'].astype("category")
    data['artist'] = data['artist'].astype("category")
    # create a sparse matrix of all the users/plays
    plays = coo_matrix((data['plays'].astype(float),
                       (data['artist'].cat.codes.copy(),
                        data['user'].cat.codes.copy())))

    return data, plays

if __name__ == "__main__":

    df, plays = read_data()
    b = ALSEngine(df, plays)
    #uidInfo = dict([("a", (103, 105)),("b", (103, 104)),("c", (104))])
    #pidInfo = dict([(103, (set(["a", "b"]), set())),(104, (set(["c", "b"]), set(["a"]))),(105, (set(["a"]), set(["c"])))])

    print b.recommend(dict())
    print b.recommend(dict([(1296384L, 0)]))
    #print recommendByAction([(103, 1)], uidInfo, pidInfo)
    #print recommendByAction(dict([(105, 0)]), uidInfo, pidInfo)
