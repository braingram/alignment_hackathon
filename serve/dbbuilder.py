#!/usr/bin/env python
"""
Take a file glob string and a file template
and a regex
"""

import glob
import os
import re

import pymongo

ddir = '~/Desktop/montages/140307_1120_zxy_rep_grid_small/*.tif'
dregex = 'c0_(?P<x>[0-9]*)_(?P<y>[0-9]*)_'


def build_tile_spec(fn, regex):
    s = re.search(regex, fn).groupdict()
    s['x'] = int(s['x'])
    s['y'] = int(s['y'])
    s['url'] = {"0": fn}
    s['bbox'] = [
        s['x'] - 4150, s['x'] + 4150,
        s['y'] - 4150, s['y'] + 4150,
        1000, 0]
    s['filters'] = []  # TODO build lens correction filter, etc
    s['transforms'] = []  # TODO build linear transform
    s['level'] = 'raw'
    s['parent'] = 0
    s['minIntensity'] = 0
    s['maxIntensity'] = 65535
    return s


def build_database(coll, glob_string, regex):
    fns = glob.glob(os.path.expanduser(glob_string))
    for fn in fns:
        d = build_tile_spec(fn, regex)
        print("Tilespec built for fn: {} = {}".format(fn, d))
        coll.insert(d)


if __name__ == '__main__':
    coll = pymongo.Connection('localhost')['140307_rep_grid']['tiles']
    coll.drop()
    build_database(coll, ddir, dregex)
    map(coll.create_index, (
        'bbox.left', 'bbox.right',
        'bbox.north', 'bbox.south',
        'bbox.top', 'bbox.bottom'))
    print("Resulting database has {} tiles".format(coll.count()))
