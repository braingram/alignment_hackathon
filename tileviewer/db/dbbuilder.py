#/usr/bin/env python
"""
Take a file glob string and a file template
and a regex
"""

import glob
import json
import os
import re
import sys

import pymongo

#cname = '140307_rep_grid'
#dregex = 'c0_(?P<x>[-,0-9]*)_(?P<y>[-,0-9]*)_'
dregex = '(?P<x>[-,0-9]*)_(?P<y>[-,0-9]*).tif'
#hfov = 4150
#ddir = '/home/graham/Desktop/140708_temcagt_bg_correction/corrected/ds/*.tif'
ddir = '/home/graham/Desktop/montages/150707153407/processed/ds8/tiles/*.tif'
#ddir = 'tests/tiles/*.tif'
#cname = '140310'
cname = '150707153407'
#dregex = '(?P<x>[0-9]*)_(?P<y>[0-9]*)'
#hfov = 4150
hfov = 486
#hfov = 0.5


def build_tile_spec(fn, regex):
    s = re.search(regex, fn).groupdict()
    x = float(s['x']) * 486
    y = -float(s['y']) * 486
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


def build_json(output_fn, glob_string, regex):
    fns = glob.glob(os.path.expanduser(glob_string))
    print("Found {} files".format(len(fns)))
    docs = [build_tile_spec(fn, regex) for fn in fns]
    with open(output_fn, 'w') as f:
        json.dump(docs, f)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        coll = pymongo.Connection('localhost')[cname]['tiles']
        coll.drop()
        build_database(coll, ddir, dregex)
        map(coll.create_index, (
            'bbox.left', 'bbox.right',
            'bbox.north', 'bbox.south',
            'bbox.top', 'bbox.bottom'))
        print("Resulting database has {} tiles".format(coll.count()))
    else:
        build_json(sys.argv[1], ddir, dregex)
