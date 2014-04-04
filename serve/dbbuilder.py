#!/usr/bin/env python
"""
Take a file glob string and a file template
and a regex
"""

import glob
import os
import re

import pymongo

#cname = '140307_rep_grid'
#dregex = 'c0_(?P<x>[0-9]*)_(?P<y>[0-9]*)_'
#hfov = 4150
ddir = 'tests/tiles/*.tif'
cname = 'test'
dregex = '(?P<x>[0-9]*)_(?P<y>[0-9]*)'
hfov = 0.5


def build_tile_spec(fn, regex):
    s = re.search(regex, fn).groupdict()
    x = float(s['x'])
    y = float(s['y'])
    s['url'] = {"0": os.path.abspath(fn)}
    s['bbox'] = {
        'left': x - hfov,
        'right': x + hfov,
        'north': y + hfov,
        'south': y - hfov,
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
        #print("Tilespec built for fn: {} = {}".format(fn, d))
        coll.insert(d)


if __name__ == '__main__':
    coll = pymongo.Connection('localhost')[cname]['tiles']
    coll.drop()
    build_database(coll, ddir, dregex)
    map(coll.create_index, (
        'bbox.left', 'bbox.right',
        'bbox.north', 'bbox.south',
        'bbox.top', 'bbox.bottom'))
    print("Resulting database has {} tiles".format(coll.count()))
