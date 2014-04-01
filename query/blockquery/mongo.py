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
    'transforms': [list of transforms]
    'bbox': ?
    'level': ?

docs:
    'url': <str: image locator>
    'maskUrl': <str: image mask locator>
    'minIntensity': <why?>
    'maxIntensity': <why?>
    'transforms': <[transforms]: of {type, properties}>
    'filters': <list: pre-filters (lens, etc...)>
    'bbox': <[l, r, t, b]: bounds at level>
    'level': <str: level of transform>
    'parent': <link to parent transform>
"""

import random
import time

import pymongo

from . import protocol


class MongoParser(protocol.QueryParser):
    def __init__(self, host='localhost', port=None, db='db', coll='test'):
        protocol.QueryParser.__init__(self)
        self.coll = pymongo.Connection(host, port)[db][coll]

    def find_images(self, bbox):
        # turn this into a mongo query
        q = {'level': bbox['level'], '$or': []}
        # for any point in the bounding box [ulx uly lrx lry]
        # test if in bbox
        q['$or'].append({'$and': [
            {'bbox.left': {'$lte': bbox['bbox'][0]}},
            {'bbox.right': {'$gte': bbox['bbox'][0]}},
            ]})
        q['$or'].append({'$and': [
            {'bbox.left': {'$lte': bbox['bbox'][2]}},
            {'bbox.right': {'$gte': bbox['bbox'][2]}},
            ]})
        q['$or'].append({'$and': [
            {'bbox.top': {'$lte': bbox['bbox'][1]}},
            {'bbox.bototom': {'$gte': bbox['bbox'][1]}},
            ]})
        q['$or'].append({'$and': [
            {'bbox.top': {'$lte': bbox['bbox'][3]}},
            {'bbox.bototom': {'$gte': bbox['bbox'][3]}},
            ]})
        images = [image for image in self.coll.find(q)]
        for image in images:
            del image['_id']
        return images


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
    q = MongoParser()
    q.coll.drop()
    rs = []
    for n in ns:
        fill_database(q.coll, n)
        t0 = time.time()
        q.parse_query('b[0,0,0,0,0]')
        t1 = time.time()
        rs.append(t1 - t0)
    return rs
