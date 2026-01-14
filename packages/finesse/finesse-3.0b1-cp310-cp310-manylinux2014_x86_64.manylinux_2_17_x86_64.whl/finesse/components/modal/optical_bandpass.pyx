from finesse.simulations.simulation cimport BaseSimulation
from finesse.simulations.sparse.solver cimport SparseSolver


import numpy as np
cimport numpy as np

ctypedef (double*, double*) ptr_tuple_2

cdef class OpticalBandpassValues(BaseCValues):
    def __init__(self):
        cdef ptr_tuple_2 ptr = (&self.fc, &self.bandwidth)
        cdef tuple params = ("fc", "bandwidth")
        self.setup(params, sizeof(ptr), <double**>&ptr)


cdef class OpticalBandpassConnections:
    """Contains C accessible references to submatrices for
    optical connections for this element.
    """
    def __cinit__(self, object mirror, SparseSolver mtx):
        # Only 1D arrays of submatrices as no frequency coupling happening
        cdef int Nf = mtx.optical_frequencies.size
        self.P1i_P2o = SubCCSView1DArray(Nf)
        self.P2i_P1o = SubCCSView1DArray(Nf)
        self.ptrs.P1i_P2o = <PyObject**>self.P1i_P2o.views
        self.ptrs.P2i_P1o = <PyObject**>self.P2i_P1o.views


cdef class OpticalBandpassWorkspace(KnmConnectorWorkspace):
    def __init__(self, owner, BaseSimulation sim, object HOM_filter_index):
        cdef int index
        super().__init__(
            owner,
            sim,
            OpticalBandpassConnections(owner, sim.carrier),
            OpticalBandpassConnections(owner, sim.signal) if sim.signal else None,
            OpticalBandpassValues()
        )
        # Casting python objects to known types for faster access
        self.cvalues = self.values
        self.carrier_opt_conns = self.carrier.connections
        if sim.signal:
            self.signal_opt_conns = self.signal.connections
        else:
            self.signal_opt_conns = None

        if HOM_filter_index is not None:
            self.M = np.zeros((sim.model_settings.num_HOMs, sim.model_settings.num_HOMs), dtype=complex)
            index = int(HOM_filter_index)
            self.M[index, index] = 1 # transmit a single HOM
        else:
            self.M = np.eye(sim.model_settings.num_HOMs, dtype=complex)


cdef void fill_optical_matrix(
        OpticalBandpassWorkspace ws,
        SparseSolver matrix,
        optical_bandpass_connections *connections
    ) noexcept:
    cdef double B = 2*np.pi*ws.cvalues.bandwidth
    cdef complex_t H
    cdef frequency_info_t *frequencies = matrix.optical_frequencies.frequency_info
    cdef Py_ssize_t i
    cdef complex_t[:, ::1] M = ws.K12.data @ ws.M

    for i in range(matrix.optical_frequencies.size):
        H = 1 / (1 + 1j*(2*np.pi*abs(frequencies[i].f-ws.cvalues.fc))/B)
        if connections.P1i_P2o:
            (<SubCCSView>connections.P1i_P2o[frequencies[i].index]).fill_negative_za_zm(
                H, M
            )

        if connections.P2i_P1o:
            (<SubCCSView>connections.P2i_P1o[frequencies[i].index]).fill_negative_za_zm(
                H, M
            )


optical_bandpass_carrier_fill = FillFuncWrapper.make_from_ptr(c_fill_carrier)
cdef object c_fill_carrier(ConnectorWorkspace ws) :
    fill_optical_matrix(
        ws,
        ws.sim.carrier,
        &(<OpticalBandpassWorkspace>ws).carrier_opt_conns.ptrs
    )

optical_bandpass_signal_fill = FillFuncWrapper.make_from_ptr(c_fill_signal)
cdef object c_fill_signal(ConnectorWorkspace ws) :
    fill_optical_matrix(
        ws,
        ws.sim.signal,
        &(<OpticalBandpassWorkspace>ws).signal_opt_conns.ptrs
    )
