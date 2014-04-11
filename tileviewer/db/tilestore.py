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

import json

import numpy

from .. import profiler


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
        # section [id?]
        # level
        raise NotImplementedError("tile_query not implemented in DataStore")

    def get_max(self, k):
        raise NotImplementedError("get_max not implemented in DataStore")

    def get_min(self, k):
        raise NotImplementedError("get_min not implemented in DataStore")


@profiler.timeit
def find(tiles, indexes, bbox):
    # nieve find TODO time this, speed it up
    m = indexes['bbox.left'] <= bbox[1]
    m = numpy.logical_and(m, indexes['bbox.right'] >= bbox[0])
    if not numpy.any(m):  # shortcut exit for no finds
        return []
    m = numpy.logical_and(m, indexes['bbox.north'] >= bbox[3])
    m = numpy.logical_and(m, indexes['bbox.south'] <= bbox[2])
    if not numpy.any(m):
        return []
    m = numpy.logical_and(m, indexes['bbox.top'] >= bbox[5])
    m = numpy.logical_and(m, indexes['bbox.bottom'] <= bbox[4])
    if not numpy.any(m):
        return []
    #print numpy.where(m)
    return [tiles[i] for i in numpy.where(m)[0]]


class JSONTileStore(TileStore):
    def __init__(self, fn):
        TileStore.__init__(self)
        # load tiles from json
        with open(fn, 'r') as f:
            self.tiles = json.load(f)
        # index by several keys
        self.indexes = {}
        for k in ['bbox.left', 'bbox.right', 'bbox.north',
                  'bbox.south', 'bbox.top', 'bbox.bottom']:
            self.indexes[k] = numpy.array(
                [reduce(lambda x, y: x[y], k.split('.'), t)
                 for t in self.tiles])

    def tile_query(self, q):
        return find(self.tiles, self.indexes, q['bbox'])

    def get_max(self, k):
        return self.indexes[k].max()

    def get_min(self, k):
        return self.indexes[k].min()
