// PyKLU/klu_interf.h
// PyKLU – Python bindings for SuiteSparse KLU
// Copyright (C) 2015-2025 CERN
// Licensed under the LGPL-2.1-or-later. See LICENSE for details.

#ifndef __KLUINTERF
#define __KLUINTERF

#include <stdio.h>
#include "klu.h"

typedef struct{
	int m;
	klu_common Common;
	klu_symbolic *Symbolic ;
    klu_numeric *Numeric ;
} lu_state;

lu_state* construct_superlu(int m, int n, int nnz, double* Acsc_data_ptr, 
		int* Acsc_indices_ptr, int* Acsc_indptr_ptr);

void lusolve(lu_state* lus, double* BX, int nrhs);

void lu_destroy(lu_state* lus);

#endif
