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

import glob
import os
import re

from . import tilestore
from .. import renderer


class FFTileStore(tilestore.JSONTileStore):
    def __init__(self, directory, regex, wc=None, xeval=None, yeval=None):
        tilestore.JSONTileStore.__init__(self, None)
        self.regex = regex
        if wc is None:
            self.wc = '*'
        else:
            self.wc = wc
        if xeval is None:
            self.xeval = lambda groups: groups['x']
        else:
            self.xeval = xeval

        if yeval is None:
            self.yeval = lambda groups: groups['y']
        else:
            self.yeval = yeval
        self.tiles = []
        self.load_directory(directory)

    def load_directory(self, directory):
        self.directory = directory
        fns = glob.glob(os.path.join(directory, self.wc))
        im_shape = None
        self.tiles = []
        for fn in fns:
            bfn = os.path.basename(fn)
            m = re.match(self.regex, bfn)
            if m is None:
                raise Exception(
                    "Filename %s does not match regex: %s" % (bfn, self.regex))
            gd = m.groupdict()
            if im_shape is None:
                im = renderer.open_image(fn)
                im_shape = im.shape
                del im
            x = self.xeval(gd)
            y = self.yeval(gd)
            ts = {
                'url': {
                    '0': os.path.abspath(fn),
                },
                'bbox': {
                    'left': x,
                    'right': x + im_shape[1],
                    'north': y,
                    'south': y - im_shape[0],
                    'top': 1000,
                    'bottom': 0,
                },
                'filters': [],
                'transforms': [
                    {
                        'name': 'affine',
                        'params': [1., 0., 0., 1., x, y],
                    }
                ]
            }
            self.tiles.append(ts)
        print("{} tiles in tilestore".format(len(self.tiles)))
        self.rebuild_indexes()
