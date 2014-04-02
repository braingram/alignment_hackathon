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
tilestore = tilestore.MongoTileStore(db='140307_rep_grid', coll='tiles')


@app.route('/<int:z>/<int:x>/<int:y>')
def get_tile(x, y, z):
    print("x:{}, y:{}, z:{}".format(x, y, z))
    print(flask.request.args)  # TODO log these with logging
    q = dict(x=x, y=y, z=z)
    for k in flask.request.args:
        q[k] = flask.request.args[k]
    h = float(q.get('h', 100000))
    w = float(q.get('w', 100000))
    d = float(q.get('d', 100000))
    # convert tile query into tile spec
    q['bbox'] = [
        x - w / 2., x + w / 2.,
        y - h / 2., y + h / 2.,
        z - d / 2., z + d / 2.]
    print(q)
    tiles = tilestore.query(dict(tile=q))
    return flask.jsonify(dict(tiles=tiles))


@app.route('/')
def default():
    return flask.Response()


def run(*args, **kwargs):
    app.run(*args, **kwargs)


if __name__ == '__main__':
    run(debug=True)
