import argparse
import asyncio
import datetime as dt
import itertools
import os
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from fudstop4.apis.polygonio.polygon_options import PolygonOptions


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Scan bearish base + addon combos and append strong finds.")
    ap.add_argument("--timespan", default="m1")
    ap.add_argument("--lookback-days", type=int, default=180)
    ap.add_argument("--val-days", type=int, default=60)
    ap.add_argument("--window-min", type=int, default=5)
    ap.add_argument("--window-max", type=int, default=10)
    ap.add_argument("--min-n", type=int, default=30)
    ap.add_argument("--min-hit20", type=float, default=0.85)
    ap.add_argument("--min-hit10", type=float, default=0.0)
    ap.add_argument("--min-hit30", type=float, default=0.0)
    ap.add_argument("--min-hit50", type=float, default=0.0)
    ap.add_argument("--min-p15", type=float, default=0.0)
    ap.add_argument("--min-avg", type=float, default=0.0)
    ap.add_argument("--max-k", type=int, default=3)
    ap.add_argument("--out-file", default="runs/bearish_combo_findings.csv")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval-seconds", type=int, default=900)
    return ap.parse_args()


def _build_sql(
    *,
    timespan: str,
    lookback_days: int,
    val_days: int,
    window_min: int,
    window_max: int,
) -> str:
    return f"""
WITH
params AS (
    SELECT
        '{timespan}'::text AS timespan,
        interval '{lookback_days} days' AS lookback,
        interval '{val_days} days' AS val_window
),
max_ts AS (
    SELECT c.ts_utc AS max_ts
    FROM candle_analysis c, params p
    WHERE c.timespan = p.timespan
      AND c.ts_utc IS NOT NULL
    ORDER BY c.ts_utc DESC
    LIMIT 1
),
bounds AS (
    SELECT
        p.*,
        m.max_ts,
        (m.max_ts - p.lookback)   AS start_ts,
        (m.max_ts - p.val_window) AS cutoff_ts
    FROM params p
    CROSS JOIN max_ts m
),
base AS MATERIALIZED (
    SELECT
        c.ticker,
        c.ts_utc,
        c.c,
        c.h,
        c.l,
        c.rsi,
        c.td_sell_count,
        c.candle_completely_above_upper,
        c.bb_width,
        (c.atr / NULLIF(c.c, 0)) AS atr_pct,
        c.rvol,
        c.mfi,
        c.stoch_k,
        c.williams_r,
        c.volume_confirm,
        c.vwap_dist_pct,
        c.vwap_cross_dn,
        c.ema_stack_bear,
        c.macd_cross_dn,
        c.tsi_cross_dn,
        c.di_bear,
        c.adx_strong,
        c.trend_regime,
        c.stoch_rsi_k,
        c.bearish_engulfing,
        c.is_shooting_star,
        c.is_doji,
        c.candle_red,
        c.candle_green,
        max(c.h) OVER w_fwd AS max_h_fwd,
        min(c.l) OVER w_fwd AS min_l_fwd,
        count(*) OVER w_fwd AS n_fwd
    FROM candle_analysis c
    CROSS JOIN bounds b
    WHERE c.timespan = b.timespan
      AND c.ts_utc >= b.start_ts
      AND c.ts_utc <  b.max_ts
      AND c.ts_utc IS NOT NULL
    WINDOW
      w_fwd AS (
        PARTITION BY c.ticker
        ORDER BY c.ts_utc
        ROWS BETWEEN {window_min} FOLLOWING AND {window_max} FOLLOWING
      )
)
SELECT
    b.ticker,
    b.ts_utc,
    b.rsi,
    b.td_sell_count,
    b.bb_width,
    b.atr_pct,
    b.rvol,
    b.mfi,
    b.stoch_k,
    b.williams_r,
    b.volume_confirm,
    b.vwap_dist_pct,
    b.vwap_cross_dn,
    b.ema_stack_bear,
    b.macd_cross_dn,
    b.tsi_cross_dn,
    b.di_bear,
    b.adx_strong,
    b.trend_regime,
    b.stoch_rsi_k,
    b.bearish_engulfing,
    b.is_shooting_star,
    b.is_doji,
    b.candle_red,
    b.candle_green,
    (-1) * (b.min_l_fwd / NULLIF(b.c, 0) - 1) AS best_signed_ret,
    (b.ts_utc >= (SELECT cutoff_ts FROM bounds)) AS is_val
FROM base b
WHERE b.n_fwd = ({window_max} - {window_min} + 1)
  AND b.rsi >= 70
  AND b.td_sell_count >= 10
  AND b.candle_completely_above_upper IS TRUE;
"""


def _build_addons(df: pd.DataFrame) -> List[Tuple[str, np.ndarray]]:
    return [
        ("bb_width>=0.03", df["bb_width"] >= 0.03),
        ("bb_width>=0.04", df["bb_width"] >= 0.04),
        ("bb_width>=0.05", df["bb_width"] >= 0.05),
        ("bb_width>=0.06", df["bb_width"] >= 0.06),
        ("atr_pct>=0.003", df["atr_pct"] >= 0.003),
        ("atr_pct>=0.006", df["atr_pct"] >= 0.006),
        ("atr_pct>=0.009", df["atr_pct"] >= 0.009),
        ("rvol>=1.5", df["rvol"] >= 1.5),
        ("rvol>=2.0", df["rvol"] >= 2.0),
        ("rvol>=2.5", df["rvol"] >= 2.5),
        ("rvol>=3.0", df["rvol"] >= 3.0),
        ("mfi>=80", df["mfi"] >= 80),
        ("mfi>=90", df["mfi"] >= 90),
        ("stoch_k>=80", df["stoch_k"] >= 80),
        ("stoch_k>=90", df["stoch_k"] >= 90),
        ("williams_r>=-20", df["williams_r"] >= -20),
        ("williams_r>=-10", df["williams_r"] >= -10),
        ("volume_confirm", df["volume_confirm"] == True),
        ("vwap_dist>=0.01", df["vwap_dist_pct"] >= 0.01),
        ("vwap_dist>=0.02", df["vwap_dist_pct"] >= 0.02),
        ("vwap_dist>=0.03", df["vwap_dist_pct"] >= 0.03),
        ("vwap_cross_dn", df["vwap_cross_dn"] == True),
        ("ema_stack_bear", df["ema_stack_bear"] == True),
        ("macd_cross_dn", df["macd_cross_dn"] == True),
        ("tsi_cross_dn", df["tsi_cross_dn"] == True),
        ("di_bear", df["di_bear"] == True),
        ("adx_strong", df["adx_strong"] == True),
        ("trend_regime", df["trend_regime"] == True),
        ("stoch_rsi_k>=80", df["stoch_rsi_k"] >= 80),
        ("stoch_rsi_k>=90", df["stoch_rsi_k"] >= 90),
        ("rsi>=80", df["rsi"] >= 80),
        ("rsi>=85", df["rsi"] >= 85),
        ("rsi>=90", df["rsi"] >= 90),
        ("td_sell>=13", df["td_sell_count"] >= 13),
        ("td_sell>=20", df["td_sell_count"] >= 20),
        ("bearish_engulfing", df["bearish_engulfing"] == True),
        ("is_shooting_star", df["is_shooting_star"] == True),
        ("is_doji", df["is_doji"] == True),
        ("candle_green", df["candle_green"] == True),
        ("candle_red", df["candle_red"] == True),
    ]


def _ensure_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for col in [
        "bb_width",
        "atr_pct",
        "rvol",
        "mfi",
        "stoch_k",
        "williams_r",
        "vwap_dist_pct",
        "stoch_rsi_k",
        "best_signed_ret",
        "rsi",
        "td_sell_count",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in [
        "volume_confirm",
        "vwap_cross_dn",
        "ema_stack_bear",
        "macd_cross_dn",
        "tsi_cross_dn",
        "di_bear",
        "adx_strong",
        "trend_regime",
        "bearish_engulfing",
        "is_shooting_star",
        "is_doji",
        "candle_red",
        "candle_green",
    ]:
        df[col] = df[col].fillna(False).astype(bool)
    return df


def _append_findings(out_file: str, rows: List[Dict[str, object]]) -> int:
    if not rows:
        return 0

    os.makedirs(os.path.dirname(out_file) or ".", exist_ok=True)

    existing = None
    if os.path.exists(out_file):
        try:
            existing = pd.read_csv(out_file)
        except Exception:
            existing = None

    new_df = pd.DataFrame(rows)
    if existing is not None and "key" in existing.columns:
        existing_keys = set(existing["key"].astype(str))
        new_df = new_df[~new_df["key"].astype(str).isin(existing_keys)]

    if new_df.empty:
        return 0

    if existing is None or not os.path.exists(out_file):
        new_df.to_csv(out_file, index=False)
    else:
        new_df.to_csv(out_file, mode="a", header=False, index=False)

    return len(new_df)


async def _scan_once(args: argparse.Namespace) -> int:
    sql = _build_sql(
        timespan=args.timespan,
        lookback_days=args.lookback_days,
        val_days=args.val_days,
        window_min=args.window_min,
        window_max=args.window_max,
    )

    db = PolygonOptions()
    await db.connect()
    try:
        rows = await db.fetch(sql)
    finally:
        await db.disconnect()

    if not rows:
        print("no_val_rows")
        return 0

    df = pd.DataFrame([dict(r) for r in rows])
    df = _ensure_numeric(df)

    val_df = df[df["is_val"] == True].copy()
    if val_df.empty:
        print("no_val_rows")
        return 0

    val_df["hit_10bp"] = val_df["best_signed_ret"] >= 0.001
    val_df["hit_20bp"] = val_df["best_signed_ret"] >= 0.002
    val_df["hit_30bp"] = val_df["best_signed_ret"] >= 0.003
    val_df["hit_50bp"] = val_df["best_signed_ret"] >= 0.005

    addons = _build_addons(val_df)

    results = []
    for k in range(1, args.max_k + 1):
        for combo in itertools.combinations(addons, k):
            label = " AND ".join([c[0] for c in combo])
            mask = combo[0][1].copy()
            for _, m in combo[1:]:
                mask &= m
            n = int(mask.sum())
            if n < args.min_n:
                continue
            hit10 = float(val_df.loc[mask, "hit_10bp"].mean())
            hit20 = float(val_df.loc[mask, "hit_20bp"].mean())
            hit30 = float(val_df.loc[mask, "hit_30bp"].mean())
            hit50 = float(val_df.loc[mask, "hit_50bp"].mean())
            if hit20 < args.min_hit20 or hit10 < args.min_hit10:
                continue
            if hit30 < args.min_hit30 or hit50 < args.min_hit50:
                continue
            avg_move = float(val_df.loc[mask, "best_signed_ret"].mean())
            p15 = float(np.quantile(val_df.loc[mask, "best_signed_ret"].values, 0.15))
            if not np.isfinite(avg_move) or not np.isfinite(p15):
                continue
            if avg_move < args.min_avg or p15 < args.min_p15:
                continue
            tickers_val = int(val_df.loc[mask, "ticker"].nunique())
            key = (
                f"{label}|n{args.min_n}"
                f"|h20{args.min_hit20:.3f}|h30{args.min_hit30:.3f}|h50{args.min_hit50:.3f}"
                f"|p15{args.min_p15:.4f}|avg{args.min_avg:.4f}"
                f"|w{args.window_min}-{args.window_max}|lb{args.lookback_days}|val{args.val_days}"
            )
            results.append(
                {
                    "found_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                    "label": label,
                    "n_val": n,
                    "tickers_val": tickers_val,
                    "hit_10bp": hit10,
                    "hit_20bp": hit20,
                    "avg_best_move": avg_move,
                    "p15_best_move": p15,
                    "window_min": args.window_min,
                    "window_max": args.window_max,
                    "lookback_days": args.lookback_days,
                    "val_days": args.val_days,
                    "min_n": args.min_n,
                    "min_hit20": args.min_hit20,
                    "min_hit10": args.min_hit10,
                    "key": key,
                }
            )

    added = _append_findings(args.out_file, results)
    print(f"scan_done found={len(results)} added={added}")
    return added


async def main() -> None:
    args = _parse_args()
    while True:
        await _scan_once(args)
        if not args.loop:
            break
        await asyncio.sleep(max(30, args.interval_seconds))


if __name__ == "__main__":
    asyncio.run(main())
