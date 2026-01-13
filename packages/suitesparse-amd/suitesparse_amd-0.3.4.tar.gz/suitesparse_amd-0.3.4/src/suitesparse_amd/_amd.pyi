from typing import Sequence, Tuple, Any

AMD_DEFAULT_DENSE: float
AMD_DEFAULT_AGGRESSIVE: int
AMD_INFO: int


def amd(
        matrix: Any,
        dense: float,
        aggressive: bool,
        verbose: bool
) -> Tuple[Sequence[int], Sequence[float]]: ...
