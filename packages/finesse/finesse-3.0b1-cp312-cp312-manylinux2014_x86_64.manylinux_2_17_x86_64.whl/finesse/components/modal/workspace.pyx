cimport cython

import logging

import numpy as np
cimport numpy as np

from ...env import warn

from finesse.cymath.complex cimport carg, cexp
from scipy.linalg.cython_blas cimport zscal, zgemm

from libc.stdlib cimport free, calloc
from cpython.ref cimport PyObject

from finesse.knm cimport (
    KnmMatrix,
    knm_bh_workspace,
    knm_bh_ws_init,
    knm_bh_ws_free,
    knm_bh_ws_is_changing,
    knm_bh_ws_recompute_mismatch,
    knm_bh_ws_recompute,
    knm_bh_ws_recompute_misalignment,
)
from finesse.knm.bayerhelms cimport fast_compute_knm_matrix_bh
from finesse.cymath.gaussbeam cimport bp_beamsize
from finesse.knm.matrix cimport knm_loss, c_flip_odd_horizontal
from finesse.cymath.cmatrix cimport SubCCSView
from finesse.components.workspace cimport ConnectorWorkspace, FillFuncWrapper, NoiseInfo
from finesse.components.general import NodeType, NoiseType
from finesse.cymath.gaussbeam cimport c_transform_q
from finesse.cymath.homs cimport unm_ws_recache_from_bp, unm_factor_store_recache
from finesse.frequency cimport frequency_info_t
from finesse.simulations.base cimport NodeBeamParam
from finesse.knm.maps cimport (
    set_knm_map_workspace,
    free_knm_map_workspace,
    init_knm_map_workspace,
    c_scattering_coefficients_to_KnmMatrix,
    update_map_data_in_workspace
)
from finesse.knm.integrators cimport c_riemann_optimised, c_outer_conj_product_2, update_U_xy_array
from finesse.utilities.collections cimport OrderedSet


LOGGER = logging.getLogger(__name__)

cdef double[:,::1] abcd_unity = np.eye(2, dtype=float)


cdef class KnmConnectorWorkspace(ConnectorWorkspace):
    def __cinit__(self, *args, **kwargs):
        self.onode_ids = NULL
        self.oconn_info = NULL
        self.Kws = NULL

    def __init__(self, object owner, object sim, *args, **kwargs):
        from finesse.simulations.simulation import BaseSimulation
        assert(isinstance(sim, BaseSimulation))
        ConnectorWorkspace.__init__(self, owner, sim, *args, **kwargs)

        # Here we automatically generate the coupling strings used
        # for generating the Knm matricies. We use the optical to optical
        # connections that have been registered, the port number is taken
        # from the order in which they are added to the component. I guess
        # there could also be a more explicit defition of the port "index"
        # given in the _add_port method but we'll use this for now.

        # TODO ddb could store index in port object perhaps, along with the
        # list of optical ports
        self.o2o = owner.all_internal_optical_connections
        oports = list(p for p in owner.ports if p.type == NodeType.OPTICAL)

        self.N_opt_ports = len(oports)
        self.N_opt_conns = len(self.o2o)

        if self.onode_ids != NULL or self.oconn_info != NULL or self.Kws != NULL:
            raise MemoryError()

        self.onode_ids = <Py_ssize_t*> calloc(self.N_opt_ports * 2, sizeof(Py_ssize_t))
        if not self.onode_ids:
            raise MemoryError()

        self.oconn_info = <KnmInfo*> calloc(self.N_opt_conns, sizeof(KnmInfo))
        if not self.oconn_info:
            raise MemoryError()

        # 2 lots per connection because of x and y planes
        self.Kws = <knm_bh_workspace*> calloc(2*self.N_opt_conns, sizeof(knm_bh_workspace))
        if not self.Kws:
            raise MemoryError()

        # Indexes for access the simulation trace, 2 because we have inputs and outputs
        self.trace_node_indices = <Py_ssize_t*> calloc(self.N_opt_ports * 2, sizeof(Py_ssize_t))
        if not self.trace_node_indices:
            raise MemoryError()

        # need these node ids for the simulation for indexing traces
        # Signal and carrier all have the same optical node IDs so
        # use carrier here because it should always exist
        for i, p in enumerate(oports):
            self.onode_ids[2*i] = sim.carrier.node_id(p.i)
            self.onode_ids[2*i+1] = sim.carrier.node_id(p.o)
            self.trace_node_indices[2*i] = sim.trace_node_index[p.i]
            self.trace_node_indices[2*i+1] = sim.trace_node_index[p.o]

        cdef np.ndarray[double, ndim=1, mode="c"] scatter_loss
        self.__knm_matrices = []

        for i, (conn, (f, t)) in enumerate(self.o2o.items()):
            # TODO ddb should probably use some fixed index rather than a list of the order
            # they are defined in the element definition
            a = oports.index(f.port)
            b = oports.index(t.port)
            coupling = f"{a+1}{b+1}"
            self.oconn_info[i].ptr_owner = <PyObject*>self
            self.oconn_info[i].from_port_idx = a
            self.oconn_info[i].to_port_idx = b
            self.oconn_info[i].K_ws_x = &self.Kws[2*i]
            self.oconn_info[i].K_ws_y = &self.Kws[2*i+1]
            self.oconn_info[i].abcd_x = &abcd_unity[0,0]
            self.oconn_info[i].abcd_y = &abcd_unity[0,0]
            # The final matrix to be used for filling
            knm = KnmMatrix(self.sim.model_settings.homs_view, self.owner.name, coupling)
            self.oconn_info[i].knm_mtx = &knm.mtx
            self.__knm_matrices.append(knm) # store these objects for access later if needed
            try:
                setattr(self, f"K{coupling}", knm)
            except AttributeError:
                raise AttributeError(f"Cannot set K{coupling} in {self}. Check that this workspace is a Python object or if it is a Cython workspace that K{coupling} is defined.")

            # Make the buffer of knm loss data
            scatter_loss = np.zeros(self.sim.model_settings.num_HOMs)
            try:
                setattr(self, f"K{coupling}_loss", scatter_loss)
            except AttributeError:
                raise AttributeError(f"Cannot set K{coupling}_loss in {self}. Check that this workspace is a Python object or if it is a Cython workspace that K{coupling}_loss is defined.")
            # Keep ptr to the buffer for use in compute_knm_losses
            self.oconn_info[i].loss = &scatter_loss[0]

        self.total_losses = np.zeros(self.sim.model_settings.num_HOMs)
        if sim.signal:
            self.signal.set_fill_noise_function(NoiseType.QUANTUM, optical_quantum_noise_knm)


    def __dealloc__(self):
        cdef:
            int i

        if self.onode_ids:
            free(self.onode_ids)

        if self.oconn_info:
            for i in range(self.N_opt_conns):
                if self.oconn_info[i].use_map:
                    free_knm_map_workspace(&self.oconn_info[i].map_ws)
            free(self.oconn_info)

        free(self.trace_node_indices)

        if self.Kws:
            for i in range(2*self.N_opt_conns):
                knm_bh_ws_free(&self.Kws[i])

            free(self.Kws)

        if self.__knm_matrices:
            self.__knm_matrices.clear()


    cpdef set_knm_info(self, connection,
        double[:,::1] abcd_x = abcd_unity,
        double[:,::1] abcd_y = abcd_unity,
        double nr_from=1, double nr_to=1,
        bint is_transmission=False,
        Parameter beta_x = None,
        double beta_x_factor = 0,
        Parameter beta_y = None,
        double beta_y_factor = 0,
        Parameter alpha = None,
        Map apply_map = None,
        double map_phase_factor = 1,
        bint map_fliplr = False
    ) :
        """
        Python facing method to set how Knm calculations should be handled for a
        particular connection. When the workspace is being created this should be called
        if modal simualtions are being used. This then sets which ABCD matricies to use,
        various parameters required, and whether the connection is a transmission or
        reflection.

        This method should only be called once with the required settings. Calling it
        again will rewrite settings for this connection.

        Parameters
        ----------
        abcd_x, abcd_y : double[:,::1]
            ABCD matrices that transform some input beam parameter to the output
            of this connection

        nr_from, nr_to : double
            refractive index at the input and output of this connection

        is_transmission : bool
            True if this connection represents a transmission through an element

        beta_x, beta_y : Parameter
            Parameter objects that reference a yaw (beta_x) and pitch (beta_y)
            misalignment

        beta_x_factor, beta_y_factor : double
            Scaling factor for misalignment parameters

        alpha : Parameter
            Macroscopic angle of incidence parameter for the element

        apply_map : Map
            When set this will apply the map object to this connection

        map_fliplr : bool
            When True the map is flipped left-to-right when computing the scattering
            coefficients
        """
        cdef:
            KnmInfo *conn
            int index
            object model = self.sim.model

        if abcd_x.shape[0] != abcd_x.shape[1] != 2:
            raise Exception("ABCD X is not 2x2")
        if abcd_y.shape[0] != abcd_y.shape[1] != 2:
            raise Exception("ABCD Y is not 2x2")
        # First find the connection str in our connections then store the information)
        if connection not in self.o2o:
            raise Exception(f"Connection {connection} is not a valid connection in the element {self.owner}")

        index = list(self.o2o.keys()).index(connection)
        conn = &self.oconn_info[index]
        conn.has_been_set = True
        conn.abcd_x = &abcd_x[0, 0]
        conn.abcd_y = &abcd_y[0, 0]
        conn.is_transmission = is_transmission
        conn.nr_from = nr_from
        conn.nr_to = nr_to
        conn.use_map = apply_map is not None
        conn.use_bh = True
        conn.bhelms_mtx_func = fast_compute_knm_matrix_bh

        if conn.use_map:
            set_knm_map_workspace(model, &conn.map_ws, apply_map, self.sim.model_settings.k0, map_phase_factor)
            conn.map_fliplr = map_fliplr

        if beta_x is not None:
            # If the value of the parameter is a symbolic reference, at this point
            # the c_value of the parameter will not be updated yet
            # https://gitlab.com/ifosim/finesse/finesse3/-/issues/691
            beta_x._reset_cvalue()
            conn.beta_x = &beta_x.__cvalue
            conn.beta_x_is_changing = beta_x.is_changing if beta_x is not None else False
            conn.beta_x_factor = beta_x_factor
        if beta_y is not None:
            # If the value of the parameter is a symbolic reference, at this point
            # the c_value of the parameter will not be updated yet
            # https://gitlab.com/ifosim/finesse/finesse3/-/issues/691
            beta_y._reset_cvalue()
            conn.beta_y = &beta_y.__cvalue
            conn.beta_y_is_changing = beta_y.is_changing if beta_y is not None else False
            conn.beta_y_factor = beta_y_factor
        if alpha is not None:
            # If the value of the parameter is a symbolic reference, at this point
            # the c_value of the parameter will not be updated yet
            # https://gitlab.com/ifosim/finesse/finesse3/-/issues/691
            alpha._reset_cvalue()
            conn.alpha = &alpha.__cvalue
            conn.alpha_is_changing = alpha.is_changing
            if alpha.is_changing:
                raise NotImplementedError("Changing angle of incidence not supported yet")


    cdef initialise_knm_workspaces(KnmConnectorWorkspace self) :
        cdef:
            NodeBeamParam *q_from
            NodeBeamParam *q_to
            NodeBeamParam *q1
            NodeBeamParam *q2
            KnmInfo *info
            KnmMatrix knm
            # From Beam parameters transformed by ABCD
            complex_t qx_from_trns, qy_from_trns

            double lambda0 = self.sim.model_settings.lambda0
            int maxtem = max(self.sim.model_settings.max_n, self.sim.model_settings.max_m)
            int i = 0
            double beta_x, beta_y

        oconn_names = tuple(self.o2o.keys())
        # Loop over the node ids stored in input, output pairs and get the
        # beam param data
        for i in range(self.N_opt_conns):
            info = &self.oconn_info[i]
            coupling = f"{info.from_port_idx+1}{info.to_port_idx+1}"

            if not info.has_been_set:
                raise Exception(f"Information for connection {oconn_names[i]} at {self.owner.name} has not been set with `set_knm_info`")

            if info.abcd_x == NULL:
                raise Exception(f"Knm info ABCDx for connection {oconn_names[i]} at {self.owner.name} is NULL")
            if info.abcd_y == NULL:
                raise Exception(f"Knm info ABCDy for connection {oconn_names[i]} at {self.owner.name} is NULL")
            if info.beta_x == NULL and info.beta_x_factor != 0:
                raise Exception(f"Knm info beta_x for connection {oconn_names[i]} at {self.owner.name} is NULL but has a beta_x_factor set")
            if info.beta_y == NULL and info.beta_y_factor != 0:
                raise Exception(f"Knm info beta_y for connection {oconn_names[i]} at {self.owner.name} is NULL but has a beta_y_factor set")

            q_from = &self.sim.trace[self.trace_node_indices[2*info.from_port_idx]]
            q_to = &self.sim.trace[self.trace_node_indices[2*info.to_port_idx+1]]
            # Get any misalignment factor is one has been set
            beta_x = info.beta_x[0] if info.beta_x else 0
            beta_y = info.beta_y[0] if info.beta_y else 0

            info.use_bh = True # always use/initialise BH for now

            if not info.use_map or (info.use_map and not info.map_ws.is_focusing_element):
                # we're using a map and it's not a focusing element map, or just not using a map
                # then use BH for mode projection.
                # 'From' Beam parameters after propagation through the connections ABCD
                qx_from_trns = c_transform_q(info.abcd_x, q_from.qx.q, info.nr_from, info.nr_to)
                qy_from_trns = c_transform_q(info.abcd_y, q_from.qy.q, info.nr_from, info.nr_to)
            elif info.use_map and info.map_ws.is_focusing_element:
                # BH is just doing tilts so use output mode
                qx_from_trns = q_to.qx.q
                qy_from_trns = q_to.qy.q

            # print("")
            # print("! Knm flags", self.owner.name)
            # print("! Connection port", info.from_port_idx+1, "->", info.to_port_idx+1)
            # print("! use BH", info.use_bh)
            # print("! use map", info.use_map)
            # print("! q_from changing", q_from.is_changing)
            # print("! q_to changing", q_to.is_changing)
            # print("! beta_x changing", info.beta_x_is_changing)
            # print("! beta_y changing", info.beta_y_is_changing)
            # print("! map changing", info.map_ws.map_is_changing)

            # Initialise the Knm workspaces with the current values
            if info.use_bh:
                knm_bh_ws_init(
                    info.K_ws_x, qx_from_trns, q_to.qx.q, beta_x, info.beta_x_factor, info.nr_to, lambda0, maxtem
                )
                knm_bh_ws_init(
                    info.K_ws_y, qy_from_trns, q_to.qy.q, beta_y, info.beta_y_factor, info.nr_to, lambda0, maxtem,
                )

            if info.use_map:
                # if the map is marked as a focusing element then
                # it does the from-to mode projection, otherwise BH
                # does it
                if not info.map_ws.is_focusing_element:
                    q1 = q_from
                    q2 = q_from
                else:
                    q1 = q_from
                    q2 = q_to

                init_knm_map_workspace(
                    &info.map_ws,
                    max(self.sim.model_settings.max_m, self.sim.model_settings.max_n)+1,
                    q1, q2,
                    # BH already includes the reflection minus flip
                    not info.is_transmission and not info.use_bh
                )

            if info.use_bh and not info.use_map:
                knm = getattr(self, f"K{coupling}")
                info.bh_mtx = &knm.mtx
                info.map_mtx = NULL
            elif not info.use_bh and info.use_map:
                knm = getattr(self, f"K{coupling}")
                info.bh_mtx = NULL
                info.map_mtx = &knm.mtx
            else:
                # if we have a map, then we will probably have both BH and map calcuations.
                # in this case we need to compute multiple scattering matrices then
                # multiply them together to get the matrix used for filling.
                knm = KnmMatrix(self.sim.model_settings.homs_view, self.owner.name, coupling + "_bh")
                info.bh_mtx = &knm.mtx
                self.__knm_matrices.append(knm) # keep a reference so doesn't get cleaned up
                # Same again for map matrix
                knm = KnmMatrix(self.sim.model_settings.homs_view, self.owner.name, coupling + "_map")
                info.map_mtx = &knm.mtx
                self.__knm_matrices.append(knm) # keep a reference so doesn't get cleaned up


    cpdef update_map_data(KnmConnectorWorkspace self):
        cdef:
            KnmInfo *info
        # not the most efficient way to loop over all possible
        # Knm connections and look for maps, but this doesn't
        # get called much...
        for i in range(self.N_opt_conns):
            info = &self.oconn_info[i]
            if info.use_map and info.map_ws.map_is_changing:
                update_map_data_in_workspace(&info.map_ws)


    cpdef flag_changing_beam_parameters(
        KnmConnectorWorkspace self,
        OrderedSet changing_mismatch_edges
    ):
        """Iterate through all optical connections and checks/flag which optical
        connections need to having their scattering matrices recalculated. This
        occurs if the beam tracer traces some new q-parameters, or if an ABCD has
        a changing parameter, or if some optical path distortion map is changing.

        Parameters
        ----------
        changing_couplings : tuple
            Tuple of (node_in, node_out) which must be recomputed.

        Notes
        -----
        `changing_couplings` typically comes from the trace forest`s method
        `trace_forest.find_potential_mismatch_couplings`. Which determines
        potential changes in mode scattering parameters, from changing ABCD
        properties.
        """
        cdef:
            KnmInfo *info
            bint is_mm_changing
            Py_ssize_t ni_idx, no_idx
            const NodeBeamParam* q_from
            const NodeBeamParam* q_to

        for i in range(self.N_opt_conns):
            info = &self.oconn_info[i]
            if info.use_bh:
                ni_idx = self.onode_ids[2*info.from_port_idx]
                no_idx = self.onode_ids[2*info.to_port_idx+1]
                q_from = &self.sim.trace[self.trace_node_indices[2*info.from_port_idx]]
                q_to = &self.sim.trace[self.trace_node_indices[2*info.to_port_idx+1]]

                is_mm_changing = (
                    not q_from.is_fixed or not q_to.is_fixed
                )
                # Need to determine if ABCD is changing here, as that
                # will also change how q_from is projected into q_to
                if (ni_idx, no_idx) in changing_mismatch_edges:
                    is_mm_changing = True

                info.K_ws_x.is_mm_changing = is_mm_changing
                info.K_ws_y.is_mm_changing = is_mm_changing
                info.K_ws_x.is_alignment_changing = info.beta_x_is_changing
                info.K_ws_y.is_alignment_changing = info.beta_y_is_changing

                if knm_bh_ws_is_changing(info.K_ws_x) or knm_bh_ws_is_changing(info.K_ws_y):
                    LOGGER.debug(f"{self.owner.name}.K{info.from_port_idx+1}{info.to_port_idx+1} is changing")

    cdef void update_changing_knm_workspaces(KnmConnectorWorkspace self) noexcept:
        cdef:
            NodeBeamParam *q_from
            NodeBeamParam *q_to
            KnmInfo *info
            complex_t qx_from_trns, qy_from_trns

        for i in range(self.N_opt_conns):
            info = &self.oconn_info[i]
            if info.use_bh:
                q_from = &self.sim.trace[self.trace_node_indices[2*info.from_port_idx]]
                q_to = &self.sim.trace[self.trace_node_indices[2*info.to_port_idx+1]]

                # if there's some changing Knm then we need to recompute it. Which parts need
                # to be recomputed are decided here then performed
                if info.K_ws_x.is_mm_changing:
                    # If we use a map which is doing the focussing, do the mode projection there
                    if info.use_map and info.map_ws.is_focusing_element:
                        qx_from_trns = q_to.qx.q
                    else:
                        qx_from_trns = c_transform_q(info.abcd_x, q_from.qx.q, info.nr_from, info.nr_to)

                    if info.beta_x == NULL:
                        knm_bh_ws_recompute_mismatch(info.K_ws_x, qx_from_trns, q_to.qx.q)
                    else:
                        knm_bh_ws_recompute(info.K_ws_x, qx_from_trns, q_to.qx.q, info.beta_x[0])

                elif info.K_ws_x.is_alignment_changing and info.beta_x != NULL:
                    knm_bh_ws_recompute_misalignment(info.K_ws_x, info.beta_x[0])

                if info.K_ws_y.is_mm_changing:
                    # If we use a map which is doing the focussing, do the mode projection there
                    if info.use_map and info.map_ws.is_focusing_element:
                        qy_from_trns = q_to.qy.q
                    else:
                        qy_from_trns = c_transform_q(info.abcd_y, q_from.qy.q, info.nr_from, info.nr_to)

                    if info.beta_y == NULL:
                        knm_bh_ws_recompute_mismatch(info.K_ws_y, qy_from_trns, q_to.qy.q)
                    else:
                        knm_bh_ws_recompute(info.K_ws_y, qy_from_trns, q_to.qy.q, info.beta_y[0])

                elif info.K_ws_y.is_alignment_changing and info.beta_y != NULL:
                    knm_bh_ws_recompute_misalignment(info.K_ws_y, info.beta_y[0])


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void compute_scattering_matrices(KnmConnectorWorkspace self) noexcept:
        cdef:
            KnmInfo *info = NULL
            Py_ssize_t i = 0
            knm_map_workspace *map_ws = NULL
            bint map_q_changed = False
            complex_t alpha, beta
            int N, inc
            bint updated
            bint is_reflection

        for i in range(self.N_opt_conns):
            info = &self.oconn_info[i]
            updated = False # whether the knm has been updated or not
            is_reflection = not info.is_transmission

            if info.use_bh and (knm_bh_ws_is_changing(info.K_ws_x) or knm_bh_ws_is_changing(info.K_ws_y)):
                info.bhelms_mtx_func(
                    info.K_ws_x,
                    info.K_ws_y,
                    &(self.sim.model_settings.homs_view[0,0]),
                    info.bh_mtx.ptr,
                    self.sim.model_settings.num_HOMs,
                    self.sim.config_data.nthreads_homs,
                )
                updated = True

            if info.use_map:
                map_ws = &info.map_ws
                map_q_changed = False
                if map_ws.new_map_data or not map_ws.q_from.is_fixed or not map_ws.q_to.is_fixed:
                    if not map_ws.q_from.is_fixed:
                        unm_ws_recache_from_bp(map_ws.uiws, &map_ws.q_from.qx, &map_ws.q_from.qy)
                        unm_factor_store_recache(
                            map_ws.unm_i_factor_ws, map_ws.uiws,
                            True, # remove Gouy
                            # we don't actually flip the map here, we just
                            # flip the modes relative to the map
                            info.map_fliplr,
                        )
                    if not map_ws.q_to.is_fixed:
                        unm_ws_recache_from_bp(map_ws.uows, &map_ws.q_to.qx, &map_ws.q_to.qy)
                        unm_factor_store_recache(
                            map_ws.unm_o_factor_ws,
                            map_ws.uows,
                            True,
                            info.map_fliplr
                        )

                    w = min(
                        bp_beamsize(&map_ws.q_to.qx),
                        bp_beamsize(&map_ws.q_to.qy),
                        bp_beamsize(&map_ws.q_from.qx),
                        bp_beamsize(&map_ws.q_from.qy),
                    )

                    if w/map_ws.dx < 10 or w/map_ws.dy < 10:
                        warn(
                            "Spot size vs map resolution is low, increase map resolution or spot size\n" +
                            f"for {self.owner.name} connection {info.from_port_idx+1}->{info.to_port_idx+1}"
                        )

                    # Then update the Un and Um arrays
                    update_U_xy_array(
                        map_ws.x, map_ws.Nx,
                        map_ws.y, map_ws.Ny,
                        map_ws.Un, map_ws.Um, map_ws.Nm,
                        map_ws.uiws, map_ws.unm_i_factor_ws
                    )
                    update_U_xy_array(
                        map_ws.x, map_ws.Nx,
                        map_ws.y, map_ws.Ny,
                        map_ws.Un_, map_ws.Um_, map_ws.Nm,
                        map_ws.uows, map_ws.unm_o_factor_ws
                    )
                    # update the outer products for all modes for Un and Um
                    c_outer_conj_product_2(map_ws.Nm, map_ws.Ny, map_ws.Um, map_ws.Um_, map_ws.Umm_)
                    c_outer_conj_product_2(map_ws.Nm, map_ws.Nx, map_ws.Un, map_ws.Un_, map_ws.Unn_)
                    map_q_changed = True

                if map_ws.new_map_data or map_q_changed:
                    map_ws.new_map_data = False # mark that we've calculated this at least once
                    updated = True
                    # calculate new scattering coefficients using the optimised
                    # method using BLAS functions
                    c_riemann_optimised(
                        map_ws.Nx, map_ws.Ny, map_ws.Nm,
                        map_ws.dx * map_ws.dy,
                        map_ws.z,
                        map_ws.Unn_,
                        map_ws.Umm_,
                        map_ws.tmp,
                        map_ws.K,
                    )
                    # convert the 4D scattering coefficients into the modal matrix for filling
                    c_scattering_coefficients_to_KnmMatrix(
                        self.sim.model_settings.homs_view,
                        map_ws.Nm,
                        map_ws.K,
                        info.map_mtx
                    )

            # only do these steps if a knm matrix has been updated. Currently
            # this loop is called constantly for every element, regardless of
            # whether it is changing or not
            if updated:
                if info.use_bh and info.use_map:
                    # using two Knm so need to multiply them
                    alpha = 1
                    beta = 0 # rewrite output matrix
                    N = info.bh_mtx.size1
                    zgemm(
                        "T", "T", # KnmMatrices are C ordered, but zgemm expects F ordered
                        &N, &N, &N, # Square matrix
                        &alpha, # include any phase removal
                        info.bh_mtx.ptr, &N,
                        info.map_mtx.ptr, &N,
                        &beta, info.knm_mtx.ptr, &N
                    )

                if self.sim.model_settings.phase_config.zero_k00:
                    # final step zero 00->00 phase, which is just removing a plane
                    # wave phase from the entire scattering calculation
                    #  - arg of 00->00 term
                    #  - create unit complex vector with -1 * arg
                    #  - apply to all elements in matrix
                    alpha = cexp(-1j*carg(info.knm_mtx.ptr[0]))
                    N = info.knm_mtx.size1 * info.knm_mtx.size2
                    inc = 1 # DenseZMatrix is memory contiguous
                    zscal(&N, &alpha, info.knm_mtx.ptr, &inc)

                if is_reflection:
                    # if we're doing a reflection we need to apply the
                    # parity operator
                    c_flip_odd_horizontal(
                        info.knm_mtx,
                        self.sim.model_settings.homs_view
                    )

                # Note: no need for reversing gouy here compared to
                # Finesse v2. The BH and map calculations do that
                # themselves - for the map it's essentially free
                # as it's just not added in the first place


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void compute_knm_losses(KnmConnectorWorkspace self) noexcept nogil:
        cdef:
            KnmInfo *info
            Py_ssize_t i

        for i in range(self.N_opt_conns):
            info = &self.oconn_info[i]
            #if knm_bh_ws_is_changing(info.K_ws_x) or knm_bh_ws_is_changing(info.K_ws_y):
            # use full knm matrix to compute the HOM losses, could add some way to
            # compute if this has changed
            knm_loss(info.knm_mtx.ptr, info.loss, self.sim.model_settings.num_HOMs)


# N.B. This function depends on the order of ports / nodes being consistent between
# ws.onode_ids and ws.oconn_info, and may break if this order is changed.
# TODO: This doesn't consider the couplings in the signal matrix, effectively assuming they're 1,
# which isn't always correct. In such cases a custom function will be needed such
# as for a mirror or beamsplitter.
optical_quantum_noise_knm = FillFuncWrapper.make_from_ptr(c_optical_quantum_noise_knm)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cdef object c_optical_quantum_noise_knm(ConnectorWorkspace cws) :
    cdef:
        KnmConnectorWorkspace ws = <KnmConnectorWorkspace> cws
        NoiseInfo noises = ws.output_noise
        frequency_info_t *freq

        Py_ssize_t i, j, k, h
        Py_ssize_t port_idx

        complex_t factor

    if ws.sim.signal.nhoms == 0:
        return
    for i in range(ws.sim.signal.optical_frequencies.size):
        freq = &(ws.sim.signal.optical_frequencies.frequency_info[i])
        factor = 0.5 * (1 + freq.f_car[0] / ws.sim.model_settings.f0)
        for j in range(noises.num_nodes):
            port_idx = -1
            for k in range(ws.N_opt_ports):
                if ws.onode_ids[2 * k + 1] == noises.node_info[j].idx:
                    port_idx = k
                    break
            if port_idx == -1:
                continue
            ws.total_losses[:] = 0
            for k in range(ws.N_opt_conns):
                if ws.oconn_info[k].to_port_idx == port_idx:
                    for h in range(ws.sim.signal.nhoms):
                        ws.total_losses[h] += ws.oconn_info[k].loss[h]
            (<SubCCSView>noises.ptrs[j][freq.index]).fill_za_dv(factor, ws.total_losses)
