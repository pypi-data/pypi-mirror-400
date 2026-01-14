__all__ = (
    "MeasureOfCentralTendency",
    "harmonic_mean",
    "geometric_mean",
    "trimmed_mean",
    "winsorized_mean",
    "dwe",
    "spwe",
)

from typing import Protocol

import numpy as np
from scipy.stats import mstats

from statmeasures.utils import Vector, ensure_1d


class MeasureOfCentralTendency(Protocol):
    """Return a measure of central tendency for a numeric vector with shape (n,)."""

    def __call__(self, vec: Vector, /, *args, **kwargs) -> float: ...


def harmonic_mean(vec: Vector, /, *, validate: bool = False) -> float:
    """Return the harmonic mean."""
    v = ensure_1d(vec) if validate else vec
    res = mstats.hmean(v)
    return float(res)


def geometric_mean(vec: Vector, /, *, validate: bool = False) -> float:
    """Return the geometric mean."""
    v = ensure_1d(vec) if validate else vec
    res = mstats.gmean(v)
    return float(res)


def trimmed_mean(vec: Vector, /, *, alpha: float, validate: bool = False) -> float:
    """Return the trimmed mean."""
    v = ensure_1d(vec) if validate else vec
    res = mstats.trimmed_mean(v, limits=(alpha, alpha))
    return float(res)


def winsorized_mean(vec: Vector, /, *, alpha: float, validate: bool = False) -> float:
    """Return the winsorized mean."""
    v = ensure_1d(vec) if validate else vec
    winsorized_data = mstats.winsorize(v, limits=(alpha, alpha))
    res = winsorized_data.mean()
    return float(res)


def dwe(vec: Vector, /, *, validate: bool = False) -> float:
    """Return the distance-weighted estimator."""
    v = ensure_1d(vec) if validate else vec
    distances = np.abs(np.subtract.outer(v, v, dtype=float))
    weights = (len(v) - 1) / distances.sum(axis=1)
    res = (weights * v).sum() / weights.sum()
    return float(res)


def spwe(vec: Vector, /, *, validate: bool = False) -> float:
    """Return the scalar-product weighted estimator."""
    v = ensure_1d(vec) if validate else vec
    e = np.pi / 2 * (v - v.min()) / (v.max() - v.min())
    w = np.abs(np.cos(np.subtract.outer(e, e)))
    x = np.add.outer(v, v) / 2.0

    np.fill_diagonal(w, 0.0)
    np.fill_diagonal(x, 0.0)

    res = (w * x).sum() / w.sum()
    return float(res)
