# PyKLU – Python bindings for SuiteSparse KLU
# Copyright (C) 2015-2025 CERN
# Licensed under the LGPL-2.1-or-later. See LICENSE for details.

import numpy as np
import scipy.sparse as sp
import pytest
from PyKLU._test_helpers import *
import PyKLU

SPARSE_SYSTEM_SIZE = 2000 # (n,n) matrix
NUM_BATCHES = 20
PRECISION = np.finfo(float).eps
ABS_TOL = 1e-12
TOLERANCE_FACTOR = 2

'''
The following tests rely on computing the relative residual of the solution
The relative residual can be defined as:
                               || A * x - b ||
                        η = ---------------------
                                    ||b||

Typically, the expected value for this quantity is:
* Ideally: 1e-12 - 1e-14
* Ill-conditioned systems: 1e-9 - 1e-10

In this module, we evaluate the residual as follows:
* We compare the residual of the reference solver (scipy) with ABS_TOL
* We compare the residual of the KLU solver with ABS_TOL
* We ensure that the residual of the KLU Solver is within TOLERANCE_FACTOR
  of the reference solver. 
  
For reference, the machine precision for FP64 is ~2.2e-16 (PRECISION)
'''

def batch_vectors_as_matrix(vector_list):
    return np.asfortranarray(np.moveaxis(np.array(vector_list),0,-1))

@fix_random_seed(1337)
def make_random_sparse_system(n, nbatches, density=0.01):
    A = sp.random(
        n, n,
        density=density,
        format="csc",
        random_state=np.random,
        data_rvs=np.random.standard_normal
    )
    # Make it nonsingular & better conditioned:
    # Add something on the diagonal so pivots aren't tiny/zero
    A = A + sp.eye(n, format="csc") * 5.0  # tweak factor as you like
    b_array = []
    if nbatches == 0:
        b = np.random.standard_normal(n)
        b_array.append(b)
    else:
        for i in range(nbatches):
            b = np.cos(2*i/(nbatches-1)*np.pi) * np.random.standard_normal(n)
            b_array.append(b)
        b = batch_vectors_as_matrix(b_array)
    solver = sp.linalg.splu(A)
    x = solver.solve(b)
    return (A, b, x, b_array)

@fix_random_seed(1337)
def make_tridiagonal_system(n, nbatches):
    main = 2.0 + np.abs(np.random.standard_normal(n))
    lower = np.random.standard_normal(n-1)
    upper = np.random.standard_normal(n-1)
    A = sp.diags(
        diagonals=[lower, main, upper],
        offsets=[-1, 0, 1],
        format="csc"
    )
    b_array = []
    if nbatches == 0:
        b = np.random.standard_normal(n)
        b_array.append(b)
    else:
        for i in range(nbatches):
            b = np.cos(2*i/(nbatches-1)*np.pi) * np.random.standard_normal(n)
            b_array.append(b)
        b = batch_vectors_as_matrix(b_array)
    solver = sp.linalg.splu(A)
    x = solver.solve(b)
    return (A, b, x, b_array)

random_system = make_random_sparse_system(SPARSE_SYSTEM_SIZE, 0)
tridiag_system = make_tridiagonal_system(SPARSE_SYSTEM_SIZE, 0)

@pytest.mark.parametrize("sparse_system", [random_system, tridiag_system])
def test_vector_solve(sparse_system):
    A_sp, b_sp, x_sp, _ = sparse_system
    assert not issymmetric(A_sp)

    scipy_residual = rel_residual(A_sp,x_sp,b_sp)
    solver = PyKLU.Klu(A_sp)
    x = solver.solve(b_sp)
    klu_residual = rel_residual(A_sp,x,b_sp)

    assert_residual_ok(scipy_residual,klu_residual, 
                       abs_tol = ABS_TOL, factor = TOLERANCE_FACTOR)

random_system = make_random_sparse_system(SPARSE_SYSTEM_SIZE, NUM_BATCHES)
tridiag_system = make_tridiagonal_system(SPARSE_SYSTEM_SIZE, NUM_BATCHES)

@pytest.mark.parametrize("sparse_system", [random_system, tridiag_system])
def test_batched_solve(sparse_system):
    A_sp, b_sp, x_sp, _ = sparse_system
    assert not issymmetric(A_sp)
    scipy_residual = rel_residual(A_sp,x_sp,b_sp)
    
    b_sp = np.asfortranarray(b_sp)
    solver = PyKLU.Klu(A_sp)
    x = solver.solve(b_sp)
    klu_residual = rel_residual(A_sp,x,b_sp)
    
    assert_residual_ok(scipy_residual,klu_residual, 
                       abs_tol = ABS_TOL, factor = TOLERANCE_FACTOR)