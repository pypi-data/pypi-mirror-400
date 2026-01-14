# cython: profile=False
"""
Sparse matrix objects with factorisation and solving routines performed via KLU.
"""
import weakref

import numpy as np
cimport numpy as np
import cython
from cpython.ref cimport PyObject, Py_XINCREF, Py_XDECREF
from libc.stdlib cimport calloc, free, malloc
from libc.string cimport memset
from finesse.cymath.complex cimport conj
from finesse.cymath cimport complex_t # type: np.complex128_t (i.e. double complex)
from finesse.exceptions import NoLinearEquations

cdef sortkey(x) :
    return int(x.to)

cdef status_string(int status) :
    if status == KLU_SINGULAR:
        return "KLU_SINGULAR"
    elif status == KLU_OUT_OF_MEMORY:
        return "KLU_OUT_OF_MEMORY"
    elif status == KLU_INVALID:
        return "KLU_INVALID"
    elif status == KLU_TOO_LARGE:
        return "KLU_TOO_LARGE"
    else:
        return "UNKNOWN"

cdef class _Column:
    cdef public:
        Py_ssize_t start
        Py_ssize_t size
        Py_ssize_t index
        unicode name
        list submatrices

    def __init__(self, size, index, name):
        assert(size>0)
        self.size = size
        self.index = index
        self.name = name
        self.submatrices = []

    def __str__(self):
        submatrices = ", ".join(str(mat) for mat in self.submatrices)
        return f"Column(index={self.index}, name='{self.name}', submatrices=[{submatrices}])"


cdef class _SubMatrix:
    cdef public:
        Py_ssize_t to
        Py_ssize_t rows
        Py_ssize_t columns
        unicode name
        unicode type

    def __init__(self, type_, from_size, to_size, to, name):
        assert(from_size>0)
        assert(to_size>0)
        self.to = to
        self.type = type_
        self.name = name
        self.columns = from_size #
        self.rows = to_size

    def __str__(self):
        return f"Submatrix(name='{self.name}')"


cdef class CCSMatrix:
    def __init__(self, name):
        self.__name = name
        self.__indexes = {}
        self.sub_columns = {}
        self.num_nodes   = 0
        self.num_eqs     = 0
        self.num_rhs     = 1
        self.allocated   = 0

        self.values  = NULL
        self.col_ptr = NULL
        self.row_idx = NULL
        self.diag_map = {}
        self.nnz  = 0
        self.__callbacks = []

    @property
    def num_equations(self): return int(self.num_eqs)

    @property
    def num_rhs(self): return int(self.num_rhs)

    @property
    def indexes(self): return self.__indexes

    @property
    def name(self): return self.__name

    @property
    def nnz(self): return self.__nnz

    cdef unsigned request_rhs_view(self) noexcept:
        if self.rhs:
            raise Exception("Can't request rhs_view after the matrix has been built")
        self.num_rhs += 1
        return self.num_rhs - 1

    def declare_submatrix_view(self, Py_ssize_t from_node, Py_ssize_t to_node, unicode name, bint conjugate_fill):
        mat = SubCCSMatrixView(self, from_node, to_node, name, conjugate_fill)
        self._declare_submatrix(from_node, to_node, name, mat, type_="m")
        return mat

    def declare_subdiagonal_view(self, Py_ssize_t from_node, Py_ssize_t to_node, unicode name, bint conjugate_fill):
        mat = SubCCSMatrixViewDiagonal(self, from_node, to_node, name, conjugate_fill)
        self._declare_submatrix(from_node, to_node, name, mat, type_="d")
        return mat

    def __dealloc__(self):
        if self.col_ptr: free(self.col_ptr)
        if self.row_idx: free(self.row_idx)
        if self.values:  free(self.values)
        if self.rhs:     free(self.rhs)

    cpdef declare_equations(
        self,
        SuiteSparse_long Neqs,
        SuiteSparse_long index,
        unicode name,
        is_diagonal = True,
        add_view = True
    ) :
        """
        This defines generally what equations exist in the matrix. It essentially defines
        the order of the RHS vector for which equations map to what index.

        This method decalres a group of `Neqs` equations at once which form a "block"
        or submatrix within the matrix itself. This block can be referenced by the unique
        index provided.

        When adding this block of equations a view of the diagonal of the matrix can
        also be added and returned if required. By default it will.

        Parameters
        ----------
        Neqs : Py_ssize_t
            Number of equations this submatrix represents
        index : long
            Subcolumn index
        name : unicode
            Name used to indentify this coupling in the matrix for debugging
        is_diagonal : bool, optional
            If true, the view created and returned is a diagonal submatrix. If False,
            the view will be a dense submatrix.
        add_view : bool, optional
            If True, a submatrix view will be added to the matrix so that the diagonal
            submatrix for these elements is available for altering the values automatically.

        Returns
        -------
        view : SubCCSMatrixView
            If add_view == True, a view of the diagonal submatrix for these elements
            will be returned.
        """
        if Neqs <= 0:
            raise Exception("Must have at least one equation")
        if index in self.sub_columns:
            raise Exception("Diagonal elements already specified at index {}".format(index))
        mat = None

        self.sub_columns[index] = _Column(Neqs, index, name)

        if add_view:
            if is_diagonal:
                self.sub_columns[index].submatrices.append(_SubMatrix("d", Neqs, Neqs, index, name))
                mat = SubCCSMatrixViewDiagonal(self, index, index, name, False)
            else:
                self.sub_columns[index].submatrices.append(_SubMatrix("m", Neqs, Neqs, index, name))
                mat = SubCCSMatrixView(self, index, index, name, False)
            self.__callbacks.append(mat)

        # Record what RHS index/number of equations this submatrix will start in
        self.diag_map[index] = self.num_eqs
        self.num_eqs += Neqs

        return mat

    cpdef _declare_submatrix(self, SuiteSparse_long _from, SuiteSparse_long _to,
                        unicode name, callback=None, type_="m") :
        """
        Adds a submatrix to the matrix. The nomenclature of `_from` and `_to` refer to the variable
        dependency of the equations this submatrix represents, i.e. the equations in submatrix
        `_to` depends on the values in `-from`. Therefore `_from` is the subcolumn index and `_to`
        is the subrow index.

        Parameters
        ----------
        _from : long
            Subcolumn index
        _to : long
            Subcolumn index
        name : unicode
            Name used to indentify this coupling in the matrix for debugging
        callback : function()
            A callback function that will be called once the matrix has been constructed
        type_ : char, optional
            Either 'm' for a full submatrix or 'd' for a diagonal element only submatrix
        """
        if _from not in self.sub_columns:
            raise Exception("Must add a diagonal submatrix at index {} first for this subcolumn".format(_from))
        if _to   not in self.sub_columns:
            raise Exception("Must add a diagonal submatrix at index {} first for this subcolumn".format(_to))

        _to_size = self.sub_columns[_to].size
        _from_size = self.sub_columns[_from].size

        self.sub_columns[_from].submatrices.append(_SubMatrix(type_, _from_size, _to_size, _to, name))

        if callback: self.__callbacks.append(callback)

    cpdef set_rhs(self, SuiteSparse_long index, complex_t value, unsigned rhs_index=0) :
        """Sets the value of the entry at position `index` of the `rhs_index`th right-hand-side
        vector to `value`.

        Parameters
        ----------
        index : long
            The index in the rhs vector to set
        value : complex_t
            The value to set
        rhs_index : unsigned, optional
            Which rhs vector to change; defaults to 0
        """
        assert(self.rhs)
        if rhs_index >= self.num_rhs or rhs_index < 0:
            raise IndexError(f"Invalid rhs index {rhs_index}")
        if index >= self.num_eqs or index < 0:
            raise IndexError(f"Invalid index {index}")
        self.rhs[rhs_index * self.num_eqs + index] = value

    cdef int c_set_rhs(self, SuiteSparse_long index, complex_t value, Py_ssize_t rhs_index) except -1:
        """Sets the value of the entry at position `index` of the `rhs_index`th right-hand-side
        vector to `value`.

        Parameters
        ----------
        index : long
            The index in the rhs vector to set
        value : complex_t
            The value to set
        rhs_index : unsigned, optional
            Which rhs vector to change; defaults to 0

        Return
        ------
        Returns -1 on error
        """
        cdef SuiteSparse_long i = rhs_index * self.num_eqs + index
        if not self.rhs:
            raise Exception("RHS not initialised")
        if index < 0 or i > self.num_eqs * self.num_rhs:
            raise Exception(f"Index out of bounds, {index}, for rhs {rhs_index}")
        self.rhs[i] = value
        return 0

    cpdef construct(self, complex_t diagonal_fill=complex(1, 0)):
        """
        Constructing the matrix involves taking the metadata submatrix positions
        throughout the matrix and allocating the memory and building the various
        CCS matrix structures. After this the matrix can be populated and solved.

        Parameters
        ----------
        diagonal_fill : complex_t, optional
            Value to fill the diagonal of the matrix with; defaults to 1+0j
        """

        cdef:
            SuiteSparse_long i      = 0
            SuiteSparse_long j      = 0
            SuiteSparse_long k      = 0
            SuiteSparse_long cnnz   = 0 # current element number
            SuiteSparse_long crow   = 0 # current row
            SuiteSparse_long ccol   = 0 # current column in a submatrix
            SuiteSparse_long nnz    = 0
            _Column col
            _SubMatrix sm

        if self.num_eqs == 0:
            raise NoLinearEquations("Sparse matrix has no equations to solve")

        for col in self.sub_columns.values():
            # sort so that the the submatrices are in row order
            # ddb: This sort takes up about half the time of this method
            #      maybe some optimised instertion sorted list might be better
            col.submatrices.sort(key=sortkey)
            assert(col.size > 0)
            for sm in col.submatrices:
                # count how many elements per column for allocating memory
                if sm.type == "m": # matrix
                    nnz += sm.rows * sm.columns
                elif sm.type == "d": # diagonal
                    nnz += col.size
                else:
                    raise Exception("Unhandled")

        self.col_ptr  = <SuiteSparse_long*> malloc(sizeof(SuiteSparse_long) * (self.num_eqs + 1))
        if not self.col_ptr:
            raise MemoryError()
        self.row_idx  = <SuiteSparse_long*> malloc(sizeof(SuiteSparse_long) * nnz)
        if not self.row_idx:
            raise MemoryError()
        self.values   = <complex_t*>        calloc(nnz, sizeof(complex_t))
        if not self.values:
            raise MemoryError()
        self.rhs      = <complex_t*>       calloc(self.num_eqs * self.num_rhs, sizeof(complex_t))
        if not self.rhs:
            raise MemoryError()
        self.rhs_view = <complex_t[:self.num_rhs, :self.num_eqs]>self.rhs

        for i, col in enumerate(self.sub_columns.values()): # For each subcolumn...
            col.start = cnnz # record index where this column starts

            for j in range(col.size): # then for each actual column in the subcolumn
                # set the starting location of the column in the pointer vector
                self.col_ptr[ccol] = cnnz

                for sm in col.submatrices: # select each submatrix...
                    crow = self.diag_map[sm.to]

                    # then set the elements in the column for...
                    if sm.type == "m": # a matrix
                        for k in range(sm.rows):
                            self.row_idx[cnnz+k] = crow + k
                            # Set a default position, real=col, imag=row, helps with debugging
                            self.values[cnnz+k] = 0 #complex(ccol, self.row_idx[cnnz+k])

                        # keep track of how many nnz we have actually done...
                        cnnz += sm.rows
                        crow += sm.rows
                    elif sm.type == "d": # a diagonal
                        self.row_idx[cnnz] = crow + j # set the diagonal position
                        if ccol == self.row_idx[cnnz]:
                            self.values[cnnz] = diagonal_fill
                        else:
                            self.values[cnnz] = complex(0, 0) #complex(ccol, self.row_idx[cnnz])
                        cnnz += 1
                        crow += 1
                    else:
                        raise Exception("Unhandled")

                # increment to the next column
                ccol += 1

        self.col_ptr[self.num_eqs] = cnnz
        self.nnz = cnnz

        for cb in self.__callbacks:
            cb._updateview_()

    cdef np.ndarray get_numpy_array_view(self, SuiteSparse_long _from, SuiteSparse_long _to, complex_t** start_ptr, SuiteSparse_long* from_rhs_index) :
        """
        Returns the submatrix that describes the coupling from a given
        block to another. For example, if you know the index for the block
        describing the HOM in a particular frequency, you can get the coupling
        submatrix to another set of HOMs at a frequency at a different node.

        This requires that `declare_equations` has been called to define a
        block with a certain index. Then `declare_submatrix_view` must be called
        to state that a coupling will exist between two blocks.

        A block is a set of equations grouped together. A dense matrix decribes
        the coupling between blocks at different nodes. Blocks can have different
        shapes.

        .. todo:: What does `from_rhs_index` do?

        Parameters
        ----------
        _from : int
            Index of the block for coupling from
        _to : int
            Index of the block for coupling to
        start_ptr : complex_t**
            where to store memory start pointer
        """
        cdef:
            Py_ssize_t cdx = 0 # index where subcolumn starts in values array
            Py_ssize_t rowcount = 0 # number of non-zero rows in subcolumn
            Py_ssize_t rows = 0

            str _type = ""
            Py_ssize_t sdx = 0 # actual row index where submatrix starts
            complex_t[:] ptr

            _Column sub_col
            _SubMatrix sm

        from_rhs_index[0] = self.diag_map[_from]
        sub_col = self.sub_columns[_from]
        # actual index in sparse format where this subcolumn starts
        cdx = sub_col.start
        cols = sub_col.size

        # Loop over each submatrix in the subcolumn
        for sm in sub_col.submatrices:
            if sm.to == _to:
                _type = sm.type
                sdx   = rowcount
                rows  = sm.rows

            if sm.type == "d":
                rowcount += 1
            elif sm.type == "m":
                rowcount += sm.rows
            else:
                raise Exception("Unexpected result {}".format(sm.type))

        # get a memoryview of the entire subcolumn
        ptr = <complex_t[:(rowcount*cols)]>(self.values + cdx)

        # numpy array view of the matrix which we reshape into the proper
        # subcolumn size
        cdef np.ndarray arr = np.asarray(ptr).reshape(cols, rowcount).T
        cdef np.ndarray[complex, ndim=1] rtnD = None
        cdef np.ndarray[complex, ndim=2] rtnM = None

        # now we return a numpy view of just the part of the matrix requested
        if _type == "d":
            rtnD = arr[sdx, :]
        elif _type == "m":
            rtnM = arr[sdx:(sdx+rows), :]
        else:
            raise Exception("Submatrix connecting {} -> {} does not exist".format(_from, _to))

        if start_ptr != NULL:
            if rtnD is not None:
                start_ptr[0] = &rtnD[0]
            else:
                start_ptr[0] = &rtnM[0,0]

        if rtnD is None:
            return rtnM
        else:
            return rtnD

    cpdef complex_t[::1] get_rhs_view(self, unsigned index) noexcept:
        """
        Returns a view of the rhs vector corresponding to `index`.

        Parameters
        ----------
        index : unsigned
            The rhs vector to return a view of
        """
        if index >= self.num_rhs:
            raise ValueError(f"Invalid rhs index {index}")
        return self.rhs_view[index]

    @property
    def num_equations(self):
        """Returns the number of equations (rows) in this matrix."""
        return self.num_eqs

    def get_matrix_elements(self):
        """
        Returns the sparse CCS format for the current state of this matrix.

        Returns
        -------
        data : list[complex]
            Value of each non-zero element

        rows : list[complex]
            Row index of each non-zero element

        cols : list[complex]
            Column index of each non-zero element
        """
        data = []
        rows = []
        cols = []

        ccol = -1
        for i in range(self.nnz):
            if self.col_ptr[ccol+1] == i:
                ccol += 1
            data.append(self.values[i])
            cols.append(ccol)
            rows.append(self.row_idx[i])

        return data, rows, cols

    def to_scipy_coo(self):
        """
        Converts the current matrix to a scipy COO (Coordinate) sparse matrix.

        This method retrieves the matrix elements using the `get_matrix_elements` method and then uses these elements to create a scipy COO sparse matrix.

        Returns
        -------
        coo_matrix
            The scipy COO sparse matrix representation of the current matrix.
        """
        from scipy.sparse import coo_matrix
        data, rows, cols = self.get_matrix_elements()
        return coo_matrix((data, (rows, cols)), dtype=complex)

    def to_scipy_csr(self):
        """
        Converts the current matrix to a scipy CSR (Compressed Sparse Row) sparse matrix.

        This method retrieves the matrix elements using the `get_matrix_elements` method and then uses these elements to create a scipy CSR sparse matrix.

        Returns
        -------
        csr_matrix
            The scipy CSR sparse matrix representation of the current matrix.
        """
        from scipy.sparse import csr_matrix
        data, rows, cols = self.get_matrix_elements()
        return csr_matrix((data, (rows, cols)), dtype=complex)

    def to_scipy_csc(self):
        """
        Converts the current matrix to a scipy CSC (Compressed Sparse Column) sparse matrix.

        This method retrieves the matrix elements using the `get_matrix_elements` method and then uses these elements to create a scipy CSC sparse matrix.

        Returns
        -------
        csc_matrix
            The scipy CSC sparse matrix representation of the current matrix.
        """
        from scipy.sparse import csc_matrix
        data, rows, cols = self.get_matrix_elements()
        return csc_matrix((data, (rows, cols)), dtype=complex)

    # TODO test
    def matrix_to_str(self) -> str:
        """Creates a string representation of the non-zero elements in the matrix"""
        string = ""
        cidx = {}
        C = 0

        for col in self.sub_columns:
            for mat in self.sub_columns[col].submatrices:
                # There may be multiple submatrices per sub_column, some of them
                # declared with 'declare_equations' and some with
                # 'declare_submatrix_view' or 'declare_subdiagonal_view' We use the
                # convention that names of submatrices declared with 'declare_equations'
                # start with 'I' such that these names are used to the rows of the total
                # matrix and the RHS vector
                if mat.name[0] == "I":
                    for i in range(mat.rows):
                        cidx[C] = f"{mat.name} mode={i}"
                        C+=1

        # Ms variable currently not used, but contains an overview of where the
        # submatrices are and which type they have like:
        # [['d' ' ' ' ' ' ']
        #  ['m' 'd' 'm' ' ']
        #  [' ' ' ' 'd' ' ']
        #  ['m' ' ' 'm' 'd']]
        N = len(self.sub_columns)
        Ms = np.zeros((N,N),dtype=str)
        Ms[:] = " "

        for col in self.sub_columns:
            for mat in self.sub_columns[col].submatrices:
                Ms[mat.to, self.sub_columns[col].index] = mat.type

        string += "\n"
        string += f"Matrix {self.name}: nnz={self.nnz} neqs={self.num_eqs}\n"
        string += "    (col, row) = value\n"
        ccol = -1

        # determine the longest string for both the row indices and the values
        # to format the number such that they align in the final output
        longest = np.zeros(2, dtype=int)
        for i in range(self.nnz):
            if self.col_ptr[ccol+1] == i:
                ccol += 1
            longest[0] = max(longest[0], len(f"({ccol}, {self.row_idx[i]})"))
            longest[1] = max(longest[1], len(f"{self.values[i]}"))

        ccol = -1
        for i in range(self.nnz):
            if self.col_ptr[ccol+1] == i:
                ccol += 1

            idx = f"({ccol}, {self.row_idx[i]})"
            value = f"{self.values[i]}"
            string += f"    {idx:{longest[0]}} = {value:{longest[1]}} : {cidx[ccol] if ccol in cidx else ''} -> {cidx[self.row_idx[i]] if self.row_idx[i] in cidx else ''}\n"
        return string

    def print_matrix(self):
        """Print a view of the non-zero elements in this matrix."""
        print(self.matrix_to_str())

    def print_submatrices(self):
        for column in self.sub_columns.values():
            print(column)

    # TODO test
    def rhs_to_string(self, unsigned rhs_index=0) -> str:
        """
        Create a string representation of the rhs vector corresponding to `rhs_index`.

        Parameters
        ----------
        rhs_index : unsigned, optional
            The rhs vector to print; defaults to 0

        Returns
        -------
        str
            RHS vector
        """
        string = ""
        cdef int i
        cdef const complex_t[::1] rhs
        cidx = {}
        C = 0

        if rhs_index >= self.num_rhs:
            raise ValueError(f"Invalid rhs index {rhs_index}")
        rhs = self.rhs_view[rhs_index]

        for col in self.sub_columns:
            for mat in self.sub_columns[col].submatrices:
                # There may be multiple submatrices per sub_column, some of them
                # declared with 'declare_equations' and some with
                # 'declare_submatrix_view' or 'declare_subdiagonal_view' We use the
                # convention that names of submatrices declared with 'declare_equations'
                # start with 'I' such that these names are used to the rows of the total
                # matrix and the RHS vector
                if mat.name[0] == "I":
                    for i in range(mat.rows):
                        cidx[C] = f"{mat.name} mode={i}"
                        C+=1
        string += "\n"
        string += f"Vector {self.name}: neqs={self.num_eqs}\n"
        string += "    (row) = value\n"

        # determine the longest string for both the row indices and the values
        # to format the number such that they align in the final output
        longest = np.zeros(2, dtype=int)
        for i in range(self.num_eqs):
            longest[0] = max(longest[0], len(f"({i})"))
            longest[1] = max(longest[1], len(f"{rhs[i]}"))

        for i in range(self.num_eqs):
            idx = f"({i})"
            value = f"{rhs[i]}"
            string += f"    {idx:{longest[0]}} = {value:{longest[1]}} : {cidx[i]}\n"
        return string


    def print_rhs(self, unsigned rhs_index=0):
        """
        Print a view of the rhs vector corresponding to `rhs_index`.

        Parameters
        ----------
        rhs_index : unsigned, optional
            The rhs vector to print; defaults to 0
        """
        print(self.rhs_to_string(rhs_index=rhs_index))


    cpdef clear_rhs(self, unsigned rhs_index=0) :
        """
        Zero all elements in the rhs vector corresponding to `rhs_index`.

        Parameters
        ----------
        rhs_index : unsigned, optional
            The rhs vector to clear; defaults to 0
        """
        if rhs_index >= self.num_rhs:
            raise ValueError(f"Invalid rhs index {rhs_index}")
        memset(&self.rhs[rhs_index * self.num_eqs], 0, self.num_eqs*sizeof(complex_t))

    cpdef factor(self) :
        """
        Factors the matrix.

        This method is not yet implemented.

        Raises
        ------
        NotImplementedError
            Always, as this method is not yet implemented.
        """
        raise NotImplementedError()

    cpdef refactor(self) :
        """
        Refactors the matrix.

        This method is not yet implemented.

        Raises
        ------
        NotImplementedError
            Always, as this method is not yet implemented.
        """
        raise NotImplementedError()

    cpdef const complex_t[::1] solve(self, int transpose=False, bint conjugate=False, unsigned rhs_index=0) noexcept:
        """
        Solves the matrix equation.

        This method is not yet implemented.

        Parameters
        ----------
        transpose : int, optional
            Whether to transpose the matrix before solving, by default False.
        conjugate : bint, optional
            Whether to conjugate the matrix before solving, by default False.
        rhs_index : unsigned, optional
            The index of the right-hand side to solve for, by default 0.

        Raises
        ------
        NotImplementedError
            Always, as this method is not yet implemented.

        Returns
        -------
        complex_t[::1]
            The solution to the matrix equation.
        """
        raise NotImplementedError()

    cpdef void solve_extra_rhs(self, int transpose=False, bint conjugate=False) noexcept:
        """
        Solves the matrix equation for extra right-hand sides.

        This method is not yet implemented.

        Parameters
        ----------
        transpose : int, optional
            Whether to transpose the matrix before solving, by default False.
        conjugate : bint, optional
            Whether to conjugate the matrix before solving, by default False.

        Raises
        ------
        NotImplementedError
            Always, as this method is not yet implemented.
        """
        raise NotImplementedError()

    cdef void zgemv(self, complex_t[::1] out, unsigned rhs_index=0) noexcept:
        """
        Performs a matrix-vector multiplication.

        This method is not yet implemented.

        Parameters
        ----------
        out : complex_t[::1]
            The output vector.
        rhs_index : unsigned, optional
            The index of the right-hand side to multiply with, by default 0.

        Raises
        ------
        NotImplementedError
            Always, as this method is not yet implemented.
        """
        raise NotImplementedError()


cdef class SubCCSView:
    """
    An abstract class representing common features between dense and sparse diagonal
    structured sub-matrices.

    This class serves as a base class for other classes that represent specific types of
    sub-matrices, such as dense or sparse diagonal structured sub-matrices. It provides a
    unified interface for accessing and manipulating these sub-matrices.

    The class holds a weak reference to the original matrix, the starting and ending
    indices of the submatrix view in the original matrix, and a flag indicating whether
    to fill the submatrix view with the conjugate of the original matrix values.

    It also provides properties to get the starting and ending indices of the submatrix
    view (`from_idx` and `to_idx`), the shape of the submatrix view (`shape`), and the
    strides of the submatrix view (`strides`).

    Attributes
    ----------
    name : unicode
        The name of the submatrix view.
    M : weakref
        A weak reference to the original matrix.
    A : NoneType
        Placeholder for the actual submatrix data. This should be implemented in
        subclasses.
    _from : Py_ssize_t
        The starting index of the submatrix view in the original matrix.
    _to : Py_ssize_t
        The ending index of the submatrix view in the original matrix.
    conjugate_fill : bint
        Whether to fill the submatrix view with the conjugate of the original matrix
        values.
    """
    def __init__(self, CCSMatrix Matrix, Py_ssize_t _from, Py_ssize_t _to, unicode name, bint conjugate_fill):
        self.name = name
        self.M = weakref.ref(Matrix)
        self.A = None
        self._from  = _from
        self._to    = _to
        self.conjugate_fill = conjugate_fill

    @property
    def from_idx(self):
        """
        Returns the starting index of the submatrix view in the original matrix.

        Returns
        -------
        Py_ssize_t
            The starting index of the submatrix view.
        """
        return self._from

    @property
    def to_idx(self):
        """
        Returns the ending index of the submatrix view in the original matrix.

        Returns
        -------
        Py_ssize_t
            The ending index of the submatrix view.
        """
        return self._to

    @property
    def shape(self):
        """
        Returns the shape of the submatrix view.

        Returns
        -------
        tuple
            The shape of the submatrix view, as a tuple of two integers.
        """
        return (self.size1, self.size2)

    @property
    def strides(self):
        """
        Returns the strides of the submatrix view.

        Returns
        -------
        tuple
            The strides of the submatrix view, as a tuple of two integers.
        """
        return (self.stride1, self.stride2)

    @property
    def view(self):
        return self.A

    def __getitem__(self, key):
        return self.A[key]

    def __setitem__(self, key, value):
        # replace all elements
        if self.conjugate_fill:
            self.A[key] = -value.conjugate() # minus sign for off-diag blocks
        else:
            self.A[key] = -value # minus sign for off-diag blocks

    def _updateview_(self):
        """
        Updates the numpy array view of the submatrix when the underlying matrix
        has been constructed.

        This method retrieves the numpy array view of the submatrix from the original
        matrix, and stores it along with some details about it. These details are used
        in the fast filling routines.

        It also updates the shape and strides of the submatrix view, and the view and
        size of the right-hand side (rhs) of the system of equations represented by
        the original matrix.

        Note: This method is intended to be called internally, not by users of the class.
        """
        # Here we store the numpy array wrapper for the memory location
        # as well as some details about it. The details are used in the
        # fast filling routines
        cdef CCSMatrix m = self.M()
        self.A = m.get_numpy_array_view(self._from, self._to, &self.ptr, &self.from_rhs_index)
        self.size1 = self.A.shape[0]
        self.stride1 = self.A.strides[0]//16
        if self.A.ndim == 2:
            self.size2 = self.A.shape[1]
            self.stride2 = self.A.strides[1]//16
            self.from_rhs_view = m.rhs_view[:, self.from_rhs_index:(self.from_rhs_index+self.size2)]
            self.from_rhs_view_size = self.size2
        else:
            self.size2 = 0
            self.stride2 = 0
            self.from_rhs_view = m.rhs_view[:, self.from_rhs_index:(self.from_rhs_index+self.size1)]
            self.from_rhs_view_size = self.size1

    cdef void fill_za(self, complex_t a) noexcept:
        raise NotImplementedError()

    cdef void fill_zd(self, complex_t[::1] D) noexcept:
        raise NotImplementedError()

    cdef void fill_dv(self, double[::1] D) noexcept:
        raise NotImplementedError()

    cdef void fill_za_dv(self, complex_t a, double[::1] D) noexcept:
        raise NotImplementedError()

    cdef void fill_zd_2(self, const complex_t* D, int s1) noexcept nogil:
        raise NotImplementedError()

    cdef void fill_za_zd_2(self, complex_t a, const complex_t* D, int stride) noexcept nogil:
        raise NotImplementedError()

    cdef void fill_za_zm(self, complex_t a, complex_t[:,::1] M) noexcept:
        raise NotImplementedError()

    cdef void fill_za_zm_2(self, complex_t a, const complex_t* M, int s1, int s2) noexcept:
        raise NotImplementedError()

    cdef void fill_za_zmc(self, complex_t a, const complex_t* M, int s1, int s2) noexcept:
        raise NotImplementedError()

    cdef void fill_za_zmv(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept:
        raise NotImplementedError()

    cdef void fill_za_zmvc(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept:
        raise NotImplementedError()

    cdef void fill_zm(self, complex_t[:,::1] M) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_za(self, complex_t a) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_zd(self, complex_t[::1] D) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_dd(self, double[::1] D) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_za_dd(self, complex_t a, double[::1] D) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_zd_2(self, const complex_t* D, int s1) noexcept nogil:
        raise NotImplementedError()

    cdef void fill_negative_za_zd_2(self, complex_t a, const complex_t* D, int stride) noexcept nogil:
        raise NotImplementedError()

    cdef void fill_negative_za_zv(self, complex_t a, DenseZVector*V) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_za_zm(self, complex_t a, complex_t[:,::1] M) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_za_zm_2(self, complex_t a, DenseZMatrix* M) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_za_zmc(self, complex_t a, const complex_t* M, int s1, int s2) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_za_zmv(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_za_zmvc(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept:
        raise NotImplementedError()

    cdef void fill_negative_zm(self, complex_t[:,::1] M) noexcept:
        raise NotImplementedError()

    cdef void fill_prop_za_zm(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, DenseZMatrix* M, bint increment) noexcept:
        raise NotImplementedError()

    cdef void fill_neg_prop_za_zm(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, DenseZMatrix* M, bint increment) noexcept:
        raise NotImplementedError()

    cdef void fill_prop_za(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, bint increment) noexcept:
        raise NotImplementedError()

    cdef void fill_neg_prop_za(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, bint increment) noexcept:
        raise NotImplementedError()


cdef class SubCCSMatrixView(SubCCSView):
    """
    This class represents a sub-matrix view of a CCS sparse matrix. This allows
    code to access and set values without worrying about the underlying
    sparse compression being used. Although so far this is just for CCS
    formats.

    This object will get a view of a n-by-m sub-matrix starting at index (i,j).
    The values of his matrix will be set initially to the coordinates.
    """
    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_za(self, complex_t a) noexcept:
        cdef Py_ssize_t i, j
        if self.conjugate_fill:
            a = a.conjugate()

        for i in range(self.size1):
            for j in range(self.size2):
                self.ptr[i*self.stride1 + j*self.stride2] = a

    # Just here so it can be called from python for demonstration purposes
    # could maybe be a cleaner way?
    cpdef void _fill_za_debug(self, complex_t a) noexcept:
        self.fill_za(a)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_zm(self, complex_t[:,::1] M) noexcept:
        assert(M.shape[0] == self.size1 and M.shape[1] == self.size2)
        cdef Py_ssize_t i, j
        if self.conjugate_fill:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = conj(M[i,j])
        else:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = M[i,j]

    # Just here so it can be called from python for demonstration purposes
    # could maybe be a cleaner way?
    cpdef void _fill_zm_debug(self, complex_t[:,::1] M) noexcept:
        self.fill_zm(M)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_za_zm(self, complex_t a, complex_t[:,::1] M) noexcept:
        assert(M.shape[0] == self.size1 and M.shape[1] == self.size2)
        cdef Py_ssize_t i, j
        if self.conjugate_fill:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = conj(a * M[i,j])
        else:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = a * M[i,j]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_za_zm_2(self, complex_t a, const complex_t* M, int s1, int s2) noexcept:
        cdef int i, j
        if self.conjugate_fill:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = conj(a * M[i*s1 + j*s2])
        else:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = a * M[i*s1 + j*s2]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_za_zmc(self, complex_t a, const complex_t* M, int s1, int s2) noexcept:
        cdef int i, j
        if self.conjugate_fill:
            a = conj(a)
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = a * M[i*s1 + j*s2]
        else:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = a * conj(M[i*s1 + j*s2])

    def test_za_zm_2(self, complex a, np.ndarray[complex, ndim=2, mode="c"] M):
        self.fill_za_zm_2(a, <complex_t*>&M[0,0], M[:].strides[0]//16, M[:].strides[1]//16)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_za_zmv(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept:
        """Sets view of submatrix to a * M @ V
        """
        cdef int i, k, stride
        assert(self.size1 == 1 or self.size2 == 1) # This view must be some 1D array either col or row
        assert(M.size1 == V.size) # Make sure size of matrix is correct for product
        assert( # check we vector is right size for this input matrix
            (self.size1 == 1 and self.size2 == V.size)
            or (self.size2 == 1 and self.size1 == V.size)
        )
        if V.size == self.size1:
            stride = self.stride1
        else:
            stride = self.stride2

        for i in range(V.size): # for each output element
            self.ptr[i*stride] = 0 # reset for M@V
            # do the matrix product
            for k in range(M.size2): # k-th col
                self.ptr[i*stride] = self.ptr[i*stride] + M.ptr[i*M.stride1 + k*M.stride2] * V.ptr[k*V.stride]
            self.ptr[i*stride] *= a

        if self.conjugate_fill:
            for i in range(V.size):
                # Can't use .imag to just select the imaginary part otherwise
                # cython injects python code... so do a bit of pointer math to get
                # double* access to imaginary part
                ((<double*>self.ptr) + 2*i*stride + 1)[0] *= -1

    def do_fill_za_zmvc(self, complex_t a, complex_t[:,::1] M, complex_t[::1] V):
        cdef DenseZVector v
        cdef DenseZMatrix m

        m.ptr = &M[0,0]
        m.size1 = M.shape[0]
        m.size2 = M.shape[1]
        m.stride1 = M.strides[0]//16
        m.stride2 = M.strides[1]//16

        v.ptr = &V[0]
        v.size = V.shape[0]
        v.stride = V.strides[0]//16

        self.fill_za_zmvc(a, &m, &v)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_za_zmvc(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept:
        """Sets view of submatrix to

        .. math::
            a * (M @ V^*)
        """
        cdef int i, k, stride
        assert(self.size1 == 1 or self.size2 == 1) # This view must be some 1D array either col or row
        assert(M.size1 == V.size) # Make sure size of matrix is correct for product
        assert( # check the vector is right size for this input matrix
            (self.size1 == 1 and self.size2 == V.size)
            or (self.size2 == 1 and self.size1 == V.size)
        )
        # Not being too fussed about the shape of the input vector, can
        # be either row or column vector
        if V.size == self.size1:
            stride = self.stride1
        else:
            stride = self.stride2

        for i in range(V.size): # for each output element
            self.ptr[i*stride] = 0 # reset for M@V
            # do the matrix product
            for k in range(M.size2): # k-th col
                self.ptr[i*stride] = self.ptr[i*stride] + M.ptr[i*M.stride1 + k*M.stride2] * conj(V.ptr[k*V.stride])
            self.ptr[i*stride] *= a

        if self.conjugate_fill:
            for i in range(V.size):
                # Can't use .imag to just select the imaginary part otherwise
                # cython injects python code... so do a bit of pointer math to get
                # double* access to imaginary part
                ((<double*>self.ptr) + 2*i*stride + 1)[0] *= -1

    def do_fill_prop_za_zm(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, complex_t[:,::1] M, bint increment):
        cdef DenseZMatrix m
        m.ptr = &M[0,0]
        m.size1 = M.shape[0]
        m.size2 = M.shape[1]
        m.stride1 = M.strides[0]//16
        m.stride2 = M.strides[1]//16
        self.fill_prop_za_zm(V, rhs_idx, a, &m, increment)


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_prop_za_zm(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, DenseZMatrix* M, bint increment) noexcept:
        """Computes the product of SubCCSView with it's current incoming RHS value, then multiplies it with another matrix M
        and a constant a. This method is primarily used when propagating a carrier field through a particular connection,
        such as a mirror reflection, then multiplies it with a scattering matrix to compute how much signal field is
        generated - such as from pitch/yaw signal injections.

        .. math::
            a M \cdot V \cdot v_{\mathrm{rhs}}

        Notes
        -----
        This filled method can only be used on row or column vectors.

        Parameters
        ----------
        V : SubCCSView
            A view from this or another matrix. This is dot product with the RHS entries that correspond
            to the fields going into this particular sub-matrix.

        rhs_idx : unsigned int
            Which RHS index to use, typically 0 unless using multiple RHS noise vectors

        a : complex
            Complex value

        M : *DenseZMatrix
            Pointer to dense matrix to left multiply with SubCCSView product

        increment : boolean
            When true, the result of the calculation is added to the pre-existing matrix values
        """
        cdef:
            Py_ssize_t i, _i, j, k
            complex_t tmp

        assert(self.size1 == 1 or self.size2 == 1) # This view must be some 1D array either col or row
        assert(M.size1 == self.size1)
        assert(M.size2 == V.size1)
        # this function needs some memory to store intermediate values.
        # check if we need to allocate some memory, and if there is some, make sure we have enough
        if self.prop_za_zm_workspace is None or self.prop_za_zm_workspace.shape[0] < V.from_rhs_view.shape[1]:
            # GC should deal with any previous allocations here. In general this should not need to be
            # called multiples times per simulation as it shouldn't change
            self.prop_za_zm_workspace = np.zeros(V.from_rhs_view.shape[1], dtype=complex)
        # Zero workspace for V.matrix @ V.rhs
        for i in range(V.from_rhs_view.shape[1]):
            self.prop_za_zm_workspace[i] = 0
        # Remember that V is a CCS view, so we iterate over it
        # per column, rather than per row
        for j in range(V.size1):
            for i in range(V.size2):
                self.prop_za_zm_workspace[i] = self.prop_za_zm_workspace[i] + V.from_rhs_view[0][i] * V.ptr[i*V.stride1 + j*V.stride2]

        if increment:
            # when incrementing we can't just conjugate after the fact
            for i in range(M.size1):
                _i = i*self.stride1
                # do the matrix product
                tmp = 0
                for k in range(M.size2): # k-th col
                    tmp += M.ptr[i*M.stride1 + k*M.stride2] * self.prop_za_zm_workspace[k]
                if self.conjugate_fill:
                    self.ptr[_i] += conj(a * tmp)
                else:
                    self.ptr[_i] += a * tmp
        else:
            for i in range(M.size1):
                _i = i*self.stride1
                self.ptr[_i] = 0 # reset for M @ V
                # do the matrix product
                for k in range(M.size2): # k-th col
                    self.ptr[_i] += M.ptr[i*M.stride1 + k*M.stride2] * self.prop_za_zm_workspace[k]
                self.ptr[_i] *= a
            # As we are overwriting the original submatrix values we can just
            if self.conjugate_fill:
                for i in range(self.size1):
                    # Can't use .imag to just select the imaginary part otherwise
                    # cython injects python code... so do a bit of pointer math to get
                    # double* access to imaginary part
                    ((<double*>self.ptr) + 2*i*self.stride1 + 1)[0] *= -1


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_neg_prop_za_zm(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, DenseZMatrix* M, bint increment) noexcept:
        self.fill_prop_za_zm(V, rhs_idx, -a, M, increment)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_prop_za(self, SubCCSView M, Py_ssize_t rhs_idx, complex_t a, bint increment) noexcept:
        cdef complex_t* V = &M.from_rhs_view[rhs_idx][0]
        cdef Py_ssize_t N, stride, i, k
        # this current subview that we'll fill should be a row or column vector
        # we don't worry here about whether the matrix product is with a col or row
        # inuput vector though
        if self.size1 == self.size2 == 1:
            N = 1
            stride = max(self.stride1, self.stride2)
        else:
            # does a matrix vector product, so output must be a vector, or a 1x1
            # TODO assert statement temporarily disabled, see https://gitlab.com/ifosim/finesse/finesse3/-/issues/612
            # assert self.size1 == 1 ^ self.size2 == 1, f"self.size wrong: size1:{self.size1} size2{self.size2}"
            if self.size1 == 1:
                N = self.size2
                stride = self.stride2
            else:
                N = self.size1
                stride = self.stride1
            assert M.size1 == N, "M.side1 != N"

        # By the nature of how we get the rhs slice of the vector associated with the submatrix
        # V, it should always be the right size for a matrix product
        for i in range(N): # for each output element
            if not increment:
                self.ptr[i*stride] = 0 # reset for M@V
            # do the matrix product
            if self.conjugate_fill:
                for k in range(M.size2): # k-th col
                    self.ptr[i*stride] += conj(a * M.ptr[i*M.stride1 + k*M.stride2] * V[k]) # V stride is always 1
            else:
                for k in range(M.size2): # k-th col
                    self.ptr[i*stride] += a*M.ptr[i*M.stride1 + k*M.stride2] * V[k] # V stride is always 1

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_neg_prop_za(self, SubCCSView V, Py_ssize_t rhs_idx, complex_t a, bint increment) noexcept:
        self.fill_prop_za(V, rhs_idx, -a, increment)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za(self, complex_t a) noexcept:
        self.fill_za(-a)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za_zv(self, complex_t a, DenseZVector*V) noexcept:
        cdef int i
        cdef Py_ssize_t stride
        assert(self.size1 == 1 or self.size2 == 1) # this view must be a row/col vector
        if self.size1 == V.size:
            stride = self.stride1
        elif self.size2 == V.size:
            stride = self.stride2
        else:
            raise Exception(f"Wrong dimensions for vector fill in {self.name}")

        a = -a # do negative fill
        if self.conjugate_fill:
            for i in range(self.size1):
                self.ptr[i*stride] = conj(a * V.ptr[i*V.stride])
        else:
            for i in range(self.size1):
                self.ptr[i*stride] = a * V.ptr[i*V.stride]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_zm(self, complex_t[:,::1] M) noexcept:
        self.fill_za_zm(-1, M)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za_zm(self, complex_t a, complex_t[:,::1] M) noexcept:
        self.fill_za_zm(-a, M)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za_zm_2(self, complex_t a, DenseZMatrix* M) noexcept:
        a = -a
        cdef int i, j
        if self.conjugate_fill:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = conj(a * M.ptr[i*M.stride1 + j*M.stride2])
        else:
            for i in range(self.size1):
                for j in range(self.size2):
                    self.ptr[i*self.stride1 + j*self.stride2] = a * M.ptr[i*M.stride1 + j*M.stride2]


    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za_zmc(self, complex_t a, const complex_t* M, int s1, int s2) noexcept:
        self.fill_za_zmc(-a, M, s1, s2)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za_zmv(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept:
        self.fill_za_zmv(-a, M, V)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za_zmvc(self, complex_t a, DenseZMatrix* M, DenseZVector* V) noexcept:
        self.fill_za_zmvc(-a, M, V)


cdef class SubCCSMatrixViewDiagonal(SubCCSView):
    """
    This class represents a sub-matrix view of a CCS sparse matrix. This allows
    code to access and set values without worrying about the underlying
    sparse compression being used. Although so far this is just for CCS
    formats.

    This object will get a view of a n-by-m sub-matrix starting at index (i,j).
    The values of his matrix will be set initially to the coordinates.
    """
    cdef void fill_za(self, complex_t a) noexcept:
        cdef int i
        if self.conjugate_fill:
            a = a.conjugate()

        for i in range(self.size1):
            self.ptr[i*self.stride1] = a

    # Just here so it can be called from python for demonstration purposes
    # could maybe be a cleaner way?
    cpdef void _fill_za_debug(self, complex_t a) noexcept:
        self.fill_za(a)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_zd(self, complex_t[::1] D) noexcept:
        cdef int i
        if self.conjugate_fill:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = conj(D[i])
        else:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = D[i]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_dv(self, double[::1] D) noexcept:
        cdef int i
        for i in range(self.size1):
            self.ptr[i*self.stride1] = D[i]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_za_dv(self, complex_t a, double[::1] D) noexcept:
        cdef int i
        for i in range(self.size1):
            self.ptr[i*self.stride1] = a * D[i]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_zd_2(self, const complex_t* D, int s1) noexcept nogil:
        cdef int i
        if self.conjugate_fill:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = conj(D[i*s1])
        else:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = D[i*s1]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_za_zd_2(self, complex_t a, const complex_t* D, int D_stride) noexcept nogil:
        cdef int i
        if self.conjugate_fill:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = conj(D[i*D_stride]*a)
        else:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = D[i*D_stride]*a

    cdef void fill_negative_za(self, complex_t a) noexcept:
        self.fill_za(-a)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_zd(self, complex_t[::1] D) noexcept:
        cdef int i
        if self.conjugate_fill:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = conj(-D[i])
        else:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = -D[i]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_dd(self, double[::1] D) noexcept:
        self.fill_za_dv(-1, D)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za_dd(self, complex_t a, double[::1] D) noexcept:
        self.fill_za_dv(-a, D)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_zd_2(self, const complex_t* D, int s1) noexcept nogil:
        cdef int i
        if self.conjugate_fill:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = conj(-D[i*s1])
        else:
            for i in range(self.size1):
                self.ptr[i*self.stride1] = -D[i*s1]

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef void fill_negative_za_zd_2(self, complex_t a, const complex_t* D, int D_stride) noexcept nogil:
        self.fill_za_zd_2(-a, D, D_stride)

    # def test_za(self, value):
    #     self.fill_negative_za(value)

    # def test_zd(self, value):
    #     self.fill_negative_zd(value)s


cdef class SubCCSView1DArray:
    """
    This is a class for storing sub-matrix views for
    coupling directly to another single SubCCSView. It
    offers a 1D `PyObject*` array which can be iterated
    over in C for fast access matrix data without having
    to do reference inc/dec in fast loops.

    It can be accessed from Python for setting views,
    however it doesn't support slicing or wraparounds.

    Examples
    --------

    Cython access to views should be cast to a `SubCCSView`
    before using it:

    >>>> (<SubCCSView>arr.views[i]).fill()

    This should result in no python calls when checking the
    Cython analysis information.

    If you store this `SubCCSView` into a variable then a
    reference count will happen.
    """
    def __cinit__(self, Py_ssize_t size):
        self.size = size
        self.views = <PyObject**> calloc(size, sizeof(PyObject*))
        if not self.views:
            raise MemoryError()

    @property
    def ndim(self):
        """Number of dimensions of this collection of SubCCSViews"""
        return 1

    def __getitem__(self, key):
        cdef int idx = <int?>key
        if idx < 0 or idx >= self.size:
            raise IndexError(f"Index must be {0} <= key < {self.size}")

        if self.views[idx] == NULL:
            return None
        else:
            return <object>self.views[idx]

    def __setitem__(self, key, value):
        cdef int idx = <int?>key
        if idx < 0 or idx >= self.size:
            raise IndexError(f"Index must be {0}<= key < {self.size}")
        if value is not None and not isinstance(value, SubCCSView):
            raise ValueError("Value is not a derivative of SubCCSView")

        if self.views[idx] != NULL:
            # Decrease ref for anything stored already
            Py_XDECREF(self.views[idx])

        cdef PyObject* ptr

        if value is None:
            ptr = NULL
        else:
            ptr = <PyObject*>value
            Py_XINCREF(ptr)

        self.views[idx] = ptr

    def __dealloc__(self):
        cdef int i
        for i in range(self.size):
            if self.views[i] != NULL:
                Py_XDECREF(self.views[i])

        free(self.views)


cdef class SubCCSView2DArray:
    """
    This is a class for storing sub-matrix views. It
    offers a 2D `PyObject**` array which can be iterated
    over in C for fast access matrix data without having
    to do reference inc/dec in fast loops.

    It can be accessed from Python for setting views,
    however it doesn't support slicing or wraparounds.

    Examples
    --------

    Cython access to views should be cast to a `SubCCSView`
    before using it:

    >>>> (<SubCCSView>arr.views[i][j]).fill()

    This should result in no python calls when checking the
    Cython analysis information.

    If you store this `SubCCSView` into a variable then a
    reference count will happen.
    """
    def __cinit__(self, Py_ssize_t rows, Py_ssize_t cols):
        cdef int i
        self.rows = rows
        self.cols = cols
        self.shape = (rows, cols)
        self.views = <PyObject***> calloc(rows, sizeof(PyObject**))
        if not self.views:
            raise MemoryError()
        for i in range(rows):
            self.views[i] = <PyObject**> calloc(cols, sizeof(PyObject*))
            if not self.views[i]:
                raise MemoryError()


    @property
    def ndim(self):
        """Number of dimensions of this collection of SubCCSViews"""
        return 2

    def __getitem__(self, key):
        cdef tuple idx = key
        if len(key) != 2:
            raise IndexError("Index must be 2D")
        if idx[0] < 0 or idx[0] >= self.rows:
            raise IndexError(f"Row index must be {0} <= key < {self.rows}")
        if idx[1] < 0 or idx[1] >= self.cols:
            raise IndexError(f"Column index must be {1} <= key < {self.cols}")

        if self.views[idx[0]][idx[1]] == NULL:
            return None
        else:
            return <object>self.views[idx[0]][idx[1]]

    def __setitem__(self, key, value):
        cdef tuple idx = key
        if len(key) != 2:
            raise IndexError("Index must be 2D")
        if idx[0] < 0 or idx[0] >= self.rows:
            raise IndexError(f"Row index must be 0 <= key:{idx[0]} < {self.rows}")
        if idx[1] < 0 or idx[1] >= self.cols:
            raise IndexError(f"Column index must be 0 <= key:{idx[1]} < {self.cols}")
        if value is not None and not isinstance(value, SubCCSView):
            raise ValueError("Value is not a derivative of SubCCSView")

        if self.views[idx[0]][idx[1]] != NULL:
            # Decrease ref for anything stored already
            Py_XDECREF(self.views[idx[0]][idx[1]])

        cdef PyObject* ptr

        if value is None:
            ptr = NULL
        else:
            ptr = <PyObject*>value
            Py_XINCREF(ptr)

        self.views[idx[0]][idx[1]] = ptr

    def __dealloc__(self):
        cdef int i
        cdef int j
        for i in range(self.rows):
            for j in range(self.cols):
                if self.views[i][j] != NULL:
                    Py_XDECREF(self.views[i][j])
            free(self.views[i])
        free(self.views)


cdef class KLUMatrix(CCSMatrix):
    """An object representation of a CCS matrix with methods to factor
    and solve the matrix via KLU.

    Parameters
    ----------
    name : unicode
        The name of the matrix.
    klu_ordering : int, optional
        The ordering method to use in KLU, by default 0.
    klu_scale : int, optional
        The scaling method to use in KLU, by default 2.
    klu_btf : int, optional
        Whether to use BTF preordering in KLU, by default 1.
    klu_maxwork : int, optional
        The maximum amount of work to do in KLU, by default 0.
    tol : float, optional
        The tolerance to use in KLU for partial pivotting, by default 1e-3.
    """

    def __cinit__(self, unicode name, *, int klu_ordering=0, int klu_scale=2, int klu_btf=1, int klu_maxwork=0, double tol=1e-3):
        self.Symbolic = NULL
        self.Numeric  = NULL

        klu_l_defaults(&self.Common)

        self.Common.tol      = tol
        self.Common.ordering = klu_ordering
        self.Common.scale    = klu_scale
        self.Common.btf      = klu_btf
        self.Common.maxwork  = klu_maxwork

    def __init__(self, name, *, klu_ordering=0, klu_scale=2, klu_btf=1, klu_maxwork=0, double tol=1e-3):
        super().__init__(name)

    def __dealloc__(self):
        if self.Numeric:  klu_zl_free_numeric(&self.Numeric, &self.Common)
        if self.Symbolic: klu_l_free_symbolic(&self.Symbolic, &self.Common)

    cpdef factor(self) :
        """
        Factor the matrix using KLU.

        This method first analyzes the matrix structure using `klu_l_analyze`,
        then factors the matrix using `klu_zl_factor`, and finally sorts the
        factorization using `klu_zl_sort`.

        Raises
        ------
        Exception
            If an error occurs in KLU during analysis, factoring, or sorting,
            an exception is raised with a message indicating the status code
            and its corresponding string.
        """
        self.Symbolic = klu_l_analyze(self.num_eqs,
                                      self.col_ptr,
                                      self.row_idx,
                                      &self.Common)

        if self.Common.status != KLU_OK:
            # TODO refactor into common method?
            raise Exception(
                "An error occurred in KLU during analysis: STATUS={} ({})\n".format(
                    self.Common.status, status_string(self.Common.status)
                    )
                )

        self.Numeric = klu_zl_factor(self.col_ptr,
                                     self.row_idx,
                                     <double*>self.values,
                                     self.Symbolic,
                                     &(self.Common))

        if self.Common.status != KLU_OK:
            raise Exception(
                "An error occurred in KLU during factoring: STATUS={} ({})\n".format(
                    self.Common.status, status_string(self.Common.status)
                    )
                )

        klu_zl_sort(self.Symbolic, self.Numeric, &(self.Common))

        if self.Common.status != KLU_OK:
            raise Exception(
                "Sort failed: STATUS={} ({})\n".format(
                    self.Common.status, status_string(self.Common.status)
                    )
                )

    cpdef refactor(self) :
        """
        Refactor the matrix using KLU.

        This method attempts to refactor the matrix using `klu_zl_refactor`. If the
        refactorization is not successful and the matrix appears singular (status
        code 1), it tries to factor the matrix again using the `factor` method. If
        the matrix is still not factorizable, an exception is raised.

        Raises
        ------
        RuntimeError
            If an error occurs in KLU during refactorization and the matrix does not
            appear singular, a runtime error is raised with a message indicating the
            status code and its corresponding string.
        """
        klu_zl_refactor(self.col_ptr,
                        self.row_idx,
                         <double*>self.values,
                         self.Symbolic,
                         self.Numeric,
                         &(self.Common))

        if self.Common.status != KLU_OK:
            # Occassionaly the refactor is not good enough and the matrix appears singular
            # In some cases this can be fixed with a proper factorisation again
            if self.Common.status == 1:
                # warn("Matrix appears singular, trying factorisation again") # probably not worth warning user about
                self.factor() # if the matrix is properly messed up this will raise an exception
            else:
                raise RuntimeError("An error occurred in KLU during refactor: STATUS={} ({})".format(self.Common.status, status_string(self.Common.status)))


    cpdef const complex_t[::1] solve(self, int transpose=False, bint conjugate=False, unsigned rhs_index=0) noexcept:
        """
        Solve the matrix with options for transposing and conjugating.

        If `transpose` is False, solves the linear system :math:`Ax = b` using the
        ``Symbolic`` and ``Numeric`` objects stored by this class.

        Otherwise, solves the linear system :math:`A^T x = b` or :math:`A^H x = b`. The
        `conjugate` option is zero for :math:`A^T x = b` or non-zero for :math:`A^H x = b`.

        Parameters
        ----------
        transpose : bool
            Flag determining whether to solve the transpose of the matrix.

        conjugate : bool
            Flag determining whether to solve :math:`A^T x =b` or :math:`A^H x = b`
            for the transposed linear system.

        rhs_index : unsigned, optional
            Which rhs vector to solve for. If unset, the default rhs vector is used.

        Returns
        -------
        out : np.ndarray
            The (negative) solution vector.
        """
        if rhs_index >= self.num_rhs:
            raise ValueError(f"Invalid rhs index {rhs_index}")

        if transpose:
            klu_zl_tsolve(self.Symbolic, self.Numeric, self.num_eqs, 1, <double*>&self.rhs[rhs_index * self.num_eqs], conjugate, &self.Common);
        else:
            klu_zl_solve( self.Symbolic, self.Numeric, self.num_eqs, 1, <double*>&self.rhs[rhs_index * self.num_eqs], &self.Common);

        # rtn = self.rhs_view.copy()
        # rtn.flags.writeable = False

        # return rtn
        return self.rhs_view[rhs_index]

    cpdef void solve_extra_rhs(self, int transpose=False, bint conjugate=False) noexcept:
        """
        Solve the matrix for all present rhs vectors except the main one, with options for
        transposing and conjugating.

        If `transpose` is False, solves the linear system :math:`Ax = b` using the
        ``Symbolic`` and ``Numeric`` objects stored by this class.

        Otherwise, solves the linear system :math:`A^T x = b` or :math:`A^H x = b`. The
        `conjugate` option is zero for :math:`A^T x = b` or non-zero for :math:`A^H x = b`.

        As multiple rhs vectors are solved simultaneously, the result is not returned here,
        and must be retrieved via ``get_rhs_view``.

        Parameters
        ----------
        transpose : bool
            Flag determining whether to solve the transpose of the matrix.

        conjugate : bool
            Flag determining whether to solve :math:`A^T x =b` or :math:`A^H x = b`
            for the transposed linear system.
        """
        if transpose:
            klu_zl_tsolve(self.Symbolic, self.Numeric, self.num_eqs, self.num_rhs - 1, <double*>&self.rhs[self.num_eqs], conjugate, &self.Common);
        else:
            klu_zl_solve( self.Symbolic, self.Numeric, self.num_eqs, self.num_rhs - 1, <double*>&self.rhs[self.num_eqs], &self.Common);

    cpdef double rgrowth(self) noexcept:
        """klu_rgrowth : compute the reciprocal pivot growth

        Pivot growth is computed after the input matrix is permuted, scaled, and
        off-diagonal entries pruned.  This is because the LU factorization of each
        block takes as input the scaled diagonal blocks of the BTF form.  The
        reciprocal pivot growth in column j of an LU factorization of a matrix C
        is the largest entry in C divided by the largest entry in U; then the overall
        reciprocal pivot growth is the smallest such value for all columns j.  Note
        that the off-diagonal entries are not scaled, since they do not take part in
        the LU factorization of the diagonal blocks.

        In MATLAB notation:
            rgrowth = min (max (abs ((R \ A(p,q)) - F)) ./ max (abs (U)))

        Returns
        -------
        reciprocal_pivot_growth : double
        """
        cdef SuiteSparse_long ok

        ok = klu_zl_rgrowth (
            self.col_ptr,
            self.row_idx,
            <double*>self.values,
            self.Symbolic,
            self.Numeric,
            &self.Common
        )

        if ok == 0:
            raise Exception("Error occurred whilst computing rgrowth")

        return self.Common.rgrowth

    cpdef double rcond(self) noexcept:
        """ klu_rcond: compute min(abs(diag(U))) / max(abs(diag(U)))

        This function returns the smallest diagonal entry of U divided by the largest, which is a
        very crude estimate of the reciprocal of the condition number of the matrix A. It is very
        cheap to compute, however. In MATLAB notation, rcond = min(abs(diag(U))) /
        max(abs(diag(U))). If the matrix is singular, rcond will be zero.
        """
        cdef SuiteSparse_long ok

        ok = klu_zl_rcond (
            self.Symbolic,
            self.Numeric,
            &self.Common
        )

        if ok == 0:
            raise Exception("Error occurred whilst computing rcond")

        return self.Common.rcond

    cpdef double condest(self) noexcept:
        """klu_condest

        Computes a reasonably accurate estimate of the 1-norm condition number, using
        Hager's method, as modified by Higham and Tisseur (same method as used in
        MATLAB's condest)
        """
        cdef SuiteSparse_long ok

        ok = klu_zl_condest (
            self.col_ptr,
            <double*>self.values,
            self.Symbolic,
            self.Numeric,
            &self.Common
        )

        if ok == 0:
            raise Exception("Error occurred whilst computing condest")

        return self.Common.condest

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cpdef void zgemv(self, complex_t[::1] out, unsigned rhs_index=0) noexcept:
        """
        Multiply this matrix with the rhs vector corresponding to `rhs_index`, and store the result
        in `out`.

        Performs the operation :math:`y = A x`.

        Parameters
        ----------
        out : complex_t[::1]
            The vector to store the result in.
        rhs_index : unsigned, optional
            The rhs vector to multiply this matrix with; defaults to 0.
        """
        cdef:
            int ccol
            int crow

        if rhs_index >= self.num_rhs:
            raise ValueError(f"Invalid rhs index {rhs_index}")
        x = self.rhs_view[rhs_index]

        out[:] = 0
        ccol = -1
        for i in range(self.nnz):
            if self.col_ptr[ccol+1] == i:
                ccol += 1

            crow = self.row_idx[i]

            out[ccol] = out[ccol] + x[crow] * self.values[i]
