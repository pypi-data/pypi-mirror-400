from cpython.ref cimport PyObject

cdef extern from "tinyexpr.h" nogil:
    ctypedef struct te_expr:
        pass

    ctypedef struct te_variable:
        const char* name
        const void* address
        int type
        void* context

    cdef te_expr* te_compile(
        const char* expression,
        const te_variable* variables,
        int var_count,
        int* error
    ) noexcept

    cdef double te_eval(const te_expr* n) noexcept

    cdef void te_free(te_expr* n) noexcept


from .parameter cimport Parameter

# Wrapper for tinyexpr's expression and variables
# -> an array of ptrs to these get stored in ElementWorkspace
#    for fast evaluation of changing symbolic parameters
cdef struct cy_expr:
    te_expr* expr
    te_variable* variables

    const char* expression

    PyObject* byte_op_str

cdef cy_expr* cy_expr_new() except NULL nogil

cdef int cy_expr_init(cy_expr* ex, object operation) except -1

cdef void cy_expr_free(cy_expr* ex) noexcept

cdef double cy_expr_eval(cy_expr* ex) noexcept nogil
