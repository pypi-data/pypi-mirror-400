__all__ = (
    "MeasureOfDispersion",
    "stderr",
)

from typing import Protocol

import numpy as np

from statmeasures.utils import Vector, ensure_1d


class MeasureOfDispersion(Protocol):
    """Return a measure of dispersion for a numeric vector with shape (n,)."""

    def __call__(self, vec: Vector, /, *args, **kwargs) -> float: ...


def stderr(vec: Vector, /, *, validate: bool = False) -> float:
    """Return the standard error."""
    v = ensure_1d(vec) if validate else vec
    res = v.std(ddof=1) / np.sqrt(len(v))
    return float(res)
