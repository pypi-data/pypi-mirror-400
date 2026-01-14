from finesse.tree import TreeNode
from finesse.tree cimport TreeNode

cdef class ParameterChangingTreeNode(TreeNode):
    cdef public tuple parameters_changing

cdef class BaseSolution(ParameterChangingTreeNode):
    cdef public:
        double time # time taken to generate this solution
