#!/usr/bin/env python

from .tilestore import JSONTileStore
try:
    import pymongo
    has_mongo = True
except ImportError:
    has_mongo = False

if has_mongo:
    from .mongotilestore import MongoTileStore


def get_store(loc):
    """
    """
    if loc.split('.')[-1] == 'json':
        return JSONTileStore(loc)
    if loc.split(':')[0] == 'mongo':
        if not has_mongo:
            raise ValueError(
                'mongo store requested {}, pymongo not found'.format(loc))
        tokens = loc.split(':')
        if len(tokens) < 3:
            raise ValueError(
                'invalid mongo store location {}, must have at least '
                'database and collection'.format(loc))
        elif len(tokens) == 3:
            _, db, coll = tokens
            host = 'localhost'
        elif len(tokens) == 4:
            _, host, db, coll = tokens
        elif len(tokens) > 4:
            raise ValueError(
                'invalid mongo store location {}, must only have '
                'mongo:host:database:collection'.format(loc))
        return MongoTileStore(host=host, db=db, coll=coll)
    raise ValueError("Unknown store location {}".format(loc))

__all__ = ['get_store', 'JSONTileStore']
if has_mongo:
    __all__.append('MongoTileStore')
