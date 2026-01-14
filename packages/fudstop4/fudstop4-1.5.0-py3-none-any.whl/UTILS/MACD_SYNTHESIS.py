from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
import math
import re

import numpy as np
import pandas as pd


# ---------- timespan parsing ----------
def timespan_to_seconds(timespan: str) -> int:
    """
    Supports: 'm1', 'm5', 'm15', '1m', '5m', '15m', '1min', '1h', 'h1', '1d', 'd1', etc.
    """
    s = timespan.strip().lower()

    # webull-ish: m1, h1, d1
    m = re.fullmatch(r'([mhdw])(\d+)', s)
    if m:
        unit = m.group(1)
        n = int(m.group(2))
    else:
        # human-ish: 1m, 1min, 1h, 1d
        m = re.fullmatch(r'(\d+)\s*(min|m|h|d|w)', s)
        if not m:
            raise ValueError(f"Unrecognized timespan format: {timespan!r}")
        n = int(m.group(1))
        unit = m.group(2)
        if unit == "min":
            unit = "m"

    if unit == "m":
        return 60 * n
    if unit == "h":
        return 3600 * n
    if unit == "d":
        return 86400 * n
    if unit == "w":
        return 604800 * n
    raise ValueError(f"Unsupported unit in timespan: {timespan!r}")


def sort_timespans_small_to_large(timespans: List[str]) -> List[str]:
    return sorted(timespans, key=timespan_to_seconds)


# ---------- MACD cross metrics ----------
@dataclass(frozen=True)
class MacdCrossMetric:
    direction: str               # "bullish" or "bearish"
    hist_now: float
    slope_per_bar: float
    bars_to_cross: float
    time_to_cross_sec: float


def _linear_regression_slope(y: np.ndarray) -> float:
    """
    Slope of y vs x=[0..n-1] using least squares.
    Stable and fast for tiny windows.
    """
    y = np.asarray(y, dtype=np.float64)
    n = y.size
    if n < 2:
        return 0.0
    x = np.arange(n, dtype=np.float64)
    x -= x.mean()
    y = y - y.mean()
    denom = float(np.dot(x, x))
    if denom <= 0.0:
        return 0.0
    return float(np.dot(x, y) / denom)


def macd_pre_cross_metric(
    hist: np.ndarray,
    ts_seconds: int,
    slope_lookback: int = 5,
    max_bars_to_cross: float = 8.0,
    eps: float = 1e-12,
) -> Optional[MacdCrossMetric]:
    """
    Detects *pre-cross* conditions only:
      bullish: hist < 0 and rising
      bearish: hist > 0 and falling

    bars_to_cross uses linear extrapolation based on slope.
    """
    hist = np.asarray(hist, dtype=np.float64)
    if hist.size < slope_lookback + 1:
        return None

    hist_now = float(hist[-1])
    hist_prev = float(hist[-2])

    # Avoid "just crossed" whipsaw by requiring last two points stay on same side
    # (pre-cross means still on the starting side).
    if hist_now < 0.0:
        if hist_prev >= 0.0:
            return None
    elif hist_now > 0.0:
        if hist_prev <= 0.0:
            return None
    else:
        # exactly zero: already at cross, treat as not "about to"
        return None

    slope = _linear_regression_slope(hist[-slope_lookback:])
    if abs(slope) < eps:
        return None

    # bullish pre-cross: below zero and rising toward zero
    if hist_now < 0.0 and slope > 0.0:
        bars_to_cross = (-hist_now) / slope
        direction = "bullish"
    # bearish pre-cross: above zero and falling toward zero
    elif hist_now > 0.0 and slope < 0.0:
        bars_to_cross = (hist_now) / (-slope)
        direction = "bearish"
    else:
        return None

    if not math.isfinite(bars_to_cross):
        return None
    if bars_to_cross < 0.0:
        return None
    if bars_to_cross > max_bars_to_cross:
        return None

    time_to_cross_sec = bars_to_cross * float(ts_seconds)
    return MacdCrossMetric(
        direction=direction,
        hist_now=hist_now,
        slope_per_bar=float(slope),
        bars_to_cross=float(bars_to_cross),
        time_to_cross_sec=float(time_to_cross_sec),
    )


# ---------- Synthesis detection ----------
@dataclass(frozen=True)
class MacdSynthesisResult:
    direction: str                  # "bullish" or "bearish"
    start_timespan: str
    end_timespan: str
    chain: Tuple[str, ...]
    metrics: Dict[str, MacdCrossMetric]
    score: float


def detect_macd_synthesis(
    dfs_by_timespan: Dict[str, pd.DataFrame],
    timespans_ordered: List[str],
    slope_lookback: int = 5,
    max_bars_to_cross: float = 8.0,
    min_chain_len: int = 3,
    monotonic_tolerance: float = 0.10,  # allow small noise
) -> Optional[MacdSynthesisResult]:
    """
    Finds the best contiguous chain where:
      - direction matches ("bullish" or "bearish")
      - each timeframe is pre-cross
      - time_to_cross is non-decreasing as timeframe grows
        (1m crosses sooner than 5m crosses sooner than 10m, etc.)

    If 1m conflicts with 5m/10m/15m, chain start naturally shifts to 5m.
    """
    # compute per-timespan metrics
    metrics: Dict[str, MacdCrossMetric] = {}
    for ts in timespans_ordered:
        df = dfs_by_timespan.get(ts)
        if df is None or df.empty:
            continue
        if "macd_hist" not in df.columns:
            continue

        hist = df["macd_hist"].to_numpy(np.float64, copy=False)
        ts_sec = timespan_to_seconds(ts)
        m = macd_pre_cross_metric(
            hist=hist,
            ts_seconds=ts_sec,
            slope_lookback=slope_lookback,
            max_bars_to_cross=max_bars_to_cross,
        )
        if m is not None:
            metrics[ts] = m

    if not metrics:
        return None

    best: Optional[MacdSynthesisResult] = None

    # Try every possible start index; pick best chain
    for i, ts_start in enumerate(timespans_ordered):
        m0 = metrics.get(ts_start)
        if m0 is None:
            continue

        direction = m0.direction
        chain: List[str] = [ts_start]
        last_ttc = m0.time_to_cross_sec

        for ts in timespans_ordered[i + 1:]:
            mj = metrics.get(ts)
            if mj is None:
                break
            if mj.direction != direction:
                break

            # "further from crossing" as timespan grows:
            # allow slight violations within tolerance
            if mj.time_to_cross_sec < last_ttc * (1.0 - monotonic_tolerance):
                break

            chain.append(ts)
            last_ttc = mj.time_to_cross_sec

        if len(chain) < min_chain_len:
            continue

        chain_metrics = {ts: metrics[ts] for ts in chain}

        # Scoring: prefer longer chains, then earlier/sooner start-to-cross
        # (so a 4x chain beats a 3x chain, and "crossing soon" beats "eventually").
        score = float(len(chain) * 1000.0 - chain_metrics[chain[0]].time_to_cross_sec)

        candidate = MacdSynthesisResult(
            direction=direction,
            start_timespan=chain[0],
            end_timespan=chain[-1],
            chain=tuple(chain),
            metrics=chain_metrics,
            score=score,
        )
        if best is None or candidate.score > best.score:
            best = candidate

    return best



import asyncio

async def fetch_timespans_for_ticker(self, ticker: str, timespans: List[str]) -> Dict[str, pd.DataFrame]:
    # Concurrent fetch; semaphore inside _fetch_data_for_timespan already throttles.
    tasks = [self._fetch_data_for_timespan(ticker=ticker, timespan=ts) for ts in timespans]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    out: Dict[str, pd.DataFrame] = {}
    for ts, res in zip(timespans, results):
        if isinstance(res, Exception):
            self.log.warning("Fetch error %s [%s]: %r", ticker, ts, res)
            continue
        if res is None or res.empty:
            continue
        out[ts] = res
    return out


async def scan_macd_synthesis_for_tickers(
    self,
    tickers: List[str],
    timespans: List[str],
    min_chain_len: int = 3,
    slope_lookback: int = 5,
    max_bars_to_cross: float = 8.0,
) -> pd.DataFrame:
    """
    Returns a DataFrame of synthesis hits with chain + per-timespan cross estimates.
    """
    timespans_ordered = sort_timespans_small_to_large(timespans)

    async def _one(t: str):
        dfs = await fetch_timespans_for_ticker(self, t, timespans_ordered)
        synth = detect_macd_synthesis(
            dfs_by_timespan=dfs,
            timespans_ordered=timespans_ordered,
            min_chain_len=min_chain_len,
            slope_lookback=slope_lookback,
            max_bars_to_cross=max_bars_to_cross,
        )
        if synth is None:
            return None

        # Flatten a nice row for ranking / debugging
        row = {
            "ticker": t,
            "direction": synth.direction,
            "start_timespan": synth.start_timespan,
            "end_timespan": synth.end_timespan,
            "chain": " > ".join(synth.chain),
            "chain_len": len(synth.chain),
            "score": synth.score,
        }

        # Add compact per-timespan fields
        for ts in synth.chain:
            m = synth.metrics[ts]
            row[f"{ts}_hist"] = m.hist_now
            row[f"{ts}_bars_to_cross"] = m.bars_to_cross
            row[f"{ts}_mins_to_cross"] = m.time_to_cross_sec / 60.0

        return row

    # Run tickers concurrently too (your semaphore still throttles HTTP inside each fetch)
    rows = await asyncio.gather(*[_one(t) for t in tickers])
    rows = [r for r in rows if r is not None]

    if not rows:
        return pd.DataFrame(columns=[
            "ticker", "direction", "start_timespan", "end_timespan", "chain", "chain_len", "score"
        ])

    df = pd.DataFrame(rows)
    df = df.sort_values(["chain_len", "score"], ascending=[False, False]).reset_index(drop=True)
    return df