#!/usr/bin/env python

import sys

import server

if __name__ == '__main__':
    host = 'localhost'
    port = 5555
    debug = False
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) > 3:
        debug = True
    server.run(host=host, port=port, debug=debug)
