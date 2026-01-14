from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from persistency.io import load_input
from persistency.fit import fit_weibull_and_scale
from persistency.forecast import ForecastConfig, fit_and_forecast
from persistency.report import write_results_excel


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="persistency", description="Project TRx from NBRx using VBZ S(t) retention.")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run fit + forecast and write results to Excel")
    run.add_argument("--input", "-i", required=True, help="Path to input .csv or .xlsx containing NBRx and TRx columns")
    run.add_argument("--output", "-o", required=True, help="Path to output .xlsx file")
    run.add_argument("--months-forward", type=int, default=12, help="Number of future months to project (default: 12)")
    run.add_argument("--nbrx-window", type=int, default=3, help="Trailing window for future NBRx mean (default: 3)")
    run.add_argument("--retention-horizon", type=int, default=36, help="Horizon for S(t) table (default: 36)")
    run.add_argument("--max-lag", type=int, default=36, help="Max lag used in cohort accumulation (default: 36)")
    run.add_argument("--sheet", default=None, help="Excel sheet name (optional, only for .xlsx input)")

    return p


def cmd_run(args: argparse.Namespace) -> int:
    df = load_input(args.input, sheet_name=args.sheet)

    nbrx = df["nbrx"].to_numpy(dtype=float)
    trx = df["trx"].to_numpy(dtype=float)

    fit = fit_weibull_and_scale(nbrx, trx, max_lag=args.max_lag)

    cfg = ForecastConfig(
        months_forward=args.months_forward,
        nbrx_window=args.nbrx_window,
        retention_horizon=args.retention_horizon,
        max_lag=args.max_lag,
    )

    trx_table, retention_table = fit_and_forecast(df, fit, cfg)
    out = write_results_excel(args.output, df, fit, retention_table, trx_table)

    print(f"Wrote results: {out}")
    print(f"Fit: alpha={fit.alpha:.4f}, beta={fit.beta:.4f}, k={fit.k:.6f}, RMSE={fit.rmse:.4f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return cmd_run(args)

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
