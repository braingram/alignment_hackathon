#!/usr/bin/env python

from cStringIO import StringIO

import libtiff
import numpy
import pylab


def open_tif(fn):
    f = libtiff.TIFFfile(fn)
    im = f.get_tiff_array()[0][::8, ::8]
    f.close()
    return im


def bbox_to_xyz(bb):
    if isinstance(bb, dict):
        bb = [bb[k] for k in (
            'left', 'right', 'north', 'south', 'top', 'bottom')]
    return [(bb[1] + bb[0]) / 2., (bb[3] + bb[2]) / 2., (bb[5] + bb[4]) / 2.]


def distance(bb0, bb1):
    return numpy.sum(numpy.abs(
        numpy.array(bbox_to_xyz(bb0)) - numpy.array(bbox_to_xyz(bb1))))


def render_tile(q, images, dims):
    # assume a tif for now
    if not len(images):
        return None
    # find closest image
    dists = [distance(im['bbox'], q['bbox']) for im in images]
    scale = str(q.get('scale', 0))
    im = open_tif(
        images[min(xrange(len(dists)), key=lambda i: dists[i])]['url'][scale])
    #im = open_tif(images[0]['url'][str(q.get('scale', 0))])
    io = StringIO()
    #pylab.imshow(im)
    #pylab.savefig(io, format='png')
    pylab.gray()
    pylab.imsave(io, im, format='png')
    io.seek(0)
    return io
    #return im.tostring()
