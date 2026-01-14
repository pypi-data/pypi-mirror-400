"""Functions for fitting polynomials."""

import numpy as np


def polyfit2d_index(kx, a, b):
    """Returns index of polynomial from the result of :meth:`polyfit2d` for
    :math:`x^{a} y^{b}`.

    Parameters
    ----------
    kx : int
        X polynomial order computed
    a, b : int
        x and y polynomial order
    """
    return b + ((kx + 1) * a)


def polyfit2d_eval(x, y, soln, kx, ky):
    """Evaluate polynomial fit from :meth:`polyfit2d`

    Parameters
    ----------
    x, y: array-like, 1d
        x and y coordinates.
    soln: np.ndarray
        Array of polynomial coefficients.
    kx, ky: int
        Polynomial order in x and y, respectively.
    """
    return np.polynomial.polynomial.polygrid2d(x, y, soln.reshape((kx + 1, ky + 1)))


def polyfit2d_indices(kx, ky):
    """Get indicies of polynomials returned by :meth:`polyfit2d`.

    Parameters
    ----------
    kx, ky: int
        Polynomial order in x and y, respectively.

    Returns
    -------
    indices : array_like
        Array of x^a y^b powers
    """
    coeffs = np.ones((kx + 1, ky + 1))
    return np.array(tuple(np.ndindex(coeffs.shape)), dtype=int)


def polyfit2d(x, y, z, kx, ky, *, order=None, weights=None):
    """Two dimensional polynomial fitting by least squares.
    Fits the functional form f(x,y) = z.

    Parameters
    ----------
    x, y: array-like, 1d
        x and y coordinates.
    z: np.ndarray, 2d
        Surface to fit.
    kx, ky: int
        Polynomial order in x and y, respectively.
    order: int or None
        If None, all coefficients up to maxiumum kx, ky, ie. up to and including x^kx*y^ky, are considered.
        If int, coefficients up to a maximum of kx+ky <= order are considered.
    weight: array_like, 2d
        Weighting to use for fit. Same dimenstions as z

    Returns
    -------
    Return parameters from np.linalg.lstsq.

    soln: np.ndarray
        Array of polynomial coefficients.
    residuals: np.ndarray
    rank: int
    s: np.ndarray

    Notes
    -----
    Resultant fit can be evaluated with :meth:`polyfit2d_eval`.

    Based on code from:
    https://stackoverflow.com/questions/33964913/equivalent-of-polyfit-for-a-2d-polynomial-in-python
    """
    # grid coords
    x, y = np.meshgrid(x, y)
    # coefficient array, up to x^kx, y^ky
    coeffs = np.ones((kx + 1, ky + 1))

    # solve array
    a = np.zeros((coeffs.size, x.size))
    b = np.ravel(z)

    # for each coefficient produce array x^i, y^j
    for index, (j, i) in enumerate(np.ndindex(coeffs.shape)):
        # do not include powers greater than order
        if order is not None and i + j > order:
            arr = np.zeros_like(x)
        else:
            arr = coeffs[i, j] * x ** i * y ** j
        a[index] = arr.ravel()

    if weights is not None:
        W = np.sqrt(weights).ravel()
        a *= W
        b *= W
    # do leastsq fitting and return leastsq result
    return np.linalg.lstsq(a.T, b, rcond=None)
