#!/usr/bin/env python3
"""
Builds a 1-row-per-ticker live table (candle_analysis_live) with full indicators.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Iterable, List, Optional, Tuple

import aiohttp
import numpy as np
import pandas as pd
from dotenv import load_dotenv

from fudstop4.apis._ta.ta_sdk import FudstopTA
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_trading import WebullTrading
from fudstop4.apis.helpers import generate_webull_headers
from fudstop4._markets.list_sets.ticker_lists import most_active_tight_spread_tickers

load_dotenv()

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
TIMESPAN = os.getenv("TIMESPAN", "m1")
TABLE_NAME = os.getenv("CANDLE_LIVE_TABLE", "candle_analysis_live")

FETCH_COUNT = int(os.getenv("LIVE_FETCH_COUNT", "80"))
MAX_INFLIGHT_REQUESTS = int(os.getenv("MAX_INFLIGHT_REQUESTS", "120"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
REQUEST_RETRIES = int(os.getenv("REQUEST_RETRIES", "3"))
RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "0.25"))

ONLY_CLOSED_CANDLES = os.getenv("ONLY_CLOSED_CANDLES", "true").lower() in ("1", "true", "yes")
RUN_FOREVER = os.getenv("RUN_FOREVER", "false").lower() in ("1", "true", "yes")
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "15"))

INDICATORS_IN_THREADS = os.getenv("INDICATORS_IN_THREADS", "true").lower() in ("1", "true", "yes")
DEFAULT_IND_WORKERS = min(8, (os.cpu_count() or 4))
INDICATOR_WORKERS = int(os.getenv("INDICATOR_WORKERS", str(DEFAULT_IND_WORKERS)))

ENABLE_PSAR = os.getenv("ENABLE_PSAR", "false").lower() in ("1", "true", "yes")
ENABLE_SDC = os.getenv("ENABLE_SDC", "true").lower() in ("1", "true", "yes")

SPAN_SECONDS = {
    "m1": 60,
    "m5": 300,
    "m15": 900,
    "m30": 1800,
    "m60": 3600,
    "m120": 7200,
    "m240": 14400,
    "d1": 86400,
}

try:
    import orjson  # type: ignore

    _json_loads = orjson.loads
except Exception:  # pragma: no cover
    import json

    _json_loads = json.loads


def _coerce_float(value: Any) -> float:
    if value in (None, "--", "", "—"):
        return 0.0
    try:
        return float(str(value).replace("%", "").strip())
    except Exception:
        return 0.0


def _coerce_int(value: Any) -> int:
    if value in (None, "--", "", "—"):
        return 0
    try:
        return int(float(str(value).strip()))
    except Exception:
        return 0


def _coerce_bool(value: Any) -> bool:
    if value in (None, "--", "", "—"):
        return False
    if isinstance(value, str):
        return value.strip().lower() not in ("0", "false", "no", "none", "")
    return bool(value)


def _coerce_str(value: Any) -> str:
    return "" if value is None else str(value)


class WebullMiniCandles:
    def __init__(self, raw_rows: Iterable[str], *, ticker: str, timespan: str):
        parsed = [
            {
                "ts": parts[0],
                "o": parts[1],
                "c": parts[2],
                "h": parts[3],
                "l": parts[4],
                "a": parts[5],
                "v": parts[6],
                "vwap": parts[7],
            }
            for row in raw_rows
            for parts in [row.split(",")]
            if len(parts) >= 8
        ]

        self.ts = [_coerce_int(i.get("ts")) for i in parsed]
        self.o = [_coerce_float(i.get("o")) for i in parsed]
        self.c = [_coerce_float(i.get("c")) for i in parsed]
        self.h = [_coerce_float(i.get("h")) for i in parsed]
        self.l = [_coerce_float(i.get("l")) for i in parsed]
        self.v = [_coerce_int(i.get("v")) for i in parsed]
        self.vwap = [_coerce_float(i.get("vwap")) for i in parsed]

        self.ts_utc = [
            pd.to_datetime(v, unit="s", utc=True) if v else pd.NaT
            for v in self.ts
        ]

        self.ticker = [_coerce_str(ticker) for _ in parsed]
        self.timespan = [_coerce_str(timespan) for _ in parsed]

        self.data_dict = {
            "ts": self.ts_utc,
            "ts_utc": self.ts_utc,
            "o": self.o,
            "c": self.c,
            "h": self.h,
            "l": self.l,
            "v": self.v,
            "vwap": self.vwap,
            "ticker": self.ticker,
            "timespan": self.timespan,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class CandleAnalysisLive:
    def __init__(self, df: pd.DataFrame):
        rows = df.to_dict(orient="records")
        cols = list(df.columns)

        string_cols = {
            "ticker",
            "timespan",
            "upper_bb_trend",
            "lower_bb_trend",
            "sdc_signal",
            "psar_direction",
        }

        self.data_dict: Dict[str, List[Any]] = {}
        for col in cols:
            series = df[col]
            if pd.api.types.is_datetime64_any_dtype(series):
                self.data_dict[col] = [i.get(col) for i in rows]
            elif col in string_cols:
                self.data_dict[col] = [_coerce_str(i.get(col)) for i in rows]
            elif pd.api.types.is_bool_dtype(series):
                self.data_dict[col] = [_coerce_bool(i.get(col)) for i in rows]
            else:
                self.data_dict[col] = [_coerce_float(i.get(col)) for i in rows]

        self.as_dataframe = pd.DataFrame(self.data_dict)


ta = FudstopTA()
trading = WebullTrading()
db = PolygonOptions()

_IND_EXECUTOR: Optional[ThreadPoolExecutor] = None
if INDICATORS_IN_THREADS:
    _IND_EXECUTOR = ThreadPoolExecutor(max_workers=max(1, INDICATOR_WORKERS))


def _drop_bad_cols(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["+DI", "-DI", "__orig_order"], errors="ignore")


def _add_obv_fast(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy().sort_values("ts_utc").reset_index(drop=True)
    close = pd.to_numeric(d["c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    vol = pd.to_numeric(d.get("v", 0), errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    sign = np.sign(np.diff(close, prepend=close[0]))
    d["obv"] = np.cumsum(sign * vol)
    return d


def _add_engulfing_fast(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy().sort_values("ts_utc").reset_index(drop=True)
    o = pd.to_numeric(d["o"], errors="coerce").fillna(0.0)
    c = pd.to_numeric(d["c"], errors="coerce").fillna(0.0)
    h = pd.to_numeric(d["h"], errors="coerce").fillna(0.0)
    l = pd.to_numeric(d["l"], errors="coerce").fillna(0.0)

    p_o = o.shift(1)
    p_c = c.shift(1)
    p_h = h.shift(1)
    p_l = l.shift(1)

    prev_red = p_c < p_o
    prev_green = p_c > p_o
    cur_green = c > o
    cur_red = c < o
    range_engulf = (h > p_h) & (l < p_l)

    d["bullish_engulfing"] = (prev_red & cur_green & range_engulf & (o < p_c) & (c > p_o)).fillna(False)
    d["bearish_engulfing"] = (prev_green & cur_red & range_engulf & (o > p_c) & (c < p_o)).fillna(False)
    return d


def _add_sdc_fast(df: pd.DataFrame, window: int = 50, dev_up: float = 1.5, dev_dn: float = 1.5) -> pd.DataFrame:
    d = df.copy().sort_values("ts_utc").reset_index(drop=True)
    n = len(d)
    for col in ("linreg_slope", "linreg_intercept", "linreg_std", "sdc_upper", "sdc_lower"):
        if col not in d.columns:
            d[col] = np.nan
    if "sdc_signal" not in d.columns:
        d["sdc_signal"] = pd.Series([None] * n, dtype="object")

    if n < window:
        return d

    y = pd.to_numeric(d["c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    y2 = y * y

    w = int(window)
    x = np.arange(w, dtype=np.float64)
    sum_x = x.sum()
    sum_x2 = (x * x).sum()
    denom = (w * sum_x2 - sum_x * sum_x)
    if denom == 0:
        return d

    ones = np.ones(w, dtype=np.float64)
    sum_y = np.convolve(y, ones, mode="valid")
    sum_y2 = np.convolve(y2, ones, mode="valid")
    sum_xy = np.convolve(y, x[::-1], mode="valid")

    slope = (w * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / w
    sse = (
        sum_y2
        - 2.0 * slope * sum_xy
        - 2.0 * intercept * sum_y
        + (slope * slope) * sum_x2
        + 2.0 * slope * intercept * sum_x
        + w * (intercept * intercept)
    )
    sse = np.maximum(sse, 0.0)
    std = np.sqrt(sse / max(1, (w - 1)))

    base = slope * (w - 1) + intercept
    upper = base + dev_up * std
    lower = base - dev_dn * std

    idx = np.arange(w - 1, n)
    d.loc[idx, "linreg_slope"] = slope
    d.loc[idx, "linreg_intercept"] = intercept
    d.loc[idx, "linreg_std"] = std
    d.loc[idx, "sdc_upper"] = upper
    d.loc[idx, "sdc_lower"] = lower

    h = pd.to_numeric(d["h"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    l = pd.to_numeric(d["l"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    sig_vals = np.where(l[idx] > upper, "above_both", np.where(h[idx] < lower, "below_both", "BETWEEN"))
    sig = np.full(n, None, dtype=object)
    sig[idx] = sig_vals
    d["sdc_signal"] = sig
    return d


def _indicator_pipeline(df_in: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if df_in is None or df_in.empty:
        return df_in

    d = df_in.sort_values("ts_utc").reset_index(drop=True)

    steps: List[Tuple[str, Any]] = [
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
        ("engulfing", _add_engulfing_fast),
        ("obv", _add_obv_fast),
    ]

    if ENABLE_PSAR:
        steps.append(("psar", lambda x: ta.add_parabolic_sar_signals(x)))

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
        steps.append(("sdc", lambda x: _add_sdc_fast(x, window=50, dev_up=1.5, dev_dn=1.5)))

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

    if "ts_utc" in d.columns:
        d = d.sort_values("ts_utc").reset_index(drop=True)

    return _drop_bad_cols(d)


async def _apply_indicators_async(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if _IND_EXECUTOR is None:
        return _indicator_pipeline(df, ticker)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(_IND_EXECUTOR, _indicator_pipeline, df, ticker)


def _closed_cutoff(timespan: str, now_utc: pd.Timestamp) -> Optional[pd.Timestamp]:
    sec = SPAN_SECONDS.get(timespan)
    if not sec:
        return None
    epoch = int(now_utc.timestamp())
    floored = epoch - (epoch % sec)
    cutoff = floored - sec
    return pd.to_datetime(cutoff, unit="s", utc=True)


async def _fetch_page(session: aiohttp.ClientSession, sem: asyncio.Semaphore, url: str) -> Any:
    last_exc: Optional[Exception] = None
    for attempt in range(REQUEST_RETRIES):
        try:
            async with sem:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
                    if resp.status == 429:
                        retry_after = resp.headers.get("Retry-After")
                        delay = float(retry_after) if retry_after else (RETRY_BASE_DELAY * (2 ** attempt))
                        await asyncio.sleep(delay)
                        continue
                    resp.raise_for_status()
                    return await resp.json(loads=_json_loads)
        except Exception as exc:
            last_exc = exc
            if attempt < REQUEST_RETRIES - 1:
                await asyncio.sleep(RETRY_BASE_DELAY * (2 ** attempt))
    raise last_exc if last_exc else RuntimeError("request failed")


def _build_url(*, timespan: str, ticker_id: int, anchor: int, count: int) -> str:
    return (
        "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
        f"?type={timespan}&count={count}&timestamp={anchor}"
        f"&restorationType=0&tickerId={ticker_id}&hasMore=true"
    )


async def _process_ticker(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    ticker: str,
    *,
    timespan: str,
    count: int,
    only_closed: bool,
) -> Optional[pd.DataFrame]:
    ticker_id = trading.ticker_to_id_map.get(ticker)
    if not ticker_id:
        return None

    url = _build_url(timespan=timespan, ticker_id=ticker_id, anchor=int(time.time()), count=count)
    data = await _fetch_page(session, sem, url)
    raw_rows = (data[0] or {}).get("data") if isinstance(data, list) and data else None
    if not raw_rows:
        return None

    model = WebullMiniCandles(raw_rows, ticker=ticker, timespan=timespan)
    df = model.as_dataframe
    if df is None or df.empty:
        return None

    out = await _apply_indicators_async(df, ticker)
    out = _drop_bad_cols(out)
    if out is None or out.empty:
        return None

    if only_closed:
        cutoff = _closed_cutoff(timespan, pd.Timestamp.now(tz="UTC"))
        if cutoff is not None:
            out = out[out["ts_utc"] <= cutoff]
    if out.empty:
        return None

    out = out.sort_values("ts_utc").drop_duplicates(subset=["ts_utc"], keep="last")
    return out.iloc[[-1]].copy()


async def run_once(tickers: List[str]) -> int:
    await db.connect()

    sem = asyncio.Semaphore(MAX_INFLIGHT_REQUESTS)
    headers = generate_webull_headers(access_token=ACCESS_TOKEN)

    rows: List[pd.DataFrame] = []
    async with aiohttp.ClientSession(
        headers=headers,
        connector=aiohttp.TCPConnector(limit=MAX_INFLIGHT_REQUESTS, limit_per_host=MAX_INFLIGHT_REQUESTS, ttl_dns_cache=300),
    ) as session:
        tasks = [
            _process_ticker(
                session,
                sem,
                ticker,
                timespan=TIMESPAN,
                count=FETCH_COUNT,
                only_closed=ONLY_CLOSED_CANDLES,
            )
            for ticker in tickers
        ]
        for coro in asyncio.as_completed(tasks):
            try:
                df = await coro
                if df is not None and not df.empty:
                    rows.append(df)
            except Exception as exc:
                print(f"[live] ticker failed: {repr(exc)}")

    if not rows:
        await db.disconnect()
        return 0

    merged = pd.concat(rows, ignore_index=True)
    merged = merged.sort_values("ts_utc").drop_duplicates(subset=["ticker", "timespan"], keep="last").reset_index(drop=True)

    live_model = CandleAnalysisLive(merged)
    await db.batch_upsert_dataframe(
        live_model.as_dataframe,
        table_name=TABLE_NAME,
        unique_columns=["ticker", "timespan"],
    )

    await db.disconnect()
    return int(len(merged))


def _parse_tickers(args: argparse.Namespace) -> List[str]:
    if args.tickers:
        return [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    if args.tickers_file:
        with open(args.tickers_file, "r", encoding="utf-8") as f:
            return [line.strip().upper() for line in f if line.strip() and not line.startswith("#")]
    return [t.upper() for t in most_active_tight_spread_tickers]


def main() -> None:
    ap = argparse.ArgumentParser(description="Maintain candle_analysis_live (1 row per ticker)")
    ap.add_argument("--tickers", help="Comma separated tickers (e.g., SPY,QQQ,AAPL)")
    ap.add_argument("--tickers-file", help="Path to file containing tickers")
    ap.add_argument("--once", action="store_true", help="Run a single update and exit")
    args = ap.parse_args()

    tickers = _parse_tickers(args)
    if not tickers:
        raise SystemExit("No tickers provided.")

    async def _run() -> None:
        if args.once or not RUN_FOREVER:
            n = await run_once(tickers)
            print(f"[live] upserted {n} rows into {TABLE_NAME}")
            return

        while True:
            start = time.perf_counter()
            n = await run_once(tickers)
            elapsed = time.perf_counter() - start
            print(f"[live] upserted {n} rows in {elapsed:.2f}s")
            await asyncio.sleep(max(1.0, POLL_SECONDS - elapsed))

    asyncio.run(_run())


if __name__ == "__main__":
    main()
