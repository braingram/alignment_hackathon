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

import pymongo

from . import tilestore


class MongoTileStore(tilestore.TileStore):
    def __init__(self, host='localhost', port=None, db='db', coll='test'):
        tilestore.TileStore.__init__(self)
        self.coll = pymongo.Connection(host, port)[db][coll]
        print("{} tiles in tilestore".format(self.coll.count()))

    def tile_query(self, q):
        #return [self.coll.find_one({}), ]
        mq = {}  # build a mongo query
        if 'level' in q:
            mq['level'] = q['level']
        assert len(q['bbox']) == 6
        # left, right, north, south, top, bottom
        l, r, n, s, t, b = q['bbox']
        mq['bbox.left'] = {'$lte': r}
        mq['bbox.right'] = {'$gte': l}
        mq['bbox.north'] = {'$gte': s}
        mq['bbox.south'] = {'$lte': n}
        mq['bbox.top'] = {'$gte': b}
        mq['bbox.bottom'] = {'$lte': t}
        print("querying db with {}".format(mq))
        tiles = [tile for tile in self.coll.find(mq)]
        print("found {} tiles".format(len(tiles)))
        for t in tiles:
            del t['_id']
        return tiles

    def get_max(self, k):
        cursor = self.coll.find({}, {k: True}).sort(k, -1).limit(1)
        d = cursor.next()
        return reduce(lambda x, y: x[y], k.split('.'), d)

    def get_min(self, k):
        cursor = self.coll.find({}, {k: True}).sort(k, 1).limit(1)
        d = cursor.next()
        return reduce(lambda x, y: x[y], k.split('.'), d)
