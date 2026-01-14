# vbz-drug-persistency

A Python package that estimates **treatment persistency (retention)** and produces a **Total TRx fit (and optional projection)** using:

- **New Patients** per period (input column: `NBRx`)
- **Total Prescriptions (TRx)** per period (input column: `TRx`)
- a **Weibull-based retention curve** (“VBZ S(t)”)

This tool is designed for longitudinal brand analytics where total prescriptions (new + refills) depend on how long patients remain on therapy.

> **Terminology note:** The input column is named `NBRx` for compatibility with common datasets, but in this package it represents **new patients / new starts**, not “new prescriptions.”

---

## What the package does

Given a time series of:

- `NBRx` = **New Patients (New Starts)** each period  
- `TRx` = **Total Prescriptions** each period

IMPORTANT: This should be provided from the launch of the drug. Not at any given time.

the package fits a retention model and returns:

1. **Retention curve:**  
   - \(S(t)\) = probability a patient is still on therapy at age \(t\) periods  
   - plus dropout summaries (optional)

2. **TRx fitted series:**  
   - \(\widehat{TRx}_t\) generated from new patient cohorts + retention


---

## Model (VBZ Retention)

### Retention Curve (Weibull Survival)
The retention curve is modeled as:

$$S(t) = \exp\left(-\left(\frac{t}{\alpha}\right)^\beta\right)$$

Where:
* $t$: Patient "age" in periods since start ($0, 1, 2, \dots$)
* $\alpha > 0$: Scale parameter
* $\beta > 0$: Shape parameter

### From New Patients to Total TRx
Each month's total retained "active cohort mass" ($A_t$) is computed as:

$$A_t = \sum_{i=0}^{t} \text{NBRx}_i \cdot S(t-i)$$

Total prescriptions are modeled as:

$$\widehat{TRx}_t = k \cdot A_t$$

Where:
* $k > 0$: A fitted multiplier that maps retained patient mass to prescription volume (captures refills and average fill behavior at an aggregate level).

### Fitting
The package fits $\alpha$, $\beta$, and $k$ by minimizing the squared error between observed TRx and fitted $\widehat{TRx}$.

---

## Input Format

### CSV or Excel
The package accepts `.csv` or `.xlsx` input with **two columns only**:

| Column | Meaning |
| :--- | :--- |
| `NBRx` | New Patients (New Starts) per period |
| `TRx` | Total Prescriptions per period |

**Notes:**
- **One row per period** (typically monthly).
- **Chronological order** (oldest → newest).
- Values must be **non-negative**.
- Data **MUST** be right from launch (no missing early history).

**Example CSV:**
```csv
NBRx,TRx
120,120
135,205
150,295
...
```

## Installation

```bash
pip install vbz-drug-persistency
```

## Quick Start (CLI)

You can run the model directly from the command line.

**1. Standard Run:**
```bash
persistency run --input input.csv --months-forward 0 --output results.xlsx
```
This writes an Excel file with the following sheets:
- **Inputs_Clean**: The processed input data.
- **Fit_Params**: The fitted values for $\alpha$, $\beta$, and $k$.
- **Retention_S(t)**: The retention curve values over time.
- **TRx_Fit_Forecast**: Contains Actual vs Fitted data.

**2. With Projection:**
To project future values, specify the number of months forward:
```bash
persistency run --input input.csv --months-forward 12 --output results.xlsx
```

## Jupyter Notebook Example

Below is an example of how to run the model, view tables, and plot results within a Python script or Jupyter Notebook.

```python
import pandas as pd
import matplotlib.pyplot as plt

from persistency.io import load_input
from persistency.fit import fit_weibull_and_scale, predict_trx
from persistency.forecast import build_retention_table

# 1. Load Data
df = load_input("input.csv")
nbrx = df["nbrx"].to_numpy()
trx  = df["trx"].to_numpy()

# 2. Fit Model
# max_lag defines the historical window used for fitting
fit = fit_weibull_and_scale(nbrx, trx, max_lag=36)
trx_hat = predict_trx(nbrx, fit.alpha, fit.beta, fit.k, max_lag=36)

# 3. Create Fit Table
fit_table = pd.DataFrame({
    "t": df["t"],
    "new_patients": df["nbrx"],
    "trx_actual": df["trx"],
    "trx_fitted": trx_hat
})

# 4. Create Retention Table
ret = build_retention_table(fit.alpha, fit.beta, horizon=36)
ret["dropout_cum"] = 1.0 - ret["S_t"]

# 5. Display Results
print(f"Fitted Parameters: {fit}")
display(fit_table.tail(12))
display(ret.head(12))

# 6. Plot Retention Curve
plt.figure(figsize=(10, 5))
plt.plot(ret["age_months"], ret["S_t"], linewidth=2)
plt.xlabel("Age (months)")
plt.ylabel("Retention S(t)")
plt.title("Retention Curve (VBZ S(t))")
plt.grid(True, alpha=0.3)
plt.show()

# 7. Plot Actual vs Fitted TRx
plt.figure(figsize=(10, 5))
plt.plot(fit_table["t"], fit_table["trx_actual"], label="Actual", marker='o')
plt.plot(fit_table["t"], fit_table["trx_fitted"], label="Fitted", linestyle="--")
plt.xlabel("Time (t)")
plt.ylabel("TRx")
plt.title("TRx: Actual vs Fitted")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

## Model Details

### Retention Curve (Weibull Survival)
The retention curve describes the expected fraction of patients retained at age $t$. It is modeled as:

$$S(t) = \exp\left(-\left(\frac{t}{\alpha}\right)^\beta\right)$$

Where:
* $t$: Patient "age" in periods since start ($0, 1, 2, \dots$)
* $\alpha > 0$: Scale parameter
* $\beta > 0$: Shape parameter

### From New Patients to Total TRx
Each month's total retained "active cohort mass" ($A_t$) is computed as the sum of all previous cohorts' remaining patients:

$$A_t = \sum_{i=0}^{t} \text{NBRx}_i \cdot S(t-i)$$

Total prescriptions are modeled as:

$$\widehat{TRx}_t = k \cdot A_t$$

Where:
* $k > 0$: A fitted multiplier that maps retained patient mass to prescription volume (captures refills and average fill behavior at an aggregate level).

## Interpretation Tips

* **Cumulative Dropout:** Calculated as $1 - S(t)$.
* **Month-to-month Dropout:** Calculated as $S(t-1) - S(t)$.
* **Scaling Factor $k$:**
    > **Important:** $k$ is not a direct "refills per patient" parameter; it is an aggregate mapping factor linking patient mass to prescription units.

## Limitations

* **Aggregate Scope:** This is an aggregate-level model; it does not represent individual patient behavior.
* **Data Requirements:** Parameter stability improves with longer time series (**12+ periods** recommended).
* **Forecasting Dependencies:** Forecasts depend on assumptions for future new patients (NBRx) if projection is enabled.

## Disclaimer

This package is for analytics and modeling purposes only and does not provide medical advice.