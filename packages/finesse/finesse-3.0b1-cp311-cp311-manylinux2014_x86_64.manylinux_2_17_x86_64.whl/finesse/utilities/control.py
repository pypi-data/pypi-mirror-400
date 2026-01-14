"""Control system functions."""

import numpy as np
from numpy.polynomial.polynomial import polyvalfromroots


def zpk_fresp(zs, ps, k, w):
    """Evaluate the frequency response of a zpk filter.

    The evaluation is done by multiplying the poles and zeros in pairs which is
    more numerically stable than multiplying all of the zeros and then dividing
    by all of the poles as is done with other tools when there are a large number
    of zeros and poles.

    Parameters
    ----------
    zs : array
        zeros of the filter
    ps : array
        poles of the filter
    k : float
        gain of the filter
    w : array
        frequencies at which to compute the filter
    """
    zs = np.atleast_1d(zs)
    ps = np.atleast_1d(ps)
    s = 1j * w
    tf = k * np.ones_like(s)
    minlen = min(len(zs), len(ps))
    # first multiply the poles and zeros in pairs
    for z, p in zip(zs[:minlen], ps[:minlen]):
        tf *= (s - z) / (s - p)
    # then multiply the remaining poles or zeros
    return tf * polyvalfromroots(s, zs[minlen:]) / polyvalfromroots(s, ps[minlen:])
