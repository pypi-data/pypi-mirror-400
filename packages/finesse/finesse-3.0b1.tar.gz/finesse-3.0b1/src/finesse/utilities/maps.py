"""Collection of tools for computing different maps."""

import numpy as np
from scipy.special import erf


def make_coordinates(N, a):
    """Makes the 1D and square 2D grid of coordinates for map calculations.

    Parameters
    ----------
    N_samples : int
        Number of samples in each dimension (`N` x `N`)
    a : float
        Dimension of square grid (`a` x `a`) to generate

    Returns
    -------
    x,y : array_like[float]
        1D arrays for the x and y coordinates
    X,Y,R : array_like[float]
        2D Arrays of the X, Y, and radial R coordinates
    """

    x = y = np.linspace(-a, a, N)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    return x, y, X, Y, R


def circular_aperture(x, y, R_ap, x_offset=0, y_offset=0):
    """Circular aperture map.

    Parameters
    ----------
    x, y : array
        1D arrays describing uniform 2D grid to compute map
        over in meters
    R : float
        Radius of aperture in meters
    x_offset, y_offset : float, optional
        Offset of aperture from origin
    """
    X, Y = np.meshgrid(x, y)
    R = np.sqrt((X - x_offset) ** 2 + (Y - y_offset) ** 2)
    ap_map = np.ones_like(X)
    ap_map[R > R_ap] = 0
    return ap_map


def surface_point_absorber(
    xs, ys, w, h, power_absorbed, alpha=0.55e-6, kappa=1.38, zero_min=False
):
    """Models the surface deformation from a small point absorber in a coating of a
    mirror. It calcaultes the thermo-elastic deformation due to excess heat being
    deposited in the mirror.

    Parameters
    ----------
    xs, ys : array
        1D array for the x and y axis to calculate the distortion over
    w : double
        Area of the absorber size
    h : double
        Thickness of mirror
    power_absorbed : double
        Amount of power absorbed over the area w
    alpha : double, optional
        Thermo-elastic coefficient of material, default value for fused silica
    kappa : double, optional
        Thermal conductivity of the material, default value for fused silica

    Returns
    -------
    Height map in meters

    Notes
    -----
    Equation from:
        A. Brooks, et.al "Point absorbers in Advanced LIGO," Appl. Opt. (2021)
    """
    dx = xs[1] - xs[0]
    dy = ys[1] - ys[0]
    r = np.sqrt(np.add.outer(ys**2, xs**2))
    c0 = -1 / 2 - np.log((h**2 + np.sqrt(w**2 + h**2)) / w)
    out = np.zeros_like(r)
    # most of the time the absorber is very small, much smaller than
    # the discretisation of the map, so we can simplify this calculation
    if w > dx or w > dy:
        b1 = np.abs(r) <= w
        b2 = np.abs(r) > w
        out[b1] = -1 / 2 * (r[b1] / w) ** 2
        out[b2] = c0 + np.log((h**2 + np.sqrt(r[b2] ** 2 + h**2)) / r[b2])
    else:
        out = c0 + np.log((h**2 + np.sqrt(r**2 + h**2)) / r)

    if zero_min:
        out -= np.min(out)

    return alpha * power_absorbed / (2 * np.pi * kappa) * out


def overlap_piston_coefficient(x, y, z, weight_spot: float):
    """Computes the amount of weighted piston term there is in some 2D data like a
    surface map. This is computed by evaluating a weighted Hermite polynomial overlap
    integral in an efficient manner.

    Parameters
    ----------
    x, y : array_like
        1D Array of x and y describing the 2D plane of `z`
    z : array_like
        2D optical path depth [metres]
    weight_spot : float
        Beam spot size to weight over

    Returns
    -------
    piston : float
        amount of piston term
    """
    dx = (x[1] - x[0]) / weight_spot
    dy = (y[1] - y[0]) / weight_spot

    Wx = np.exp(-((x / weight_spot) ** 2))
    Wy = np.exp(-((y / weight_spot) ** 2))

    k00 = np.dot((z @ Wx), Wy) * dx / (np.sqrt(np.pi) * 2) * dy / (np.sqrt(np.pi) * 2)

    return 4 * k00


def overlap_tilt_coefficients(x, y, z, weight_spot: float):
    """Computes the amount of yaw and pitch terms present in a map's displacement data.

    This is computed by evaluating a weighted Hermite polynomial overlap integral in an
    efficient manner.

    Parameters
    ----------
    x, y : array_like
        1D Array of x and y describing the 2D plane of `z`
    z : array_like
        2D optical path depth [metres]
    weight_spot : float
        Beam spot size to weight over

    Returns
    -------
    k10, k01 : complex
        Complex-valued overlap tilt for the HG10 and HG01 mode
    """
    weight_spot /= np.sqrt(2)

    dx = (x[1] - x[0]) / weight_spot
    dy = (y[1] - y[0]) / weight_spot

    Wx = np.exp(-((x / weight_spot) ** 2))
    Wy = np.exp(-((y / weight_spot) ** 2))

    Hn = 2 * x / weight_spot * Wx
    Hm = 2 * y / weight_spot * Wy

    k10 = np.dot((z @ Hn), Wy) * dx / (np.sqrt(np.pi) * 2) * dy / (np.sqrt(np.pi) * 2)
    k01 = np.dot((z @ Wx), Hm) * dx / (np.sqrt(np.pi) * 2) * dy / (np.sqrt(np.pi) * 2)

    return (
        # convert back to normal x units in displacement map
        4 * k10 / weight_spot,
        4 * k01 / weight_spot,
    )


def overlap_curvature_coefficients(x, y, z, weight_spot: float):
    """Computes the amount of x and y curvature terms present in a map's displacement
    data.

    This is computed by evaluating a weighted Hermite polynomial overlap integral in an
    efficient manner.

    Parameters
    ----------
    x, y : array_like
        1D Array of x and y describing the 2D plane of `z`
    z : array_like
        2D optical path depth [metres]
    weight_spot : float
        Beam spot size to weight over

    Returns
    -------
    k20, k02 : complex
        Complex-valued overlap coefficients for the HG20 and HG02 mode
    """
    # Normalisation constant
    weight_spot /= np.sqrt(2)
    dx = (x[1] - x[0]) / weight_spot
    dy = (y[1] - y[0]) / weight_spot
    # Spot size weightings
    Wx = np.exp(-((x / weight_spot) ** 2))
    Wy = np.exp(-((y / weight_spot) ** 2))
    # 2nd order HG mode
    Hn = ((2 * x / weight_spot) ** 2 - 2) * Wx
    Hm = ((2 * y / weight_spot) ** 2 - 2) * Wy
    # Compute the overlap integrals
    k20 = np.dot((z @ Hn), Wy) * dx / (np.sqrt(np.pi) * 2**3) * dy / (np.sqrt(np.pi))
    k02 = np.dot((z @ Wx), Hm) * dx / (np.sqrt(np.pi) * 2**3) * dy / (np.sqrt(np.pi))
    return (
        # convert back to normal x units in displacement map
        4 * k20 / weight_spot / weight_spot,
        4 * k02 / weight_spot / weight_spot,
    )


def overlap_1D_curvature_coefficients(x, z, weight_spot: float):
    """Computes the amount of spot size weighted quadratic `x**2` term there is present
    in some 1D data.

    Parameters
    ----------
    x : ndarray(dtype=float)
        Sample points, ideally should be symmetric about 0.
    z : ndarray(dtype=float)
        function at sample points x
    weight_spot : float
        Spot size to use as weighting

    Returns
    -------
    quadratic_term : double
        Weighted quadratic term of z

    Notes
    -----
    This function is essentially evaluating a weighted Hermite polynomial
    overlap integral with `z(x)` to determine the linear term.

    .. math::

        \\int_{\\min(x)}^{\\max(x)} H_{2}(x) z(x) W(x) dx

    Where the weighting function is :math:`W(x) = exp(-x**2)`.
    """
    weight_spot /= np.sqrt(2)
    dx = (x[1] - x[0]) / weight_spot
    # exponential weighting of spot size
    W = np.exp(-((x / weight_spot) ** 2))
    # Second order Hermite, H_2(x)
    Hn = ((2 * x / weight_spot) ** 2 - 2) * W
    # normalisation constant as integral of H_0(x) over
    # domain is not 1
    norm = (
        0.5 * np.sqrt(np.pi) * (erf(x.max() / weight_spot) - erf(x.min() / weight_spot))
    )
    k20 = (z @ Hn).sum() * dx / norm
    return (
        # convert back to normal x units in displacement map
        k20
        / weight_spot
        / weight_spot
        / 2
    )


def overlap_1D_tilt_coefficients(x, z, weight_spot: float):
    """Computes the amount of spot size weighted linear `x` term there is present in
    some 1D data.

    Parameters
    ----------
    x : ndarray(dtype=float)
        Sample points, ideally should be symmetric about 0.
    z : ndarray(dtype=float)
        function at sample points x
    weight_spot : float
        Spot size to use as weighting

    Returns
    -------
    linear_term : double
        Weighted linear term of z

    Notes
    -----
    This function is essentially evaluating a weighted Hermite polynomial
    overlap integral with `z(x)` to determine the linear term.

    .. math::

        \\int_{\\min(x)}^{\\max(x)} H_{1}(x) z(x) W(x) dx

    Where the weighting function is :math:`W(x) = exp(-x**2)`.
    """
    weight_spot /= np.sqrt(2)
    dx = (x[1] - x[0]) / weight_spot
    # exponential weighting of spot size
    W = np.exp(-((x / weight_spot) ** 2))
    # Second order Hermite, H_1(x)
    Hn = 2 * x / weight_spot * W
    # normalisation constant as integral of H_0(x) over
    # domain is not 1
    norm = np.sqrt(np.pi) * (erf(x.max() / weight_spot) - erf(x.min() / weight_spot))
    k10 = (z @ Hn).sum() * dx / norm
    return (
        # convert back to normal x units in displacement map
        2
        * k10
        / weight_spot
    )


def rms(x, y, z, weight_spot: float, xo: float = 0, yo: float = 0):
    """Computes the spot weight RMS over some 2D data, such as optical path depth.

    Parameters
    ----------
    x, y : array_like
        1D Array of x and y describing the 2D plane of `z`
    z : array_like
        2D optical path depth [metres]
    weight_spot : float
        Beam spot size to weight over
    xo, yo : float
        Origin of the beam position

    Returns
    -------
    rms : float
        Root mean squared in units of whatever `z` is

    Notes
    -----
    Based on Equation 4 in:
        A. Brooks, et.al
        Overview of Advanced LIGO adaptive optics
        Appl. Opt. 55, 8256-8265 (2016)
    """
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    Wx = np.exp(-(((x - xo) / weight_spot) ** 2))
    Wy = np.exp(-(((y - yo) / weight_spot) ** 2))
    scaling = np.sqrt(2 / np.pi / weight_spot**2)
    deltaW = z
    deltaWbar = ((deltaW @ Wx) @ Wy) * dx * dy * scaling
    return np.sqrt((((deltaW - deltaWbar) ** 2 @ Wx) @ Wy) * dx * dy * scaling)


class BinaryReaderEOFException(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Not enough bytes in file to satisfy read request"


class BinaryReader:
    """MetroPro binary data format reader."""

    # Map well-known type names into struct format characters.
    typeNames = {
        "int8": "b",
        "uint8": "B",
        "int16": "h",
        "uint16": "H",
        "int32": "i",
        "uint32": "I",
        "int64": "q",
        "uint64": "Q",
        "float": "f",
        "double": "d",
        "char": "s",
    }

    def __init__(self, fileName):
        self.file = open(fileName, "rb")

    def read(self, typeName, size=None):
        """Read a datatype from the binary file.

        Parameters
        ----------
        typename : str
            See `BinaryReader.typeNames`.
        size : int
            Number of bytes to read
        """
        import struct

        typeFormat = BinaryReader.typeNames[typeName.lower()]
        typeFormat = ">" + typeFormat
        typeSize = struct.calcsize(typeFormat)
        if size is None:
            value = self.file.read(typeSize)
            if typeSize != len(value):
                raise BinaryReaderEOFException
            unpacked = struct.unpack(typeFormat, value)[0]
        else:
            value = self.file.read(size * typeSize)
            if size * typeSize != len(value):
                raise BinaryReaderEOFException
            unpacked = np.zeros(size)
            for k in range(size):
                i = k * typeSize
                unpacked[k] = struct.unpack(typeFormat, value[i : i + typeSize])[0]
        return unpacked

    def seek(self, offset, refPos=0):
        """Offset in bytes and refPos gives reference position, where 0 means origin of
        the file, 1 uses current position and 2 uses the end of the file."""
        self.file.seek(offset, refPos)

    def __del__(self):
        self.file.close()


def read_metropro_file(filename):
    """Reading the metroPro binary data files. Translated from Hiro Yamamoto's
    'LoadMetroProData.m'.

    Parameters
    ----------
    filename
        Name of metropro data file.
    """
    f = BinaryReader(filename)
    # Read header
    hData = read_metropro_header(f)
    if hData["format"] < 0:
        print(
            "Error: Format unknown to readMetroProData()\nfilename: {:s}".format(
                filename
            )
        )
        return 0
    # Read phase map data
    # Skipping header and intensity data
    f.seek(hData["size"] + hData["intNBytes"])
    # Reading data
    dat = f.read("int32", size=hData["Nx"] * hData["Ny"])
    # Marking unmeasured data as NaN
    dat[dat >= hData["invalid"]] = np.nan
    # Scale data to meters
    dat = dat * hData["convFactor"]
    # Reshaping into Nx * Ny matrix
    dat = dat.reshape(hData["Ny"], hData["Nx"])
    # Flipping up/down, i.e., change direction of y-axis.
    dat = dat[::-1, :]
    # Auxiliary data to return
    # dxy = hData['cameraRes']
    # Unnecessary
    # x1 = dxy * np.arange( -(len(dat[0,:])-1)/2, (len(dat[0,:])-1)/2 + 1)
    # y1 = dxy * np.arange( -(len(dat[:,0])-1)/2, (len(dat[:,1])-1)/2 + 1)
    return dat, hData  # , x1, y1


def read_metropro_header(binary):
    """Reads header of the metroPro binary format files. Translated from the
    readerHeader() function within the 'LoadMetroProData.m' function written by Hiro
    Yamamoto.

    Parameters
    ----------
    binary : :class:`BinaryReader`
        Name of metropro data file.
    """
    f = binary
    hData = {}
    hData["magicNum"] = f.read("uint32")
    hData["format"] = f.read("int16")
    hData["size"] = f.read("int32")
    # Check if the magic string and format are known ones.
    if not (
        hData["format"] >= 1
        and hData["format"] <= 3
        and hData["magicNum"] - hData["format"] == int("881B036E", 16)
    ):
        hData["format"] = -1
    # Read necessary data
    hData["invalid"] = int("7FFFFFF8", 16)
    f.seek(60)
    # Intensity data, which we will skip over.
    hData["intNBytes"] = f.read("int32")
    # Top-left coordinates, which are useless.
    hData["X0"] = f.read("int16")
    hData["Y0"] = f.read("int16")
    # Number of data points alng x and y
    hData["Nx"] = f.read("int16")
    hData["Ny"] = f.read("int16")
    # Total data, 4*Nx*Ny
    hData["phaNBytes"] = f.read("int32")
    f.seek(218)
    # Scale factor determined by phase resolution tag
    phaseResTag = f.read("int16")
    if phaseResTag == 0:
        phaseResVal = 4096
    elif phaseResTag == 1:
        phaseResVal = 32768
    elif phaseResTag == 2:
        phaseResVal = 131072
    else:
        phaseResVal = 0
    f.seek(164)
    intf_scale_factor = f.read("float")
    hData["waveLength"] = f.read("float")
    f.seek(176)
    obliquity_factor = f.read("float")
    # Eq. in p12-6 in MetroPro Reference Guide
    hData["convFactor"] = (
        intf_scale_factor * obliquity_factor * hData["waveLength"] / phaseResVal
    )
    # Bin size of each measurement
    f.seek(184)
    hData["cameraRes"] = f.read("float")

    return hData
