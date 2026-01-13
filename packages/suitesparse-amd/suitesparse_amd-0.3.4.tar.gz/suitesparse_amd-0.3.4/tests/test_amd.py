"""
Test suite for AMD using Numpy and lists as inputs
"""

import unittest
from pathlib import Path
from unittest import skipIf

from suitesparse_amd.amd import amd

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class TestList(unittest.TestCase):
    """
    Unit test suite for validating the Approximate Minimum Degree (AMD) algorithm
    using standard Python `list` data structures.

    This class focuses on:
    1. Input validation (Type checks, dimension checks).
    2. Boundary conditions (Empty lists, single elements).
    3. Algorithmic correctness on known adjacency structures.
    """

    def test_empty(self):
        """
        Validates the error handling mechanism for null inputs.

        Asserts:
            TypeError: When the input matrix is explicitly None.
        """
        matrix = None

        with self.assertRaises(TypeError):
            amd(matrix)

    def test_one_d_empty(self):
        """
        Validates behavior for an instantiated but empty 1D list.

        Mathematically corresponds to a graph $G=(V, E)$ where $|V|=0$.

        Asserts:
            - The resulting permutation vector $p$ has length 0.
            - The control values $v$ indicate zero cost/info.
        """
        matrix = []

        p, v = amd(matrix)

        self.assertEqual(len(p), 0)
        self.assertEqual(v[0], 0)
        self.assertEqual(v[1], 0)

    def test_one_d_full(self):
        """
        Validates input rejection for 1D lists containing scalar data.

        The AMD algorithm requires a 2D adjacency structure (or equivalent CSR/CSC format).
        A flat list `[0]` implies a scalar, not a matrix.

        Asserts:
            TypeError: When input is a 1D list of integers.
        """
        matrix = [0]

        with self.assertRaises(TypeError):
            amd(matrix)

    def test_two_d_empty(self):
        r"""
        Validates input rejection for a 2D list containing empty rows (`[[]]`).

        While technically 2D, this structure lacks column definition required
        to form a square matrix $A \in \mathbb{R}^{n \times n}$.

        Asserts:
            TypeError: When structure is `[[]]`.
        """
        matrix = [[]]

        with self.assertRaises(TypeError):
            amd(matrix)

    def test_two_d_non_list(self):
        """
        Validates structural consistency checks for heterogeneous list content.

        The input must be a list of lists. A mixture of scalars and lists
        violates the matrix definition.

        Asserts:
            TypeError: When input is mixed type, e.g., `[0, [0]]`.
        """
        matrix = [0, [0]]

        with self.assertRaises(TypeError):
            amd(matrix)

    def test_two_d_non_square(self):
        """
        Validates the requirement that the input matrix must be square.

        AMD operates on the graph of a symmetric matrix. If $A$ is rectangular ($M \times N$),
        the concept of symmetric permutation $P A P^T$ is ill-defined without
        implicit symmetrization (usually $A^T A$). The wrapper expects a square input.

        Asserts:
            TypeError: If row lengths satisfy $len(row_i) \neq len(matrix)$.
        """
        matrix = [[0], [0, 1]]

        with self.assertRaises(TypeError):
            amd(matrix)

    def test_two_d_square_not_number(self):
        """
        Validates the algorithm's resilience to non-numeric data in the sparsity pattern.

        AMD utilizes the *structure* (non-zero entries), not the *values*.
        However, data type handling depends on the underlying implementation.

        Asserts:
            A valid permutation is returned even if values are strings, provided
            the structure is interpretable.
        """
        matrix = [[0, 0], [0, "s"]]

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [0, 1])

    def test_two_d_square_simple_string(self):
        """
        Validates handling of string-based dense matrices and warning emissions.

        Asserts:
            - RuntimeWarning: Is issued when non-numeric types are processed in specific contexts.
            - Correctness: The resulting permutation reverses the order [3, 2, 1, 0] for this
            specific pattern.
        """
        matrix = [
            ["a", "bc", "d", "e"],
            ["ff", "gg", "", ""],
            ["qq", "", "q", ""],
            ["f", "", "", "laugh"],
        ]

        with self.assertWarns(RuntimeWarning):
            p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [3, 2, 1, 0])

    def test_two_d_square_identity_dense(self):
        """
        Validates the 'dense_permutation' flag on an Identity matrix.

        For $I = \text{diag}(1, 1)$, any permutation $P$ that preserves diagonal structure
        is valid. Here, we verify the output format matches the input structure
        when `dense_permutation=True`.

        Asserts:
            The output $p$ matches the input $matrix$ (Identity).
        """
        matrix = [[1, 0], [0, 1]]

        p, _ = amd(matrix, dense_permutation=True)

        self.assertEqual(matrix, p)

    def test_two_d_square_identity(self):
        """
        Validates the standard permutation vector output on an Identity matrix.

        For $I_2$, the optimal ordering is trivial.

        Asserts:
            The permutation vector $p$ is the identity permutation $[0, 1]$.
        """
        matrix = [[1, 0], [0, 1]]

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [0, 1])

    def test_two_d_square_simple(self):
        """
        Validates AMD ordering on a 4x4 binary matrix (Test Case 1).

        Matrix Structure:
        [[1, 1, 1, 1],
         [1, 1, 0, 0],
         [1, 0, 1, 0],
         [1, 0, 0, 1]]

        This represents a "star" graph or arrowhead matrix where node 0 is connected to all others.
        To minimize fill-in, the dense row/column (node 0) should be ordered last.

        Asserts:
            Permutation pushes index 0 to the end: $[3, 2, 1, 0]$.
        """
        matrix = [[1, 1, 1, 1], [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1]]

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [3, 2, 1, 0])

    def test_two_d_square_simple_2(self):
        """
        Validates AMD ordering on a 4x4 sparse matrix (Test Case 2).

        Structure: Diagonal plus corners.
        The algorithm attempts to reduce the bandwidth or profile.

        Asserts:
            Expected permutation: $[1, 2, 0, 3]$.
        """
        matrix = [[1, 0, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 1]]

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [1, 2, 0, 3])

    def test_two_d_square_simple_3(self):
        """
        Validates AMD ordering on a 4x4 matrix with a dense sub-block (Test Case 3).

        Asserts:
            Expected permutation: $[1, 2, 0, 3]$.
        """
        matrix = [[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]]

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [1, 2, 0, 3])

    def test_two_d_square_simple_4(self):
        """
        Validates AMD ordering on a 4x4 block matrix (Test Case 4).

        Asserts:
            Expected permutation: $[3, 0, 1, 2]$.
        """
        matrix = [[1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 1], [0, 0, 1, 1]]

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [3, 0, 1, 2])

    def test_two_d_square_complex(self):
        """
        Validates AMD against a canonical MATLAB benchmark.

        This test loads an adjacency matrix ($A$) and an expected permutation vector ($P$)
        from external CSV files. This ensures parity with the reference implementation
        of AMD in MATLAB.

        References:
            MATLAB `amd` function documentation:
            https://www.mathworks.com/help/matlab/ref/amd.html

        Asserts:
            The computed permutation matches the expected `P.csv` exactly.
        """

        base_dir = Path(__file__).parent

        with open(base_dir / "P.csv", encoding="utf-8") as f:
            expected_p = list(map(int, f.readline().split(",")))

        n = len(expected_p)

        matrix = [[0 for _ in range(n)] for _ in range(n)]

        with open(base_dir / "A.csv", encoding="utf-8") as f:
            for line in f.readlines():
                data = list(map(int, line.split(",")))

                matrix[data[0]][data[1]] = data[2]

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, expected_p)


@skipIf(not HAS_NUMPY, "Numpy is not installed")
class TestNumpy(unittest.TestCase):
    """
    Unit test suite for validating the AMD algorithm using NumPy array structures.
    This class is conditionally skipped if the `numpy` library is not present in the environment.

    Focuses on:
    1. Integration with `numpy.ndarray` objects.
    2. Data type (dtype) resilience (integers, floats, complex numbers).
    3. Memory layout handling (C-contiguous vs F-contiguous, implied by numpy handling).
    """

    def test_one_d_empty(self):
        """
        Validates exception handling for empty 1D NumPy arrays.

        Asserts:
            ValueError: NumPy arrays with shape (0,) or ambiguous shapes are rejected.
        """
        matrix = np.array([])

        with self.assertRaises(ValueError):
            amd(matrix)

    def test_one_d_full(self):
        """
        Validates exception handling for 1D scalar NumPy arrays.

        Asserts:
            ValueError: Arrays with shape (1,) containing scalars are rejected
            as they do not represent a valid adjacency matrix.
        """
        matrix = np.array([0])

        with self.assertRaises(ValueError):
            amd(matrix)

    def test_two_d_empty(self):
        """
        Validates exception handling for 2D NumPy arrays with dimension 0 on one axis.

        Asserts:
            ValueError: Shapes like (1, 0) or (0, 0) that are malformed for AMD.
        """
        matrix = np.array([[]])

        with self.assertRaises(ValueError):
            amd(matrix)

    def test_two_d_square_not_number(self):
        """
        Validates NumPy integration with 'object' dtype arrays containing non-numerics.

        Asserts:
            The wrapper correctly extracts the sparsity pattern even if the
            data type is `object` containing strings.
        """
        matrix = np.array([[0, 0], [0, "s"]])

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [0, 1])

    def test_two_d_square_identity_dense(self):
        """
        Validates `dense_permutation` output for a larger (10x10) Identity matrix using NumPy.

        Asserts:
            The return value is a dense Identity matrix (allclose check).
        """
        matrix = np.eye(10)

        p, _ = amd(matrix, dense_permutation=True)

        self.assertTrue(np.allclose(matrix, p))

    def test_two_d_square_datatypes(self):
        """
        Comprehensive validation of NumPy data types (dtypes).

        The AMD algorithm relies on the binary existence of edges ($a_{ij} \neq 0$).
        This test iterates through standard integer, floating-point, and complex types
        to ensure the wrapper correctly detects non-zeros regardless of bit-width or encoding.

        Types Tested:
            - Integers: int8 to int64, uint8 to uint64.
            - Floats: float16 to float128.
            - Complex: complex64 to complex256.

        Asserts:
            The identity permutation is recovered for $I_{10}$ across all dtypes.
        """
        datatypes = [
            np.bool,
            np.int8,
            np.uint8,
            np.int16,
            np.uint16,
            np.int32,
            np.uint32,
            np.intp,
            np.uintp,
            np.int64,
            np.uint64,
            np.float16,
            np.float32,
            np.float64,
            np.float128,
            np.complex64,
            np.complex128,
            np.complex256,
        ]

        for dtype in datatypes:
            matrix = np.eye(10, dtype=dtype)

            p, _ = amd(matrix, dense_permutation=True)

            self.assertTrue(np.allclose(matrix, p), f"Failed to handle numpy array of type: {dtype}")  # pylint: disable=line-too-long # noqa: E501

    def test_two_d_square_identity(self):
        """
        Validates standard permutation output for a 2x2 Identity NumPy array.

        Asserts:
            Returns permutation vector $[0, 1]$.
        """
        matrix = np.array([[1, 0], [0, 1]])

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [0, 1])

    def test_two_d_square_simple(self):
        """
        Validates AMD ordering on a 4x4 NumPy matrix (Test Case 1).
        Equivalent to `TestList.test_two_d_square_simple`.
        """
        matrix = np.array([[1, 1, 1, 1], [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1]])

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [3, 2, 1, 0])

    def test_two_d_square_simple_2(self):
        """
        Validates AMD ordering on a 4x4 NumPy matrix (Test Case 2).
        Equivalent to `TestList.test_two_d_square_simple_2`.
        """
        matrix = np.array([[1, 0, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 1]])

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [1, 2, 0, 3])

    def test_two_d_square_simple_3(self):
        """
        Validates AMD ordering on a 4x4 NumPy matrix (Test Case 3).
        Equivalent to `TestList.test_two_d_square_simple_3`.
        """
        matrix = np.array([[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]])

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [1, 2, 0, 3])

    def test_two_d_square_simple_4(self):
        """
        Validates AMD ordering on a 4x4 NumPy matrix (Test Case 4).
        Equivalent to `TestList.test_two_d_square_simple_4`.
        """
        matrix = np.array([[1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 1, 1], [0, 0, 1, 1]])

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, [3, 0, 1, 2])

    def test_two_d_square_complex(self):
        """
        Validates AMD against the MATLAB benchmark using NumPy arrays.

        Loads `P.csv` and `A.csv` to reconstruct the sparse matrix and expected permutation.

        Asserts:
            The computed permutation matches the expected benchmark exactly.
        """

        base_dir = Path(__file__).parent

        with open(base_dir / "P.csv", encoding="utf-8") as f:
            expected_p = list(map(int, f.readline().split(",")))

        n = len(expected_p)

        matrix = [[0 for _ in range(n)] for _ in range(n)]

        with open(base_dir / "A.csv", encoding="utf-8") as f:
            for line in f.readlines():
                data = list(map(int, line.split(",")))

                matrix[data[0]][data[1]] = data[2]

        matrix = np.array(matrix)

        p, _ = amd(matrix, dense_permutation=False)

        self.assertEqual(p, expected_p)


if __name__ == "__main__":
    unittest.main()
