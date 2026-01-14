#!/usr/bin/env python3
"""candle_ingest_m1_fast.py

Goal
----
Seed (backfill) and optionally maintain (tail) the `candle_analysis` table with:
  - raw 1m candles from Webull
  - a full indicator pack (via fudstop4.apis._ta.ta_sdk.FudstopTA)

Why this version is faster / safer
---------------------------------
1) Faster Webull row parsing
   Webull's endpoint returns each candle as a CSV string. The slow path is
   per-row `.split(',')`. This script uses `np.fromstring` to parse a whole page
   at once, with a robust fallback when parsing fails.

2) Less pandas churn
   We build the DataFrame from numpy arrays directly and cast dtypes once.

3) Chunk-boundary correctness when backfilling backwards
   When you backfill from "now" backwards, the earliest rows of the *newer*
   chunk don't have enough history yet to compute rolling indicators.
   We carry `INDICATOR_WARMUP_ROWS` of those earliest rows forward and re-run
   them once older data arrives (upsert overwrites the indicator columns).

4) Uses ts_utc as the upsert key
   `ts` is TEXT in your schema and can drift in formatting. `ts_utc` is the
   canonical timestamp and already has a unique constraint.

Usage
-----
Backfill only:
  python scripts/candle_ingest_m1_fast.py --mode backfill --tickers SPY,QQQ,AAPL --pages 120 --count 1000

Tail only (keeps last N bars up to date):
  python scripts/candle_ingest_m1_fast.py --mode tail --tickers SPY,QQQ,AAPL --tail-count 500 --poll-seconds 55

Backfill then tail:
  python scripts/candle_ingest_m1_fast.py --mode backfill+tail --tickers SPY,QQQ,AAPL --pages 120 --count 1000 --tail-count 500

Notes
-----
- This script assumes you have already replaced fudstop4/apis/_ta/ta_sdk.py with
  the optimized version we produced (Download link in chat).
- For huge ticker universes: backfill in batches (e.g., 25-50 tickers at a time).
"""

from __future__ import annotations

import argparse
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Tuple, Any, Callable

import aiohttp
import numpy as np
import pandas as pd
from dotenv import load_dotenv

from fudstop4.apis._ta.ta_sdk import FudstopTA
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_trading import WebullTrading
from fudstop4.apis.helpers import generate_webull_headers
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

load_dotenv()

# ───────────────────────── config ─────────────────────────
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# Webull fetch concurrency
MAX_INFLIGHT_REQUESTS = int(os.getenv("MAX_INFLIGHT_REQUESTS", "150"))
DEFAULT_TICKER_TASKS = min(12, max(2, (os.cpu_count() or 4) * 2))
MAX_TICKER_TASKS = int(os.getenv("MAX_TICKER_TASKS", str(DEFAULT_TICKER_TASKS)))

# Default page sizing (per ticker)
DEFAULT_PAGES = int(os.getenv("DEFAULT_PAGES", "500"))
DEFAULT_COUNT = int(os.getenv("DEFAULT_COUNT", "1000"))

# Flush/DB batching
FLUSH_ROWS = int(os.getenv("FLUSH_ROWS", "5000"))
UPSERT_BATCH_ROWS = int(os.getenv("UPSERT_BATCH_ROWS", "5000"))
INDICATOR_WARMUP_ROWS = int(os.getenv("INDICATOR_WARMUP_ROWS", "150"))

# Pipeline toggles
APPLY_INDICATORS = os.getenv("APPLY_INDICATORS", "true").lower() in ("1", "true", "yes")
INDICATORS_IN_THREADS = os.getenv("INDICATORS_IN_THREADS", "true").lower() in ("1", "true", "yes")
DEFAULT_IND_WORKERS = min(8, (os.cpu_count() or 4))
INDICATOR_WORKERS = int(os.getenv("INDICATOR_WORKERS", str(DEFAULT_IND_WORKERS)))

ENABLE_PSAR = os.getenv("ENABLE_PSAR", "false").lower() in ("1", "true", "yes")
ENABLE_SDC = os.getenv("ENABLE_SDC", "true").lower() in ("1", "true", "yes")

OVERLAP_BACKFILL = os.getenv("OVERLAP_BACKFILL", "true").lower() in ("1", "true", "yes")

# Timespan/table
TIMESPAN = os.getenv("TIMESPAN", "m1")
TABLE_NAME = os.getenv("CANDLE_TABLE", "candle_analysis")

# Networking
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "12"))
REQUEST_RETRIES = int(os.getenv("REQUEST_RETRIES", "4"))
RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "0.35"))

# Queue sizes (backpressure)
COMPUTE_QUEUE_MAXSIZE = int(os.getenv("COMPUTE_QUEUE_MAXSIZE", "8"))
DB_QUEUE_MAXSIZE = int(os.getenv("DB_QUEUE_MAXSIZE", "8"))

# DB writers
DB_WRITE_WORKERS = int(os.getenv("DB_WRITE_WORKERS", "2"))
LOG_UPSERTS = os.getenv("LOG_UPSERTS", "true").lower() in ("1", "true", "yes")

# Tail mode
TAIL_COUNT = int(os.getenv("TAIL_COUNT", "500"))
TAIL_UPSERT_ROWS = int(os.getenv("TAIL_UPSERT_ROWS", str(max(INDICATOR_WARMUP_ROWS * 2, 250))))
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "5"))

# Faster JSON if orjson exists
try:
    import orjson  # type: ignore

    _json_loads = orjson.loads
except Exception:  # pragma: no cover
    import json

    _json_loads = json.loads

# ───────────────────────── globals ─────────────────────────
ta = FudstopTA()
trading = WebullTrading()
db = PolygonOptions()

_IND_EXECUTOR: Optional[ThreadPoolExecutor] = None
if APPLY_INDICATORS and INDICATORS_IN_THREADS:
    _IND_EXECUTOR = ThreadPoolExecutor(max_workers=max(1, INDICATOR_WORKERS))


# ───────────────────────── parsing ─────────────────────────
def _rows_to_numpy_fast(raw_rows: List[str]) -> np.ndarray:
    """Parse Webull CSV candle rows to ndarray shape (n, 8).

    Each row is like: "ts,o,c,h,l,a,v,vwap".

    Fast path: np.fromstring over the whole page.
    Fallback: per-row split (robust).
    """
    if not raw_rows:
        return np.empty((0, 8), dtype=np.float64)

    # Fast path
    try:
        blob = "\n".join(raw_rows)
        arr = np.fromstring(blob, sep=",", dtype=np.float64)
        if arr.size % 8 == 0:
            return arr.reshape((-1, 8))
    except Exception:
        pass

    # Fallback
    out = np.empty((len(raw_rows), 8), dtype=np.float64)
    k = 0
    for row in raw_rows:
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

    if k == 0:
        return np.empty((0, 8), dtype=np.float64)
    return out[:k]


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
    # SQL-unfriendly and internal helper columns
    return df.drop(columns=["+DI", "-DI", "__orig_order"], errors="ignore")


def _indicator_pipeline(df_in: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if df_in is None or df_in.empty:
        return df_in

    d = df_in

    # Ensure ASC ts for all rolling indicators
    if "ts" in d.columns:
        d = d.sort_values("ts").reset_index(drop=True)

    # Indicator order matters for derived features.
    steps: List[Tuple[str, Callable[[pd.DataFrame], pd.DataFrame]]] = [
        ("bollinger_bands", lambda x: ta.add_bollinger_bands(x)),
        ("aroon", lambda x: ta.add_aroon(x)),
        ("atr", lambda x: ta.add_atr(x)),
        ("cci", lambda x: ta.add_cci(x)),
        ("cmo", lambda x: ta.add_cmo(x)),
        ("td9_counts", lambda x: ta.add_td9_counts(x)),
        ("mfi", lambda x: ta.add_mfi(x)),
        ("stochastic", lambda x: ta.add_stochastic_oscillator(x)),
        ("ao", lambda x: ta.add_awesome_oscillator(x)),
        ("donchian", lambda x: ta.add_donchian_channels(x)),
        ("volume_metrics", lambda x: ta.add_volume_metrics(x)),
        ("keltner", lambda x: ta.add_keltner_channels(x)),
        ("cmf", lambda x: ta.add_chaikin_money_flow(x)),
        ("engulfing", lambda x: ta.add_engulfing_patterns(x)),
        ("obv", lambda x: ta.add_obv(x)),
    ]

    if ENABLE_PSAR:
        steps.append(("psar", lambda x: ta.add_parabolic_sar_signals(x)))

    # Expanded pack
    steps.extend(
        [
            ("roc", lambda x: ta.add_roc(x)),
            ("rsi", lambda x: ta.compute_wilders_rsi(x)),
            ("stoch_rsi", lambda x: ta.add_stoch_rsi(x)),
            ("macd", lambda x: ta.add_macd(x)),
            ("ema_pack", lambda x: ta.add_ema_pack(x, periods=(9, 21, 50), slope_lookback=3)),
            ("vwap_features", lambda x: ta.add_vwap_features(x, reset_daily=True, tz="US/Eastern")),
            ("tsi", lambda x: ta.add_tsi(x, long=25, short=13, signal=7)),
            ("force_index", lambda x: ta.add_force_index(x, ema_period=13)),
            ("rvol", lambda x: ta.add_relative_volume(x, window=20)),
            ("chop", lambda x: ta.add_choppiness_index(x, window=14)),
            ("band_position", lambda x: ta.add_band_position_metrics(x)),
            ("squeeze", lambda x: ta.add_squeeze_flags(x)),
            ("candle_shapes", lambda x: ta.add_candle_shape_metrics(x)),
            ("adx_clean", lambda x: ta.add_adx_clean(x, window=14)),
            ("momentum_flags", lambda x: ta.add_momentum_flags(x)),
            ("williams_r", lambda x: ta.add_williams_r(x)),
            ("vortex", lambda x: ta.add_vortex_indicator(x)),
            ("ppo", lambda x: ta.add_ppo(x)),
        ]
    )

    if ENABLE_SDC:
        steps.append(("sdc", lambda x: ta.add_sdc_indicator(x, window=50, dev_up=1.5, dev_dn=1.5)))

    steps.append(("trix", lambda x: ta.add_trix(x)))

    for name, fn in steps:
        try:
            out = fn(d)
            if out is None:
                print(f"[{ticker}] indicator {name} returned None")
                continue
            d = out
        except Exception as exc:
            print(f"[{ticker}] indicator {name} failed: {exc}")

    if "ts" in d.columns:
        d = d.sort_values("ts").reset_index(drop=True)

    return _drop_bad_cols(d)


async def _apply_indicators_async(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if not APPLY_INDICATORS:
        return df
    if _IND_EXECUTOR is not None:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_IND_EXECUTOR, _indicator_pipeline, df, ticker)
    return _indicator_pipeline(df, ticker)


# ───────────────────────── DB writer ─────────────────────────
async def _db_writer_worker(q: asyncio.Queue, worker_id: int):
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

            # Chunk writes to keep statement sizes sane
            for start in range(0, len(df), UPSERT_BATCH_ROWS):
                chunk = df.iloc[start : start + UPSERT_BATCH_ROWS]
                chunk = _drop_bad_cols(chunk)

                # Use ts_utc as the conflict target (canonical)
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
async def _compute_worker(compute_q: asyncio.Queue, db_q: asyncio.Queue, worker_id: int):
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


# ───────────────────────── backfill ─────────────────────────
async def backfill_one_ticker(
    *,
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    ticker: str,
    compute_q: asyncio.Queue,
    pages: int = DEFAULT_PAGES,
    count: int = DEFAULT_COUNT,
    restorationType: int = 0,
) -> Dict[str, Any]:
    """Backfill one ticker backwards from now."""

    ticker_id = trading.ticker_to_id_map.get(ticker)
    if not ticker_id:
        return {"ticker": ticker, "error": "unknown ticker_id"}

    anchor = int(time.time())

    buffer_blocks: List[np.ndarray] = []
    buffer_nrows = 0
    overlap_df: Optional[pd.DataFrame] = None

    min_ts: Optional[int] = None
    max_ts: Optional[int] = None
    last_oldest: Optional[int] = None
    pages_used = 0

    BASE_COLS = ["ts", "ts_utc", "o", "c", "h", "l", "v", "vwap", "ticker", "timespan"]

    async def _flush() -> int:
        nonlocal buffer_blocks, buffer_nrows, overlap_df

        if buffer_nrows <= 0:
            return 0

        arr = np.concatenate(buffer_blocks, axis=0) if len(buffer_blocks) > 1 else buffer_blocks[0]
        buffer_blocks = []
        buffer_nrows = 0

        # Columns: ts,o,c,h,l,a,v,vwap
        ts_epoch = arr[:, 0].astype(np.int64)

        df_new = pd.DataFrame(
            {
                "ts": pd.to_datetime(ts_epoch, unit="s", utc=True),
                "o": arr[:, 1].astype(np.float64),
                "c": arr[:, 2].astype(np.float64),
                "h": arr[:, 3].astype(np.float64),
                "l": arr[:, 4].astype(np.float64),
                "v": arr[:, 6].astype(np.int64),
                "vwap": arr[:, 7].astype(np.float64),
            }
        )

        # Canonical ts_utc (used for upsert key)
        df_new["ts_utc"] = df_new["ts"]

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
            return 0

        # Combine overlap (newer) so earliest rows in that newer chunk get recomputed
        if OVERLAP_BACKFILL and overlap_df is not None and not overlap_df.empty:
            # Ensure base cols exist in overlap
            for c in BASE_COLS:
                if c not in overlap_df.columns:
                    overlap_df[c] = np.nan
            df = pd.concat([df_new[BASE_COLS], overlap_df[BASE_COLS]], ignore_index=True)
            df = (
                df.drop_duplicates(subset=["ts_utc"], keep="last")
                .sort_values("ts_utc")
                .reset_index(drop=True)
            )
        else:
            df = df_new

        # Meta for logging
        meta = None
        if LOG_UPSERTS:
            meta = (ticker, df["ts_utc"].min(), df["ts_utc"].max(), int(len(df)))

        # Push to compute queue
        await compute_q.put((df, ticker, meta))

        # Carry forward overlap (earliest rows of the NEWER chunk)
        if OVERLAP_BACKFILL and INDICATOR_WARMUP_ROWS > 0:
            overlap_df = df_new.iloc[:INDICATOR_WARMUP_ROWS].copy()
            overlap_df = overlap_df[BASE_COLS].copy()
        else:
            overlap_df = None

        return int(len(df_new))

    # Page loop
    for i in range(pages):
        url = (
            "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
            f"?type={TIMESPAN}&count={count}&timestamp={anchor}"
            f"&restorationType={restorationType}&tickerId={ticker_id}&hasMore=true"
        )

        try:
            data = await _fetch_page(session, sem, url)
        except Exception as exc:
            return {"ticker": ticker, "error": f"fetch failed: {repr(exc)}", "pages_used": i + 1}

        raw_rows = (data[0] or {}).get("data") if isinstance(data, list) and data else None
        if not raw_rows:
            break

        page_arr = _rows_to_numpy_fast(raw_rows)
        if page_arr.size == 0:
            break

        # Track oldest/newest timestamps on this page
        ts_page = page_arr[:, 0]
        page_oldest = int(np.nanmin(ts_page))
        page_newest = int(np.nanmax(ts_page))

        pages_used = i + 1
        if min_ts is None or page_oldest < min_ts:
            min_ts = page_oldest
        if max_ts is None or page_newest > max_ts:
            max_ts = page_newest

        # Stop if API stops moving backward
        if last_oldest is not None and page_oldest >= last_oldest:
            break
        last_oldest = page_oldest
        anchor = page_oldest - 1

        buffer_blocks.append(page_arr)
        buffer_nrows += page_arr.shape[0]

        if buffer_nrows >= FLUSH_ROWS:
            await _flush()

    if buffer_nrows:
        await _flush()

    result: Dict[str, Any] = {"ticker": ticker, "pages_used": pages_used}
    if min_ts is not None and max_ts is not None:
        result["start"] = pd.to_datetime(min_ts, unit="s", utc=True)
        result["end"] = pd.to_datetime(max_ts, unit="s", utc=True)
    return result


async def run_backfill(
    tickers: List[str],
    *,
    semaphore_limit: int = MAX_INFLIGHT_REQUESTS,
    pages: int = DEFAULT_PAGES,
    count: int = DEFAULT_COUNT,
    restorationType: int = 0,
) -> List[Dict[str, Any]]:
    if isinstance(tickers, str):
        tickers = [tickers]

    await db.connect()

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

    results: List[Dict[str, Any]] = []
    done = 0
    total = len(tickers)

    async with aiohttp.ClientSession(
        headers=headers,
        connector=aiohttp.TCPConnector(limit=semaphore_limit, limit_per_host=semaphore_limit, ttl_dns_cache=300),
    ) as session:

        async def _ticker_worker() -> None:
            nonlocal done
            while True:
                try:
                    tkr = ticker_q.get_nowait()
                except asyncio.QueueEmpty:
                    return

                try:
                    r = await backfill_one_ticker(
                        session=session,
                        sem=sem,
                        ticker=tkr,
                        compute_q=compute_q,
                        pages=pages,
                        count=count,
                        restorationType=restorationType,
                    )
                    results.append(r)
                except Exception as exc:
                    results.append({"ticker": tkr, "error": repr(exc)})

                done += 1
                if done % 5 == 0 or done == total:
                    print(
                        f"completed {done}/{total} | compute_q={compute_q.qsize()}/{COMPUTE_QUEUE_MAXSIZE} db_q={db_q.qsize()}/{DB_QUEUE_MAXSIZE}"
                    )

                ticker_q.task_done()

        workers = [asyncio.create_task(_ticker_worker()) for _ in range(max(1, min(MAX_TICKER_TASKS, total)))]
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

    # Shutdown executor cleanly
    if _IND_EXECUTOR is not None:
        _IND_EXECUTOR.shutdown(wait=True)

    return results


# ───────────────────────── tail mode ─────────────────────────
async def _get_last_ts_utc_map(tickers: List[str]) -> Dict[str, Optional[pd.Timestamp]]:
    """Fetch last ts_utc per ticker for this timespan."""
    if not tickers:
        return {}

    # NOTE: PolygonOptions wrapper likely has `fetch()` which returns list[Record].
    # We'll do one query for all tickers to avoid N round-trips.
    query = f"""
        SELECT ticker, max(ts_utc) AS last_ts
        FROM {TABLE_NAME}
        WHERE timespan = $1 AND ticker = ANY($2)
        GROUP BY ticker
    """

    rows = await db.fetch(query, TIMESPAN, tickers)

    out: Dict[str, Optional[pd.Timestamp]] = {t: None for t in tickers}
    for r in rows or []:
        try:
            out[str(r["ticker"]) if isinstance(r, dict) else str(r[0])] = (r["last_ts"] if isinstance(r, dict) else r[1])
        except Exception:
            continue
    return out


async def _tail_one_ticker(
    *,
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    ticker: str,
    last_ts: Optional[pd.Timestamp],
    tail_count: int,
) -> Tuple[str, Optional[pd.Timestamp], int]:
    """Fetch last `tail_count` bars, compute indicators, upsert last `TAIL_UPSERT_ROWS` bars."""

    ticker_id = trading.ticker_to_id_map.get(ticker)
    if not ticker_id:
        return ticker, last_ts, 0

    url = (
        "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
        f"?type={TIMESPAN}&count={tail_count}&timestamp={int(time.time())}"
        f"&restorationType=0&tickerId={ticker_id}&hasMore=true"
    )

    data = await _fetch_page(session, sem, url)
    raw_rows = (data[0] or {}).get("data") if isinstance(data, list) and data else None
    if not raw_rows:
        return ticker, last_ts, 0

    arr = _rows_to_numpy_fast(raw_rows)
    if arr.size == 0:
        return ticker, last_ts, 0

    ts_epoch = arr[:, 0].astype(np.int64)

    df = pd.DataFrame(
        {
            "ts": pd.to_datetime(ts_epoch, unit="s", utc=True),
            "o": arr[:, 1].astype(np.float64),
            "c": arr[:, 2].astype(np.float64),
            "h": arr[:, 3].astype(np.float64),
            "l": arr[:, 4].astype(np.float64),
            "v": arr[:, 6].astype(np.int64),
            "vwap": arr[:, 7].astype(np.float64),
        }
    )

    df["ts_utc"] = df["ts"]
    df["ticker"] = ticker
    df["timespan"] = TIMESPAN

    df = (
        df.drop_duplicates(subset=["ts_utc"], keep="last")
        .sort_values("ts_utc")
        .reset_index(drop=True)
    )

    if df.empty:
        return ticker, last_ts, 0

    newest = df["ts_utc"].max()

    # If nothing new, still upsert a small tail to keep shifted/rolling features consistent
    n_new = 0
    if last_ts is not None:
        n_new = int((df["ts_utc"] > last_ts).sum())
    else:
        n_new = int(len(df))

    # Compute indicators on the full tail window (cheap; avoids DB reads).
    out = await _apply_indicators_async(df, ticker) if APPLY_INDICATORS else df

    # Upsert only the last N rows to reduce DB load
    out_tail = out.iloc[-TAIL_UPSERT_ROWS:].copy() if len(out) > TAIL_UPSERT_ROWS else out

    await db.batch_upsert_dataframe(
        out_tail,
        table_name=TABLE_NAME,
        unique_columns=["ticker", "timespan", "ts_utc"],
    )

    return ticker, newest, n_new


async def run_tail(
    tickers: List[str],
    *,
    semaphore_limit: int = MAX_INFLIGHT_REQUESTS,
    tail_count: int = TAIL_COUNT,
    poll_seconds: float = POLL_SECONDS,
) -> None:
    if isinstance(tickers, str):
        tickers = [tickers]

    await db.connect()

    last_map = await _get_last_ts_utc_map(tickers)

    sem = asyncio.Semaphore(semaphore_limit)
    headers = generate_webull_headers(access_token=ACCESS_TOKEN)

    async with aiohttp.ClientSession(
        headers=headers,
        connector=aiohttp.TCPConnector(limit=semaphore_limit, limit_per_host=semaphore_limit, ttl_dns_cache=300),
    ) as session:
        while True:
            t0 = time.perf_counter()

            # Fan out tickers with a bounded number of tasks
            q: asyncio.Queue = asyncio.Queue()
            for t in tickers:
                q.put_nowait(t)

            async def _worker() -> None:
                while True:
                    try:
                        tkr = q.get_nowait()
                    except asyncio.QueueEmpty:
                        return

                    try:
                        prev = last_map.get(tkr)
                        tkr2, newest, n_new = await _tail_one_ticker(
                            session=session,
                            sem=sem,
                            ticker=tkr,
                            last_ts=prev,
                            tail_count=tail_count,
                        )
                        last_map[tkr2] = newest
                        if n_new:
                            print(f"[tail] {tkr2} new_rows={n_new} newest={newest}")
                    except Exception as exc:
                        print(f"[tail] {tkr} failed: {repr(exc)}")
                    finally:
                        q.task_done()

            workers = [asyncio.create_task(_worker()) for _ in range(max(1, min(MAX_TICKER_TASKS, len(tickers))))]
            await asyncio.gather(*workers)

            # Sleep to next poll
            elapsed = time.perf_counter() - t0
            sleep_for = max(1.0, poll_seconds - elapsed)
            await asyncio.sleep(sleep_for)


# ───────────────────────── CLI ─────────────────────────

def _parse_tickers(args: argparse.Namespace) -> List[str]:
    if args.tickers:
        return [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    if args.tickers_file:
        p = args.tickers_file
        with open(p, "r", encoding="utf-8") as f:
            out = []
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                out.append(s.upper())
            return out
    return []


def main() -> None:
    ap = argparse.ArgumentParser(description="Fast Webull M1 candle ingest (backfill and/or tail)")
    ap.add_argument("--mode", choices=["backfill", "tail", "backfill+tail"], default="backfill")
    ap.add_argument("--tickers", help="Comma separated tickers (e.g., SPY,QQQ,AAPL)")
    ap.add_argument("--tickers-file", help="Path to file containing tickers (one per line)")

    # Backfill
    ap.add_argument("--pages", type=int, default=DEFAULT_PAGES)
    ap.add_argument("--count", type=int, default=DEFAULT_COUNT)
    ap.add_argument("--restorationType", type=int, default=0)

    # Tail
    ap.add_argument("--tail-count", type=int, default=TAIL_COUNT)
    ap.add_argument("--poll-seconds", type=float, default=POLL_SECONDS)

    # Concurrency
    ap.add_argument("--semaphore", type=int, default=MAX_INFLIGHT_REQUESTS)

    args = ap.parse_args()

    tickers = most_active_tickers
    if not tickers:
        raise SystemExit("No tickers provided. Use --tickers or --tickers-file")

    async def _run() -> None:
        if args.mode in ("backfill", "backfill+tail"):
            res = await run_backfill(
                tickers,
                semaphore_limit=args.semaphore,
                pages=max(1, args.pages),
                count=max(10, args.count),
                restorationType=args.restorationType,
            )
            # Basic summary
            ok = sum(1 for r in res if not r.get("error"))
            err = sum(1 for r in res if r.get("error"))
            print(f"backfill done: ok={ok} err={err}")

        if args.mode in ("tail", "backfill+tail"):
            await run_tail(
                tickers,
                semaphore_limit=args.semaphore,
                tail_count=max(50, args.tail_count),
                poll_seconds=max(5.0, args.poll_seconds),
            )

    asyncio.run(_run())


if __name__ == "__main__":
    main()
