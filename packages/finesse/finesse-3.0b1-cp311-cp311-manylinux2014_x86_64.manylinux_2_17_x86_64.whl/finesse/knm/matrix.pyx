#cython: boundscheck=False, wraparound=False, initializedcheck=False

"""Scattering matrix data structure and associated functions
for constructing different formats of this object."""

cimport numpy as np
import numpy as np

from finesse.cymath.math cimport sqrt
from finesse.cymath.complex cimport cnorm
from finesse.cymath.homs cimport field_index
from finesse.cymath.complex cimport carg # Standard complex.h functions
from finesse.cymath.complex cimport crotate, crotate2, cnorm
from finesse.cymath.math cimport sqrt, cos, sin # Standard math.h functions
from finesse.cymath.math cimport msign

import copy
import cython


cdef class KnmMatrix:
    """
    Higher-Order-Mode scattering matrix container. Essentially a wrapper
    around a 2D NumPy array with methods for conveniently accessing specific
    couplings and plotting the matrix as a color-mesh.

    The underlying :class:`numpy.ndarray` object can be accessed via the ``data``
    attribute.

    Construction of KnmMatrix objects should, generally, not be performed manually. Objects
    of this type are the return type of the general scattering matrix computing routines,
    see :func:`.make_scatter_matrix`. To make a KnmMatrix object from a pre-existing
    matrix of complex coupling coefficients, use :meth:`.KnmMatrix.from_buffer`.

    Parameters
    ----------
    modes : array-like
        A 2D array, or memory-view to the array, of the mode indices
        associated with the scattering matrix.

    comp_name : str, optional; default: ""
        Name of the component associated with the matrix (if any).

    kdir : str, optional; default: ""
        A string representing the coupling direction of the matrix, e.g.
        "11" for a reflection at the first surface of a mirror-like optic.
    """

    def __init__(self, const int[:, ::1] modes, comp_name="", kdir=""):
        if modes.shape[0] == 0 and modes.shape[1] == 0:
            raise Exception(f"Empty mode list provided: {np.array(modes)}")

        if comp_name:
            self.name = f"{comp_name}.K{kdir}"
        else:
            self.name = f"K{kdir}"

        self.modes_view = modes
        self.homs = self.modes = np.asarray(self.modes_view)
        matrix = np.eye(self.modes_view.shape[0], dtype=np.complex128)
        self.data = matrix
        self.data_view = self.data
        self.mtx.ptr = <complex_t*>&self.data_view[0,0]
        self.mtx.size1 = self.data_view.shape[0]
        self.mtx.size2 = self.data_view.shape[1]
        self.mtx.stride1 = self.data_view.strides[0]//sizeof(complex_t)
        self.mtx.stride2 = self.data_view.strides[1]//sizeof(complex_t)

    @staticmethod
    def from_buffer(
        np.ndarray[complex_t, ndim=2, mode="c"] buffer,
        const int[:, ::1] modes,
        **kwargs,
    ):
        """Construct a KnmMatrix object from a pre-existing 2D array buffer.

        This method is useful for creating KnmMatrix objects from scattering matrix
        data which have been computed elsewhere. One of the most common use-cases
        is when using :class:`.KnmDetector` objects in "matrix-mode"; see the documentation
        of this class for an example.

        Parameters
        ----------
        buffer : :class:`numpy.ndarray`
            A 2D array of complex values corresponding to the underlying
            buffer of scattering matrix data.

        modes : array-like
            A 2D array, or memory-view to the array, of the mode indices
            associated with the scattering matrix.

        kwargs : keyword arguments, optional
            Additional args to pass to constructor of KnmMatrix.

        Returns
        -------
        kmat : :class:`.KnmMatrix`
            The KnmMatrix wrapper around the array buffer.
        """
        cdef Py_ssize_t N = modes.shape[0]
        if buffer[:].shape[0] != N or buffer[:].shape[1] != N:
            bshape = (buffer[:].shape[0], buffer[:].shape[1])
            raise ValueError(
                f"Error in KnmMatrix.from_buffer:\n"
                f"    Shape of matrix buffer {bshape} inconsistent "
                f"with number of modes ({N})"
            )

        cdef KnmMatrix kmat = KnmMatrix(modes, **kwargs)
        kmat.data = buffer
        kmat.data_view = buffer
        kmat.mtx.ptr = <complex_t*>&kmat.data_view[0,0]
        kmat.mtx.size1 = kmat.data_view.shape[0]
        kmat.mtx.size2 = kmat.data_view.shape[1]
        kmat.mtx.stride1 = kmat.data_view.strides[0]//sizeof(complex_t)
        kmat.mtx.stride2 = kmat.data_view.strides[1]//sizeof(complex_t)
        return kmat

    @staticmethod
    def of_zeros(const int[:, ::1] modes, **kwargs):
        """Constuct a KnmMatrix where each element is (complex) zero.

        Parameters
        ----------
        modes : array-like
            A 2D array, or memory-view to the array, of the mode indices
            associated with the scattering matrix.

        kwargs : keyword arguments, optional
            Additional args to pass to constructor of KnmMatrix.

        Returns
        -------
        kmat : :class:`.KnmMatrix`
            The KnmMatrix object consisting of a matrix of zeroes.
        """
        cdef KnmMatrix kmat = KnmMatrix(modes, **kwargs)
        kmat.data[:] = 0 + 0j
        return kmat

    def __str__(self):
        cdef:
            Py_ssize_t i, j
            int n1, m1, n2, m2
            Py_ssize_t N = self.modes_view.shape[0]

        s = ""
        for i in range(N):
            n1 = self.modes_view[i][0]
            m1 = self.modes_view[i][1]
            for j in range(N):
                n2 = self.modes_view[j][0]
                m2 = self.modes_view[j][1]

                s += (f"{self.name}[{j}][{i}]: {n1} {m1} "
                      f"-> {n2} {m2} = {self.data_view[j][i]}\n")

        return s

    cdef (Py_ssize_t, Py_ssize_t) field_indices_from(self, key):
        cdef:
            Py_ssize_t i = 0
            Py_ssize_t j = 0
            int n1, m1, n2, m2
            Py_ssize_t N = self.modes_view.shape[0]

            Py_ssize_t key_size
            str skey
            str mode1, mode2
            list smodes

        if isinstance(key, str):
            skey = "".join(key.split()) # strip all whitespace from the key
            key_size = len(skey)
            smodes = skey.split("->")
            if not smodes or len(smodes) > 2:
                i = j = N
            else:
                # Key is a str of format "nmn'm'"
                if len(smodes) == 1:
                    if key_size != 4:
                        i = j = N
                    else:
                        mode1, mode2 = smodes[0][:2], smodes[0][2:]

                # Key is a str of format "nm->n'm'"
                elif len(smodes) == 2:
                    if key_size != 6:
                        i = j = N
                    else:
                        mode1, mode2 = smodes

                if not i and not j:
                    # Have to convert to python int class
                    # first before setting C ints
                    nn1 = int(mode1[0])
                    mm1 = int(mode1[1])
                    nn2 = int(mode2[0])
                    mm2 = int(mode2[1])
                    n1 = nn1
                    m1 = mm1
                    n2 = nn2
                    m2 = mm2

                    i = field_index(n1, m1, self.modes_view)
                    j = field_index(n2, m2, self.modes_view)

        else:
            key_size = len(key)
            if key_size == 2: # getting [i, j] element directly
                i, j = key
            elif key_size == 4: # getting nm -> n'm' coupling
                n1, m1, n2, m2 = key

                i = field_index(n1, m1, self.modes_view)
                j = field_index(n2, m2, self.modes_view)
            else:
                i = j = N

        return i, j

    def __getitem__(self, key):
        cdef:
            Py_ssize_t i, j
            Py_ssize_t N = self.modes_view.shape[0]

        i, j = self.field_indices_from(key)

        if i >= N or j >= N:
            raise ValueError(f"Invalid or non-existent key {key}")

        return self.data_view[j][i]

    def get(self, key, default=None):
        """Retrieves the coupling coefficient corresponding to the `key`, returning
        `default` if this `key` is invalid.

        Parameters
        ----------
        key : str or integer sequence
            A string of the format:

                - "nm->n'm'" or,
                - "nmn'm'",

            where n, m, n' and m' are all convertible to integers

            Or an integer sequence of:

                - length 2 -- i.e. an i, j pair corresponding to the field indices.
                - or length 4 -- i.e. a n1, m1, n2, m2 coupling.

        default : Any, optional
            The default value returned if the `key` is invalid.

        Returns
        -------
        out : complex
            The value of the coupling coefficient associated with `key`.
        """
        cdef:
            Py_ssize_t i, j
            Py_ssize_t N = self.modes_view.shape[0]

        i, j = self.field_indices_from(key)

        if i >= N or j >= N:
            return default

        return self.data_view[j][i]

    cdef complex_t coupling(self, int n1, int m1, int n2, int m2) noexcept nogil:
        cdef:
            Py_ssize_t i = field_index(n1, m1, self.modes_view)
            Py_ssize_t j = field_index(n2, m2, self.modes_view)

        return self.data_view[j][i]

    def plot(
            self, mode="amplitude", log=False, deg=False, cmap=None, show=True, filename=None,
    ):
        """Plots the coupling coefficient matrix as a color-mesh.

        Parameters
        ----------
        mode : str, optional
            Specifier for which attribute of the coupling coefficient to
            plot. This can be one of 'amplitude', 'phase', 'real', 'imag',
            'amplitude/phase', or 'real/imag'. Defaults to 'amplitude'.

        log : bool, optional
            Whether the log of the data should be plotted. This is only used for
            'amplitude' and is ignored for all other options. Defaults to False.

        deg : bool, optional
            Whether the data should be plotted in degrees or radians. This is only
            used for 'phase' and is ignored for all other options. Defaults to False.

        cmap : str, matplotlib colormap, optional
            Colormap to use. Defaults to the default colormap loaded in
            matplotlib.rcParams.

        show : bool, optional
            Whether to show plot or not. Defaults to true.

        filename : str, path, optional
            The name of a file to save the figure to. Defaults to None so
            that no file is saved.

        Returns
        -------
        fig : matplotlib figure
            A handle to the figure.
        """
        import matplotlib.pyplot as plt
        import matplotlib.colors as colors
        from finesse.plotting.tools import add_colorbar
        from functools import partial

        knm = self.data[:]

        valid_modes = [
            "amplitude", "phase", "real", "imag", "amplitude/phase", "real/imag",
        ]
        if mode not in valid_modes:
            raise ValueError(
                f"Invalid mode={mode} argument. Must be one of {valid_modes}"
            )
        modes = mode.split("/")
        nplots = len(modes)

        func_map = {
            "amplitude": np.abs,
            "phase": partial(np.angle, deg=deg),
            "real": np.real,
            "imag": np.imag,
        }
        label_map = {
            "amplitude": "abs",
            "phase": f"phase [{'deg' if deg else 'rad'}]",
            "real": "real",
            "imag": "imag",
        }

        fig = plt.figure()
        gs = fig.add_gridspec(nplots, 1, hspace=0.04 * (nplots - 1))
        ax_top = fig.add_subplot(gs[0])
        if nplots == 2:
            ax_bot = fig.add_subplot(gs[1], sharex=ax_top)

        numrows, numcols = knm.shape
        hom_ticks = []
        for i in range(self.modes_view.shape[0]):
            hom_ticks.append(f"{self.modes_view[i][0]}{self.modes_view[i][1]}")
        A = np.arange(1, self.modes_view.shape[0] + 1) - 0.5

        def make_subplot(ax, mode):
            func = func_map[mode]
            label = label_map[mode]

            if log and mode == "amplitude":
                norm = colors.LogNorm()
                # Make sure any zero couplings get displayed as black rather than white
                cmap_handle = copy.copy(plt.colormaps.get_cmap(cmap))
                cmap_handle.set_bad((0,0,0))
            else:
                norm = None
                cmap_handle = cmap

            cax = ax.pcolormesh(func(knm), cmap=cmap_handle, norm=norm)
            add_colorbar(cax, label=label)

            ax.set_xticks(A)
            ax.set_yticks(A)
            ax.set_xticklabels(hom_ticks)
            ax.set_yticklabels(hom_ticks)

            ax.set_xlim(None, np.max(A) + 0.5)
            ax.set_ylim(None, np.max(A) + 0.5)

            def format_coord(x, y):
                col = int(np.floor(x))
                row = int(np.floor(y))

                if col >= 0 and col < numcols and row >= 0 and row < numrows:
                    z = knm[row, col]
                    return (
                        f"nm={hom_ticks[col]}, n'm'={hom_ticks[row]}, z={z:.4g}"
                        f" -> {label}(z) = {func(z):.4g}"
                    )

                return None

            ax.format_coord = format_coord
            # ax.set_aspect("equal")

        make_subplot(ax_top, mode=modes[0])
        if nplots == 2:
            make_subplot(ax_bot, mode=modes[1])
            # don't label the top xaxis since the bottom one will have them
            plt.setp(ax_top.get_xticklabels(), visible=False)

        figsize = fig.get_size_inches()
        fig.set_size_inches(figsize[0], figsize[1] * nplots)
        fig.tight_layout()

        if filename is not None:
            # need bbox_inches here even after tight_layout has been called
            fig.savefig(filename, bbox_inches="tight")

        if show:
            plt.show()

        return fig


cpdef make_unscaled_X_scatter_knm_matrix(int[:, ::1] modes) :
    """ This method returns an unscaled KnmMatrix object that represents
    a distortion from the integral:

    iint_inf U_nm(x,y) x U_n'm'(x,y) dx dy

    This essentially scatters modes by mode index n ± 1. There are some scalings
    proportional to w(x)*exp(±1j*Gouy(z)) missing as these can be applied as single
    scalars in addition to this matrix if needed.

    Returns
    -------
    KnmMatrix
    """
    cdef int i, j, n_, m_, n, m
    cdef KnmMatrix k_yaw = KnmMatrix.of_zeros(modes)
    i = j = -1
    for n_, m_ in modes: # from
        i += 1
        j = -1
        for n, m in modes: # to
            j += 1
            if m == m_:
                if n + 1 == n_:
                    # matrix is hermitian
                    k_yaw.data_view[j, i] = sqrt(n+1)/2
                    k_yaw.data_view[i, j] = sqrt(n+1)/2

    return k_yaw


cpdef make_unscaled_Y_scatter_knm_matrix(int[:, ::1] modes) :
    """ This method returns an unscaled KnmMatrix object that represents
    a distortion from the integral:

    iint_inf U_nm(x,y) y U_n'm'(x,y) dx dy

    This essentially scatters modes by mode index m ± 1. There are some scalings
    proportional to w(x)*exp(±1j*Gouy(z)) missing as these can be applied as single
    scalars in addition to this matrix if needed.

    Returns
    -------
    KnmMatrix
    """
    cdef int i, j, n_, m_, n, m
    cdef KnmMatrix k_pitch = KnmMatrix.of_zeros(modes)
    i = j = -1
    for n_, m_ in modes: # from
        i += 1
        j = -1
        for n, m in modes: # to
            j += 1
            if n == n_:
                if m + 1 == m_:
                    # matrix is hermitian
                    k_pitch.data_view[j, i] = sqrt(m+1)/2
                    k_pitch.data_view[i, j] = sqrt(m+1)/2

    return k_pitch


cdef void knm_loss(const complex_t* knm_mat, double* out, Py_ssize_t N) noexcept nogil:
    """Compute per mode losses due to scattering.

    Each entry in out is then 1 - \sum_{n'm'} |k_{n'm'nm}|^2 for the mode nm.
    """
    cdef:
        Py_ssize_t i, j

    for i in range(N):
        out[i] = 1.0
        for j in range(N):
            out[i] -= cnorm(knm_mat[j*N + i])


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef void c_zero_tem00_phase(
    const complex_t[:, ::1] knm_mat,
    complex_t[:, ::1] out
) noexcept nogil:
    """Rotates all coupling coefficients in the matrix `knm_mat`
    by the phase of the zeroth (00 -> 00) coupling coefficient.

    This has the effect of zeroing the phase of the 00 -> 00 coupling
    coefficient, resulting in cavities being resonant for the 00 mode
    by default if this function (along with zeroing of space Gouy phase
    for 00 mode) is applied."""
    cdef:
        Py_ssize_t i, j
        Py_ssize_t N = knm_mat.shape[0]
        double phase_k0000 = carg(knm_mat[0][0])
        double cph = cos(phase_k0000)
        double sph = -sin(phase_k0000)

    for i in range(N):
        for j in range(N):
            out[i][j] = crotate2(knm_mat[i][j], cph, sph)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef void c_flip_odd_horizontal(
    DenseZMatrix *mat,
    const int[:, ::1] homs
) noexcept nogil:
    """Flips the sign of all odd couplings in the sagittal plane."""
    cdef:
        Py_ssize_t i, j
        int n2
        Py_ssize_t N = mat.size1

    for i in range(N):
        for j in range(N):
            n2 = homs[j][0]
            if msign(n2) == -1:
                mat.ptr[j*mat.stride1 + i*mat.stride2] *= -1


def reverse_gouy_phases(
    x_gouy1, y_gouy1,
    x_gouy2, y_gouy2,
    knm_matrix
):
    """
    Adjust the phase of all coupling coefficients in the matrix `knm_mat` with
    respect to the Gouy phases.

    This is required for :math:`k_{nmn'm'}` calculations because in Finesse the
    Gouy phase is added explicitly to the amplitude coefficients in a
    :class:`.Space` whereas the coupling coefficients are derived using a
    formula in which the Gouy phase resides in the equation for the spatial
    profile.
    """
    c_reverse_gouy_phases(
        x_gouy1, y_gouy1,
        x_gouy2, y_gouy2,
        knm_matrix.data,
        knm_matrix.modes,
        knm_matrix.data
    )


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef void c_reverse_gouy_phases(
    double x_gouy1, double y_gouy1,
    double x_gouy2, double y_gouy2,
    const complex_t[:, ::1] knm_mat,
    const int[:, ::1] homs,
    complex_t[:, ::1] out
) noexcept nogil:
    """
    Adjust the phase of all coupling coefficients in the matrix `knm_mat` with
    respect to the Gouy phases.

    This is required for :math:`k_{nmn'm'}` calculations because in Finesse the
    Gouy phase is added explicitly to the amplitude coefficients in a
    :class:`.Space` whereas the coupling coefficients are derived using a
    formula in which the Gouy phase resides in the equation for the spatial
    profile.
    """
    cdef:
        Py_ssize_t i, j
        int n1, m1, n2, m2
        Py_ssize_t N = knm_mat.shape[0]

    for i in range(N):
        n1 = homs[i][0]
        m1 = homs[i][1]
        for j in range(N):
            n2 = homs[j][0]
            m2 = homs[j][1]

            out[j][i] = rev_gouy(
                x_gouy1, y_gouy1,
                x_gouy2, y_gouy2,
                knm_mat[j][i],
                n1, m1, n2, m2,
            )


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef complex_t rev_gouy(
    double x_gouy1,
    double y_gouy1,
    double x_gouy2,
    double y_gouy2,
    complex_t k,
    int n1, int m1, int n2, int m2,
) noexcept nogil:
    cdef:
        double phase1, phase2

    phase1 = (n1 + 0.5) * x_gouy1 + (m1 + 0.5) * y_gouy1
    phase2 = (n2 + 0.5) * x_gouy2 + (m2 + 0.5) * y_gouy2

    return crotate(k, phase2 - phase1)
