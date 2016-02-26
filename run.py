#!/usr/bin/env python

import tileviewer

ts = tileviewer.db.FFTileStore(
    '.', '(?P<row>[0-9]{4})_(?P<col>[0-9]{4})_(?P<camera>[0-9])_m.tif',
    '*_m.tif',
    lambda gd: (int(gd['col'])-1) * 4096 + 2048 * (int(gd['camera']) % 2),
    lambda gd: -((int(gd['row'])-1) * 4096 + 2048 * (int(gd['camera']) / 2)))

tileviewer.server.run(ts, debug=True)
