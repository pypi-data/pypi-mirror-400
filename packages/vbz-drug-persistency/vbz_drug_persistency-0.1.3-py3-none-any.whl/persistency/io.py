from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


REQUIRED_COLUMNS = {"nbrx", "trx"}


class InputDataError(ValueError):
    """Raised when the input file is missing required columns or has invalid values."""


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names: strip spaces, lowercase, remove internal spaces/underscores
    new_cols = []
    for c in df.columns:
        c2 = str(c).strip().lower()
        c2 = c2.replace(" ", "").replace("_", "")
        new_cols.append(c2)
    df = df.copy()
    df.columns = new_cols
    return df


def _validate_two_column_input(df: pd.DataFrame) -> pd.DataFrame:
    df = _normalize_columns(df)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise InputDataError(
            f"Missing required column(s): {sorted(missing)}. "
            f"Found columns: {list(df.columns)}. "
            "Required: NBRx and TRx (case-insensitive)."
        )

    # Keep only required columns (ignore extras if present)
    df = df[["nbrx", "trx"]].copy()

    # Convert to numeric
    for col in ["nbrx", "trx"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[["nbrx", "trx"]].isna().any().any():
        bad_rows = df[df[["nbrx", "trx"]].isna().any(axis=1)].index.tolist()
        raise InputDataError(
            f"Non-numeric or missing values found in NBRx/TRx at row indices: {bad_rows}. "
            "Please ensure both columns contain numbers for every row."
        )

    # Enforce non-negative
    if (df["nbrx"] < 0).any() or (df["trx"] < 0).any():
        bad_rows = df[(df["nbrx"] < 0) | (df["trx"] < 0)].index.tolist()
        raise InputDataError(
            f"Negative values found in NBRx/TRx at row indices: {bad_rows}. "
            "Values must be >= 0."
        )

    # Add time index (1..N)
    df.insert(0, "t", range(1, len(df) + 1))

    return df


def load_input(path: str | Path, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Load input data from CSV or XLSX.

    Expected input: two columns (NBRx and TRx), one row per period.
    Returns a DataFrame with columns: t, nbrx, trx.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")

    suffix = p.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(p)
    elif suffix in {".xlsx", ".xls"}:
        # Default: first sheet if sheet_name not provided
        df = pd.read_excel(p, sheet_name=sheet_name)
    else:
        raise InputDataError("Unsupported file type. Please upload a .csv or .xlsx file.")

    if df.empty:
        raise InputDataError("Input file contains no rows.")

    return _validate_two_column_input(df)

