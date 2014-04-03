#!/usr/bin/env python
"""
Support general queries for stuff within a bounding box
Returns images
Support tile based queries [x, y, zoom]
Convert tile query to bounding box
Query db for images
Sample and return images
"""

from cStringIO import StringIO

import flask
import Image

try:  # HACK
    from . import tilestore
except:
    import tilestore

try:  # HACK
    from . import renderer
except:
    import renderer


app = flask.Flask('tile server')
tilestore = tilestore.MongoTileStore(db='140307_rep_grid', coll='tiles')


def array_to_png(a):
    im = Image.fromarray(a.astype('u1'))
    io = StringIO()
    im.save(io, format='png')
    io.seek(0)
    return io


@app.route('/<int:z>/<int:x>/<int:y>')
def get_tile(x, y, z):
    # z is 1 - 8, 1 is zoomed out
    z -= 1  # now 0 - 7
    # x & y are [0, (2 **z - 1)]
    # 1 is most zoomed out make 8 most zoomed in
    #print("x:{}, y:{}, z:{}".format(x, y, z))
    #print(flask.request.args)  # TODO log these with logging
    q = dict(x=x, y=y, z=z)
    for k in flask.request.args:
        q[k] = flask.request.args[k]
    q['h'] = float(q.get('h', 1))
    q['w'] = float(q.get('w', 1))
    q['d'] = float(q.get('d', 0))
    x0 = q.get('x0', 487547)  # min x (nm) of all tiles
    y0 = q.get('y0', 1987541)  # min y (nm) of all tiles
    #z0 = q.get('z0', 0)
    xs = q.get('xs', 26566.)  # x width (nm) of all tiles
    ys = q.get('ys', 26587.)  # y height (nm) of all tiles
    #zs = q.get('zs', 1.)
    #q['scale'] = 9 - z
    # convert tile query into tile spec
    d = 2. ** z
    q['bbox'] = [
        x0 + xs * (x / d), x0 + xs * ((x + 1) / d),
        y0 + ys * ((y + 1) / d), y0 + xs * (y / d),
        0, 0]
    #q['bbox'] = [
    #    x0 + xs * (x - q['w'] / 2.), x0 + xs * (x + q['w'] / 2.),
    #    y0 + ys * (y + q['h'] / 2.), y0 + ys * (y - q['h'] / 2.),
    #    0, 0]
        #z0 + zs * (z + q['d'] / 2.), z0 + zs * (z - q['d'] / 2.)]
    print("get_tile {}".format(q))
    tiles = tilestore.query(dict(tile=q))
    # render images to a 256 x 256 tile
    rendered_tile = renderer.render_tile(q, tiles, (256, 256))
    if rendered_tile is None:
        return flask.Response(status=404)
    # convert rendered_tile to a png
    # return render result as image
    return flask.send_file(array_to_png(rendered_tile), 'image/png')


@app.route('/')
def default():
    return flask.render_template('map.html')


def run(*args, **kwargs):
    app.run(*args, **kwargs)


if __name__ == '__main__':
    run(debug=True)
