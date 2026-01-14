#!/usr/bin/env python3
"""
recompute_indicators_history.py

Purpose
-------
Recompute (or backfill newly-added) indicator columns for *existing* candles already
stored in `candle_analysis`.

Use this when:
- You already ingested raw candles, but some indicators failed (NULLs)
- You updated ta_sdk (added/fixed indicators) and want to populate historical rows
- You want a "clean sweep" to guarantee indicator consistency across the full dataset

How it works
------------
- Streams candles from DB in ascending ts_utc order in chunks
- Maintains an overlap buffer (last day slice + warmup rows) so rolling + daily-reset
  features (VWAP) remain correct across chunk boundaries
- Runs the same indicator pack as your ingest scripts
- Upserts the computed rows back into the same table (unique key: ticker,timespan,ts_utc)

Usage
-----
Recompute for the default most_active_tickers:
  python scripts/recompute_indicators_history.py

Recompute for a subset:
  python scripts/recompute_indicators_history.py --tickers SPY,QQQ,AAPL

Control chunk size:
  python scripts/recompute_indicators_history.py --chunk-rows 50000
"""

from __future__ import annotations

import argparse
import asyncio
import os
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, date
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from fudstop4.apis._ta.ta_sdk import FudstopTA
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

load_dotenv()

warnings.filterwarnings(
    "ignore",
    category=pd.errors.PerformanceWarning,
    message="DataFrame is highly fragmented.*",
)

# ───────────────────────── config ─────────────────────────
TIMESPAN = os.getenv("TIMESPAN", "m1")
TABLE_NAME = os.getenv("CANDLE_TABLE", "candle_analysis")

APPLY_INDICATORS = os.getenv("APPLY_INDICATORS", "true").lower() in ("1", "true", "yes")
INDICATORS_IN_THREADS = os.getenv("INDICATORS_IN_THREADS", "true").lower() in ("1", "true", "yes")
DEFAULT_IND_WORKERS = min(8, (os.cpu_count() or 4))
INDICATOR_WORKERS = int(os.getenv("INDICATOR_WORKERS", str(DEFAULT_IND_WORKERS)))

UPSERT_BATCH_ROWS = int(os.getenv("UPSERT_BATCH_ROWS", "8000"))
OVERLAP_MAX_ROWS = int(os.getenv("OVERLAP_MAX_ROWS", "1200"))
WARMUP_ROWS = int(os.getenv("INDICATOR_WARMUP_ROWS", "200"))

# Indicator toggles (match your mining columns)
ENABLE_PSAR = os.getenv("ENABLE_PSAR", "false").lower() in ("1", "true", "yes")
ENABLE_SDC = os.getenv("ENABLE_SDC", "true").lower() in ("1", "true", "yes")

db = PolygonOptions()

_IND_EXECUTOR: Optional[ThreadPoolExecutor] = None
if APPLY_INDICATORS and INDICATORS_IN_THREADS:
    _IND_EXECUTOR = ThreadPoolExecutor(max_workers=max(1, INDICATOR_WORKERS))


def _drop_bad_cols(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["+DI", "-DI", "__orig_order"], errors="ignore")


def _indicator_pipeline(df_in: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if df_in is None or df_in.empty:
        return df_in

    d = df_in.sort_values("ts_utc").reset_index(drop=True)

    TA = FudstopTA  # call on class for safety

    steps: List[Tuple[str, Callable[[pd.DataFrame], pd.DataFrame]]] = [
        ("bollinger_bands", lambda x: TA.add_bollinger_bands(x)),
        ("aroon", lambda x: TA.add_aroon(x)),
        ("atr", lambda x: TA.add_atr(x)),
        ("cci", lambda x: TA.add_cci(x)),
        ("cmo", lambda x: TA.add_cmo(x)),
        ("td9_counts", lambda x: TA.add_td9_counts(x)),
        ("mfi", lambda x: TA.add_mfi(x)),
        ("stochastic", lambda x: TA.add_stochastic_oscillator(x)),
        ("ao", lambda x: TA.add_awesome_oscillator(x)),
        ("donchian", lambda x: TA.add_donchian_channels(x)),
        ("volume_metrics", lambda x: TA.add_volume_metrics(x)),
        ("keltner", lambda x: TA.add_keltner_channels(x)),
        ("cmf", lambda x: TA.add_chaikin_money_flow(x)),
        ("engulfing", lambda x: TA.add_engulfing_patterns(x)),
        ("obv", lambda x: TA.add_obv(x)),
    ]

    if ENABLE_PSAR:
        steps.append(("psar", lambda x: TA.add_parabolic_sar_signals(x)))

    steps.extend(
        [
            ("roc", lambda x: TA.add_roc(x)),
            ("rsi", lambda x: TA.compute_wilders_rsi(x)),
            ("stoch_rsi", lambda x: TA.add_stoch_rsi(x)),
            ("macd", lambda x: TA.add_macd(x)),
            ("ema_pack", lambda x: TA.add_ema_pack(x, periods=(9, 21, 50), slope_lookback=3)),
            ("vwap_features", lambda x: TA.add_vwap_features(x, reset_daily=True, tz="US/Eastern")),
            ("tsi", lambda x: TA.add_tsi(x, long=25, short=13, signal=7)),
            ("force_index", lambda x: TA.add_force_index(x, ema_period=13)),
            ("rvol", lambda x: TA.add_relative_volume(x, window=20)),
            ("chop", lambda x: TA.add_choppiness_index(x, window=14)),
            ("band_position", lambda x: TA.add_band_position_metrics(x)),
            ("squeeze", lambda x: TA.add_squeeze_flags(x)),
            ("candle_shapes", lambda x: TA.add_candle_shape_metrics(x)),
            ("adx_clean", lambda x: TA.add_adx_clean(x, window=14)),
            ("momentum_flags", lambda x: TA.add_momentum_flags(x)),
            ("williams_r", lambda x: TA.add_williams_r(x)),
            ("vortex", lambda x: TA.add_vortex_indicator(x)),
            ("ppo", lambda x: TA.add_ppo(x)),
        ]
    )

    if ENABLE_SDC:
        steps.append(("sdc", lambda x: TA.add_sdc_indicator(x, window=50, dev_up=1.5, dev_dn=1.5)))

    steps.append(("trix", lambda x: TA.add_trix(x)))

    for name, fn in steps:
        try:
            out = fn(d)
            if out is None:
                continue
            d = out
        except Exception as exc:
            print(f"[{ticker}] indicator {name} failed: {exc}")

    d = d.sort_values("ts_utc").reset_index(drop=True).copy()
    return _drop_bad_cols(d)


async def _apply_indicators_async(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if not APPLY_INDICATORS:
        return df
    if _IND_EXECUTOR is not None:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_IND_EXECUTOR, _indicator_pipeline, df, ticker)
    return _indicator_pipeline(df, ticker)


def _select_overlap(raw_tail: pd.DataFrame) -> pd.DataFrame:
    """Carry last-day slice, but ensure at least WARMUP_ROWS."""
    if raw_tail.empty:
        return raw_tail

    raw_tail = raw_tail.sort_values("ts_utc").reset_index(drop=True)
    last_day = raw_tail["ts_utc"].iloc[-1].date()
    day_slice = raw_tail[raw_tail["ts_utc"].dt.date == last_day]

    if len(day_slice) >= WARMUP_ROWS:
        out = day_slice
    else:
        out = raw_tail.iloc[-min(len(raw_tail), WARMUP_ROWS):]

    if len(out) > OVERLAP_MAX_ROWS:
        out = out.iloc[-OVERLAP_MAX_ROWS:]

    base_cols = ["ts", "ts_utc", "o", "c", "h", "l", "v", "vwap", "ticker", "timespan"]
    return out[base_cols].copy()


async def _iter_db_chunks(ticker: str, chunk_rows: int) -> Any:
    """Async generator yielding base-candle DataFrames for one ticker (ascending)."""
    last_ts: Optional[pd.Timestamp] = None

    while True:
        if last_ts is None:
            query = f"""
                SELECT ts_utc, o, c, h, l, v, vwap
                FROM {TABLE_NAME}
                WHERE ticker = $1 AND timespan = $2
                ORDER BY ts_utc ASC
                LIMIT $3
            """
            rows = await db.fetch(query, ticker, TIMESPAN, int(chunk_rows))
        else:
            query = f"""
                SELECT ts_utc, o, c, h, l, v, vwap
                FROM {TABLE_NAME}
                WHERE ticker = $1 AND timespan = $2 AND ts_utc > $3
                ORDER BY ts_utc ASC
                LIMIT $4
            """
            rows = await db.fetch(query, ticker, TIMESPAN, last_ts, int(chunk_rows))

        if not rows:
            break

        df = pd.DataFrame(rows)
        if df.empty:
            break

        # Normalize
        if "ts_utc" not in df.columns:
            # If db.fetch returns tuples, fall back to known column order
            df.columns = ["ts_utc", "o", "c", "h", "l", "v", "vwap"]

        df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
        df = df.dropna(subset=["ts_utc"]).sort_values("ts_utc").reset_index(drop=True)
        if df.empty:
            break

        df["ts"] = df["ts_utc"]
        df["ticker"] = ticker
        df["timespan"] = TIMESPAN

        # Cast numerics once
        for col in ("o", "c", "h", "l", "vwap"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(np.float64)
        df["v"] = pd.to_numeric(df["v"], errors="coerce").fillna(0).astype(np.int64)

        last_ts = df["ts_utc"].iloc[-1]
        yield df


async def _upsert_df(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        return

    df = _drop_bad_cols(df)

    for start in range(0, len(df), UPSERT_BATCH_ROWS):
        chunk = df.iloc[start : start + UPSERT_BATCH_ROWS]
        await db.batch_upsert_dataframe(
            chunk,
            table_name=TABLE_NAME,
            unique_columns=["ticker", "timespan", "ts_utc"],
        )


async def recompute_one_ticker(ticker: str, chunk_rows: int) -> None:
    t0 = time.perf_counter()

    overlap: Optional[pd.DataFrame] = None
    total_rows = 0
    chunks = 0

    async for df_new in _iter_db_chunks(ticker, chunk_rows=chunk_rows):
        chunks += 1
        total_rows += len(df_new)

        base_cols = ["ts", "ts_utc", "o", "c", "h", "l", "v", "vwap", "ticker", "timespan"]

        if overlap is not None and not overlap.empty:
            raw = pd.concat([overlap[base_cols], df_new[base_cols]], ignore_index=True)
            raw = raw.drop_duplicates(subset=["ts_utc"], keep="last").sort_values("ts_utc").reset_index(drop=True)
        else:
            raw = df_new

        out = await _apply_indicators_async(raw, ticker)

        # Upsert only the rows we just handled (including overlap is fine; it's small)
        await _upsert_df(out)

        # Prepare overlap for next chunk using the RAW (not indicator) frame
        overlap = _select_overlap(raw)

        if chunks % 5 == 0:
            print(f"[{ticker}] chunks={chunks} rows={total_rows}")

    elapsed = time.perf_counter() - t0
    print(f"[{ticker}] recompute done chunks={chunks} rows={total_rows} elapsed={elapsed:.1f}s")


def _parse_tickers(args: argparse.Namespace) -> List[str]:
    if args.tickers:
        return [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    if args.tickers_file:
        out: List[str] = []
        with open(args.tickers_file, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                out.append(s.upper())
        return out
    return list(most_active_tickers)


async def main_async(args: argparse.Namespace) -> None:
    tickers = _parse_tickers(args)
    if not tickers:
        raise SystemExit("No tickers provided")

    await db.connect()

    # Process tickers with limited concurrency (DB + CPU heavy)
    q: asyncio.Queue = asyncio.Queue()
    for t in tickers:
        q.put_nowait(t)

    worker_n = max(1, min(args.ticker_workers, len(tickers)))

    async def _worker(worker_id: int) -> None:
        while True:
            try:
                tkr = q.get_nowait()
            except asyncio.QueueEmpty:
                return
            try:
                await recompute_one_ticker(tkr, chunk_rows=args.chunk_rows)
            except Exception as exc:
                print(f"[{tkr}] recompute failed: {repr(exc)}")
            finally:
                q.task_done()

    workers = [asyncio.create_task(_worker(i)) for i in range(worker_n)]
    await asyncio.gather(*workers)

    await db.disconnect()

    if _IND_EXECUTOR is not None:
        _IND_EXECUTOR.shutdown(wait=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Recompute historical indicators from candles stored in DB")
    ap.add_argument("--tickers", help="Comma separated tickers (default: most_active_tickers)")
    ap.add_argument("--tickers-file", help="Path to file containing tickers (one per line)")
    ap.add_argument("--chunk-rows", type=int, default=50000, help="How many rows to read per DB chunk")
    ap.add_argument("--ticker-workers", type=int, default=2, help="How many tickers to process concurrently")
    args = ap.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
