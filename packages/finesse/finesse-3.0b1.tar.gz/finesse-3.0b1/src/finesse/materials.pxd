cimport cython

# At some point we could make these all arrays and have some
# temperature dependence that could be interpolated
cdef struct material:
    double alpha   # thermal expansion coefficient
    double nr      # refractive Index
    double dndT    # dn/dt
    double kappa   # thermal conductivity
    double emiss   # emissivity
    double poisson # Poisson's ratio
    double E       # Young's modulus
    double rho     # density
    double C       # specific heat
    double T       # reference temperature

@cython.auto_pickle(True)
cdef class Material(object):
    cdef:
        material values
