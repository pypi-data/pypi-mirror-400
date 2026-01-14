from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from persistency.fit import FitResult, predict_trx
from persistency.model import weibull_survival


@dataclass(frozen=True)
class ForecastConfig:
    months_forward: int = 12
    nbrx_window: int = 3           # trailing window for NBRx default
    retention_horizon: int = 36    # how many months for S(t) table
    max_lag: Optional[int] = 36    # cohort max age used in A_t


def make_future_nbrx(nbrx_hist: np.ndarray, months_forward: int, window: int = 3) -> np.ndarray:
    """
    Default assumption: future NBRx = trailing mean of last `window` periods.
    """
    nbrx_hist = np.asarray(nbrx_hist, dtype=float)
    if len(nbrx_hist) == 0:
        raise ValueError("nbrx_hist cannot be empty")
    if window <= 0:
        raise ValueError("window must be >= 1")
    w = min(window, len(nbrx_hist))
    trailing_mean = float(np.mean(nbrx_hist[-w:]))
    return np.full(shape=(months_forward,), fill_value=trailing_mean, dtype=float)


def build_retention_table(alpha: float, beta: float, horizon: int = 36) -> pd.DataFrame:
    """
    Return a DataFrame with columns:
      - age_months: 0..horizon
      - S_t: Weibull survival S(t)
    """
    ages = np.arange(0, horizon + 1, dtype=int)
    s = [weibull_survival(int(a), alpha, beta) for a in ages]
    return pd.DataFrame({"age_months": ages, "S_t": s})


def fit_and_forecast(
    df: pd.DataFrame,
    fit: FitResult,
    config: ForecastConfig = ForecastConfig(),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Given cleaned input df with columns: t, nbrx, trx
    and a FitResult, produce:

    1) trx_table: historical fitted + future projected
    2) retention_table: S(t) from 0..retention_horizon
    """
    nbrx_hist = df["nbrx"].to_numpy(dtype=float)
    trx_hist = df["trx"].to_numpy(dtype=float)

    # future nbrx assumption
    nbrx_future = make_future_nbrx(nbrx_hist, config.months_forward, config.nbrx_window)
    nbrx_all = np.concatenate([nbrx_hist, nbrx_future])

    # fitted TRx for historical + projected TRx for all periods
    trx_all_hat = predict_trx(
        nbrx_all,
        alpha=fit.alpha,
        beta=fit.beta,
        k=fit.k,
        max_lag=config.max_lag,
    )

    n_hist = len(df)
    n_all = len(nbrx_all)

    t_all = np.arange(1, n_all + 1, dtype=int)

    trx_table = pd.DataFrame(
        {
            "t": t_all,
            "nbrx": nbrx_all,
            "trx_actual": np.concatenate([trx_hist, np.full(config.months_forward, np.nan)]),
            "trx_fitted": np.concatenate([trx_all_hat[:n_hist], np.full(config.months_forward, np.nan)]),
            "trx_projected": np.concatenate([np.full(n_hist, np.nan), trx_all_hat[n_hist:]]),
        }
    )

    retention_table = build_retention_table(fit.alpha, fit.beta, horizon=config.retention_horizon)

    return trx_table, retention_table
