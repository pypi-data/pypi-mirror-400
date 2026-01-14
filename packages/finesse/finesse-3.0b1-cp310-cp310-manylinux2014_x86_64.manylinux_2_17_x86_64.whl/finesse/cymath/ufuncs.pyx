"""Numpy ufuncs for custom functions that support numeric and symbolic arguments.

See https://cython.readthedocs.io/en/latest/src/userguide/fusedtypes.html for more
information on fused types.
"""
cimport cython
from scipy.special.cython_special cimport jv as _jv

ctypedef fused numeric_or_object:
    float
    double
    object


@cython.ufunc
cdef numeric_or_object jv(numeric_or_object v, numeric_or_object x):
    """
        Calculate the Bessel function of the first kind of order v at x. Internally this
        evaluates using the scipy.special.jv function.

        Parameters
        ----------
        v : numeric_or_object
            The order of the Bessel function. It should be a numeric object, such as an integer or a float.
        x : numeric_or_object
            The argument at which to evaluate the Bessel function. It should also be a numeric object.

        Returns
        -------
        result : [double | float | object]
            The value of the Bessel function at the given order and argument.
        """
    if numeric_or_object is object:
        # If we're applying to symbolic arguments then just return a symbolic function
        from finesse.symbols import FUNCTIONS
        return FUNCTIONS['jv'](v, x)
    else:
        return _jv(v, x)
