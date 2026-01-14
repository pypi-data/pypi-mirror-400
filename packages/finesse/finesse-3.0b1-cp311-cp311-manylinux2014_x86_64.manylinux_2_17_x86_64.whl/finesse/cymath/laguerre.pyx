import numpy as np
cimport numpy as np
from scipy.special import factorial, eval_genlaguerre


cdef extern from "constants.h":
    long double PI
    long double ROOT2


cdef struct Workspace:
    int p           # Radial index
    int l           # Azimuthal index
    int abs_l       # Absolute of azimuthal index
    int order       # Order of LG mode
    double w0       # Beam waist
    double z        # Propagation distance
    double k        # Wave number (2*PI/lambda)
    double wz       # Beam radius at z
    double Rz       # Radius of curvature at z
    double Gouy     # Gouy phase at z
    double amplitude # Precomputed amplitude factor


cdef initialize_workspace(Workspace *ws, int p, int l, double w0, double z, double wavelength):
    """Initialize the workspace and precompute values that do not change.

    Parameters
    ----------
    ws : Pointer to Workspace struct
        The workspace to be initialized.
    p : int
        Radial index.
    l : int
        Azimuthal index.
    w0 : float
        Beam waist.
    z : float
        Propagation distance.
    wavelength : float
        Wavelength of the beam.
    """
    ws.p = p
    ws.l = l
    ws.abs_l = abs(l)
    ws.w0 = w0
    ws.z = z
    ws.k = 2 * PI / wavelength
    ws.order = 2 * p + ws.abs_l

    # Compute derived values
    cdef double zR = (PI * w0**2) / wavelength  # Rayleigh range
    ws.wz = w0 * np.sqrt(1 + (z / zR)**2)
    ws.Rz = float("inf") if z == 0 else z * (1 + (zR / z)**2)
    ws.Gouy = np.arctan(z / zR)
    ws.amplitude = 1/ ws.wz
    ws.amplitude *= np.sqrt(2 * factorial(p) / (PI * factorial(p + abs(l))))


cdef double complex lg_mode(Workspace *ws, double x, double y, bint is_helical):
    """Calculate the value of the Laguerre-Gaussian mode at a given point (x, y).

    Parameters
    ----------
    ws : Workspace *
        A pointer to the workspace structure containing necessary parameters and precomputed values.
    x : double
        The x-coordinate at which to evaluate the Laguerre-Gaussian mode.
    y : double
        The y-coordinate at which to evaluate the Laguerre-Gaussian mode.
    is_helical : bool
        True if this is a helical LG mode, False for Sinusoidal

    Returns
    -------
    double complex
        The value of the Laguerre-Gaussian mode at the specified (x, y) coordinates.

    """
    cdef double r = np.sqrt(x**2 + y**2)
    cdef double theta = np.arctan2(y, x)
    cdef double rho = (2 * r**2) / (ws.wz**2)
    cdef double L_lp = eval_genlaguerre(ws.p, ws.abs_l, rho)

    cdef double phase = (
        (ws.k * r**2) / (2 * ws.Rz)
        - ws.Gouy * (ws.order + 1)
    )

    if is_helical:
        phase += - ws.l * theta

    cdef double complex LG = (
        (r * ROOT2 / ws.wz)**ws.abs_l
        * L_lp
        * np.exp(-rho / 2 + 1j * phase)
    )

    if not is_helical:
        LG *= ROOT2 * np.cos(ws.abs_l * theta)

    return ws.amplitude * LG


def compute_lg_mode(
    int p,
    int l,
    double w0,
    double z,
    double wavelength,
    np.ndarray[double, ndim=1] x,
    np.ndarray[double, ndim=1] y,
    helical=True,
) -> np.ndarray[np.complex128]:
    """Compute a Laguerre-Gaussian mode.

    Parameters
    ----------
    p : int
        Radial index of the Laguerre-Gaussian mode.
    l : int
        Azimuthal index of the Laguerre-Gaussian mode.
    w0 : double
        Beam waist.
    z : double
        Propagation distance.
    wavelength : double
        Wavelength of the beam.
    x : np.ndarray[double, ndim=1]
        Array of x-coordinates.
    y : np.ndarray[double, ndim=1]
        Array of y-coordinates.
    helical : bool
        True if this is a helical LG mode, False for Sinusoidal

    Returns
    -------
    np.ndarray[np.complex128]
        2D array of complex values representing the Laguerre-Gaussian mode at the given coordinates.

    Examples
    --------

    >>> import finesse
    >>> from finesse.cymath import laguerre as lg
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> finesse.init_plotting()
    >>>
    >>> fig, axes = plt.subplots(3, 3, figsize=(8, 8))
    >>>
    >>>  w0 = 1e-3
    >>>  z = 0
    >>>  x = np.linspace(-4 * w0, +4 * w0, 50)
    >>>  y = np.linspace(-4 * w0, +4 * w0, 51)
    >>>  X, Y = np.meshgrid(x, y)
    >>>  helical = False  # whether to plot helical LG modes or sinusoidal LG modes
    >>>
    >>> for i, p in enumerate([0, 1, 2]):
    >>>    for j, l in enumerate([0, 1, 2]):
    >>>        E = lg.compute_lg_mode(p, l, w0, z, 1064e-9, x, y, helical)
    >>>        intensity = np.abs(E) ** 2
    >>>        ax = axes[i, j]
    >>>        C = ax.contourf(X, Y, intensity.T, levels=100)
    >>>        C.set_edgecolor("face")
    >>>        ax.set_title(f"LG Mode p={p}, l={l}")
    >>>        ax.set_aspect("equal")
    >>>
    >>> for ax in axes.flatten():
    >>>     ax.set_xticks([])
    >>>     ax.set_yticks([])
    >>> plt.tight_layout()
    >>> plt.show()
    """
    cdef Workspace ws
    initialize_workspace(&ws, p, l, w0, z, wavelength)
    cdef int i, j
    cdef int nx = x.shape[0]
    cdef int ny = y.shape[0]
    cdef np.ndarray result = np.zeros((nx, ny), dtype=np.complex128)

    for i in range(nx):
        for j in range(ny):
            result[i, j] = lg_mode(&ws, x[i], y[j], helical)

    return result
