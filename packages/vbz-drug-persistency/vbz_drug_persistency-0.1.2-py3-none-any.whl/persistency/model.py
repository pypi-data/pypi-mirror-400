from __future__ import annotations

import math
from typing import Iterable, List


class ModelError(ValueError):
    """Raised when model parameters are invalid."""


def weibull_survival(age: int, alpha: float, beta: float) -> float:
    """
    VBZ retention curve S(t) using Weibull survival:
        S(t) = exp(-(t/alpha)^beta)

    Parameters
    ----------
    age : int
        Months since start (0, 1, 2, ...)
    alpha : float
        Scale parameter (> 0)
    beta : float
        Shape parameter (> 0)
    """
    if age < 0:
        raise ModelError("age must be >= 0")
    if alpha <= 0 or beta <= 0:
        raise ModelError("alpha and beta must be > 0")

    if age == 0:
        return 1.0

    x = (age / alpha) ** beta
    return math.exp(-x)


def retained_starters_mass(nbrx: Iterable[float], alpha: float, beta: float, max_lag: int | None = None) -> List[float]:
    """
    Compute retained-starters mass A_t from a sequence of NBRx values.

    A_t = sum_{i=0..t} NBRx_i * S(t-i)

    Returns a list A where A[t] corresponds to period t (0-indexed).

    max_lag:
      If provided, only include cohort ages up to max_lag (helps performance and stability).
    """
    if alpha <= 0 or beta <= 0:
        raise ModelError("alpha and beta must be > 0")

    nbrx_list = [float(x) for x in nbrx]
    n = len(nbrx_list)
    if n == 0:
        return []

    if max_lag is not None and max_lag < 0:
        raise ModelError("max_lag must be >= 0 or None")

    A: List[float] = []
    for t in range(n):
        total = 0.0
        # cohort start index i ranges from 0..t
        # age = t - i
        i_min = 0
        if max_lag is not None:
            i_min = max(0, t - max_lag)

        for i in range(i_min, t + 1):
            age = t - i
            total += nbrx_list[i] * weibull_survival(age, alpha, beta)

        A.append(total)

    return A
