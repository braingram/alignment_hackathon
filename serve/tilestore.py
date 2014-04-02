#!/usr/bin/env python
"""
queries can take the form of:

    v -> version
    b[l,bbox]level{scale}

document spec:
    'url': image url
    'maskUrl' : mask url
    'minIntensity': ?
    'maxIntensity': ?
    'transforms': [list of transforms, {name, params}]
    'bbox': ?
    'level': ?

docs:
    '_id': unique ID
    'url': <str: image locator>
    'maskUrl': <str: image mask locator>
    'minIntensity': <why?>
    'maxIntensity': <why?>
    'transforms': <[transforms]: of {type, properties}>
    'filters': <list: pre-filters (lens, etc...)>
    'bbox': <[l, r, t, b]: bounds at level> [only at level 0]
    'level': <str: level of transform>
    'parent': <id of parent transform>
"""

import random
import time

import pymongo


class TileStore(object):
    def __init__(self):
        self.version = '0.0.0'

    def query(self, q):
        if 'version' in q:
            return self.version
        if 'tile' in q:
            return self.tile_query(q['tile'])
        raise Exception("Unknown query {}".format(q))

    def tile_query(self, q):
        # bbox x y z
        # scale
        # section [id?] [ this is in z
        # level
        raise NotImplementedError("tile_query not implemented in DataStore")


class MongoTileStore(TileStore):
    def __init__(self, host='localhost', port=None, db='db', coll='test'):
        TileStore.__init__(self)
        self.coll = pymongo.Connection(host, port)[db][coll]

    def tile_query(self, q):
        mq = {}  # build a mongo query
        if 'level' in q:
            mq['level'] = q['level']
        mq['scale'] = q.get('scale', 0)
        assert mq['scale'] >= 0
        # todo scale bounding box for scale
        assert len(q['bbox']) == 6
        if mq['scale'] == 0:
            # left, right, north, south, top, bottom
            l, r, n, s, t, b = q['bbox']
        else:
            scale = 2 ** mq['scale']
            l, r, n, s, t, b = [i * scale for i in q['bbox']]
        mq['$or'] = [
            {'bbox.left': {'$lte': l}, 'bbox.right': {'$gte': l}},
            {'bbox.left': {'$lte': r}, 'bbox.right': {'$gte': r}},
            {'bbox.north': {'$lte': n}, 'bbox.south': {'$gte': n}},
            {'bbox.north': {'$lte': s}, 'bbox.south': {'$gte': s}},
            {'bbox.top': {'$lte': t}, 'bbox.top': {'$gte': t}},
            {'bbox.bottom': {'$lte': b}, 'bbox.bottom': {'$gte': b}},
        ]
        return [image for image in self.coll.find(mq)]


def fill_database(c, n=1000, drop=False):
    if drop:
        c.drop()
    for i in xrange(n):
        x, y = random.random(), random.random()
        w, h = random.random(), random.random()
        level = str(random.randint(0, 4))
        d = {
            'url': '/images/{}'.format(i),
            'maskUrl': '/masks/{}'.format(i),
            'transforms': [],
            'filters': [],
            'bbox': dict(left=x, right=x+w, top=y, bottom=y+h),
            'level': level,
            'parent': ''
        }
        c.insert(d)
    c.reindex()


def time_queries(ns=None):
    if ns is None:
        ns = [100, 900, 9000, 900000, 9000000]
    q = MongoTileStore()
    q.coll.drop()
    rs = []
    for n in ns:
        fill_database(q.coll, n)
        t0 = time.time()
        q.parse_query('b[0,0,0,0,0]')
        t1 = time.time()
        rs.append(t1 - t0)
    return rs
