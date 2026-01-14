# PyKLU/_klu.pyx
# PyKLU – Python bindings for SuiteSparse KLU
# Copyright (C) 2015-2025 CERN
# Licensed under the LGPL-2.1-or-later. See LICENSE for details.

import numpy as np
from scipy.sparse import csc_matrix
cimport numpy as cnp

cdef class Klu:
    cdef lu_state* lus
    cdef int m, n

    def __init__(self, Acsc):
        if not isinstance(Acsc, csc_matrix):
            raise TypeError("A must be a scipy.sparse.csc_matrix")
        
        # ensure correct dtype (float64 for data, int32 for indices)
        if Acsc.data.dtype != np.float64 or \
           Acsc.indptr.dtype != np.int32 or \
           Acsc.indices.dtype != np.int32:
            Acsc = Acsc.astype(np.float64) 

        self.m, self.n = Acsc.shape
        cdef int nnz = Acsc.nnz

        cdef cnp.ndarray[cnp.float64_t, ndim=1] Acsc_data = Acsc.data
        cdef cnp.ndarray[cnp.int32_t,   ndim=1] Acsc_indptr = Acsc.indptr
        cdef cnp.ndarray[cnp.int32_t,   ndim=1] Acsc_indices = Acsc.indices

        self.lus = construct_superlu(
            self.m, self.n, nnz,
            <double*> Acsc_data.data,
            <int*>    Acsc_indices.data,
            <int*>    Acsc_indptr.data,
        )

    cpdef solve(self, B, bint copy=True):
        """
        Solve A X = B.

        B can be:
          - shape (m,)  -> returns shape (m,)
          - shape (m,k) -> returns shape (m,k)

        copy=True  -> always work on a copy, return new array.
        copy=False -> operate in-place on the given array (which must be
                      float64 and with suitable layout).
        """
        cdef cnp.ndarray arr
        cdef cnp.ndarray[cnp.float64_t, ndim=1] X1, A1
        cdef cnp.ndarray[cnp.float64_t, ndim=2] X2, A2
        cdef int nrhs

        # Convert to ndarray and handle dtype
        arr = np.asarray(B)

        if arr.dtype != np.float64:
            if not copy:
                raise TypeError("copy=False requires B.dtype == float64")
            arr = arr.astype(np.float64, copy=True)

        if arr.ndim == 1:
            # --- 1D RHS: shape (m,) ---
            if arr.shape[0] != self.m:
                raise ValueError(
                    "b has length %d, expected %d" % (arr.shape[0], self.m)
                )

            A1 = <cnp.ndarray[cnp.float64_t, ndim=1]> arr
            nrhs = 1

            if copy:
                # work on a separate array, user input untouched
                X1 = np.array(A1, dtype=np.float64, copy=True, order="C")
            else:
                # in-place: overwrite arr (and thus B, if it *is* that array)
                if not (A1.flags["C_CONTIGUOUS"] or A1.flags["F_CONTIGUOUS"]):
                    raise ValueError(
                        "copy=False requires a contiguous 1D float64 array"
                    )
                X1 = A1

            lusolve(self.lus, <double*> X1.data, nrhs)

            if copy:
                return X1
            else:
                return arr  # same underlying array as A1

        elif arr.ndim == 2:
            # --- 2D RHS: shape (m,k) ---
            if arr.shape[0] != self.m:
                raise ValueError(
                    "B has shape %s, expected (%d, k)" % (tuple([arr.shape[0],arr.shape[1]]), self.m)
                )

            A2 = <cnp.ndarray[cnp.float64_t, ndim=2]> arr
            nrhs = A2.shape[1]

            if copy:
                # KLU expects column-major layout for multi-RHS
                X2 = np.array(A2, dtype=np.float64, copy=True, order="F")
            else:
                if not A2.flags["F_CONTIGUOUS"]:
                    raise ValueError(
                        "copy=False with 2D B requires Fortran-contiguous "
                        "(column-major) float64 array with shape (m, k)"
                    )
                X2 = A2

            lusolve(self.lus, <double*> X2.data, nrhs)

            if copy:
                return X2
            else:
                return arr  # same underlying array as A2

        else:
            raise ValueError("B must be 1D or 2D array")

    cpdef inplace_solve_batched(self, cnp.ndarray[cnp.float64_t, ndim=2, mode="fortran"] B):
        cdef int nrhs = B.shape[1]
        lusolve(self.lus, &B[0,0], nrhs)
    
    cpdef inplace_solve_vector(self, cnp.ndarray[cnp.float64_t, ndim=1] B):
        cdef int nrhs = 1
        lusolve(self.lus, &B[0], nrhs)

    def __dealloc__(self):
        if self.lus is not NULL:
            lu_destroy(self.lus)
            self.lus = NULL
