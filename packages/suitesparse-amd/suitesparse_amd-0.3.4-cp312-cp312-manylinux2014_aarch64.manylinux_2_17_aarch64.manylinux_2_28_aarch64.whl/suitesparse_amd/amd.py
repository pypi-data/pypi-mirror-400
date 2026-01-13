# pylint: disable=duplicate-code

"""
SuiteSparse: Approximate Minimum Degree (AMD) Ordering
======================================================

This module provides a high-performance Python interface to the Approximate Minimum
Degree (AMD) ordering algorithm, originally developed by Amestoy, Davis, and Duff.

Mathematical Context
--------------------
The primary objective of this module is to solve the graph-theoretic problem of
finding a symmetric permutation :math:`P` that minimizes "fill-in" during the factorization
of a sparse matrix :math:`A`.

Given a large, sparse, symmetric positive definite matrix :math:`A`, the Cholesky factor
:math:`L` (where :math:`A = LL^T`) often suffers from fill-in, where entries that were zero in
:math:`A` become non-zero in :math:`L`. Minimizing this fill-in is an NP-complete problem.
The AMD algorithm provides a heuristic solution by selecting pivot nodes with the
minimum degree in the elimination graph at each step.

The computed permutation :math:`P` satisfies:
.. math::
   \\tilde{A} = P A P^T
such that the factor :math:`\\tilde{L}` of :math:`\\tilde{A}` is
significantly sparser than :math:`L`.

Dependencies
------------
* `numpy` (Optional): Required for matrix operations involving arrays.
    Algorithm falls back to list processing if absent.
* `torch` (Optional): Required for GPU/Tensor-based workflows.

References
----------
.. [1] Amestoy, P. R., Davis, T. A., & Duff, I. S. (1996). An approximate minimum
       degree ordering algorithm. *SIAM Journal on Matrix Analysis and Applications*,
       17(4), 886-905.
"""

import numbers
from typing import TYPE_CHECKING, Any, Sequence, Tuple, TypeGuard, Union

from . import _amd as _c_ext  # pylint: disable=no-name-in-module

try:
    import torch

    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

if TYPE_CHECKING:
    from numpy.typing import NDArray
    from torch import Tensor
else:
    NDArray = Any
    Tensor = Any

AMD_DEFAULT_DENSE = getattr(_c_ext, "AMD_DEFAULT_DENSE", 10.0)
AMD_DEFAULT_AGGRESSIVE = bool(getattr(_c_ext, "AMD_DEFAULT_AGGRESSIVE", 1))
AMD_INFO = getattr(_c_ext, "AMD_INFO", 20)


def _is_torch_tensor(x: Any) -> TypeGuard["Tensor"]:
    return HAS_PYTORCH and isinstance(x, torch.Tensor)


def amd(
    matrix: Union[NDArray, Tensor, Sequence[Sequence[numbers.Real]]],
    *,
    dense: float = AMD_DEFAULT_DENSE,
    aggressive: bool = AMD_DEFAULT_AGGRESSIVE,
    verbose: bool = False,
    dense_permutation: bool = True,
) -> Tuple[Sequence[int], Sequence[float]]:
    """
    Compute an Approximate Minimum Degree (AMD) symmetric ordering.

    This function computes a permutation :math:`P` such that the Cholesky
    factorization of the symmetrically permuted matrix

    .. math::
        P A P^T

    has reduced fill-in and arithmetic complexity compared to the
    factorization of :math:`A`. If the input matrix is not symmetric,
    the ordering is computed on the sparsity pattern of :math:`A + A^T`.

    The algorithm is based on the Approximate Minimum Degree method of
    Amestoy, Davis, and Duff (1996), and supports both:

    * **AMD** ordering (with aggressive absorption), and
    * **AMDBAR** ordering (without aggressive absorption).

    Compared to the original Fortran implementations, this implementation:

    1. Detects and ignores dense rows/columns to improve runtime.
    2. Automatically symmetrizes the pattern for nonsymmetric matrices.
    3. Applies a depth-first postordering of the elimination (assembly) tree.

    Parameters
    ----------
    matrix : ndarray or sequence of sequences of real
        Input matrix :math:`A`. Only the sparsity pattern is used.
        The matrix may be symmetric or nonsymmetric. Diagonal entries,
        if present, are ignored for ordering purposes.
        Internally, the matrix is treated in compressed sparse column (CSC)
        form; if the input does not satisfy sorted indices or contains
        duplicates, a cleaned copy is constructed.

    dense : float, default=AMD_DEFAULT_DENSE
        Threshold controlling the treatment of *dense* rows/columns.
        A row/column of :math:`A + A^T` with more than

        .. math::
            \\text{dense} \\cdot \\sqrt{n}

        off-diagonal entries is considered dense, removed prior to ordering,
        and placed last in the permutation.
        If `dense < 0`, no rows/columns are treated as dense.
        Rows/columns with 16 or fewer off-diagonal entries are never
        considered dense.

    aggressive : bool, default=AMD_DEFAULT_AGGRESSIVE
        If ``True``, enables *aggressive absorption*, in which an element
        is absorbed into the current element if its adjacency pattern
        is a subset of the current one, even if it is not adjacent to
        the pivot. This generally improves degree estimates and reduces
        runtime and fill-in, but may occasionally yield a slightly worse
        ordering. Setting this to ``False`` yields the AMDBAR variant.

    verbose : bool, default=False
        If ``True``, diagnostic information may be printed during execution.

    Returns
    -------
    P : list[int]
        Permutation vector of length ``n``. If ``P[k] = i``, then row/column
        ``i`` of the original matrix is the ``k``-th pivot.

    info : list[float]
        Array of statistical information describing the ordering. The
        entries follow the AMD convention and include:

        * ``info[AMD_STATUS]`` :
          Status code (``AMD_OK``, ``AMD_OK_BUT_JUMBLED``,
          ``AMD_OUT_OF_MEMORY``, or ``AMD_INVALID``).
        * ``info[AMD_N]`` :
          Matrix dimension ``n``.
        * ``info[AMD_NZ]`` :
          Number of nonzeros in the input matrix.
        * ``info[AMD_SYMMETRY]`` :
          Symmetry measure of the sparsity pattern.
        * ``info[AMD_NZDIAG]`` :
          Number of diagonal entries.
        * ``info[AMD_NZ_A_PLUS_AT]`` :
          Number of off-diagonal nonzeros in :math:`A + A^T`.
        * ``info[AMD_NDENSE]`` :
          Number of dense rows/columns removed.
        * ``info[AMD_MEMORY]`` :
          Estimated memory usage (bytes).
        * ``info[AMD_NCMPA]`` :
          Number of garbage collections.
        * ``info[AMD_LNZ]`` :
          Estimated number of nonzeros in the Cholesky factor ``L``
          (excluding the diagonal).
        * ``info[AMD_NDIV]`` :
          Estimated number of divisions in a subsequent LDLᵀ factorization.
        * ``info[AMD_NMULTSUBS_LDL]`` :
          Estimated multiply–subtract pairs for LDLᵀ.
        * ``info[AMD_NMULTSUBS_LU]`` :
          Estimated multiply–subtract pairs for LU (no pivoting).
        * ``info[AMD_DMAX]`` :
          Maximum column count in ``L`` (including diagonal).

        Remaining entries are reserved for future use.

    dense_permutation : bool
        returns the dense representation of the permutation matrix

    Notes
    -----
    The ordering is computed purely from the sparsity pattern and is suitable
    for sparse Cholesky, :math:`LDL^T`, or LU factorizations without numerical
    pivoting. The reported fill and operation counts are *upper bounds*,
    and may be loose when many dense rows/columns are present or when
    mass elimination occurs.

    References
    ----------
    Amestoy, P. R., Davis, T. A., & Duff, I. S. (1996).
    *An approximate degree ordering algorithm*.
    SIAM Journal on Matrix Analysis and Applications, 17(4), 886–905.

    Examples
    --------
    >>> import numpy as np
    >>> def sparse_dense(n, density=0.15, seed=42):
    >>>     np.random.seed(seed)
    >>>     mask = np.abs(np.random.randn(n, n)) < density
    >>>     mask = np.triu(mask)
    >>>     sym_mask = mask + mask.T
    >>>     sym_mask = sym_mask.astype(np.int32)
    >>>     sym_mask -= np.diag(np.diag(sym_mask))
    >>>     sym_mask += np.diag(sym_mask.sum(axis=0) + 1)
    >>>
    >>>     return sym_mask
    >>>
    >>> n = 100
    >>> A = sparse_dense(n)               # Generate sparse matrix
    >>>
    >>> from suitesparse_amd import amd
    >>> P, info = amd.amd(A)              # Compute the AMD
    >>>
    >>> full_P = np.zeros((n, n))
    >>> full_P[np.arange(n), P] = 1       # Dense Permutation matrix
    >>>
    >>> ordered_A = full_P @ A @ full_P.T # Ordered A matrx
    """

    if _is_torch_tensor(matrix):
        device = matrix.device
        dtype = matrix.dtype
        matrix_ = matrix.detach().cpu().numpy()
    else:
        matrix_ = matrix

    permutation, info = _c_ext.amd(matrix_, dense, aggressive, verbose)

    if dense_permutation:
        n = int(info[1])

        is_numpy = HAS_NUMPY and isinstance(matrix, np.ndarray)

        if _is_torch_tensor(matrix):
            permutation_out = torch.zeros((n, n), dtype=dtype, device=device)
            permutation_out[torch.arange(n), permutation] = 1
        elif is_numpy:
            permutation_out = np.zeros((n, n))
            permutation_out[np.arange(n), permutation] = 1
        else:
            permutation_out = [[int(permutation[j] == i) for i in range(n)] for j in range(n)]

        permutation = permutation_out

    return permutation, info
