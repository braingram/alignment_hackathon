#!/usr/bin/env python

import json

import cv2
import libtiff
import numpy
import pylab

import qarg


args = qarg.get(
    'i(input=test.tif,t(transform,H(height[int=100,W(width[int=100')
print(args)
if args.transform is None:
    args.transform = [[1., 0., 0.], [0., 1., 0.]]
else:
    args.transform = json.loads(args.transform)


def load_image(fn):
    if '.tif' in fn.lower():
        f = libtiff.TIFFfile(fn)
        im = f.get_tiff_array()[0]
        f.close()
        return im
    return cv2.imread(fn, -1)


# create canvas
# load image
im = load_image(args.input)
# paste transformed image (can this be done in one step?
r = cv2.warpAffine(
    im, numpy.array(args.transform).astype('f8'),
    (args.width, args.height))
# return image
pylab.imshow(r)
pylab.gray()
pylab.show()
