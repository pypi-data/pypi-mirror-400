# ----------------------------------------
#  exposure.py  (patched)
# ----------------------------------------
from __future__ import annotations
import pandas as pd
from typing import Dict, Tuple, Any

CONTRACT_MULTIPLIER: int = 100     # OCC standard

_CALL_PUT_MAP = {"call": 1, "put": -1, "c": 1, "p": -1}  # robust mapping

def _signed_gamma(series: pd.Series) -> pd.Series:
    """Map call/put flags → +1 / –1; unknown → 0."""
    return (
        series.astype(str)               # tolerate non‑string dtypes
              .str.lower()
              .map(_CALL_PUT_MAP)
              .fillna(0)
              .astype(int)
    )

def compute_exposures(
    df: pd.DataFrame,
    spot_price: float,
    *,
    contract_multiplier: int = CONTRACT_MULTIPLIER,
    gamma_is_percent: bool = False,         # <‑‑ new toggle
) -> Tuple[pd.DataFrame, Dict[str, Any]]:

    if df.empty:
        return df, {
            "total_gex": 0, "total_vex": 0, "total_thex": 0,
            "max_pos_gamma_strike": None, "max_neg_gamma_strike": None,
            "max_pos_gamma_value": 0, "max_neg_gamma_value": 0,
            "spot_price": spot_price,                    # always return it
        }

    # ---------- 1. Direction‑adjusted exposures ----------
    sign = _signed_gamma(df["call_put"])
    contracts = df["oi"].fillna(0).astype(float)

    # Optional scaling if gamma came in as a percentage
    gamma_scale = 0.01 if gamma_is_percent else 1.0
    gamma = df["gamma"].astype(float) * gamma_scale

    df["gex"]  = gamma * contracts * contract_multiplier * (spot_price ** 2) * sign
    df["vex"]  = df["vega"].astype(float)  * contracts * contract_multiplier
    df["thex"] = df["theta"].astype(float) * contracts * contract_multiplier

    # ---------- 2. Aggregations ----------
    total_GEX  = df["gex"].sum(skipna=True)
    total_VEX  = df["vex"].sum(skipna=True)
    total_THEX = df["thex"].sum(skipna=True)

    # Strikes that matter for hedgers – ignore pure‑zero rows
    non_zero = df["gex"].ne(0)
    if non_zero.any():
        pos_idx = df.loc[non_zero, "gex"].idxmax()
        neg_idx = df.loc[non_zero, "gex"].idxmin()
        max_pos_row = df.loc[pos_idx]
        max_neg_row = df.loc[neg_idx]
    else:
        # fallback when absolutely every value is zero
        max_pos_row = max_neg_row = pd.Series({"strike": None, "gex": 0})

    summary = {
        "total_gex":            float(total_GEX),
        "total_vex":            float(total_VEX),
        "total_thex":           float(total_THEX),
        "max_pos_gamma_strike": None if pd.isna(max_pos_row["strike"]) else float(max_pos_row["strike"]),
        "max_neg_gamma_strike": None if pd.isna(max_neg_row["strike"]) else float(max_neg_row["strike"]),
        "max_pos_gamma_value":  float(max_pos_row["gex"]),
        "max_neg_gamma_value":  float(max_neg_row["gex"]),
        "spot_price":           float(spot_price),        # <‑‑ write this back
    }

    return df, summary
