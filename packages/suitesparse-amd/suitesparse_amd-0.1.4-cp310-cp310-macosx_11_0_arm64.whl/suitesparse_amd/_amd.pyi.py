import numbers
from typing import Sequence, Tuple, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from numpy.typing import NDArray
else:
    NDArray = Any

AMD_DEFAULT_DENSE: float
AMD_DEFAULT_AGGRESSIVE: int
AMD_INFO: int


def amd(
        matrix: NDArray[Any] | Sequence[Sequence[numbers.Real]],
        dense: float = ...,
        aggressive: bool = ...,
        verbose: bool = ...
) -> Tuple[List[int], List[float]]: ...
