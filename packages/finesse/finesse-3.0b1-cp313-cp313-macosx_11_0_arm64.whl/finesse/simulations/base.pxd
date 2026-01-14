from finesse.cymath.gaussbeam cimport beam_param


cdef struct NodeBeamParam:
    beam_param qx
    beam_param qy
    bint is_fixed # Whether the q values will be changing during a simulation


cdef class PhaseConfig:
    cdef public:
        bint zero_k00 # should phase of k0000 coefficients be zeroed
        bint zero_tem00_gouy # should Gouy phase of TEM00 be zeroed
        bint v2_transmission_phase


cdef class ModelSettings:
    cdef public:
        double fsig
        double EPSILON0_C
        double UNIT_VACUUM
        double x_scale
        bint is_modal
        int[:, ::1] homs_view
        PhaseConfig phase_config
        double lambda0, f0, k0
        int num_HOMs
        int max_n # Maximum mode index in tangential plane
        int max_m # Maximum mode index in sagittal plane


# Contains non-physical configuration data, as low-level values, to be
# used during a simulation
cdef struct SimConfigData:
    # Number of threads to use for prange loops whose
    # size is proportional to the number of modes
    int nthreads_homs
