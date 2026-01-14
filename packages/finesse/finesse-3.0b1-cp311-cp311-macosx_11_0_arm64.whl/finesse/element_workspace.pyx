from libc.stdlib cimport free, calloc
from libc.string cimport memcpy
from cpython.ref cimport Py_XINCREF, Py_XDECREF

from finesse.parameter cimport (
    Parameter,
    ParameterState,
)
from finesse.symbols import Symbol

class ElementValues:
    """Standard Python object which is used to store an Elements Parameter values.
    This is used in the default case where no optimised C class is provided."""
    pass


cdef class BaseCValues:
    """Base class that elements should use for storing their parameter
    values. This contains a generic method for storing a pointers to the
    double parameter values, which is intialised using `setup()`.

    Each Parameter of an element should result in a double. This won't handle
    any other types of data.
    """
    def __cinit__(self):
        self.ptr = NULL
        self.N = 0

    cdef setup(self, tuple params, Py_ssize_t data_size, double** data_start) :
        """Allocates the memory needed to store double values for the requested parameters.

        Examples
        --------
        An array of pointers to the double variables where each parameter should be copied across
        to.

        ctypedef (double*, double*) ptr_tuple_2 # data type of double points

        cdef class OpticalBandpassValues(BaseCValues):
            def __init__(self):
                cdef ptr_tuple_2 ptr = (&self.fc, &self.bandwidth) # array of ptrs to store parameter values at
                cdef tuple params = ("fc", "bandwidth") # names that match up in order with pointers
                self.setup(params, sizeof(ptr), <double**>&ptr) # call setup

        Parameters
        ----------
        params : tuple
            Tuple of Parameter names (case-sensitive) that an element has and needs to be stored in C values
        data_size : unsigned long
            number of double* pointers (or number of parameters)
        data_start : double**
            Pointer to array of double pointers where each parameter value should be stored
        """
        if self.ptr != NULL:
            raise ValueError("Memory already allocated")
        if data_start == NULL:
            raise ValueError("data_start == NULL")

        self.params = params
        self.N = data_size//sizeof(double)

        if len(self.params) != self.N:
            raise ValueError("Tuple of parameters and length of double pointers does not match")

        self.ptr = <double**> calloc(self.N, sizeof(double*))

        if not self.ptr:
            raise MemoryError()

        memcpy(self.ptr, data_start, data_size)

    def __dealloc__(self):
        if self.ptr != NULL:
            free(self.ptr)
            self.ptr = NULL

    cdef get_param_ptr(self, unicode name, double**ptr) :
        """Get a C pointer to where an elements parameter values should be stored.

        Parameters
        ----------
        name : unicode
            Name of the parameter
        ptr : double*
            Pointer to where the parameter pointer should be stored
        """
        if self.ptr == NULL:
            raise ValueError("Value storage pointers not set")
        if ptr == NULL:
            raise ValueError("ptr is NULL")

        idx = self.params.index(name)
        if self.ptr[idx] == NULL:
            raise ValueError(f"Pointer to {name} double is NULL")

        ptr[0] = self.ptr[idx]


cdef class ElementWorkspace:
    """
    This is the most basic workspace for a model element. It keeps track of the owner element and
    its parameter values in the `self.values` object.
    """
    def __cinit__(self, *args, **kwargs):
        self.num_changing_parameters = 0
        self.chprm = NULL
        self.chprm_target = NULL
        self.chprm_expr = NULL
        self.owner_id = -1
        self.first = True

    def __init__(self, object sim, object owner, object values=None):
        cdef:
            Parameter p
            int i
        self.owner = owner
        self.sim = sim

        if values is None:
            self.values = ElementValues()
            self.type_c_values = None
            self.is_c_values = False
        else:
            if not isinstance(values, BaseCValues):
                raise Exception("Values object should be a derivative of BaseCValues")

            self.values = values
            self.type_c_values = type(values)
            self.is_c_values = True

            # Here we setup for fast parameter setting by storing
            # the pyobject pointers to Parameters and also a double
            # pointer to the value

            # Make sure that numeric parameters come before symbolic
            # parameters so that the latter get eval'd to the correct
            # value when calling cy_expr_eval
            numeric_params = []
            symbolic_params = []
            for p in owner.parameters:
                if p.is_changing:
                    self.num_changing_parameters += 1
                    if p.state == ParameterState.Symbolic:
                        symbolic_params.append(p)
                    else:
                        numeric_params.append(p)

            params = numeric_params + symbolic_params
            if self.num_changing_parameters > 0:
                if self.chprm != NULL or self.chprm_target != NULL or self.chprm_expr != NULL:
                    raise MemoryError()

                self.chprm = <PyObject**> calloc(self.num_changing_parameters, sizeof(PyObject*))
                if not self.chprm:
                    raise MemoryError()

                self.chprm_target = <double**> calloc(self.num_changing_parameters, sizeof(double*))
                if not self.chprm_target:
                    raise MemoryError()

                self.chprm_expr = <cy_expr**> calloc(self.num_changing_parameters, sizeof(cy_expr*))
                if not self.chprm_expr:
                    raise MemoryError()

                i = 0
                for p in params:
                    if p.is_changing:
                        if p.state == ParameterState.Symbolic:
                            self.chprm_expr[i] = cy_expr_new()

                        self.chprm[i] = <PyObject*>p
                        Py_XINCREF(self.chprm[i])
                        (<BaseCValues>self.values).get_param_ptr(p.name, &self.chprm_target[i])
                        i += 1
                        # Stop this changing parameter from changing the type of
                        # variable it is (See #476). Problem comes about when a
                        # non-symbolic changes to a symbolic after this code has
                        # run, so then things like cy_expr_new have not been run.
                        p.__disable_state_type_change = True

    cpdef int compile_cy_exprs(self) except -1:
        if not self.num_changing_parameters:
            return 0

        for i in range(self.num_changing_parameters):
            if (<Parameter>self.chprm[i]).state == ParameterState.Symbolic:
                try:
                    # occasionally expressions simplify and become a constant
                    # so need to check
                    expr = (<Parameter>self.chprm[i]).value.expand_symbols().eval(keep_changing_symbols=True)
                    if isinstance(expr, Symbol):
                        if cy_expr_init(
                            self.chprm_expr[i], expr
                        ) == -1:
                            return -1
                except:
                    raise RuntimeError(f"Issue compiling cython expression :: {(<Parameter>self.chprm[i]).full_name}={(<Parameter>self.chprm[i]).value}")
        return 0

    cpdef update_parameter_values(self) :
        """Updates the `self.values` container which holds the latest values
        of this elements parameters.
        """
        cdef unicode p

        if self.first or not self.is_c_values:
            # First go just fill everything.
            # This is fairly slow but robust for any python object...
            vals, _ = self.owner._eval_parameters()
            for p in vals:
                if vals[p] is not None:
                    setattr(self.values, p, vals[p])
                else:
                    setattr(self.values, p, 0)
            self.first = False

        elif self.num_changing_parameters > 0:
            # Here we do some lower level setting of parameters using pointers
            # to the workspace.value.parameter double variable to speed things up
            for i in range(self.num_changing_parameters):
                if self.chprm_target[i] == NULL or self.chprm[i] == NULL:
                    raise MemoryError()

                if (<Parameter>self.chprm[i]).state == ParameterState.Numeric:
                    self.chprm_target[i][0] = (<Parameter>self.chprm[i]).__cvalue
                elif (<Parameter>self.chprm[i]).state == ParameterState.NONE:
                    self.chprm_target[i][0] = 0 # maybe should be NaN?
                elif (<Parameter>self.chprm[i]).state == ParameterState.Symbolic:
                    self.chprm_target[i][0] = cy_expr_eval(self.chprm_expr[i])
                    # Make sure __cvalue of symbolic parameters get updated too so that
                    # anything that relies on address of this uses correct value
                    (<Parameter>self.chprm[i]).__cvalue = self.chprm_target[i][0]
                else:
                    raise ValueError("Parameter state was unexpected")

    def __dealloc__(self):
        errors = []
        if self.num_changing_parameters > 0:
            for i in range(self.num_changing_parameters):
                if (<Parameter>self.chprm[i]).state == ParameterState.Symbolic:
                    cy_expr_free(self.chprm_expr[i])

                if self.chprm[i] == NULL:
                    errors.append(i)
                else:
                    Py_XDECREF(self.chprm[i])

            if self.chprm != NULL:
                free(self.chprm)
                self.chprm = NULL
            if self.chprm_expr != NULL:
                free(self.chprm_expr)
                self.chprm_expr = NULL
            if self.chprm_target != NULL:
                free(self.chprm_target)
                self.chprm_target = NULL

            if len(errors) > 0:
                raise MemoryError(f"unexpected self.chprm indices {errors} were NULL")

    def __repr__(self):
        try:
            return "<'{}' @ {} ({})>".format(
                self.owner.name, hex(id(self)), self.__class__.__name__
            )
        except:
            return super().__repr__()
