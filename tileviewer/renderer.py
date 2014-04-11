#!/usr/bin/env python

#from cStringIO import StringIO

import struct

import cv2
try:
    import libtiff
    has_libtiff = True
except ImportError:
    has_libtiff = False
import numpy
#import pylab

from . import profiler


imgs = {}


def open_bmp(fn):
    if fn in imgs:
        return imgs[fn]
    fp = open(fn, 'rb')
    gh = fp.read(14)
    assert gh[:2] == 'BM'
    data_offset = struct.unpack('I', gh[10:])[0]
    h = fp.read(4)
    hs = struct.unpack('I', h)[0]
    h += fp.read(hs - 4)  # read the rest of the header
    if hs == 12:
        height = struct.unpack('H', h[6:8])[0]
        width = struct.unpack('H', h[4:6])[0]
        bits = struct.unpack('H', h[10:12])[0]
        direction = -1
    elif hs in [40, 64, 108, 124]:
        height = struct.unpack('I', h[8:12])[0]
        width = struct.unpack('I', h[4:8])[0]
        bits = struct.unpack('H', h[14:16])[0]
        direction = -1
        if h[11] == '\xff':
            #print "upside down"
            height = (2 ** 32) - height
            #direction = -1  TODO should this be flipped?
    fp.close()
    #print data_offset
    #print height
    #print width
    #print direction
    #print bits
    return numpy.memmap(
        fn, dtype='u{}'.format(bits / 8),
        offset=data_offset, shape=(height, width))[::direction, :]


def open_tif(fn):
    if fn in imgs:
        return imgs[fn]
    #print("Opening file {}".format(fn))
    f = libtiff.TIFFfile(fn)
    im = f.get_tiff_array()[0]
    f.close()
    imgs[fn] = im
    return im


@profiler.timeit
def open_image(fn):
    if '.bmp' in fn.lower():
        return open_bmp(fn)
    if not has_libtiff:
        raise Exception("No libtiff found, only bmp supported")
    return open_tif(fn)


def bbox_to_xyz(bb):
    if isinstance(bb, dict):
        bb = [bb[k] for k in (
            'left', 'right', 'north', 'south', 'top', 'bottom')]
    return [(bb[1] + bb[0]) / 2., (bb[3] + bb[2]) / 2., (bb[5] + bb[4]) / 2.]


def distance(bb0, bb1):
    return numpy.sum(numpy.abs(
        numpy.array(bbox_to_xyz(bb0)) - numpy.array(bbox_to_xyz(bb1))))


def multiply_affines(a, b):
    am = numpy.matrix(numpy.identity(3, dtype='f4'))
    am[:2] = a
    bm = numpy.matrix(numpy.identity(3, dtype='f4'))
    bm[:2] = b
    r = am * bm
    return numpy.array(r[:2], dtype='f4')


def combine_affines(*affines):
    return reduce(multiply_affines, affines)


@profiler.timeit
def render_image(q, image, dims, dst=None):
    # take query bounding box (world coordinates)
    qbb = q['bbox']
    qbb_wpts = [[qbb[0], qbb[2]], [qbb[1], qbb[2]], [qbb[1], qbb[3]]]
    #im_to_q_w = cv2.getAffineTransform(
    #    numpy.array(ibb_wpts, dtype='f4'),
    #    numpy.array(qbb_wpts, dtype='f4'))
    #print("im_to_q_w {}".format(im_to_q_w))
    # affine for world to tile
    tpts = [[0, 0], [dims[0], 0], [dims[0], dims[1]]]
    w_to_t = cv2.getAffineTransform(
        numpy.array(qbb_wpts, dtype='f4'),
        numpy.array(tpts, dtype='f4'))
    #print("w_to_t {}".format(w_to_t))
    # generate affine (2) to lay image (image) onto (world)
    #im = open_tif(image['url']['0'])[::4, ::4]
    im = open_image(image['url']['0'])
    imshape = im.shape
    ipts = [[0, 0], [imshape[1], 0], [imshape[1], imshape[0]]]
    # generate affine (1) to lay image bounding box (world) onto query
    ibb = image['bbox']
    ibb_wpts = [
        [ibb['left'], ibb['north']], [ibb['right'], ibb['north']],
        [ibb['right'], ibb['south']]]
    im_to_w = cv2.getAffineTransform(
        numpy.array(ipts, dtype='f4'),
        numpy.array(ibb_wpts, dtype='f4'))
    #print("im_to_w {}".format(im_to_w))
    # combine affines im_to_w -> im_to_q_w -> q_to_t
    im_to_t = combine_affines(w_to_t, im_to_w)
    #print("im_to_t {}".format(im_to_t))
    md = 1. / max(abs(im_to_t[0, 0]), abs(im_to_t[1, 1]))
    if md > 1:
        s = min(int(md), im.shape[0] / 4, im.shape[1] / 4)
        im_to_t[0, 0] = im_to_t[0, 0] * s
        im_to_t[1, 1] = im_to_t[1, 1] * s
        im = im[::s, ::s]
    # convert image
    # calculate original image bbox to world coordinates
    # convert
    #if dst is None:
    #    return cv2.warpAffine(im.astype('f8'), im_to_t, dims)
    if dst is None:
        return cv2.warpAffine(im, im_to_t, dims)
    return cv2.warpAffine(
        im, im_to_t, dims, dst=dst, borderMode=cv2.BORDER_TRANSPARENT)


@profiler.timeit
def render_tile(q, images, dims):
    # assume a tif for now
    if not len(images):
        return None
    # sort by distance, render far to close
    dists = [distance(im['bbox'], q['bbox']) for im in images]
    dists_images = sorted(zip(dists, images), reverse=True)
    dst = None
    for (d, im) in dists_images:
        dst = render_image(q, im, dims, dst)
    return dst

if __name__ == '__main__':
    import pylab
    # call renderer with something that is 1 tile
    print("-- one tile --")
    q = {'bbox': [0, 1, 0, -1, 0, 0]}
    image = {
        'url': {'0': 'tests/renderer/test.tif'},
        'bbox': {
            'left': 0,
            'right': 1,
            'north': 0,
            'south': -1,
            'top': 0,
            'bottom': 0,
        },
        'transforms': [
            {'name': 'affine', 'params': [1., 0., 0., 1., 0., 0.]}],
    }
    dims = (256, 256)
    dst = render_image(q, image, dims)
    pylab.imshow(dst, vmin=0, vmax=255)
    pylab.gray()
    pylab.show()
    pylab.clf()
    print()
    print("-- power of 2 scaled --")
    q['bbox'] = [0, 2, 0, -2, 0, 0]
    dst = render_image(q, image, dims)
    pylab.imshow(dst, vmin=0, vmax=255)
    pylab.show()
    pylab.clf()
    print()
    print("-- non-power of 2 scaled --")
    q['bbox'] = [0, 2.5, 0, -2.5, 0, 0]
    dst = render_image(q, image, dims)
    pylab.imshow(dst, vmin=0, vmax=255)
    pylab.show()
    pylab.clf()
    print()
    print("-- offset --")
    q['bbox'] = [-0.5, 0.5, 0.5, -0.5, 0, 0]
    dst = render_image(q, image, dims)
    pylab.imshow(dst, vmin=0, vmax=255)
    pylab.show()
    pylab.clf()
    print()
    print("-- offset and scaled --")
    q['bbox'] = [-0.5, 2.5, 0.5, -2.5, 0, 0]
    dst = render_image(q, image, dims)
    pylab.imshow(dst, vmin=0, vmax=255)
    pylab.show()
    pylab.clf()
