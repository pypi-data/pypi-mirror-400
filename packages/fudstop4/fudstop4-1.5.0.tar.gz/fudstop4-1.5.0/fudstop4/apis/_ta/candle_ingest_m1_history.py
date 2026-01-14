#!/usr/bin/env python3
"""
candle_ingest_m1_history.py

Purpose
-------
Build a *full* historical minute dataset (timespan=m1 by default) in `candle_analysis`
AND compute your full indicator pack for every bar so rule mining can run purely on
historic data.

Why this exists (vs candle_ingest_m1_fast.py)
---------------------------------------------
Your fast ingest script is already good for "N pages back" + tailing.
This one focuses on *max history*, *resume*, and *correctness* for daily-reset features
(VWAP) by carrying forward an overlap of the *entire oldest trading day* at each
chunk boundary (not just N warmup rows).

Key features
------------
1) Backfill-until-empty (no guessing pages):
   For each ticker, keep paging backwards until Webull returns empty or stops moving.

2) Resume from DB automatically:
   If the DB already has history for a ticker, we start from the current min(ts_utc)
   and keep going backwards from there.

3) Correct chunk-boundaries for VWAP reset_daily:
   We carry forward the entire oldest-day slice as overlap so later recomputation
   fixes VWAP (and any daily-reset features) across boundaries.

4) Same compute+DB pipeline (queue + threadpool) so the event loop stays responsive.

Usage
-----
Backfill max history (resume from DB, stop only when endpoint runs out):
  python scripts/candle_ingest_m1_history.py

Limit how far back (UTC date):
  python scripts/candle_ingest_m1_history.py --stop-date 2018-01-01

Use a custom ticker list:
  python scripts/candle_ingest_m1_history.py --tickers SPY,QQQ,AAPL
  python scripts/candle_ingest_m1_history.py --tickers-file tickers.txt

Notes
-----
- This script assumes your `fudstop4/apis/_ta/ta_sdk.py` is the optimized drop-in
  version (static methods + speed patches). If you still see "multiple values for
  argument 'window'" errors, you are likely running an older ta_sdk.
- For huge universes, consider running in batches to avoid hammering Webull.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone, date
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp
import numpy as np
import pandas as pd
from dotenv import load_dotenv

from fudstop4.apis._ta.ta_sdk import FudstopTA
from fudstop4.apis.helpers import generate_webull_headers
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_trading import WebullTrading
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

load_dotenv()

# Silence the two spammy warnings you saw while still keeping real exceptions visible.
warnings.filterwarnings(
    "ignore",
    category=pd.errors.PerformanceWarning,
    message="DataFrame is highly fragmented.*",
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message="string or file could not be read to its end due to unmatched data.*",
)

# ───────────────────────── config ─────────────────────────
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

TIMESPAN = os.getenv("TIMESPAN", "m1")
TABLE_NAME = os.getenv("CANDLE_TABLE", "candle_analysis")

# Webull fetch
MAX_INFLIGHT_REQUESTS = int(os.getenv("MAX_INFLIGHT_REQUESTS", "120"))
DEFAULT_TICKER_TASKS = min(10, max(2, (os.cpu_count() or 4) * 2))
MAX_TICKER_TASKS = int(os.getenv("MAX_TICKER_TASKS", str(DEFAULT_TICKER_TASKS)))

COUNT_PER_PAGE = int(os.getenv("COUNT_PER_PAGE", "1000"))  # Webull max is usually 1000
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "12"))
REQUEST_RETRIES = int(os.getenv("REQUEST_RETRIES", "4"))
RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "0.35"))

# Chunking / DB
FLUSH_ROWS = int(os.getenv("FLUSH_ROWS", "12000"))          # bigger = fewer indicator runs
UPSERT_BATCH_ROWS = int(os.getenv("UPSERT_BATCH_ROWS", "8000"))
OVERLAP_MAX_ROWS = int(os.getenv("OVERLAP_MAX_ROWS", "1200"))  # enough for 1-2 full sessions

# Compute pipeline
APPLY_INDICATORS = os.getenv("APPLY_INDICATORS", "true").lower() in ("1", "true", "yes")
INDICATORS_IN_THREADS = os.getenv("INDICATORS_IN_THREADS", "true").lower() in ("1", "true", "yes")
DEFAULT_IND_WORKERS = min(8, (os.cpu_count() or 4))
INDICATOR_WORKERS = int(os.getenv("INDICATOR_WORKERS", str(DEFAULT_IND_WORKERS)))

COMPUTE_QUEUE_MAXSIZE = int(os.getenv("COMPUTE_QUEUE_MAXSIZE", "6"))
DB_QUEUE_MAXSIZE = int(os.getenv("DB_QUEUE_MAXSIZE", "6"))
DB_WRITE_WORKERS = int(os.getenv("DB_WRITE_WORKERS", "1"))

LOG_UPSERTS = os.getenv("LOG_UPSERTS", "true").lower() in ("1", "true", "yes")
VERBOSE_PAGES = os.getenv("VERBOSE_PAGES", "false").lower() in ("1", "true", "yes")

# Indicator toggles (match your mining columns)
ENABLE_PSAR = os.getenv("ENABLE_PSAR", "false").lower() in ("1", "true", "yes")  # heavy; default off
ENABLE_SDC = os.getenv("ENABLE_SDC", "true").lower() in ("1", "true", "yes")

# Faster JSON if orjson exists
try:
    import orjson  # type: ignore

    _json_loads = orjson.loads
except Exception:  # pragma: no cover
    import json

    _json_loads = json.loads

# Globals
db = PolygonOptions()
trading = WebullTrading()

_IND_EXECUTOR: Optional[ThreadPoolExecutor] = None
if APPLY_INDICATORS and INDICATORS_IN_THREADS:
    _IND_EXECUTOR = ThreadPoolExecutor(max_workers=max(1, INDICATOR_WORKERS))


@dataclass
class TickerProgress:
    ticker: str
    pages: int = 0
    rows: int = 0
    newest_ts: Optional[pd.Timestamp] = None
    oldest_ts: Optional[pd.Timestamp] = None
    done: bool = False
    error: Optional[str] = None


# ───────────────────────── parsing ─────────────────────────
def _rows_to_numpy_fast(raw_rows: List[str]) -> np.ndarray:
    """Parse Webull candle rows into ndarray(n,8): ts,o,c,h,l,a,v,vwap.

    Fast path: join + np.fromstring
    Fallback: per-row split
    """
    if not raw_rows:
        return np.empty((0, 8), dtype=np.float64)

    # Quick filter: require at least 7 commas
    rows = [r for r in raw_rows if r and r.count(",") >= 7]
    if not rows:
        return np.empty((0, 8), dtype=np.float64)

    # Fast path
    try:
        blob = "\n".join(rows)
        # Clean common non-numeric tokens (rare, but avoids partial-parse warnings)
        blob = blob.replace("null", "nan").replace("None", "nan").replace("N/A", "nan")
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                message="string or file could not be read to its end.*",
            )
            arr = np.fromstring(blob, sep=",", dtype=np.float64)
        if arr.size and arr.size % 8 == 0:
            return arr.reshape((-1, 8))
    except Exception:
        pass

    # Fallback
    out = np.empty((len(rows), 8), dtype=np.float64)
    k = 0
    for row in rows:
        parts = row.split(",")
        if len(parts) < 8:
            continue
        try:
            out[k, 0] = float(parts[0])
            out[k, 1] = float(parts[1])
            out[k, 2] = float(parts[2])
            out[k, 3] = float(parts[3])
            out[k, 4] = float(parts[4])
            out[k, 5] = float(parts[5])
            out[k, 6] = float(parts[6])
            out[k, 7] = float(parts[7])
            k += 1
        except Exception:
            continue

    return out[:k] if k else np.empty((0, 8), dtype=np.float64)


# ───────────────────────── HTTP fetch ─────────────────────────
async def _fetch_page(session: aiohttp.ClientSession, sem: asyncio.Semaphore, url: str):
    last_exc: Optional[Exception] = None
    for attempt in range(REQUEST_RETRIES):
        try:
            async with sem:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                    if resp.status == 429:
                        retry_after = resp.headers.get("Retry-After")
                        delay = float(retry_after) if retry_after else (RETRY_BASE_DELAY * (2**attempt))
                        await asyncio.sleep(delay)
                        continue

                    resp.raise_for_status()
                    return await resp.json(loads=_json_loads)
        except Exception as exc:
            last_exc = exc
            if attempt < REQUEST_RETRIES - 1:
                await asyncio.sleep(RETRY_BASE_DELAY * (2**attempt))

    raise last_exc if last_exc else RuntimeError("request failed")


# ───────────────────────── indicator pipeline ─────────────────────────
def _drop_bad_cols(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["+DI", "-DI", "__orig_order"], errors="ignore")


def _indicator_pipeline(df_in: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Compute the full indicator pack for one ticker chunk."""
    if df_in is None or df_in.empty:
        return df_in

    d = df_in

    # Ensure ASC for rolling calcs
    if "ts_utc" in d.columns:
        d = d.sort_values("ts_utc").reset_index(drop=True)
    elif "ts" in d.columns:
        d = d.sort_values("ts").reset_index(drop=True)

    # IMPORTANT:
    # Call on the class, not an instance. This avoids binding bugs if a method
    # accidentally missed @staticmethod in your local ta_sdk.
    TA = FudstopTA

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
            # Keep going; you'll still upsert raw candles.
            print(f"[{ticker}] indicator {name} failed: {exc}")

    # Final ordering + consolidate blocks to avoid fragmentation
    if "ts_utc" in d.columns:
        d = d.sort_values("ts_utc").reset_index(drop=True)
    elif "ts" in d.columns:
        d = d.sort_values("ts").reset_index(drop=True)

    d = d.copy()
    return _drop_bad_cols(d)


async def _apply_indicators_async(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if not APPLY_INDICATORS:
        return df
    if _IND_EXECUTOR is not None:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_IND_EXECUTOR, _indicator_pipeline, df, ticker)
    return _indicator_pipeline(df, ticker)


# ───────────────────────── DB writer ─────────────────────────
async def _db_writer_worker(q: asyncio.Queue, worker_id: int) -> None:
    while True:
        item = await q.get()
        if item is None:
            q.task_done()
            return

        df, meta = item
        try:
            if df is None or df.empty:
                q.task_done()
                continue

            df = _drop_bad_cols(df)

            for start in range(0, len(df), UPSERT_BATCH_ROWS):
                chunk = df.iloc[start : start + UPSERT_BATCH_ROWS]
                chunk = _drop_bad_cols(chunk)
                await db.batch_upsert_dataframe(
                    chunk,
                    table_name=TABLE_NAME,
                    unique_columns=["ticker", "timespan", "ts_utc"],
                )

            if LOG_UPSERTS and meta:
                tkr, tmin, tmax, rows = meta
                print(f"[{tkr}] upserted {rows} rows ({tmin} -> {tmax})")
        except Exception as exc:
            print(f"[db-writer-{worker_id}] upsert failed: {repr(exc)}")
        finally:
            q.task_done()


# ───────────────────────── compute workers ─────────────────────────
async def _compute_worker(compute_q: asyncio.Queue, db_q: asyncio.Queue, worker_id: int) -> None:
    while True:
        item = await compute_q.get()
        if item is None:
            compute_q.task_done()
            return

        df, ticker, meta = item
        try:
            out = await _apply_indicators_async(df, ticker) if APPLY_INDICATORS else df
            out = _drop_bad_cols(out)
            await db_q.put((out, meta))
        except Exception as exc:
            print(f"[compute-{worker_id}] failed: {repr(exc)}")
        finally:
            compute_q.task_done()


# ───────────────────────── DB helpers ─────────────────────────
async def _get_db_min_ts_map(tickers: List[str]) -> Dict[str, Optional[pd.Timestamp]]:
    """Get the current min(ts_utc) per ticker in DB to resume older backfills."""
    if not tickers:
        return {}

    query = f"""
        SELECT ticker, min(ts_utc) AS min_ts
        FROM {TABLE_NAME}
        WHERE timespan = $1 AND ticker = ANY($2)
        GROUP BY ticker
    """
    out: Dict[str, Optional[pd.Timestamp]] = {t: None for t in tickers}

    try:
        rows = await db.fetch(query, TIMESPAN, tickers)
    except Exception:
        return out

    for r in rows or []:
        try:
            tkr = str(r["ticker"]) if isinstance(r, dict) else str(r[0])
            ts = r["min_ts"] if isinstance(r, dict) else r[1]
            out[tkr] = ts
        except Exception:
            continue
    return out


async def _load_overlap_seed_from_db(ticker: str, limit_rows: int = OVERLAP_MAX_ROWS) -> Optional[pd.DataFrame]:
    """Load the oldest-day slice currently in DB for this ticker (used when resuming)."""
    query = f"""
        SELECT ts_utc, o, c, h, l, v, vwap
        FROM {TABLE_NAME}
        WHERE ticker = $1 AND timespan = $2
        ORDER BY ts_utc ASC
        LIMIT $3
    """
    try:
        rows = await db.fetch(query, ticker, TIMESPAN, int(limit_rows))
    except Exception:
        return None

    if not rows:
        return None

    df = pd.DataFrame(rows)
    if df.empty or "ts_utc" not in df.columns:
        return None

    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["ts_utc"]).sort_values("ts_utc").reset_index(drop=True)
    if df.empty:
        return None

    # Keep only the oldest UTC date present
    oldest_day = df["ts_utc"].iloc[0].date()
    day_df = df[df["ts_utc"].dt.date == oldest_day].copy()

    day_df["ts"] = day_df["ts_utc"]
    day_df["ticker"] = ticker
    day_df["timespan"] = TIMESPAN

    cols = ["ts", "ts_utc", "o", "c", "h", "l", "v", "vwap", "ticker", "timespan"]
    for c in cols:
        if c not in day_df.columns:
            day_df[c] = np.nan
    return day_df[cols].copy()


# ───────────────────────── backfill core ─────────────────────────
async def backfill_one_ticker_full_history(
    *,
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    ticker: str,
    compute_q: asyncio.Queue,
    start_anchor_epoch: int,
    stop_date_utc: Optional[date],
    restorationType: int = 0,
) -> TickerProgress:
    """Backfill a single ticker backwards until empty/stop_date."""

    ticker_id = trading.ticker_to_id_map.get(ticker)
    if not ticker_id:
        return TickerProgress(ticker=ticker, done=True, error="unknown ticker_id")

    progress = TickerProgress(ticker=ticker)

    # Initial overlap for resume: oldest day currently in DB.
    overlap_df: Optional[pd.DataFrame] = await _load_overlap_seed_from_db(ticker)

    buffer_blocks: List[np.ndarray] = []
    buffer_nrows = 0

    anchor = int(start_anchor_epoch)
    last_oldest: Optional[int] = None

    BASE_COLS = ["ts", "ts_utc", "o", "c", "h", "l", "v", "vwap", "ticker", "timespan"]

    async def _flush() -> None:
        nonlocal buffer_blocks, buffer_nrows, overlap_df

        if buffer_nrows <= 0:
            return

        arr = np.concatenate(buffer_blocks, axis=0) if len(buffer_blocks) > 1 else buffer_blocks[0]
        buffer_blocks = []
        buffer_nrows = 0

        ts_epoch = arr[:, 0].astype(np.int64)

        df_new = pd.DataFrame(
            {
                "ts_utc": pd.to_datetime(ts_epoch, unit="s", utc=True),
                "o": arr[:, 1].astype(np.float64),
                "c": arr[:, 2].astype(np.float64),
                "h": arr[:, 3].astype(np.float64),
                "l": arr[:, 4].astype(np.float64),
                "v": arr[:, 6].astype(np.int64),
                "vwap": arr[:, 7].astype(np.float64),
            }
        )

        df_new["ts"] = df_new["ts_utc"]
        df_new["ticker"] = ticker
        df_new["timespan"] = TIMESPAN

        df_new = (
            df_new.dropna(subset=["ts_utc"])
            .drop_duplicates(subset=["ts_utc"], keep="last")
            .sort_values("ts_utc")
            .reset_index(drop=True)
        )

        if df_new.empty:
            overlap_df = None
            return

        # Combine with overlap to fix boundary indicators (especially VWAP reset_daily)
        if overlap_df is not None and not overlap_df.empty:
            df = pd.concat([df_new[BASE_COLS], overlap_df[BASE_COLS]], ignore_index=True)
            df = (
                df.drop_duplicates(subset=["ts_utc"], keep="last")
                .sort_values("ts_utc")
                .reset_index(drop=True)
            )
        else:
            df = df_new

        meta = None
        if LOG_UPSERTS:
            meta = (ticker, df["ts_utc"].min(), df["ts_utc"].max(), int(len(df)))

        await compute_q.put((df, ticker, meta))

        # Overlap strategy: carry forward the ENTIRE OLDEST UTC DAY slice.
        oldest_day = df_new["ts_utc"].iloc[0].date()
        overlap_df2 = df_new[df_new["ts_utc"].dt.date == oldest_day].copy()
        if len(overlap_df2) > OVERLAP_MAX_ROWS:
            overlap_df2 = overlap_df2.iloc[:OVERLAP_MAX_ROWS].copy()
        overlap_df = overlap_df2[BASE_COLS].copy()

    # Page loop (no fixed max pages; stops when endpoint runs out)
    while True:
        url = (
            "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
            f"?type={TIMESPAN}&count={COUNT_PER_PAGE}&timestamp={anchor}"
            f"&restorationType={restorationType}&tickerId={ticker_id}&hasMore=true"
        )

        data = await _fetch_page(session, sem, url)
        raw_rows = (data[0] or {}).get("data") if isinstance(data, list) and data else None
        if not raw_rows:
            # flush last buffer and stop
            if buffer_nrows:
                await _flush()
            progress.done = True
            return progress

        page_arr = _rows_to_numpy_fast(raw_rows)
        if page_arr.size == 0:
            if buffer_nrows:
                await _flush()
            progress.done = True
            return progress

        ts_page = page_arr[:, 0]
        page_oldest = int(np.nanmin(ts_page))
        page_newest = int(np.nanmax(ts_page))

        progress.pages += 1
        progress.rows += int(page_arr.shape[0])

        # Update progress timestamps
        newest = pd.to_datetime(page_newest, unit="s", utc=True)
        oldest = pd.to_datetime(page_oldest, unit="s", utc=True)
        progress.newest_ts = newest if progress.newest_ts is None else max(progress.newest_ts, newest)
        progress.oldest_ts = oldest if progress.oldest_ts is None else min(progress.oldest_ts, oldest)

        if VERBOSE_PAGES and progress.pages % 25 == 0:
            print(f"[{ticker}] pages={progress.pages} oldest={oldest} newest={newest} buffer={buffer_nrows}")

        # Stop if API stops moving backward
        if last_oldest is not None and page_oldest >= last_oldest:
            if buffer_nrows:
                await _flush()
            progress.done = True
            return progress
        last_oldest = page_oldest

        # Stop-date check
        if stop_date_utc is not None:
            if oldest.date() <= stop_date_utc:
                # still include this page, then flush & stop
                buffer_blocks.append(page_arr)
                buffer_nrows += int(page_arr.shape[0])
                await _flush()
                progress.done = True
                return progress

        # Advance anchor backward and buffer
        anchor = page_oldest - 1
        buffer_blocks.append(page_arr)
        buffer_nrows += int(page_arr.shape[0])

        if buffer_nrows >= FLUSH_ROWS:
            await _flush()


# ───────────────────────── main runner ─────────────────────────
async def run_full_history_backfill(
    tickers: List[str],
    *,
    stop_date_utc: Optional[date],
    semaphore_limit: int = MAX_INFLIGHT_REQUESTS,
    restorationType: int = 0,
) -> List[TickerProgress]:
    if not tickers:
        return []

    await db.connect()

    # Resume anchors from DB: start at min(ts_utc)-1, else now
    min_map = await _get_db_min_ts_map(tickers)
    anchors: Dict[str, int] = {}
    now_epoch = int(time.time())

    for t in tickers:
        ts = min_map.get(t)
        if ts is not None:
            try:
                anchors[t] = int(pd.Timestamp(ts).timestamp()) - 1
            except Exception:
                anchors[t] = now_epoch
        else:
            anchors[t] = now_epoch

    sem = asyncio.Semaphore(semaphore_limit)
    headers = generate_webull_headers(access_token=ACCESS_TOKEN)

    compute_q: asyncio.Queue = asyncio.Queue(maxsize=COMPUTE_QUEUE_MAXSIZE)
    db_q: asyncio.Queue = asyncio.Queue(maxsize=DB_QUEUE_MAXSIZE)

    db_tasks = [asyncio.create_task(_db_writer_worker(db_q, i)) for i in range(max(1, DB_WRITE_WORKERS))]
    compute_workers = max(1, min(INDICATOR_WORKERS, 8))
    compute_tasks = [asyncio.create_task(_compute_worker(compute_q, db_q, i)) for i in range(compute_workers)]

    ticker_q: asyncio.Queue = asyncio.Queue()
    for t in tickers:
        ticker_q.put_nowait(t)

    results: List[TickerProgress] = []
    done = 0
    total = len(tickers)

    async with aiohttp.ClientSession(
        headers=headers,
        connector=aiohttp.TCPConnector(limit=semaphore_limit, limit_per_host=semaphore_limit, ttl_dns_cache=300),
    ) as session:

        async def _ticker_worker(worker_id: int) -> None:
            nonlocal done
            while True:
                try:
                    tkr = ticker_q.get_nowait()
                except asyncio.QueueEmpty:
                    return

                try:
                    prog = await backfill_one_ticker_full_history(
                        session=session,
                        sem=sem,
                        ticker=tkr,
                        compute_q=compute_q,
                        start_anchor_epoch=anchors.get(tkr, now_epoch),
                        stop_date_utc=stop_date_utc,
                        restorationType=restorationType,
                    )
                    results.append(prog)
                except Exception as exc:
                    results.append(TickerProgress(ticker=tkr, done=True, error=repr(exc)))

                done += 1
                if done % 5 == 0 or done == total:
                    print(
                        f"completed {done}/{total} | compute_q={compute_q.qsize()}/{COMPUTE_QUEUE_MAXSIZE} db_q={db_q.qsize()}/{DB_QUEUE_MAXSIZE}"
                    )

                ticker_q.task_done()

        workers = [
            asyncio.create_task(_ticker_worker(i))
            for i in range(max(1, min(MAX_TICKER_TASKS, total)))
        ]
        await asyncio.gather(*workers)

    # Drain compute queue then stop compute workers
    await compute_q.join()
    for _ in compute_tasks:
        await compute_q.put(None)
    await asyncio.gather(*compute_tasks)

    # Drain DB queue then stop DB writers
    await db_q.join()
    for _ in db_tasks:
        await db_q.put(None)
    await asyncio.gather(*db_tasks)

    await db.disconnect()

    if _IND_EXECUTOR is not None:
        _IND_EXECUTOR.shutdown(wait=True)

    return results


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


def _parse_stop_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    # Accept YYYY-MM-DD
    return datetime.strptime(s, "%Y-%m-%d").date()


def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill max history into candle_analysis with full indicator pack")
    ap.add_argument("--tickers", help="Comma separated tickers (default: most_active_tickers)")
    ap.add_argument("--tickers-file", help="Path to file containing tickers (one per line)")
    ap.add_argument("--stop-date", help="Stop once oldest candle reaches this UTC date (YYYY-MM-DD). Default: no stop.")
    ap.add_argument("--semaphore", type=int, default=MAX_INFLIGHT_REQUESTS)
    ap.add_argument("--restorationType", type=int, default=0)
    args = ap.parse_args()

    tickers = _parse_tickers(args)
    stop_dt = _parse_stop_date(args.stop_date)

    print(f"starting full-history backfill tickers={len(tickers)} timespan={TIMESPAN} stop_date={stop_dt}")

    async def _run() -> None:
        t0 = time.perf_counter()
        res = await run_full_history_backfill(
            tickers,
            stop_date_utc=stop_dt,
            semaphore_limit=max(10, int(args.semaphore)),
            restorationType=int(args.restorationType),
        )
        elapsed = time.perf_counter() - t0

        ok = [r for r in res if not r.error]
        err = [r for r in res if r.error]

        print(f"done elapsed_seconds={elapsed:.1f} ok={len(ok)} err={len(err)}")
        if err:
            print("errors:")
            for r in err[:25]:
                print(f"  {r.ticker}: {r.error}")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
