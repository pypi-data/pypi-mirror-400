# distutils: sources = src/finesse/tinyexpr.c
# distutils: include_dirs = src/finesse/


"""Compiled symbolic expressions used internally via parameters and element workspaces.

This sub-module only exposes C code so can only be used by other Cython
extensions. The symbolic expression struct ``cy_expr`` is used in workspaces
(see :class:`.ElementWorkspace`) and parameter code (see :class:`.Parameter`)
for quick evaluation of changing symbolic expressions.

The ``cy_expr`` struct, and associated functions, are wrappers around the C
based math parsing and evaluation engine, `tinyexpr <https://github.com/codeplea/tinyexpr>`_.
"""

from libc.stdlib cimport calloc, free
from cpython.ref cimport Py_XINCREF, Py_XDECREF

cdef cy_expr* cy_expr_new() except NULL nogil:
    cdef cy_expr* ce_p = <cy_expr*> calloc(1, sizeof(cy_expr))
    if not ce_p:
        with gil:
            raise MemoryError()
    ce_p.expr = NULL
    ce_p.variables = NULL
    ce_p.byte_op_str = NULL
    return ce_p

cdef int cy_expr_init(cy_expr* ex, object operation) except -1:
    """Initialise the te_expr and te_variable type fields using the
    operation object (should be an instance of Function)."""
    if ex == NULL:
        raise MemoryError()

    cdef str op_str = str(operation)
    cdef list params = operation.parameters() # get the dependent parameter-refs
    cdef int Nparams = len(params)

    ex.variables = <te_variable*> calloc(Nparams, sizeof(te_variable))
    if not ex.variables:
        raise MemoryError()

    cdef Py_ssize_t i
    cdef Parameter p
    for i in range(Nparams):
        pref = params[i] # the ParameterRef object

        # Replace the corresponding parameter name in the operation string with
        # the tinyexpr compatible name version (see ParameterRef.cyexpr_name)
        op_str = op_str.replace(pref.name, pref.cyexpr_name.decode())
        # Also need to replace "quantity**n" with "quantity^n" as te expects powers in this form
        op_str = op_str.replace("**", "^")

        p = pref.parameter
        ex.variables[i] = te_variable(pref.cyexpr_name, &p.__cvalue, 0, NULL)

    cdef int err # position of parsing error in operation expression
    # Make byte str of operation expression, and store it in
    # cy_expr instance for info / debugging purposes later
    byte_op_str = op_str.encode("UTF-8")
    ex.byte_op_str = <PyObject*>byte_op_str
    Py_XINCREF(ex.byte_op_str)
    ex.expression = byte_op_str
    ex.expr = te_compile(byte_op_str, ex.variables, Nparams, &err)

    if not ex.expr:
        error_loc_str = "    {m: <{pos}}^".format(m="", pos=str(err - 1))
        raise RuntimeError(
            "Internal cy_expr parsing error on:\n"
           f"    {op_str}\n" +
            error_loc_str +
           "\nError near here"
        )

    return 0

cdef void cy_expr_free(cy_expr* ex) noexcept:
    if ex != NULL:
        if ex.expr != NULL:
            te_free(ex.expr)
        if ex.variables != NULL:
            free(ex.variables)

        Py_XDECREF(ex.byte_op_str)

        free(ex)
        ex = NULL

cdef double cy_expr_eval(cy_expr* ex) noexcept nogil:
    """Evaluate the cythonised symbolic expression."""
    return te_eval(ex.expr)

def test_expr(op_str, value=None):
    """Python accessible function to test the parsing of strings.

    Parameters
    ----------
    op_str : str
        String containing operation, e.g., 0.0+1

    Returns
    -------
    ex.expr : boolean
        False on parse fail
    """
    cdef int err
    cdef cy_expr* ex = cy_expr_new()

    try:
        byte_op_str = op_str.encode("UTF-8")

        ex.expr = te_compile(byte_op_str, ex.variables, 0, &err)

        # test if expression compiled
        if not ex.expr:
            return False

        if value:
            # test if expression evaluates
            return te_eval(ex.expr) == value

        return True
    finally:
        cy_expr_free(ex)
