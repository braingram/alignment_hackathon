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

try:
    import pymongo
except ImportError as e:
    no_pymongo = True

#cname = '140307_rep_grid'
#dregex = 'c0_(?P<x>[-,0-9]*)_(?P<y>[-,0-9]*)_'
dregex = '(?P<x>[-,0-9]*)_(?P<y>[-,0-9]*).tif'
#hfov = 4150
#ddir = '/home/graham/Desktop/140708_temcagt_bg_correction/corrected/ds/*.tif'
cname = '150715144606'
if len(sys.argv) > 1 and 'json' not in sys.argv[1]:
    cname = sys.argv[1]
    del sys.argv[1]
#cname = '150715084319'
#ddir = '/home/graham/Desktop/montages/150707153407/processed/ds8/tiles/*.tif'
ddir = '/home/graham/montages/{}/processed/ds8/tiles/*.tif'.format(cname)
#ddir = 'tests/tiles/*.tif'
#cname = '140310'
#cname = '150707153407'
#dregex = '(?P<x>[0-9]*)_(?P<y>[0-9]*)'
#hfov = 4150
hfov = 486
vfov = 468
#hfov = 0.5

#ydx = 33.5
#ydy = -56
#xdx = 56
#xdy = -33.6

ydx = 67
ydy = -112
xdx = 112
xdy = 67

mask = 'image_mask.tif'




def build_tile_spec(fn, regex):
    s = re.search(regex, fn).groupdict()
    x = (-float(s['x']) * hfov) + float(s['x']) * xdx + float(s['y']) * ydx
    y = (float(s['y']) * vfov) + float(s['x']) * xdy + float(s['y']) * ydy
    print fn, s, x, y
    #x = float(s['x']) * 486
    #y = -float(s['y']) * 486
    if mask is not None:
        s['mask'] = mask
    s['url'] = {"0": os.path.abspath(fn)}
    s['bbox'] = {
        'left': x,
        'right': x + hfov,
        'north': y + vfov,
        'south': y,
        #'left': x - hfov,
        #'right': x + hfov,
        #'north': y + hfov,
        #'south': y - hfov,
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
    if len(sys.argv) < 2 and not no_pymongo:
        coll = pymongo.Connection('localhost')[cname]['tiles']
        coll.drop()
        build_database(coll, ddir, dregex)
        map(coll.create_index, (
            'bbox.left', 'bbox.right',
            'bbox.north', 'bbox.south',
            'bbox.top', 'bbox.bottom'))
        print("Resulting database has {} tiles".format(coll.count()))
    else:
        if len(sys.argv) > 1:
            ofn = sys.argv[1]
        else:
            ofn = '{}.json'.format(cname)
        build_json(ofn, ddir, dregex)
