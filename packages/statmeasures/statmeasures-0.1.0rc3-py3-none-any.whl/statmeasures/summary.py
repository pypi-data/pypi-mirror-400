__all__ = ("MeasureSummary",)


from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

import statmeasures as sm
from statmeasures.utils import Vector, ensure_1d


@dataclass(frozen=True, slots=True)
class MeasureSummary:
    """Return summary of statistical measures from a numeric vector with shape (n,)."""

    vec: Vector

    def __init__(
        self,
        a: ArrayLike,
        dtype: np.dtype | type = float,
        finite: bool = True,
    ) -> None:
        v: Vector = ensure_1d(a, dtype=dtype, finite=finite)
        object.__setattr__(self, "vec", v)

    def mean(self) -> float:
        """Return the arithmetic mean."""
        return float(np.mean(self.vec))

    def median(self) -> float:
        """Return the median."""
        return float(np.median(self.vec))

    def harmonic_mean(self) -> float:
        """Return the harmonic mean."""
        return sm.center.harmonic_mean(self.vec)

    def geometric_mean(self) -> float:
        """Return the geometric mean."""
        return sm.center.geometric_mean(self.vec)

    def trimmed_mean(self, alpha: float) -> float:
        """Return the trimmed mean."""
        return sm.center.trimmed_mean(self.vec, alpha=alpha)

    def winsorized_mean(self, alpha: float) -> float:
        """Return the winsorized mean."""
        return sm.center.winsorized_mean(self.vec, alpha=alpha)

    def dwe(self) -> float:
        """Return the distance-weighted estimator."""
        return sm.center.dwe(self.vec)

    def spwe(self) -> float:
        """Return the scalar-product weighted estimator."""
        return sm.center.spwe(self.vec)

    def stddev(self) -> float:
        """Return the sample standard deviation."""
        return float(np.std(self.vec, ddof=1))

    def stderr(self) -> float:
        """Return the standard error."""
        return sm.spread.stderr(self.vec)

    def summary(self, alpha: float = 0.2) -> dict[str, float]:
        """Return all measures as a dictionary."""
        return {
            "mean": self.mean(),
            "median": self.median(),
            "harmonic_mean": self.harmonic_mean(),
            "geometric_mean": self.geometric_mean(),
            "trimmed_mean": self.trimmed_mean(alpha),
            "winsorized_mean": self.winsorized_mean(alpha),
            "dwe": self.dwe(),
            "spwe": self.spwe(),
            "stddev": self.stddev(),
            "stderr": self.stderr(),
        }
