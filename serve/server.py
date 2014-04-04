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
#tilestore = tilestore.MongoTileStore(db='test', coll='tiles')
#tilestore = tilestore.MongoTileStore(db='140307_rep_grid', coll='tiles')
#tilestore = tilestore.MongoTileStore(db='mbsem', coll='tiles')
tilestore = tilestore.JSONTileStore('mbsem.json')
bounds = {}
bounds['x0'] = tilestore.get_min('bbox.left')
bounds['y0'] = tilestore.get_min('bbox.south')
xs = tilestore.get_max('bbox.right') - bounds['x0']
ys = tilestore.get_max('bbox.north') - bounds['y0']
bounds['xs'] = max(xs, ys)
bounds['ys'] = bounds['xs']
#bounds['xs'] = tilestore.get_max('bbox.right') - bounds['x0']
#bounds['ys'] = tilestore.get_max('bbox.north') - bounds['y0']


def array_to_png(a):
    im = Image.fromarray(a.astype('u1'))
    io = StringIO()
    im.save(io, format='png')
    io.seek(0)
    return io


def test_render_tile(q, s=None):
    if s is None:
        s = tilestore
    q['bbox'] = query_to_bounding_box(q)
    #print("query {}".format(q))
    tiles = s.query(dict(tile=q))
    # render images to a 256 x 256 tile
    return renderer.render_tile(q, tiles, (256, 256))[::-1, :]


def query_to_bounding_box(q):
    ## for rep grid
    #x0 = q.get('x0', 487547)  # min x (nm) of all tiles
    #y0 = q.get('y0', 1987541)  # min y (nm) of all tiles
    #xs = q.get('xs', 26566.)  # x width (nm) of all tiles
    #ys = q.get('ys', 26587.)  # y height (nm) of all tiles
    ## for example files
    x0 = q.get('x0', bounds['x0'])  # min x (nm) of all tiles
    y0 = q.get('y0', bounds['y0'])  # min y (nm) of all tiles
    xs = q.get('xs', bounds['xs'])  # x width (nm) of all tiles
    ys = q.get('ys', bounds['ys'])  # y height (nm) of all tiles
    # 0 -> 1
    # 1 -> 2
    # 2 -> 4
    # 3 -> 8
    # 4 -> 16
    # 5 -> 32
    d = (2. ** q['z'])
    return [
        x0 + xs * (q['x'] / d), x0 + xs * ((q['x'] + 1) / d),
        y0 + ys * ((q['y'] + 1) / d), y0 + xs * (q['y'] / d),
        0, 0]


@app.route('/<int:z>/<int:x>/<int:y>')
def get_tile(x, y, z):
    # z is 1 - 8, 1 is zoomed out
    #z -= 1  # now 0 - 7
    # x & y are [0, (2 **z - 1)]
    # 1 is most zoomed out make 8 most zoomed in
    #print("x:{}, y:{}, z:{}".format(x, y, z))
    #print(flask.request.args)  # TODO log these with logging
    q = dict(x=x, y=y, z=z)
    for k in flask.request.args:
        q[k] = flask.request.args[k]

    q['bbox'] = query_to_bounding_box(q)

    #print("get_tile {}".format(q))
    tiles = tilestore.query(dict(tile=q))
    # render images to a 256 x 256 tile
    rendered_tile = renderer.render_tile(q, tiles, (256, 256))
    if rendered_tile is None:
        return flask.Response(status=404)
    # convert rendered_tile to a png
    # return render result as image
    return flask.send_file(array_to_png(rendered_tile[::-1, :]), 'image/png')


@app.route('/')
def default():
    return flask.render_template('map.html')


def run(*args, **kwargs):
    app.run(*args, **kwargs)


if __name__ == '__main__':
    #run(debug=True)
    import qarg
    import pylab
    args = qarg.get('x[int=0,y[int=0,z[int=0,g(grid')
    if args.grid is None:
        im = test_render_tile(dict(x=args.x, y=args.y, z=args.z))
        pylab.imshow(im)
        pylab.gray()
        pylab.show()
    else:
        pylab.subplot(221)
        im = test_render_tile(dict(x=0, y=0, z=1))
        pylab.imshow(im)
        pylab.gray()
        pylab.subplot(222)
        im = test_render_tile(dict(x=1, y=0, z=1))
        pylab.imshow(im)
        pylab.subplot(223)
        im = test_render_tile(dict(x=0, y=1, z=1))
        pylab.imshow(im)
        pylab.subplot(224)
        im = test_render_tile(dict(x=1, y=1, z=1))
        pylab.imshow(im)
        pylab.show()
