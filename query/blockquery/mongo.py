#!/usr/bin/env python
"""
queries can take the form of:

    v -> version
    b[l,bbox]level{scale}
"""

import pymongo

from . import protocol


class MongoParser(protocol.QueryParser):
    def __init__(self, host='localhost', port=None, db='db', coll='test'):
        protocol.QueryParser.__init__(self)
        self.conn = pymongo.Connection(host, port)[db][coll]

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
        images = [image for image in self.conn.find(q)]
        for image in images:
            del image['_id']
        return images
