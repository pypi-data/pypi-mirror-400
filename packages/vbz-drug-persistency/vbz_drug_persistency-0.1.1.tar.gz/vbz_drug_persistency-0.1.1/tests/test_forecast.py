import numpy as np
import pandas as pd

from persistency.forecast import ForecastConfig, build_retention_table, fit_and_forecast
from persistency.fit import FitResult


def test_build_retention_table_shape_and_bounds():
    tab = build_retention_table(alpha=10.0, beta=1.2, horizon=12)
    assert tab.shape[0] == 13  # 0..12 inclusive
    assert tab["S_t"].iloc[0] == 1.0
    assert (tab["S_t"] <= 1.0).all()
    assert (tab["S_t"] > 0.0).all()


def test_fit_and_forecast_outputs_expected_lengths():
    df = pd.DataFrame(
        {
            "t": [1, 2, 3, 4, 5, 6],
            "nbrx": [100, 110, 120, 115, 130, 125],
            "trx": [100, 205, 300, 380, 460, 520],
        }
    )
    fit = FitResult(alpha=12.0, beta=1.0, k=1.0, rmse=0.0)
    cfg = ForecastConfig(months_forward=4, nbrx_window=3, retention_horizon=12, max_lag=12)

    trx_table, retention_table = fit_and_forecast(df, fit, cfg)

    assert trx_table.shape[0] == 10  # 6 hist + 4 future
    assert retention_table.shape[0] == 13  # 0..12
    assert np.isnan(trx_table["trx_actual"].iloc[-1])
    assert not np.isnan(trx_table["trx_projected"].iloc[-1])
