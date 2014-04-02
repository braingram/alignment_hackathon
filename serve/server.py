#!/usr/bin/env python
"""
Support general queries for stuff within a bounding box
Returns images
Support tile based queries [x, y, zoom]
Convert tile query to bounding box
Query db for images
Sample and return images
"""

import copy

import flask

try:  # HACK
    from . import tilestore
except:
    import tilestore


app = flask.Flask('tile server')
tilestore = tilestore.MongoTileStore()


@app.route('/<int:z>/<int:x>/<int:y>')
def get_tile(x, y, z):
    print("x:{}, y:{}, z:{}".format(x, y, z))
    print(flask.request.args)  # TODO log these with logging
    q = copy.deepcopy(flask.request.args)
    q['x'] = x
    q['y'] = y
    q['z'] = z
    imgs = tilestore.query(q)
    # convert tile query into tile spec
    return flask.jsonify(imgs)


@app.route('/')
def default():
    return flask.Response()


def run(*args, **kwargs):
    app.run(*args, **kwargs)


if __name__ == '__main__':
    run()
