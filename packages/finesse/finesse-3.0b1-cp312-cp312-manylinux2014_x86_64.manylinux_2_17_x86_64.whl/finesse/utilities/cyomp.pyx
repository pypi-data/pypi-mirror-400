from finesse.cymath.math cimport ceil, floor
from finesse.cymath.math cimport nmin

IF FINESSE3_DISABLE_OPENMP == 0:
    cimport openmp

cpdef int determine_nthreads_even(int pts, int divisor) noexcept nogil:
    """Determine the number of threads to use for a routine
    with an outer loop of size `pts`.

    Parameters
    ----------
    pts : int
        Size of outer loop of routine to be parallelised.

    divisor : int
        Estimate of scaling for number of threads where the
        nominal thread count will then be ``pts // divisor``.

    Returns
    -------
    nthreads : int
        Determined thread count. Or 1 if no openmp support
        available.

    Notes
    -----
    The `divisor` arg defines the nominal number of threads
    via ``nominal = pts // divisor``. Hence, this argument
    should correspond to the best-estimate of multi-threaded
    performance scaling behaviour of the routine to follow.

    The actual value returned will be either unity or an even
    number (depending on values of `pts` and `divisor`) which
    is clipped by the maximum number of threads as given by
    the OpenMP routine ``omp_get_max_threads``.

    If Finesse was compiled without OpenMP support then this
    always returns 1.
    """
    IF FINESSE3_DISABLE_OPENMP == 1:
        return 1
    ELSE:
        # Nominal number of threads as pts // divisor
        cdef int nominal = int(ceil(pts / float(divisor)))
        # If nominal is not unity then ensure it's even
        if nominal != 1:
            nominal = int(2 * floor(nominal / 2.0))

        # Note that if OMP_NUM_THREADS is set then omp_get_max_threads
        # will return the value defined in that variable
        return nmin(nominal, openmp.omp_get_max_threads())
