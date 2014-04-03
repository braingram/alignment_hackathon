#!/usr/bin/env python

#from cStringIO import StringIO

import cv2
import libtiff
import numpy
#import pylab


def open_tif(fn):
    f = libtiff.TIFFfile(fn)
    im = f.get_tiff_array()[0]
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


def render_image(q, image, dims, dst=None):
    #r = cv2.warpAffine(
    #    im, numpy.array(args.transform).astype('f8'),
    #    (args.width, args.height))
    # calculate how much to downsample this
    # TODO don't assume square bounding box?
    world_units_per_pixel = (q['bbox'][1] - q['bbox'][0]) / float(dims[0])
    print("world_units_per_pixel {}".format(world_units_per_pixel))
    # TODO handle multi-scale data
    urls = image['url']
    im = open_tif(urls['0'])
    im_units_per_pixel = (
        image['bbox']['right'] - image['bbox']['left']) / float(im.shape[0])
    print("im_units_per_pixel {}".format(im_units_per_pixel))
    scale_ratio = world_units_per_pixel / im_units_per_pixel
    closest_2 = int(numpy.log2(scale_ratio))
    imds = 2 ** closest_2
    im = im[::-imds, ::imds]
    remaining_scale = scale_ratio / float(imds)
    print("im shape {}".format(im.shape))
    print("scale_ratio {}".format(scale_ratio))
    print("closest_2 {}".format(closest_2))
    print("imds {}".format(imds))
    print("remaining_scale {}".format(remaining_scale))
    # find closest power of 2 rescale
    t = numpy.array(
        image['transforms'][0]['params']).astype('f8')
    # reorder this
    t = numpy.array([[t[0], t[1], t[4]], [t[2], t[3], t[5]]])
    s = numpy.array([
        [1. / remaining_scale, 1., 1. / world_units_per_pixel],
        [1., 1. / remaining_scale, -1. / world_units_per_pixel]])
    o = numpy.array(
        [[0., 0., q['bbox'][0]],
         [0., 0., q['bbox'][2]]])
    T = ((t - o) * s).astype('f8')
    print("Rendering image {}".format(image))
    print("\tfrom query {}".format(q))
    print("\twith transform {}".format(T))
    print("\t\traw {}".format(t))
    print("\t\toffset {}".format(o))
    print("\t\tscaled {}".format(s))
    print(T)
    if dst is None:
        return cv2.warpAffine(im.astype('f8'), T, dims)
    return cv2.warpAffine(im.astype('f8'), T, dims, dst)


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
