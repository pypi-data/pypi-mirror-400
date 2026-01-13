import numbers
from typing import Sequence, Tuple, List, Any, TYPE_CHECKING, overload, Literal

if TYPE_CHECKING:
    from numpy.typing import NDArray
    from torch import Tensor
else:
    NDArray = Any
    Tensor = Any

_ArrayType = Sequence[Sequence[numbers.Real]]
_ArrayTypeInt = Sequence[Sequence[int]]

AMD_DEFAULT_DENSE: float
AMD_DEFAULT_AGGRESSIVE: bool
AMD_INFO: int


@overload
def amd(
        matrix: _ArrayType,
        *,
        dense: float = ...,
        aggressive: bool = ...,
        verbose: bool = ...,
        dense_permutation: Literal[False] = False,
) -> Tuple[List[int], List[float]]: ...


@overload
def amd(
        matrix: NDArray,
        *,
        dense: float = ...,
        aggressive: bool = ...,
        verbose: bool = ...,
        dense_permutation: Literal[False] = False,
) -> Tuple[List[int], List[float]]: ...


@overload
def amd(
        matrix: Tensor,
        *,
        dense: float = ...,
        aggressive: bool = ...,
        verbose: bool = ...,
        dense_permutation: Literal[False] = False,
) -> Tuple[List[int], List[float]]: ...


@overload
def amd(matrix: _ArrayType,
        *,
        dense: float = ...,
        aggressive: bool = ...,
        verbose: bool = ...,
        dense_permutation: Literal[True] = True,
        ) -> Tuple[_ArrayTypeInt, List[float]]: ...


@overload
def amd(matrix: NDArray,
        *,
        dense: float = ...,
        aggressive: bool = ...,
        verbose: bool = ...,
        dense_permutation: Literal[True] = True,
        ) -> Tuple[NDArray, List[float]]: ...


@overload
def amd(matrix: Tensor,
        *,
        dense: float = ...,
        aggressive: bool = ...,
        verbose: bool = ...,
        dense_permutation: Literal[True] = True,
        ) -> Tuple[Tensor, List[float]]: ...
