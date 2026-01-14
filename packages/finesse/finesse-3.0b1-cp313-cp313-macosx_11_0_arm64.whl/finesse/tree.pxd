cdef class TreeNode:
    cdef:
        public bint empty
        public list children
        public TreeNode parent
        public str edge_info
        str __name
