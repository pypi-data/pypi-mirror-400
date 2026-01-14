def clip_with_tolerance(
    number: float, _min: float, _max: float, tol: float = 1e-12
) -> float:
    """Clips a number to the range [_min, _max] if it is in [_min - tol, _max + tol],
    otherwise just returns the number.

    Useful for correcting numerical precision errors after calculating physical
    quantities.

    Parameters
    ----------
    number : float
        Number to clip
    _min : float
        lower end of clipping range
    _max : float
        higher end of clipping range
    tol : float, optional
        Absolute tolerance, by default 1e-12

    Returns
    -------
    float
        The clipped number
    """
    if number < _min and (number + tol) > _min:
        return _min
    elif number > _max and (number - tol) < _max:
        return _max
    else:
        return number
