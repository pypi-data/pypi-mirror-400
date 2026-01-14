#!/usr/bin/env python3
import sys
import asyncio
import logging
import math
import re
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
db = PolygonOptions()
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Iterable, List, Tuple

import aiohttp
import numpy as np
import pandas as pd
from numba import njit

# ── Project imports (adjust paths as needed)
project_dir = str(Path(__file__).resolve().parents[2])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from script_helpers import generate_webull_headers  # noqa: E402
from fudstop4.apis.webull.webull_ta import WebullTA  # noqa: E402
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers  # noqa: E402


# -----------------------------------------------------------------------------
# Numba-safe MACD (adapter avoids reflected-list issues)
# -----------------------------------------------------------------------------
@njit(cache=True)
def ema_njit(prices: np.ndarray, period: int) -> np.ndarray:
    """
    Exponential Moving Average (EMA). Pure ndarray in/out, Numba-friendly.
    """
    multiplier = 2.0 / (period + 1)
    ema = np.empty(prices.size, dtype=np.float64)
    ema[0] = prices[0]
    for i in range(1, prices.size):
        ema[i] = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
    return ema


@njit(cache=True)
def _macd_core(
    closes: np.ndarray,
    fast_period: int,
    slow_period: int,
    signal_period: int,
):
    fast = ema_njit(closes, fast_period)
    slow = ema_njit(closes, slow_period)
    macd_line = fast - slow
    signal_line = ema_njit(macd_line, signal_period)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def macd_from_close(
    closes,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
):
    """
    Python adapter: accepts list/Series/array, converts to float64 ndarray,
    then calls the jitted core.
    """
    closes_arr = np.asarray(closes, dtype=np.float64)
    return _macd_core(closes_arr, fast_period, slow_period, signal_period)


# -----------------------------------------------------------------------------
# Timespan utilities
# -----------------------------------------------------------------------------
def timespan_to_seconds(timespan: str) -> int:
    """
    Supports: m1, m5, m15, m30, m60, m120, m240, d1 (and similar).
    """
    s = timespan.strip().lower()
    m = re.fullmatch(r"([mhdw])(\d+)", s)
    if not m:
        raise ValueError(f"Unrecognized timespan format: {timespan!r}")
    unit = m.group(1)
    n = int(m.group(2))

    if unit == "m":
        return 60 * n
    if unit == "h":
        return 3600 * n
    if unit == "d":
        return 86400 * n
    if unit == "w":
        return 604800 * n
    raise ValueError(f"Unsupported timespan unit: {unit!r}")


def sort_timespans_small_to_large(timespans: List[str]) -> List[str]:
    return sorted(timespans, key=timespan_to_seconds)


# -----------------------------------------------------------------------------
# Loose MACD synthesis logic
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class TfMacdMomentum:
    """
    A permissive description of "where MACD is leaning" on a timeframe.
    direction:
      - bullish: histogram rising (delta > 0)
      - bearish: histogram falling (delta < 0)
      - flat: delta ~= 0
    """
    direction: str              # "bullish" | "bearish" | "flat"
    hist_now: float
    delta_per_bar: float        # simple delta or regression slope
    toward_zero: bool           # True when moving toward the zero-line (or near it)
    bars_to_zero: float         # estimated bars to reach zero when toward_zero, else inf
    time_to_zero_sec: float     # bars_to_zero * seconds_per_bar


@dataclass(frozen=True)
class SynthesisSegment:
    direction: str
    start_timespan: str
    end_timespan: str
    chain: Tuple[str, ...]
    chain_len: int
    toward_zero_count: int
    metrics: Dict[str, TfMacdMomentum]


def _linear_regression_slope(y: np.ndarray) -> float:
    y = np.asarray(y, dtype=np.float64)
    n = y.size
    if n < 2:
        return 0.0
    x = np.arange(n, dtype=np.float64)
    x = x - x.mean()
    yy = y - y.mean()
    denom = float(np.dot(x, x))
    if denom <= 0.0:
        return 0.0
    return float(np.dot(x, yy) / denom)


def compute_tf_momentum(
    hist: np.ndarray,
    ts_seconds: int,
    *,
    trend_lookback: int = 2,
    eps: float = 1e-12,
    zero_band_mult: float = 0.10,
) -> Optional[TfMacdMomentum]:
    """
    Very permissive momentum metric.

    - direction defaults to sign of last delta (trend_lookback=2).
      If trend_lookback > 2, uses a regression slope on the last N points.

    - toward_zero is True when:
        * hist is in a small "near zero" band, OR
        * hist < 0 and trend > 0 (bullish pre-cross pressure), OR
        * hist > 0 and trend < 0 (bearish pre-cross pressure)

    bars_to_zero only computed when toward_zero is True and trend magnitude is non-trivial.
    """
    hist = np.asarray(hist, dtype=np.float64)
    if hist.size < max(3, trend_lookback + 1):
        return None

    hist_now = float(hist[-1])

    if trend_lookback <= 2:
        trend = float(hist[-1] - hist[-2])
    else:
        trend = float(_linear_regression_slope(hist[-trend_lookback:]))

    if abs(trend) <= eps:
        direction = "flat"
    else:
        direction = "bullish" if trend > 0.0 else "bearish"

    # Adaptive "near zero" band based on recent histogram volatility.
    recent = hist[-min(20, hist.size):]
    recent_std = float(np.std(recent)) if recent.size >= 5 else float(np.std(hist))
    zero_band = max(eps, recent_std * float(zero_band_mult))

    near_zero = abs(hist_now) <= zero_band
    toward_zero = bool(
        near_zero
        or (hist_now < 0.0 and trend > 0.0)
        or (hist_now > 0.0 and trend < 0.0)
    )

    if toward_zero and abs(trend) > eps:
        bars_to_zero = abs(hist_now) / abs(trend)
        if not math.isfinite(bars_to_zero) or bars_to_zero < 0.0:
            bars_to_zero = float("inf")
    else:
        bars_to_zero = float("inf")

    time_to_zero_sec = float(bars_to_zero) * float(ts_seconds) if math.isfinite(bars_to_zero) else float("inf")

    return TfMacdMomentum(
        direction=direction,
        hist_now=hist_now,
        delta_per_bar=trend,
        toward_zero=toward_zero,
        bars_to_zero=float(bars_to_zero),
        time_to_zero_sec=float(time_to_zero_sec),
    )


def find_synthesis_segments(
    metrics_by_timespan: Dict[str, TfMacdMomentum],
    timespans_ordered: List[str],
    *,
    min_chain_len: int = 2,
) -> List[SynthesisSegment]:
    """
    Split ordered timespans into contiguous runs of identical direction.
    "flat" or missing breaks the chain.

    This matches your "continue on" behavior:
      - if m1 bullish and m5 bearish, chain doesn't start at m1
      - it starts at m5 if m15 is also bearish, etc.
    """
    segments: List[SynthesisSegment] = []
    curr_dir: Optional[str] = None
    curr_chain: List[str] = []

    def _finalize():
        nonlocal curr_dir, curr_chain
        if curr_dir and len(curr_chain) >= min_chain_len:
            seg_metrics = {ts: metrics_by_timespan[ts] for ts in curr_chain}
            toward_zero_count = sum(1 for ts in curr_chain if seg_metrics[ts].toward_zero)
            segments.append(
                SynthesisSegment(
                    direction=curr_dir,
                    start_timespan=curr_chain[0],
                    end_timespan=curr_chain[-1],
                    chain=tuple(curr_chain),
                    chain_len=len(curr_chain),
                    toward_zero_count=toward_zero_count,
                    metrics=seg_metrics,
                )
            )
        curr_dir = None
        curr_chain = []

    for ts in timespans_ordered:
        m = metrics_by_timespan.get(ts)
        if m is None or m.direction == "flat":
            _finalize()
            continue

        if curr_dir is None:
            curr_dir = m.direction
            curr_chain = [ts]
            continue

        if m.direction == curr_dir:
            curr_chain.append(ts)
        else:
            _finalize()
            curr_dir = m.direction
            curr_chain = [ts]

    _finalize()
    return segments


def pick_first_segment(segments: List[SynthesisSegment]) -> Optional[SynthesisSegment]:
    """
    First segment in timespan order (earliest start).
    """
    if not segments:
        return None
    return segments[0]


def pick_best_segment(segments: List[SynthesisSegment]) -> Optional[SynthesisSegment]:
    """
    Optional: "best" segment for ranking.
    Prefers:
      - longer chain
      - more toward-zero frames (pre-cross pressure)
      - sooner-to-zero at the start (when finite)
    """
    if not segments:
        return None

    def _score(seg: SynthesisSegment) -> float:
        start = seg.metrics[seg.start_timespan]
        ttc = start.time_to_zero_sec
        ttc_penalty = (ttc / 60.0) if math.isfinite(ttc) else 1e9
        return seg.chain_len * 1000.0 + seg.toward_zero_count * 10.0 - ttc_penalty

    return max(segments, key=_score)


# -----------------------------------------------------------------------------
# Scanner (aiohttp + Webull mapping)
# -----------------------------------------------------------------------------
class MacdSynthesisScanner:
    """
    Fetch Webull mini-charts, compute MACD, then find the earliest synthesis run
    across timespans for each ticker.
    """

    DEFAULT_TIMESPANS = ["m1", "m5", "m30", "m15", "m60", "d1", "m120", "m240"]

    def __init__(
        self,
        *,
        ta_client,
        tickers_provider: Iterable[str],
        timespans: Optional[List[str]] = None,
        sem_limit: int = 75,
        connector_limit: int = 105,
        retries: int = 3,
        retry_delay: float = 1.0,
        logger: Optional[logging.Logger] = None,
    ):
        self.ta = ta_client
        self.tickers_provider = list(tickers_provider)

        self.sem = asyncio.Semaphore(sem_limit)
        self.connector_limit = connector_limit
        self.retries = retries
        self.retry_delay = retry_delay
        self.timespans = timespans or list(self.DEFAULT_TIMESPANS)

        self._ticker_id_cache: Dict[str, int] = {}
        self._ticker_lock = asyncio.Lock()
        self._session: Optional[aiohttp.ClientSession] = None

        self.log = logger or logging.getLogger(__name__)
        if not self.log.handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.connector_limit)
        self._session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()
            self._session = None

    async def _get_ticker_id(self, ticker: str) -> Optional[int]:
        async with self._ticker_lock:
            if ticker in self._ticker_id_cache:
                return self._ticker_id_cache[ticker]
            tid = getattr(self.ta, "ticker_to_id_map", {}).get(ticker)
            if tid:
                self._ticker_id_cache[ticker] = tid
                return tid
            return None

    async def _fetch_with_retries(self, url: str) -> dict:
        assert self._session is not None
        for attempt in range(self.retries):
            try:
                async with self._session.get(
                    url,
                    headers=generate_webull_headers(),
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    resp.raise_for_status()
                    return await resp.json()
            except Exception as e:
                self.log.warning("Attempt %d/%d failed: %s", attempt + 1, self.retries, e)
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise

    async def _fetch_df_for_timespan(self, ticker: str, timespan: str) -> Optional[pd.DataFrame]:
        """
        Fetch Webull mini-chart data, parse DataFrame, attach MACD columns.
        """
        assert self._session is not None, "Session not initialized"
        try:
            async with self.sem:
                ticker_id = await self._get_ticker_id(ticker)
                if not ticker_id:
                    return None

                url = (
                    "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
                    f"?type={timespan}&count=50&restorationType=1&extendTrading=0&loadFactor=1"
                    f"&tickerId={ticker_id}"
                )
                data_json = await self._fetch_with_retries(url)

            if not data_json or not isinstance(data_json, list) or not data_json[0].get("data"):
                return None

            raw_data = data_json[0]["data"]
            df = pd.DataFrame(
                [row.split(",") for row in raw_data],
                columns=["ts", "o", "c", "h", "l", "a", "v", "vwap"],
            )

            df["ts"] = pd.to_datetime(pd.to_numeric(df["ts"], errors="coerce"), unit="s", utc=True)
            df = df.iloc[::-1].reset_index(drop=True)

            numeric_cols = ["o", "c", "h", "l", "v", "vwap"]
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
            df = df.drop(columns=["a"], errors="ignore")

            closes = df["c"].to_numpy(np.float64, copy=False)
            macd_line, signal_line, hist = macd_from_close(closes)

            df["macd_value"] = macd_line
            df["macd_signal"] = signal_line
            df["macd_hist"] = hist
            df["timespan"] = timespan
            df["ticker"] = ticker
            return df

        except Exception as e:
            self.log.warning("Fetch failed for %s [%s]: %s", ticker, timespan, e)
            return None

    async def _scan_one_ticker(
        self,
        ticker: str,
        timespans_ordered: List[str],
        *,
        min_chain_len: int,
        trend_lookback: int,
        zero_band_mult: float,
    ) -> Optional[dict]:
        """
        Fetch all timespans for one ticker, detect synthesis segments,
        return a flat row describing the earliest segment (and also the best segment).
        """
        tasks = [asyncio.create_task(self._fetch_df_for_timespan(ticker, ts)) for ts in timespans_ordered]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        dfs_by_timespan: Dict[str, pd.DataFrame] = {}
        for ts, res in zip(timespans_ordered, results):
            if isinstance(res, Exception):
                continue
            if res is None or res.empty:
                continue
            dfs_by_timespan[ts] = res

        if not dfs_by_timespan:
            return None

        metrics_by_ts: Dict[str, TfMacdMomentum] = {}
        dir_map_parts: List[str] = []
        for ts in timespans_ordered:
            df = dfs_by_timespan.get(ts)
            if df is None or df.empty or "macd_hist" not in df.columns:
                dir_map_parts.append(f"{ts}:NA")
                continue

            hist = df["macd_hist"].to_numpy(np.float64, copy=False)
            m = compute_tf_momentum(
                hist,
                timespan_to_seconds(ts),
                trend_lookback=trend_lookback,
                zero_band_mult=zero_band_mult,
            )
            if m is None:
                dir_map_parts.append(f"{ts}:NA")
                continue

            metrics_by_ts[ts] = m
            dshort = "B" if m.direction == "bullish" else ("S" if m.direction == "bearish" else "F")
            zshort = "Z" if m.toward_zero else ""
            dir_map_parts.append(f"{ts}:{dshort}{zshort}")

        segments = find_synthesis_segments(metrics_by_ts, timespans_ordered, min_chain_len=min_chain_len)
        if not segments:
            return None

        first_seg = pick_first_segment(segments)
        best_seg = pick_best_segment(segments)

        assert first_seg is not None and best_seg is not None

        def _seg_to_fields(prefix: str, seg: SynthesisSegment) -> Dict[str, object]:
            fields: Dict[str, object] = {
                f"{prefix}_direction": seg.direction,
                f"{prefix}_start_timespan": seg.start_timespan,
                f"{prefix}_end_timespan": seg.end_timespan,
                f"{prefix}_chain": " > ".join(seg.chain),
                f"{prefix}_chain_len": seg.chain_len,
                f"{prefix}_toward_zero_count": seg.toward_zero_count,
            }
            # Include compact per-timespan metrics for the segment
            for ts in seg.chain:
                m = seg.metrics[ts]
                fields[f"{prefix}_{ts}_hist"] = m.hist_now
                fields[f"{prefix}_{ts}_delta"] = m.delta_per_bar
                fields[f"{prefix}_{ts}_mins_to_zero"] = (m.time_to_zero_sec / 60.0) if math.isfinite(m.time_to_zero_sec) else math.inf
            return fields

        row = {
            "ticker": ticker,
            "dir_map": " | ".join(dir_map_parts),
        }
        row.update(_seg_to_fields("first", first_seg))
        row.update(_seg_to_fields("best", best_seg))
        return row

    async def scan_once(
        self,
        *,
        min_chain_len: int = 2,
        trend_lookback: int = 2,
        zero_band_mult: float = 0.10,
        limit_tickers: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Scan all tickers, return a ranked DataFrame of synthesis hits.

        min_chain_len:
          - 2 means "any synthesis" (two consecutive timespans align)
        trend_lookback:
          - 2 means use last-bar histogram delta (loose, lots of hits)
          - 5 means smoother slope (stricter)
        zero_band_mult:
          - larger means bigger "near zero" zone => more toward_zero flags
        """
        timespans_ordered = sort_timespans_small_to_large(list(self.timespans))

        tickers = self.tickers_provider
        if limit_tickers is not None:
            tickers = tickers[: int(limit_tickers)]

        tasks = [
            asyncio.create_task(
                self._scan_one_ticker(
                    ticker=t,
                    timespans_ordered=timespans_ordered,
                    min_chain_len=min_chain_len,
                    trend_lookback=trend_lookback,
                    zero_band_mult=zero_band_mult,
                )
            )
            for t in tickers
        ]
        rows = await asyncio.gather(*tasks, return_exceptions=True)

        clean_rows: List[dict] = []
        for r in rows:
            if isinstance(r, Exception) or r is None:
                continue
            clean_rows.append(r)

        if not clean_rows:
            return pd.DataFrame(
                columns=[
                    "ticker",
                    "dir_map",
                    "first_direction",
                    "first_start_timespan",
                    "first_end_timespan",
                    "first_chain",
                    "first_chain_len",
                ]
            )

        df = pd.DataFrame(clean_rows)

        # Rank: longer "first" chain first, then earlier start (smaller seconds).
        df["_first_start_sec"] = df["first_start_timespan"].apply(timespan_to_seconds)
        df = df.sort_values(
            ["first_chain_len", "_first_start_sec"],
            ascending=[False, True],
        ).drop(columns=["_first_start_sec"]).reset_index(drop=True)

        return df


async def main():
    await db.connect()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    ta = WebullTA()
    tickers = list(most_active_tickers)

    scanner = MacdSynthesisScanner(
        ta_client=ta,
        tickers_provider=tickers,
        timespans=MacdSynthesisScanner.DEFAULT_TIMESPANS,
        sem_limit=75,
        connector_limit=105,
        retries=3,
        retry_delay=1.0,
    )

    async with scanner:
        hits = await scanner.scan_once(
            min_chain_len=2,      # "any synthesis"
            trend_lookback=2,     # very loose (uses last histogram delta)
            zero_band_mult=0.10,
            limit_tickers=None,   # set to an int to sanity-test quickly
        )

    if hits.empty:
        print("No synthesis hits.")
        return

    await db.batch_upsert_dataframe(hits, table_name='macd_synthesis', unique_columns=['ticker'])

if __name__ == "__main__":
    asyncio.run(main())
