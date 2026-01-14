from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
from scipy.optimize import minimize

from persistency.model import retained_starters_mass


@dataclass(frozen=True)
class FitResult:
    alpha: float
    beta: float
    k: float
    rmse: float


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    err = y_true - y_pred
    return float(np.sqrt(np.mean(err * err)))


def fit_weibull_and_scale(
    nbrx: np.ndarray,
    trx: np.ndarray,
    *,
    max_lag: Optional[int] = 36,
    alpha_init: float = 12.0,
    beta_init: float = 1.0,
) -> FitResult:
    """
    Fit alpha, beta, and k by minimizing SSE between observed TRx and predicted TRx:
        TRx_hat_t = k * A_t
        A_t = sum_i NBRx_i * S(t-i)

    Parameters
    ----------
    nbrx : np.ndarray
        NBRx values (length N)
    trx : np.ndarray
        Observed TRx values (length N)
    max_lag : Optional[int]
        Max cohort age to include in A_t (None = full history)
    """
    nbrx = np.asarray(nbrx, dtype=float)
    trx = np.asarray(trx, dtype=float)

    if nbrx.ndim != 1 or trx.ndim != 1 or len(nbrx) != len(trx):
        raise ValueError("nbrx and trx must be 1D arrays of equal length")
    if len(nbrx) < 6:
        raise ValueError("Need at least 6 periods to fit parameters reliably")
    if np.any(nbrx < 0) or np.any(trx < 0):
        raise ValueError("nbrx and trx must be non-negative")

    # Loss function: given alpha,beta compute A; best k is closed-form least squares.
    def loss(params: np.ndarray) -> float:
        alpha, beta = float(params[0]), float(params[1])

        # invalid params -> big penalty
        if alpha <= 0 or beta <= 0:
            return 1e30

        A = np.array(retained_starters_mass(nbrx, alpha, beta, max_lag=max_lag), dtype=float)

        # If A is all zeros, k undefined; penalize
        denom = float(np.dot(A, A))
        if denom <= 0:
            return 1e30

        # Optimal k for SSE: k = (A·TRx)/(A·A)
        k_opt = float(np.dot(A, trx) / denom)
        if k_opt <= 0:
            return 1e30

        trx_hat = k_opt * A
        err = trx - trx_hat
        return float(np.dot(err, err))  # SSE

    x0 = np.array([alpha_init, beta_init], dtype=float)

    bounds = [
        (0.1, 240.0),  # alpha in months
        (0.1, 10.0),   # beta
    ]

    res = minimize(loss, x0=x0, bounds=bounds, method="L-BFGS-B")

    alpha_hat, beta_hat = float(res.x[0]), float(res.x[1])

    A_hat = np.array(retained_starters_mass(nbrx, alpha_hat, beta_hat, max_lag=max_lag), dtype=float)
    k_hat = float(np.dot(A_hat, trx) / np.dot(A_hat, A_hat))
    trx_fit = k_hat * A_hat

    return FitResult(
        alpha=alpha_hat,
        beta=beta_hat,
        k=k_hat,
        rmse=_rmse(trx, trx_fit),
    )


def predict_trx(
    nbrx: np.ndarray,
    alpha: float,
    beta: float,
    k: float,
    *,
    max_lag: Optional[int] = 36,
) -> np.ndarray:
    """
    Predict TRx using fitted parameters.
    """
    A = np.array(retained_starters_mass(nbrx, alpha, beta, max_lag=max_lag), dtype=float)
    return k * A
