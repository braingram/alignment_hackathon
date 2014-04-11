#!/usr/bin/env python

import time

times = {}
ns = {}


def timeit(f):
    def w(*args, **kwargs):
        t0 = time.time()
        r = f(*args, **kwargs)
        t1 = time.time()
        times[f.__name__] = times.get(f.__name__, 0) + t1 - t0
        ns[f.__name__] = ns.get(f.__name__, 0.) + 1
        print("{} took {:0.6f}[{:0.6f}] seconds".format(
            f.__name__, times[f.__name__] / ns[f.__name__], t1 - t0))
        return r
    w.__name__ = f.__name__
    w.__doc__ = f.__doc__
    return w
