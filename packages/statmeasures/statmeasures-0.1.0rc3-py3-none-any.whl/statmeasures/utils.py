import numpy as np
from numpy.typing import ArrayLike, NDArray

Vector = NDArray[np.floating]


def ensure_1d(
    a: ArrayLike,
    dtype: np.dtype | type = float,
    finite: bool = True,
) -> Vector:
    """Return a strict 1-D NumPy array with shape (n,)."""
    try:
        arr = np.asarray(a, dtype=dtype)
    except Exception as exc:
        raise TypeError("input must be array-like") from exc

    if arr.ndim == 1:
        vec = arr
    elif arr.ndim == 2 and (arr.shape[0] == 1 or arr.shape[1] == 1):
        # convert (n,1), (1,n) and (1,1) -> (n,)
        vec = arr.reshape(-1)
    else:
        raise ValueError(
            f"expected shape (n,), (n, 1) or (1, n); got array with shape {arr.shape}"
        )

    if vec.size == 0:
        raise ValueError("vector must be non-empty")

    if finite and not np.isfinite(vec).all():
        raise ValueError("vector must contain only finite values (no NaN or Inf)")

    return vec
