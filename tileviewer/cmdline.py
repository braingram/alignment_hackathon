#!/usr/bin/env python

import sys

from . import server


def run(args=None):
    if args is None:
        args = sys.argv[1:]
    if len(args) < 1:
        raise ValueError("tilestore location must be supplied")
    ts = args[0]
    if len(args) > 1:
        host = args[1]
    else:
        host = '0.0.0.0'
    if len(args) > 2:
        port = int(args[2])
    else:
        port = 5000
    if len(args) > 3:
        debug = True
    else:
        debug = False
    server.run(ts, host=host, port=port, debug=debug)
