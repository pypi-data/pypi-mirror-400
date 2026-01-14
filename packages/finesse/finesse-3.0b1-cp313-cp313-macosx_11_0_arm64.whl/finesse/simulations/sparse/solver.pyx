import logging
import weakref
import numpy as np
cimport numpy as np
from finesse.components.general import NoiseType
from finesse.components.node import NodeType
from finesse.frequency cimport Frequency, FrequencyContainer
from finesse.components.workspace cimport ConnectionSetting
from finesse.cymath.complex cimport complex_t
from finesse.components.workspace cimport ConnectorWorkspace, ConnectorMatrixSimulationInfo, fill_list_t

from finesse.cymath.cmatrix cimport SubCCSView1DArray, SubCCSView2DArray
from ..simulation cimport CNodeInfo

LOGGER = logging.getLogger(__name__)


cdef class SparseSolver(HOMSolver):
    """This class overrides the BaseSolver and adds the features required to use a
    sparse (compressed column, CCS) matrix. The type of sparse solver is not assumed
    here and must be provided by the `matrix_type` argument. This should be inherited
    and the matrix type provided for specific linear algebra solvers.

    Notes
    -----
    This is the original solver used in Finesse 3.
    """

    def __init__(
        self,
        matrix_type,
        str name,
        list nodes,
        FrequencyContainer optical_frequencies,
        dict signal_frequencies,
        bint is_signal_matrix,
        bint forced_refill,
        dict node_aliases,
        int num_optical_homs,
        bint debug_mode = False,
        dict matrix_kwargs=None,
    ):
        if matrix_kwargs is None:
            matrix_kwargs = {}
        self._M = matrix_type(name, **matrix_kwargs)
        self.out_view = None

        super().__init__(
            name,
            nodes,
            optical_frequencies,
            signal_frequencies,
            is_signal_matrix,
            forced_refill,
            node_aliases,
            num_optical_homs,
            debug_mode=debug_mode,
        )

    @property
    def M(self):
        """A weak reference to the underlying Matrix object.

        .. note::

            References to the Matrix should not be kept.

        :`getter`: Returns a weak reference to the underlying matrix (read-only).
        """
        return weakref.ref(self._M)

    def _add_matrix_equations(self, node_2_index):
        """Adds elements to the system matrix that must be solved for. By default this
        will add all nodes into the matrix.

        Parameters
        ----------
        node_2_index : dict
            Maps a full node name to a node index
        """
        cdef:
            CNodeInfo node_inf

        for n, node_info_idx in node_2_index.items():
            if n in self.node_aliases:
                continue # node is being mapped so doesn't have any equations in matrix
            node_inf = self._c_node_info[node_info_idx]
            Nsm = node_inf.nfreqs
            Neq = node_inf.nhoms

            for freq in range(Nsm):
                fidx = self.findex(n, freq)  # Get index for this submatrix
                diagonal = self._M.declare_equations(
                    Neq, fidx, f"I,node={n},f={freq},fidx={fidx},Neq={Neq}"
                )
                self._diagonals[fidx] = diagonal

    def _element_couples_frequencies(self, owner, nio):
        from finesse.components import FrequencyGenerator
        # Frequency generators might couple fields, they might not.
        # so by default we set them to.
        is_freq_gen = isinstance(owner, FrequencyGenerator)
        # If the node type is different then we also are probably
        # coupling multiple frequencies together. For examaple,
        # Rad pressure, couples all sideband/carrier beats into
        # a single force state
        if hasattr(owner, "_couples_frequency"):
            does_f_couple = owner._couples_frequency
        else:
            does_f_couple = None

        result = (
            (
                is_freq_gen
                or (nio[0].type != nio[1].type)
                or does_f_couple is not None
            )
            # Only if one of the nodes is optical do we have multiple
            # frequencies to couple into
            and (nio[0].type == NodeType.OPTICAL or nio[1].type == NodeType.OPTICAL)
        )
        return (result, does_f_couple)

    cpdef assign_operators(self, connector_workspaces):
        cdef:
            Frequency ifreq, ofreq
            bint couples_f
            ConnectorWorkspace ws

        if self._submatrices:
            raise Exception("Submatrices already assigned")

        self._submatrices  = {}
        self._diagonals = {}
        self.connections  = {}
        # Add all nodes to the matrix for calculating
        self._add_matrix_equations(self.node_2_index)

        id_owner = -1
        # for everything that needs to fill the matrix...
        for ws in connector_workspaces:
            owner = ws.owner
            id_owner += 1
            ws.owner_id = id_owner # store the owner index

            idx_connection = -1

            # For each connection this element wants...
            for name in owner._registered_connections:
                #print(name)
                idx_connection += 1

                if self.is_signal_matrix:
                    ws_conn = ws.signal.connections
                    conn_settings = ws.signal.connection_settings
                else:
                    ws_conn = ws.carrier.connections
                    conn_settings = ws.carrier.connection_settings
                # convert weak ref (input, output)
                nio = []
                for _ in owner._registered_connections[name]:
                    nio.append(owner.nodes[_])

                enabled_check = owner._enabled_checks.get(name, None)
                if enabled_check:
                    enabled_check = enabled_check()
                else:
                    enabled_check = True

                nio = tuple(nio)

                # If we are a carrier matrix only compute optics, no AC electronics or mechanics
                if not self.is_signal_matrix:
                    if (nio[0].type is not NodeType.OPTICAL
                        or nio[1].type is not NodeType.OPTICAL) or not enabled_check:
                        #print("excluded", name)
                        continue
                else:
                    # elec and mech nodes from a connection are not all necessarily modelled
                    # check if they are in the node list for this simulation
                    if (not (nio[0].full_name in self.node_2_index and nio[1].full_name in self.node_2_index)) or not enabled_check:
                        # If this connection hasn't been allocated then we set the
                        # matrix view array which is stored in the workspace connections info
                        # to None, so that fill methods can quickly check if they should
                        # touch it or not
                        idx_connection -= 1 # reduce connection idx count as we aren't allocating it now
                        if not hasattr(ws_conn, name):
                            setattr(ws_conn, name, None)
                        setattr(ws_conn, name + "_idx", -1)
                        continue

                dim = 0 # Dimension of the frequency coupling matrix
                # If we are not using a specialist connections object then
                # we need to add something to the generic Connections
                Nfi = self._c_node_info[self.node_id(nio[0])].nfreqs
                Nfo = self._c_node_info[self.node_id(nio[1])].nfreqs

                #print("!!!", owner, nio, Nfi, Nfo)
                ifreqs = self.get_node_frequencies(nio[0])
                ofreqs = self.get_node_frequencies(nio[1])
                #print("   in", nio[0], ifreqs, "\n   out", nio[1], ofreqs)
                couples_f, does_f_couple = self._element_couples_frequencies(owner, nio)
                #print(f"   is_freq_gen={is_freq_gen} couples_f={couples_f}")

                if not hasattr(ws_conn, name):
                    #print("NOT DEFINED", )
                    if couples_f:
                        # We will need a 2D array of submatrices to describe how multiple
                        # elements will couple together
                        setattr(ws_conn, name, np.empty((Nfi, Nfo) , dtype=object))
                        dim = 2
                    else:
                        # if not, just a diagonal
                        setattr(ws_conn, name, np.empty(Nfi, dtype=object))
                        dim = 1
                else:
                    #print("DEFINED", name, ws_conn)
                    # If a specialist object already exists lets probe it's shape
                    # as that will describe what can actually be coupled or not
                    dim = getattr(ws_conn, name).ndim

                # keep references for the matrices for each connection
                _conn = getattr(ws_conn, name)
                if not isinstance(_conn, (SubCCSView1DArray, SubCCSView2DArray, np.ndarray)):
                    raise ValueError(f"{ws_conn}.{name} should be a SubCCSView1DArray, SubCCSView2DArray, or np.ndarray not {type(_conn)}")
                self.connections[nio] = getattr(ws_conn, name)

                # Loop over all the frequencies we can couple between and add
                # submatrixes to the overall model
                for ifreq in ifreqs:
                    for ofreq in ofreqs:
                        #print("   &&& TRY ", ifreq, ofreq, does_f_couple)
                        # For each input and output frequency check if our
                        # element wants to couple them at this
                        if (
                            couples_f
                            and (does_f_couple is not None and not does_f_couple(ws, name, ifreq, ofreq))
                        ):
                            continue
                        elif not couples_f and ifreq.index != ofreq.index:
                            # If it doesn't couple frequencies and the
                            # frequencies are different then ignore
                            continue

                        #print("   &&& ACCEPT ", ifreq, ofreq)

                        iodx = []  # submatrix indices
                        tags = []  # descriptive naming tags for submatrix key
                        #key_name = re.sub(r"^[^.]*\.", "", name)
                        #key_name = re.sub(r">[^.]*\.", ">", key_name)
                        key = [id_owner, idx_connection]

                        # Get simulation unique indices for submatrix
                        # position. How we get these depends on the type of
                        # the nodes involved
                        for freq, node in zip((ifreq, ofreq), nio):
                            iodx.append(self.findex(node, freq.index))
                            tags.append(freq.name)
                            key.append(freq.index)

                        assert len(iodx) == 2
                        assert len(key) == 4

                        # Here we determined whether to conjugate fill a submatrix view or not
                        conjugate_fill = False
                        if self.is_signal_matrix:
                            if nio[0].type == nio[1].type == NodeType.OPTICAL:
                                # Opt-2-Opt lower sideband is conjugated
                                if ifreq.audio_order < 0 and ofreq.audio_order < 0:
                                    conjugate_fill = True
                            elif nio[0].type == NodeType.OPTICAL and ifreq.audio_order < 0:
                                # Opt-2-? lower sideband is conjugated
                                conjugate_fill = True
                            elif nio[1].type == NodeType.OPTICAL and ofreq.audio_order < 0:
                                # ?-2-Opt lower sideband is conjugated
                                conjugate_fill = True

                        if tuple(key) not in self._submatrices:
                            smname = "{}__{}__{}".format(name, *tags)

                            #print("Requesting:", key)

                            # Then we get a view of the underlying matrix which we set the values
                            # with. Store one for each frequency. By requesting this view we are
                            # telling the matrix that these elements should be non-zero in the
                            # model.
                            setting = conn_settings.get(name)
                            if setting is None:
                                # default to using full matrix if nothing set
                                setting = ConnectionSetting.MATRIX

                            if setting == ConnectionSetting.DIAGONAL:
                                #print("!!!D", owner, name, self.is_signal_matrix)
                                SM = self._M.declare_subdiagonal_view(*iodx, smname, conjugate_fill)
                            elif setting == ConnectionSetting.MATRIX:
                                #print("!!!M", owner, name, self.is_signal_matrix)
                                SM = self._M.declare_submatrix_view(*iodx, smname, conjugate_fill)
                            elif setting == ConnectionSetting.DISABLED:
                                #print("!!!DIS", owner, name, self.is_signal_matrix)
                                SM = None
                            else:
                                raise Exception(f"Unhandled setting {setting}")
                            #print("!@#", owner, name, self.is_signal_matrix, dim)
                            try:
                                if dim == 1:
                                    getattr(ws_conn, name)[ifreq.index] = SM
                                elif dim == 2:
                                    getattr(ws_conn, name)[ifreq.index, ofreq.index] = SM
                                else:
                                    raise Exception(f"Unhandled dimension size {dim}")
                            except IndexError:
                                raise IndexError(f"Error setting submatrix to connection {name} in {owner}. "
                                                  "Size of array of submatricies wrong, number of frequencies "
                                                  "assumed probably incorrect.")

                            setattr(ws_conn, name + "_idx", idx_connection)
                            self._submatrices[tuple(key)] = SM
                        else:
                            # Check if we've just requested the same submatrix.
                            SM = self._submatrices[tuple(key)]
                            if SM.from_idx != iodx[0] or SM.to_idx != iodx[1]:
                                raise Exception(
                                    "Requested submatrix has already been requested,"
                                    "but new one has different indices"
                                )
                            else:
                                continue
        #print("done")

    cpdef assign_noise_operators(self, connector_workspaces):
        import itertools
        cdef CNodeInfo node_inf
        cdef Frequency ifreq, ofreq
        cdef ConnectorWorkspace ws
        cdef int i

        self._noise_submatrices  = {}

        for noise_type, sources in self.noise_sources.items():
            M = self._noise_matrices[noise_type]
            self._noise_submatrices[noise_type] = {}

            # Add in the diagonal elements of the matrices
            for n, node_info_idx in self.node_2_index.items():
                if n in self.node_aliases:
                    continue # node is being mapped so doesn't have any equations in matrix
                node_inf = self._c_node_info[node_info_idx]
                Nsm = node_inf.nfreqs
                Neq = node_inf.nhoms
                for freq in range(Nsm):
                    fidx = self.findex(n, freq)  # Get index for this submatrix
                    mat = M.declare_equations(
                        Neq, fidx, f"I,node={n},f={freq},fidx={fidx},Neq={Neq}"
                    )
                    self._noise_submatrices[noise_type][fidx] = mat

            for comp, nodes in sources:
                ws = None
                for _ws in self.workspaces.to_noise_refill:
                    if _ws.owner is comp:
                        ws = _ws
                        break
                if ws is None:
                        raise Exception("Noise source not registered")
                for name, node in nodes:
                    freqs = self.get_node_frequencies(node)

                    if hasattr(comp, "_couples_noise"):
                        couples_noise = comp._couples_noise
                    else:
                        couples_noise = None

                    # Loop over all the noise sidebands we can couple between and add
                    # submatrixes to the overall model
                    for ifreq, ofreq in itertools.product(freqs, freqs):
                        if couples_noise is None:
                            if ifreq.index != ofreq.index:
                                continue
                        elif not couples_noise(ws, node, noise_type, ifreq, ofreq):
                            continue

                        iodx = []  # submatrix indices
                        tags = []  # descriptive naming tags for submatrix key
                        key = [ws.owner_id, self.node_id(node)]

                        # Get simulation unique indices for submatrix position.
                        for freq in [ifreq, ofreq]:
                            iodx.append(self.findex(node, freq.index))
                            tags.append(freq.name)
                            key.append(freq.index)

                        assert len(iodx) == 2
                        assert len(key) == 4

                        # Here we determined whether to conjugate fill a submatrix view or not
                        conjugate_fill = False
                        if node.type == NodeType.OPTICAL:
                            # Opt-2-Opt lower sideband is conjugated
                            if ifreq.audio_order < 0 and ofreq.audio_order < 0:
                                conjugate_fill = True

                        if tuple(key) not in self._noise_submatrices[noise_type]:
                            smname = "{}__{}__{}".format(name, *tags)

                            if ifreq == ofreq:
                                SM = self._noise_submatrices[noise_type][self.findex(node, ifreq.index)]
                            else:
                                SM = M.declare_submatrix_view(*iodx, smname, conjugate_fill)
                            getattr(ws.signal.noise_sources, name)[ifreq.index, ofreq.index] = SM

                            self._noise_submatrices[noise_type][tuple(key)] = SM
                        else:
                            # Check if we've just requested the same submatrix.
                            sm = self._noise_submatrices[noise_type][tuple(key)]
                            if sm.from_idx != iodx[0] or sm.to_idx != iodx[1]:
                                raise Exception(
                                    "Requested submatrix has already been requested,"
                                    "but new one has different indices"
                                )
                            else:
                                continue

        if NoiseType.QUANTUM in self.noise_sources:
            M = self._noise_matrices[NoiseType.QUANTUM]
            for ws in connector_workspaces:
                for i in range(ws.input_noise.num_nodes):
                    n = ws.input_noise.node_info[i].idx
                    node_inf = self._c_node_info[n]
                    Nsm = node_inf.nfreqs
                    for freq in range(Nsm):
                        fidx = self.findex_fast(n, freq)  # Get index for this submatrix
                        ws.input_noise.nodes[i, freq] = self._noise_submatrices[NoiseType.QUANTUM][fidx]
                for i in range(ws.output_noise.num_nodes):
                    n = ws.output_noise.node_info[i].idx
                    node_inf = self._c_node_info[n]
                    Nsm = node_inf.nfreqs
                    for freq in range(Nsm):
                        fidx = self.findex_fast(n, freq)  # Get index for this submatrix
                        ws.output_noise.nodes[i, freq] = self._noise_submatrices[NoiseType.QUANTUM][fidx]

    def print_matrix(self):
        self._M.print_matrix()

    cpdef clear_rhs(self):
        self._M.clear_rhs()

    cpdef set_source(self, object node, int freq_idx, int hom_idx, complex value):
        self._M.set_rhs(self.field_fast(self.node_id(node), freq_idx, hom_idx), value)

    cdef int set_source_fast(self, Py_ssize_t node_id, Py_ssize_t freq_idx, Py_ssize_t hom_idx, complex_t value, Py_ssize_t rhs_index) except -1:
        return self._M.c_set_rhs(self.field_fast(node_id, freq_idx, hom_idx), value, rhs_index)

    cdef int set_source_fast_2(self, Py_ssize_t rhs_idx, complex_t value) except -1:
        return self._M.c_set_rhs(rhs_idx, value, 0)

    cdef int set_source_fast_3(self, Py_ssize_t rhs_idx, complex_t value, Py_ssize_t rhs_index) except -1:
        return self._M.c_set_rhs(rhs_idx, value, rhs_index)

    cpdef construct(self):
        # Initialising the simulation expects there to be a self._M class that handles the
        # matrix build/memory/etc. This must be set before initialising.
        self._M.construct()
        if self.is_signal_matrix:
            for M in self._noise_matrices.values():
                M.construct(diagonal_fill=0)
        # Point output of matrix to RHS view which klu replaces with solution after solving
        self.out_view = self._M.rhs_view[0]
        self.out_view_size = len(self._M.rhs_view[0])

    cpdef initial_fill(self):
        cdef Py_ssize_t i
        cdef ConnectorWorkspace ws
        cdef ConnectorMatrixSimulationInfo cmsinfo
        cdef fill_list_t *fill_list

        self.optical_frequencies.initialise_frequency_info()
        if self.is_signal_matrix:
            for i in range(len(self.unique_elec_mech_fcnts)):
                (<FrequencyContainer>self.unique_elec_mech_fcnts[i]).initialise_frequency_info()

        for ws in self.workspaces.to_initial_fill:
            ws.update_parameter_values()
            if self.is_signal_matrix:
                cmsinfo = ws.signal
            else:
                cmsinfo = ws.carrier
            fill_list = &cmsinfo.matrix_fills

            for i in range(fill_list.size):
                if fill_list.infos[i].fn_c:
                    fill_list.infos[i].fn_c(ws)
                elif fill_list.infos[i].fn_py:
                    (<object>fill_list.infos[i].fn_py).__call__(ws)

    cpdef refill(self):
        cdef Py_ssize_t i, j
        cdef ConnectorWorkspace ws
        cdef fill_list_t *fill_list

        if self.any_frequencies_changing:
            self.update_frequency_info()

        for i in range(self.workspaces.num_to_refill):
            ws = <ConnectorWorkspace>self.workspaces.ptr_to_refill[i]
            # TODO (sjr) Probably don't need this update call for now
            #            (see start of self.run method)
            ws.update_parameter_values()
            if self.is_signal_matrix:
                fill_list = &ws.signal.matrix_fills
            else:
                fill_list = &ws.carrier.matrix_fills

            for j in range(fill_list.size):
                if fill_list.infos[j].refill or self.forced_refill:
                    if fill_list.infos[j].fn_c:
                        fill_list.infos[j].fn_c(ws)
                    elif fill_list.infos[j].fn_py:
                        (<object>fill_list.infos[j].fn_py).__call__(ws)

        # As we have changed the matrix elements we need to refactor
        self.refactor()

    cpdef refill_rhs(self):
        # Map to fill for this solver
        self.fill_rhs()

    cpdef fill_rhs(self):
        cdef ConnectorWorkspace ws
        cdef ConnectorMatrixSimulationInfo sys_ws
        for ws in self.workspaces.to_rhs_refill:
            ws.update_parameter_values()

            if self.is_signal_matrix:
                sys_ws = ws.signal
            else:
                sys_ws = ws.carrier

            if sys_ws.fn_rhs_c is not None:
                sys_ws.fn_rhs_c.func(ws)
            elif sys_ws.fn_rhs_py is not None:
                sys_ws.fn_rhs_py(ws)

    cpdef fill_noise_inputs(self):
        cdef ConnectorWorkspace ws
        for ws in self.workspaces.to_noise_input_refill:
            if NoiseType.QUANTUM in self.noise_sources:
                if ws.signal.fn_quantum_noise_input_c is not None:
                    ws.signal.fn_quantum_noise_input_c.func(ws)
                elif ws.signal.fn_quantum_noise_input_py is not None:
                    ws.signal.fn_quantum_noise_input_py(ws)

        for ws in self.workspaces.to_noise_refill:
            if NoiseType.QUANTUM in self.noise_sources:
                if ws.signal.fn_quantum_noise_c is not None:
                    ws.signal.fn_quantum_noise_c.func(ws)
                elif ws.signal.fn_quantum_noise_py is not None:
                    ws.signal.fn_quantum_noise_py(ws)

    cpdef destruct(self):
        """This is called when finishing and unbuilding the simulation.

        Classes that override this call should mindful of what this method is doing to
        and call it.
        """
        self._M = None
        HOMSolver.destruct(self)
