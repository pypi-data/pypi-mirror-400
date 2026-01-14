import numpy as np
from persistency.fit import fit_weibull_and_scale, predict_trx


def test_fit_returns_positive_params_on_simple_data():
    nbrx = np.array([100, 110, 120, 115, 130, 125, 140, 135], dtype=float)
    trx  = np.array([100, 200, 290, 360, 440, 510, 600, 660], dtype=float)

    result = fit_weibull_and_scale(nbrx, trx, max_lag=24)
    assert result.alpha > 0
    assert result.beta > 0
    assert result.k > 0
    assert result.rmse >= 0

    trx_hat = predict_trx(nbrx, result.alpha, result.beta, result.k, max_lag=24)
    assert trx_hat.shape == trx.shape
