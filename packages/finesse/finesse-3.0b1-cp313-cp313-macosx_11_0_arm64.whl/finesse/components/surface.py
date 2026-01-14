from abc import ABC
from math import isclose
import numpy as np

from ..parameter import float_parameter
from ..symbols import Resolving, Symbol
from ..utilities.misc import calltracker
from .general import Connector
from finesse.exceptions import InvalidRTLError, EvaluateResolvingSymbolError
from finesse.utilities import clip_with_tolerance


@float_parameter("R", "Reflectivity", validate="_check_R", post_validate="check_rtl")
@float_parameter("T", "Transmission", validate="_check_T", post_validate="check_rtl")
@float_parameter("L", "Loss", validate="_check_L", post_validate="check_rtl")
@float_parameter("phi", "Phase", units="degrees")
@float_parameter(
    "Rcx",
    "Radius of curvature (x)",
    units="m",
    validate="_check_Rc",
    is_geometric=True,
)
@float_parameter(
    "Rcy",
    "Radius of curvature (y)",
    units="m",
    validate="_check_Rc",
    is_geometric=True,
)
@float_parameter("xbeta", "Misalignment (x)", units="radians")
@float_parameter("ybeta", "Misalignment (y)", units="radians")
# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class Surface(ABC, Connector):
    """Abstract optical surface interface providing an object with common properties for
    :class:`.Mirror` and :class:`.Beamsplitter` to inherit from.

    Parameters
    ----------
    name : str
        Name of newly created surface.

    R : float, optional
        Reflectivity of the surface.

    T : float, optional
        Transmissivity of the surface.

    L : float, optional
        Loss of the surface.

    phi : float, optional
        Microscopic tuning of the surface (in degrees).

    Rc : float, optional
        Radius of curvature (in metres); defaults to ``numpy.inf`` to indicate a planar
        surface. An astigmatic surface can be set with `Rc = (Rcx, Rcy)`.
    """

    def __init__(self, name, R, T, L, phi, Rc, xbeta, ybeta):
        Connector.__init__(self, name)
        # must be set before set_RTL is called
        self._check_rtl = True

        # only in constructor allow setting of none of R, T, L
        # -> default to equally reflective and tranmissive with no loss
        if R is None and T is None and L is None:
            # Use some default
            self.set_RTL(0.5, T=0.5, L=0)
        else:
            self.set_RTL(R, T, L)

        self.phi = phi
        self.Rc = Rc
        self.xbeta = xbeta
        self.ybeta = ybeta

    def _check_R(self, value):
        value = clip_with_tolerance(value, 0, 1)
        if not 0 <= value <= 1:
            raise InvalidRTLError(
                f"Reflectivity must satisfy 0 <= R <= 1, but is {value}"
            )

        return value

    def _check_T(self, value):
        value = clip_with_tolerance(value, 0, 1)
        if not 0 <= value <= 1:
            raise InvalidRTLError(
                f"Transmissivity must satisfy 0 <= T <= 1, but is {value}"
            )

        return value

    def _check_L(self, value):
        value = clip_with_tolerance(value, 0, 1)
        if not 0 <= value <= 1:
            raise InvalidRTLError(f"Loss must satisfy 0 <= L <= 1, but is {value}")

        return value

    def _check_Rc(self, value):
        if value == 0:
            raise InvalidRTLError("Radius of curvature must be non-zero.")

        return value

    def set_RTL(self, R=None, T=None, L=None):
        """Set the values for the R, T and L properties of the surface.

        One of the following combination must be specified:

            - R and T or,
            - R and L or,
            - T and L or,
            - R and T and L

        In the first three cases, the remaining parameter is set via
        the condition,

        .. math::
            R + T + L = 1

        Parameters
        ----------
        R : scalar
            Value of the reflectivity to set.

        T : scalar
            Value of the transmissivity to set.

        L : scalar
            Value of the loss to set.

        Raises
        ------
        ValueError
            If a combination other than one of the above is specified.

            Or if R, T and L are all given but they sum to anything other than one.
        """
        self._check_rtl = False
        try:
            return self._set_RTL(R=R, T=T, L=L)
        finally:
            self._check_rtl = True
            self.check_rtl()

    @calltracker
    def _set_RTL(self, R=None, T=None, L=None):
        # Try and cast the input into a float, the datatype of the
        # R/T/L parameters. If it can't just ignore it, as it could be
        # None or some callable, or something else. Need this because
        # the usual datatype casting doesn't happen until much later
        # with this setter, and it is used to R/T/L in the contructor
        # not self.R = R, etc.
        if R is not None and not isinstance(R, Symbol):
            R = self.R.datatype_cast(R)
        if T is not None and not isinstance(T, Symbol):
            T = self.T.datatype_cast(T)
        if L is not None and not isinstance(L, Symbol):
            L = self.L.datatype_cast(L)

        # Count number of specified parameters in R, T, L
        N = sum(x is not None for x in (R, T, L))

        if N < 2:
            msg = f"""Invalid combination passed to {self.name}.set_RTL. One of the
following must be specified:

    - R and T or,
    - R and L or,
    - T and L or,
    - R and T and L
            """
            raise InvalidRTLError(msg.strip())

        if N == 2:
            old_R = self.R.value
            old_T = self.T.value
            old_L = self.L.value

            # We have two out of the three: check which one is None
            try:
                if L is None:
                    self.R = R
                    self.T = T
                    self.L = 1 - (self.R.ref + self.T.ref)
                elif T is None:
                    self.R = R
                    self.L = L
                    self.T = 1 - (self.R.ref + self.L.ref)
                elif R is None:
                    self.T = T
                    self.L = L
                    self.R = 1 - (self.T.ref + self.L.ref)
                else:
                    raise InvalidRTLError(f"Unexpected combination R={R}, T={T}, L={L}")
            except InvalidRTLError:
                self.R = old_R
                self.T = old_T
                self.L = old_L

                raise

        else:  # i.e. N==3
            # TODO should be context manager

            self.R = R
            self.T = T
            self.L = L

    def check_rtl(self):
        if not self._check_rtl:
            return
        R = self.R.value
        T = self.T.value
        L = self.L.value

        if R is None or T is None or L is None:
            return

        for par, name in zip((R, T, L), ("R", "T", "L")):
            if isinstance(par, Symbol) and not isinstance(par, Resolving):
                name = f"{self.name}.{name}"
                try:
                    val = clip_with_tolerance(par.eval(), 0, 1)
                    if not 0 <= val <= 1:
                        raise InvalidRTLError(
                            f"Symbolic parameter {name} must satisfy 0 <= {name} <= 1, "
                            f"but {name}={par}={val}"
                        )
                except EvaluateResolvingSymbolError:
                    # check_rtl should be called again after symbols are resolved
                    pass

        RTL_sum = R + T + L

        if any(isinstance(par, Resolving) for par in (R, T, L)):
            return

        if isinstance(RTL_sum, Symbol):
            # Evaluate symbolics, if necessary.
            try:
                RTL_sum = RTL_sum.eval()
            except EvaluateResolvingSymbolError:
                # check_rtl should be called again after symbols are resolved
                return

        # FIXME: decide what the necessary tolerance is here.
        if not isclose(RTL_sum, 1):

            def format_par(p):
                if isinstance(p, Symbol):
                    return f"{p} = {p.eval()}"
                else:
                    return p

            msg = (
                f"Expected R + T + L = 1 in '{self.name}' but "
                f"got R + T + L = {RTL_sum}"
                f"\nR = {format_par(R)}"
                f"\nT = {format_par(T)}"
                f"\nL = {format_par(L)}"
            )
            raise InvalidRTLError(msg)

    @property
    def Rc(self):
        """The radius of curvature of the mirror in metres, for both the tangential and
        sagittal planes.

        :`getter`: Returns values of both planes' radii of curvature as a
                   :class:`numpy.ndarray` where the first element is the tangential
                   plane RoC and the second element is the sagittal plane RoC.

        :`setter`: Sets the radius of curvature.

        Examples
        --------
        The following sets the radii of curvature of an object `m`, which
        is a sub-instance of `Surface`, in both directions to 2.5 m:

        >>> m.Rc = 2.5

        Whilst this would set the radius of curvature in the x-direction (tangential
        plane) to 2.5 m and the radius of curvature in the y-direction (sagittal plane)
        to 2.7 m:

        >>> m.Rc = (2.5, 2.7)
        """
        return np.array([self.Rcx.value, self.Rcy.value])

    @Rc.setter
    def Rc(self, value):
        try:
            self.Rcx = value[0]
            self.Rcy = value[1]
        except (IndexError, TypeError):
            self.Rcx = value
            self.Rcy = value

    def actuate_roc(self, dioptres, direction=("x", "y")):
        r"""Actuate on the radius of curvature (RoC) of the surface with a specified
        dioptre shift.

        Sets the RoC to a new value, :math:`R_2`, via,

        .. math::

            R_2 = \frac{2}{d + \frac{2}{R_1}},

        where :math:`R_1` is the current RoC and :math:`d` is the dioptre shift (i.e.
        the `dioptre` argument).

        By default, both planes of curvature are shifted. To shift, e.g., only the
        tangential plane, specify ``direction="x"``.

        Parameters
        ----------
        dioptres : float
            Shift in surface RoC in dioptres.

        direction : tuple or str, optional; default: ("x", "y")
            RoC plane to shift, defaults to both tangential and sagittal.
        """
        rcnew = lambda x: 2 / (dioptres + 2 / x)
        if "x" in direction:
            self.Rcx = rcnew(self.Rcx.value)
        if "y" in direction:
            self.Rcy = rcnew(self.Rcy.value)

    # NOTE this is a bit hacky but gets around using surface.R = value (etc.)
    #      directly in an axis scan without being warned

    def _on_add(self, model):
        super()._on_add(model)
        # we alse need to call check_rtl after parsing is completed and self-referencing
        # symbols are resolved as well.
        model._on_parse.append(self.check_rtl)
