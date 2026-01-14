"""Material objects are a simple structure that contain commonly used
properties for calculations. By default this includes Fused Silica and
Silicon at 123K.

.. todo::

    At some point add in wavelenth and temperature dependence to these
    Material objects.
"""
cimport cython

@cython.auto_pickle(True)
cdef class Material(object):
    """"""
    def __init__(self, alpha, nr, dndT, kappa, emiss, poisson, E, rho, C, T):
        self.values.alpha   = alpha
        self.values.nr      = nr
        self.values.dndT    = dndT
        self.values.kappa   = kappa
        self.values.emiss   = emiss
        self.values.poisson = poisson
        self.values.E       = E
        self.values.T       = T
        self.values.C       = C
        self.values.rho     = rho

    @property
    def alpha(self):
        r"""Thermal expansion coefficient :math:`\alpha`"""
        return self.values.alpha

    @property
    def nr(self):
        r"""Refractive index :math:`n`"""
        return self.values.nr

    @property
    def dndT(self):
        r"""Thermo refractive coefficient :math:`\frac{dn}{dT} \: [K^{-1}]`"""
        return self.values.dndT

    @property
    def kappa(self):
        r"""Thermal conductivity :math:`\kappa \: [W m^{-1}]`"""
        return self.values.kappa

    @property
    def emiss(self):
        r"""Emissivity"""
        return self.values.emiss

    @property
    def poisson(self):
        r"""Poisson's ratio"""
        return self.values.poisson

    @property
    def E(self):
        r"""Young's modulus :math:`[\mathrm{kg} \, m^{-3}]`"""
        return self.values.E

    @property
    def rho(self):
        r"""Density :math:`[\mathrm{kg} \, m^{-3}]`"""
        return self.values.rho

    @property
    def C(self):
        r"""specific heat :math:`[J \, \mathrm{kg}^{-1}]`"""
        return self.values.C

    @property
    def T(self):
        r"""The temperature material's properties are defined at :math:`[K]`"""
        return self.values.T

Vacuum = Material(
    0, # thermal expansion coefficient
    1, # refractive index
    0, # dn/dt
    0, # thermal conductivity
    0, # emissivity
    0, # Poisson's ration
    0, # Young's modulus
    0, # density
    0, # specific heat
    0, # reference temperature
)

FusedSilica = Material(
    5.5e-7, # thermal expansion coefficient
    1.45,   # refractive index
    8.6e-6, # dn/dt
    1.38,   # thermal conductivity
    0.91,   # emissivity
    0.17,   # Poisson's ration
    7.2e10, # Young's modulus
    2202,   # density
    772,    # specific heat
    297,    # reference temperature
)

Gold = Material(
    14.13e-6, # thermal expansion coefficient
    0.258,    # refractive index
    0,        # dn/dt
    315,      # thermal conductivity
    0.05,     # emissivity
    0.42,     # Poisson's ration
    7.9e10,   # Young's modulus
    1930,     # density
    129,      # specific heat
    297,      # reference temperature
)
# Taken from Voyager GWINC
Silicon123K_sum = Material(
    1e-10,   # thermal expansion coefficient
    3.4,     # refractive index @ 2um
    1e-4,    # dn/dt
    700,     # thermal conductivity
    0.7,     # emissivity, https://www.sciencedirect.com/science/article/pii/S0017931019361289
    0.27,    # Poisson's ration
    155.8e9, # Young's modulus
    2329,    # density
    300,     # specific heat
    123,     # reference temperature
)

CaF2_300K_2um = Material(
    18.5e-6, # thermal expansion coefficient
    1.4239,  # refractive index @ 2um
    -10e-6,  # dn/dt
    9.71,    # thermal conductivity
    0.88,    # emissivity
    0.26,    # Poisson's ration
    75.8e9,  # Young's modulus
    3180,    # density
    854,     # specific heat
    300,     # reference temperature
)

# Fused silica used for iLIGO
# reference CTE (NIST SRM  739)
Corning7940 = Material(
    4.869e-07, # thermal expansion coefficient
    1.45,      # refractive index
    9.6e-6,    # dn/dt
    1.367,     # thermal conductivity
    0.9,       # emissivity
    0.167,     # Poisson's ration
    72.93E9,   # Young's modulus
    2220.00,   # density
    704.21,    # specific heat
    293.15,    # reference temperature
)

# Suprasil ref
# n, Thermal expansion coefficient from data sheet
# https://www.heraeus.com/media/media/hca/doc_hca/products_and_solutions_8/optics/Data_and_Properties_Optics_fused_silica_EN.pdf
suprasil3002_2um = Material(
    5.9e-7,  # thermal expansion coefficient
    1.499,   # refractive index
    8.89e-6, # dn/dt
    1.38,    # thermal conductivity
    0.9,     # emissivity
    0.17,    # Poisson's ration
    73.1E9,  # Young's modulus
    2203,    # density
    964,     # specific heat
    293.15,  # reference temperature
)

BK7_2um = Material(
    7.1e-6,  # thermal expansion coefficient
    1.4946,  # refractive index
    8.94E-7, # dn/dt
    1.114,   # thermal conductivity
    0.9,     # emissivity
    0.206,   # Poisson's ration
    82e9,    # Young's modulus
    2510,    # density
    858,     # specific heat
    293.15,  # reference temperature
)

#   zblan reference   Zhu X., Peyghambarian N., High-Power ZBLAN Glass Fiber Lasers: Review and Prospect, 2010
ZBLAN_2um = Material(
    17.2e-6,   # thermal expansion coefficient
    1.4956,    # refractive index
    -14.75e-6, # dn/dt
    0.628,     # thermal conductivity
    0.9,       # emissivity
    0.206,     # Poisson's ration
    58.5e9,    # Young's modulus
    4330,      # density
    151,       # specific heat
    293.15,    # reference temperature
)
