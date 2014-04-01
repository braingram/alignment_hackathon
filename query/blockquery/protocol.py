#!/usr/bin/env python
"""
queries can take the form of:

    v -> version
    b[l,bbox]level{scale}
"""

import json
import re


class QueryError(Exception):
    pass


def parse_bounding_box(s):
    matches = re.findall('\[(.*)\]', s)
    assert len(matches) == 1
    coords = matches[0].split(',')
    assert len(coords) == 5  # l, left, top, w, h
    bbox = [float(c) for c in coords[1:]]
    level = float(coords[0])
    return dict(bbox=bbox, level=level)


class QueryParser(object):
    def __init__(self):
        pass

    def get_version(self):
        return '0.0.0'

    def get_bounding_box(self, s):
        bbq = parse_bounding_box(s)
        images = self.find_images(bbq)
        return json.dumps(images)

    def parse_query(self, s):
        if s[0] == 'v':
            return self.get_version()
        elif s[0] == 'b':
            return self.get_bounding_box(s)
        raise QueryError("Unknown query {}".format(s))

    def find_images(self, bbox):
        """
        Find the image(s) that contains this bounding box
        Each image is a dict of:
            'url': image_url,
            'filters': pre_filters,
            'affine': transform
        """
        raise NotImplementedError
