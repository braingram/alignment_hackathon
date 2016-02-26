#!/usr/bin/env python

import sys

import tileviewer

directory = '.'
host = None
port = None

if len(sys.argv) > 1:
    directory = sys.argv[1]
if len(sys.argv) > 2:
    host = sys.argv[2]
if len(sys.argv) > 3:
    port = int(sys.argv[3])

ts = tileviewer.db.FFTileStore(
    directory,
    '(?P<row>[0-9]{4})_(?P<col>[0-9]{4})_(?P<camera>[0-9])_m.tif', '*_m.tif',
    lambda gd: (int(gd['col'])-1) * 4096 + 2048 * (int(gd['camera']) % 2),
    lambda gd: -((int(gd['row'])-1) * 4096 + 2048 * (int(gd['camera']) / 2)))

tileviewer.server.run(ts, host=host, port=port, debug=True)
