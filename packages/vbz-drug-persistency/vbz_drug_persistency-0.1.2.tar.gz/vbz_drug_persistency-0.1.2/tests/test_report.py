import pandas as pd
from persistency.fit import FitResult
from persistency.report import write_results_excel


def test_write_results_excel_creates_file(tmp_path):
    inputs = pd.DataFrame({"t": [1, 2], "nbrx": [10, 12], "trx": [10, 18]})
    fit = FitResult(alpha=12.0, beta=1.2, k=1.5, rmse=10.0)
    retention = pd.DataFrame({"age_months": [0, 1], "S_t": [1.0, 0.9]})
    trx_table = pd.DataFrame(
        {"t": [1, 2], "nbrx": [10, 12], "trx_actual": [10, 18], "trx_fitted": [11, 17], "trx_projected": [None, None]}
    )

    out = write_results_excel(tmp_path / "results.xlsx", inputs, fit, retention, trx_table)
    assert out.exists()
    assert out.suffix == ".xlsx"
