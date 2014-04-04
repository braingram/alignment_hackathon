#!/usr/bin/env python
"""
Take a file glob string and a file template
and a regex
"""

import glob
import json
import os
import re
import sys

import numpy
try:
    import pymongo
    has_pymongo = True
except ImportError:
    has_pymongo = False

#cname = '140307_rep_grid'
#dregex = 'c0_(?P<x>[0-9]*)_(?P<y>[0-9]*)_'
#hfov = 4150
#ddir = 'tests/tiles/*.tif'
#cname = 'test'
#dregex = '(?P<x>[0-9]*)_(?P<y>[0-9]*)'
#hfov = 0.5
ddir = '~/Desktop/multisem_140314/*/[!t]*.bmp'
cname = 'mbsem'
dregex = '/(?P<tile>[0-9]*)_(?P<sub>[0-9]*)'

md = {}


def build_tile_spec(fn, regex):
    s = re.search(regex, fn).groupdict()
    # load meta data
    dfn = os.path.dirname(fn)
    mfn = os.path.join(dfn, 'pixelCoordinates.txt')
    if mfn not in md:
        md[mfn] = numpy.loadtxt(
            mfn, dtype=[('fn', 'S32'), ('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
    tmd = md[mfn][md[mfn]['fn'] == os.path.basename(fn)]
    x = float(tmd['x'])
    y = float(tmd['y'])
    hfov = 3340
    vfov = 2980
    s['url'] = {'0': os.path.abspath(fn)}
    s['bbox'] = {
        'left': x,
        'right': x + hfov,
        'north': y,
        'south': y - vfov,
        'top': 1000,
        'bottom': 0,
    }
    s['filters'] = []  # TODO build lens correction filter, etc
    #s['x'] = int(s['x'])
    #s['y'] = int(s['y'])
    s['transforms'] = [
        {
            'name': 'affine',
            'params': [1., 0., 0., 1., x, y],
        },
    ]
    s['level'] = 'raw'
    s['parent'] = 0
    s['minIntensity'] = 0
    s['maxIntensity'] = 255
    return s


def build_database(coll, glob_string, regex):
    fns = glob.glob(os.path.expanduser(glob_string))
    for fn in fns:
        d = build_tile_spec(fn, regex)
        print("Tilespec built for fn: {} = {}".format(fn, d))
        coll.insert(d)


def build_json(fn, glob_string, regex):
    fns = glob.glob(os.path.expanduser(glob_string))
    docs = [build_tile_spec(fn, regex) for fn in fns]
    with open(fn, 'w') as f:
        json.dump(docs, f)


if __name__ == '__main__':
    if has_pymongo:
        coll = pymongo.Connection('localhost')[cname]['tiles']
        coll.drop()
        build_database(coll, ddir, dregex)
        map(coll.create_index, (
            'bbox.left', 'bbox.right',
            'bbox.north', 'bbox.south',
            'bbox.top', 'bbox.bottom'))
        print("Resulting database has {} tiles".format(coll.count()))
    else:
        assert len(sys.argv) > 1, "Filename must be supplied"
        build_json(sys.argv[1], ddir, dregex)
