from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd

from persistency.fit import FitResult


def write_results_excel(
    output_path: str | Path,
    inputs_clean: pd.DataFrame,
    fit: FitResult,
    retention_table: pd.DataFrame,
    trx_table: pd.DataFrame,
) -> Path:
    """
    Write results to an Excel workbook with standard sheets.
    """
    out = Path(output_path)
    if out.suffix.lower() != ".xlsx":
        out = out.with_suffix(".xlsx")

    fit_df = pd.DataFrame([asdict(fit)])

    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        inputs_clean.to_excel(writer, sheet_name="Inputs_Clean", index=False)
        fit_df.to_excel(writer, sheet_name="Fit_Params", index=False)
        retention_table.to_excel(writer, sheet_name="Retention_S(t)", index=False)
        trx_table.to_excel(writer, sheet_name="TRx_Fit_Forecast", index=False)

    return out

