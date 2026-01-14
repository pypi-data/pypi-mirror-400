# PyKLU/_test_helpers.py
# PyKLU – Python bindings for SuiteSparse KLU
# Copyright (C) 2015-2025 CERN
# Licensed under the LGPL-2.1-or-later. See LICENSE for details.

from functools import wraps
import numpy.linalg as npl
import scipy.sparse.linalg as scspl


def fix_random_seed(seed: int):
    """Decorator to fix the random seed for a test."""

    def decorator(test_function):
        @wraps(test_function)
        def wrapper(*args, **kwargs):
            import numpy as np

            rng_state = np.random.get_state()
            try:
                np.random.seed(seed)
                #Return value of function instead of None
                return test_function(*args, **kwargs) 
            finally:
                np.random.set_state(rng_state)

        return wrapper

    return decorator

def issymmetric(A, tol=0):
    if A.shape[0] != A.shape[1]:
        return False
    diff = A - A.T
    if tol == 0:
        return diff.nnz == 0
    else:
        # tolerance-based check
        return abs(diff).max() <= tol

def rel_residual(A,x,b):
    return npl.norm(A@x - b) / (npl.norm(b))

def assert_close_to_precision(value, precision):
    assert value <= precision, (f"Value {value} not within precision {precision}")

def assert_residual_acceptable(reference_residual, residual, tolerance = 10):
    assert residual <= tolerance*reference_residual, (
        f"Residual {residual} not within tolerance "
        f"O({tolerance}) of reference residual {reference_residual}")


def assert_residual_ok(res_ref, res_solver,
                       abs_tol=1e-12,
                       factor=10):
    """
    Check that our solver's residual is both:
      - absolutely small enough (abs_tol),
      - not catastrophically worse than the reference (factor * res_ref).
    """
    # sanity: reference solver itself should be good
    assert res_ref < abs_tol, f"Reference residual too large: {res_ref}"

    # absolute bound
    assert res_solver < abs_tol, (
        f"Residual {res_solver} exceeds absolute tolerance {abs_tol}"
    )

    # relative bound vs reference
    assert res_solver <= factor * res_ref, (
        f"Residual {res_solver} not within factor {factor} of "
        f"reference residual {res_ref}"
    )
