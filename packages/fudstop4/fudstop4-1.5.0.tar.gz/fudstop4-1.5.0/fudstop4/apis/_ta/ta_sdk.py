#!/usr/bin/env python3
"""
fudstop4.apis._ta.ta_sdk

Fast technical-analysis indicator toolkit designed for:
  - High-throughput backfills (millions of candles)
  - Live, per-minute scanning
  - SQL-friendly, stable column names (no "+DI" / "-DI" surprises)

Primary performance goals
  1) Avoid repeated sort/copy work across indicators
  2) Prefer vectorized NumPy/Pandas ops
  3) Use Numba for tight loops where it materially helps (RSI/TD9/EMA/MACD/ADX/CCI, etc.)
  4) Never merge() indicator columns back onto the frame (prevents *_x/*_y explosions)
  5) Return DataFrames in the caller's original row-order

Important semantic notes
  - We assume "ts" is chronological (ascending) for calculations.
  - We keep the historical behavior of "candle_completely_*" being shifted forward by 1 bar,
    so the flag is actionable on the *next* candle after the full-break candle closes.
  - vwap_dist_pct is stored as a *decimal fraction* (0.02 == 2%).
    (This matches how thresholds are typically written in rules: 0.015 == 1.5%.)

If you previously stored vwap_dist_pct as a percent (x100), you should either:
  - migrate/recompute that column, or
  - change the implementation below back to percent.

"""

from __future__ import annotations

import math
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

try:
    from numba import njit  # type: ignore
except Exception:  # pragma: no cover
    # Numba is an optional speed-up. If it's unavailable (or broken in the env),
    # fall back to a no-op decorator so the module still works.
    def njit(*args, **kwargs):  # type: ignore
        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return args[0]
        def _wrap(fn):
            return fn
        return _wrap

try:
    # Optional dependency: only used for a couple of helper functions.
    from scipy.stats import linregress  # type: ignore
except Exception:  # pragma: no cover
    # Lightweight fallback (slope only) to avoid hard SciPy dependency.
    def linregress(x, y):  # type: ignore
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if len(x) < 2:
            class _R:  # minimal shim
                slope = 0.0
            return _R()
        slope, _intercept = np.polyfit(x, y, 1)
        class _R:  # minimal shim
            slope = float(slope)
        return _R()


# ───────────────────────── column aliases ─────────────────────────

OPEN_ALIASES = ("o", "open", "openprice", "price_open")
HIGH_ALIASES = ("h", "high", "highprice", "price_high")
LOW_ALIASES = ("l", "low", "lowprice", "price_low")
CLOSE_ALIASES = (
    "c",
    "close",
    "adjclose",
    "adj_close",
    "closeprice",
    "closing_price",
    "last",
    "lastprice",
    "price",
    "p",
)


# ───────────────────────── numba cores ─────────────────────────

@njit(cache=True)
def _ema_njit(prices: np.ndarray, period: int) -> np.ndarray:
    """
    Exponential moving average (EMA) with the same recursion as pandas ewm(adjust=False).
    NOTE: This function does NOT apply min_periods masking; callers may mask outputs.
    """
    n = len(prices)
    out = np.empty(n, dtype=np.float64)
    if n == 0:
        return out
    multiplier = 2.0 / (period + 1.0)
    out[0] = prices[0]
    for i in range(1, n):
        out[i] = (prices[i] - out[i - 1]) * multiplier + out[i - 1]
    return out


@njit(cache=True)
def _wilder_smooth_njit(values: np.ndarray, window: int) -> np.ndarray:
    """
    Wilder smoothing:
      smoothed[i] = (smoothed[i-1]*(window-1) + values[i]) / window

    Output matches the typical Wilder formulation:
      - NaN until index window-1
      - index window-1 is the SMA of the first window values
    """
    n = len(values)
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        out[i] = np.nan
    if window <= 1 or n < window:
        # If too small, return as-is (masked)
        return out

    s = 0.0
    for i in range(window):
        s += values[i]
    sma = s / window
    out[window - 1] = sma

    prev = sma
    for i in range(window, n):
        prev = (prev * (window - 1) + values[i]) / window
        out[i] = prev
    return out


@njit(cache=True)
def _compute_wilders_rsi_numba(closes: np.ndarray, window: int) -> np.ndarray:
    """
    Wilder RSI computed from close-to-close deltas using Wilder smoothing.
    First `window` values are NaN (to match common TA libraries).
    """
    n = len(closes)
    rsi = np.empty(n, dtype=np.float64)
    for i in range(n):
        rsi[i] = np.nan
    if n <= window:
        return rsi

    # deltas
    gains = np.empty(n, dtype=np.float64)
    losses = np.empty(n, dtype=np.float64)
    gains[0] = 0.0
    losses[0] = 0.0
    for i in range(1, n):
        d = closes[i] - closes[i - 1]
        if d > 0.0:
            gains[i] = d
            losses[i] = 0.0
        else:
            gains[i] = 0.0
            losses[i] = -d

    avg_gain = 0.0
    avg_loss = 0.0
    for i in range(1, window + 1):
        avg_gain += gains[i]
        avg_loss += losses[i]
    avg_gain /= window
    avg_loss /= window

    # first RSI at index window
    if avg_loss == 0.0:
        rsi[window] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi[window] = 100.0 - (100.0 / (1.0 + rs))

    for i in range(window + 1, n):
        avg_gain = ((avg_gain * (window - 1)) + gains[i]) / window
        avg_loss = ((avg_loss * (window - 1)) + losses[i]) / window
        if avg_loss == 0.0:
            rsi[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i] = 100.0 - (100.0 / (1.0 + rs))
    return rsi


@njit(cache=True)
def _compute_td9_counts(closes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    TD Sequential setup counts (buy/sell). Counts can extend beyond 9.

    buy setup increments when close < close[-4]
    sell setup increments when close > close[-4]
    """
    n = len(closes)
    td_buy = np.zeros(n, dtype=np.int32)
    td_sell = np.zeros(n, dtype=np.int32)

    buy_count = 0
    sell_count = 0

    for i in range(n):
        if i < 4:
            td_buy[i] = buy_count
            td_sell[i] = sell_count
            continue

        if buy_count > 0:
            if closes[i] < closes[i - 4]:
                buy_count += 1
            else:
                buy_count = 0
                if closes[i] > closes[i - 4]:
                    sell_count = 1
                else:
                    sell_count = 0

        elif sell_count > 0:
            if closes[i] > closes[i - 4]:
                sell_count += 1
            else:
                sell_count = 0
                if closes[i] < closes[i - 4]:
                    buy_count = 1
                else:
                    buy_count = 0
        else:
            if closes[i] < closes[i - 4]:
                buy_count = 1
            elif closes[i] > closes[i - 4]:
                sell_count = 1

        td_buy[i] = buy_count
        td_sell[i] = sell_count

    return td_buy, td_sell


@njit(cache=True)
def _macd_core(
    closes: np.ndarray,
    fast_period: int,
    slow_period: int,
    signal_period: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    MACD core using EMA recursion (same as pandas adjust=False).
    Returns (macd_line, signal_line, histogram).
    """
    fast = _ema_njit(closes, fast_period)
    slow = _ema_njit(closes, slow_period)
    macd_line = fast - slow
    signal_line = _ema_njit(macd_line, signal_period)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


@njit(cache=True)
def _volume_streaks_from_diffs(diffs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Given diffs[i] = v[i] - v[i-1] (diffs[0] arbitrary),
    compute consecutive increasing and decreasing streak lengths.
    """
    n = len(diffs)
    inc = np.zeros(n, dtype=np.int32)
    dec = np.zeros(n, dtype=np.int32)
    for i in range(1, n):
        if diffs[i] > 0.0:
            inc[i] = inc[i - 1] + 1
        else:
            inc[i] = 0
        if diffs[i] < 0.0:
            dec[i] = dec[i - 1] + 1
        else:
            dec[i] = 0
    return inc, dec


@njit(cache=True)
def _true_range_numba(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    n = len(close)
    out = np.empty(n, dtype=np.float64)
    out[0] = high[0] - low[0]
    for i in range(1, n):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i - 1])
        lc = abs(low[i] - close[i - 1])
        # max of three
        m = hl
        if hc > m:
            m = hc
        if lc > m:
            m = lc
        out[i] = m
    return out


@njit(cache=True)
def _adx_numba(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    window: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fast ADX implementation using Wilder smoothing.
    Returns (adx, di_plus, di_minus).
    """
    n = len(close)
    adx = np.empty(n, dtype=np.float64)
    di_plus = np.empty(n, dtype=np.float64)
    di_minus = np.empty(n, dtype=np.float64)
    for i in range(n):
        adx[i] = np.nan
        di_plus[i] = np.nan
        di_minus[i] = np.nan
    if n < window + 1:
        return adx, di_plus, di_minus

    tr = _true_range_numba(high, low, close)

    plus_dm = np.zeros(n, dtype=np.float64)
    minus_dm = np.zeros(n, dtype=np.float64)
    for i in range(1, n):
        up_move = high[i] - high[i - 1]
        down_move = low[i - 1] - low[i]
        if up_move > down_move and up_move > 0.0:
            plus_dm[i] = up_move
        else:
            plus_dm[i] = 0.0
        if down_move > up_move and down_move > 0.0:
            minus_dm[i] = down_move
        else:
            minus_dm[i] = 0.0

    tr14 = _wilder_smooth_njit(tr, window)
    plus14 = _wilder_smooth_njit(plus_dm, window)
    minus14 = _wilder_smooth_njit(minus_dm, window)

    # DI and DX
    dx = np.empty(n, dtype=np.float64)
    for i in range(n):
        dx[i] = np.nan

    for i in range(window - 1, n):
        trv = tr14[i]
        if math.isnan(trv) or trv == 0.0:
            continue
        pdi = 100.0 * (plus14[i] / trv) if not math.isnan(plus14[i]) else np.nan
        mdi = 100.0 * (minus14[i] / trv) if not math.isnan(minus14[i]) else np.nan
        di_plus[i] = pdi
        di_minus[i] = mdi

        denom = pdi + mdi
        if denom == 0.0 or math.isnan(denom):
            continue
        dx[i] = 100.0 * (abs(pdi - mdi) / denom)

    adx_vals = _wilder_smooth_njit(dx, window)
    for i in range(n):
        adx[i] = adx_vals[i]
    return adx, di_plus, di_minus


@njit(cache=True)
def _cci_numba(
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    window: int,
) -> np.ndarray:
    """
    Commodity Channel Index:
      TP = (H+L+C)/3
      SMA_TP = SMA(TP, window)
      MAD = mean(|TP - SMA_TP|, window)
      CCI = (TP - SMA_TP) / (0.015 * MAD)
    """
    n = len(close)
    out = np.empty(n, dtype=np.float64)
    for i in range(n):
        out[i] = np.nan
    if n < window:
        return out

    tp = (high + low + close) / 3.0

    # rolling sums for SMA
    s = 0.0
    for i in range(window):
        s += tp[i]
    sma = s / window

    # CCI at i=window-1
    # compute MAD
    mad = 0.0
    for j in range(window):
        mad += abs(tp[j] - sma)
    mad /= window
    denom = 0.015 * mad
    out[window - 1] = (tp[window - 1] - sma) / denom if denom != 0.0 else np.nan

    for i in range(window, n):
        # update SMA (remove i-window, add i)
        s += tp[i] - tp[i - window]
        sma = s / window

        mad = 0.0
        for j in range(i - window + 1, i + 1):
            mad += abs(tp[j] - sma)
        mad /= window
        denom = 0.015 * mad
        out[i] = (tp[i] - sma) / denom if denom != 0.0 else np.nan

    return out


@njit(cache=True)
def _aroon_numba(high: np.ndarray, low: np.ndarray, window: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Aroon Up/Down/Oscillator over a rolling window.
    Aroon Up = 100 * (window - periods_since_high) / window
    Aroon Down = 100 * (window - periods_since_low) / window
    """
    n = len(high)
    up = np.empty(n, dtype=np.float64)
    dn = np.empty(n, dtype=np.float64)
    osc = np.empty(n, dtype=np.float64)
    for i in range(n):
        up[i] = np.nan
        dn[i] = np.nan
        osc[i] = np.nan
    if n < window:
        return up, dn, osc

    for i in range(window - 1, n):
        # lookback window [i-window+1, i]
        start = i - window + 1
        hi_idx = start
        lo_idx = start
        hi_val = high[start]
        lo_val = low[start]
        for j in range(start + 1, i + 1):
            if high[j] >= hi_val:
                hi_val = high[j]
                hi_idx = j
            if low[j] <= lo_val:
                lo_val = low[j]
                lo_idx = j
        periods_since_high = i - hi_idx
        periods_since_low = i - lo_idx
        up[i] = 100.0 * (window - periods_since_high) / window
        dn[i] = 100.0 * (window - periods_since_low) / window
        osc[i] = up[i] - dn[i]
    return up, dn, osc


# ───────────────────────── helpers ─────────────────────────

def _is_numeric_series(s: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(s)


def _to_float64(series: pd.Series) -> np.ndarray:
    """
    Convert a Series to a float64 NumPy array robustly.
    """
    if _is_numeric_series(series):
        return series.to_numpy(dtype=np.float64, copy=False)
    return pd.to_numeric(series, errors="coerce").to_numpy(dtype=np.float64, copy=False)


def _to_int32(series: pd.Series) -> np.ndarray:
    if pd.api.types.is_integer_dtype(series):
        return series.to_numpy(dtype=np.int32, copy=False)
    return pd.to_numeric(series, errors="coerce").fillna(0).to_numpy(dtype=np.int32, copy=False)

def _consolidate_if_fragmented(df: pd.DataFrame, *, threshold: int = 80) -> pd.DataFrame:
    """Consolidate highly-fragmented DataFrames.

    Pandas can become very slow after many incremental column inserts (high fragmentation).
    When the internal block count grows beyond `threshold`, returning `df.copy()` tends to
    restore performance and avoids PerformanceWarning spam.
    """
    try:
        mgr = getattr(df, "_mgr", None)
        nblocks = getattr(mgr, "nblocks", 0) if mgr is not None else 0
        if nblocks and nblocks > threshold:
            return df.copy()
    except Exception:
        pass
    return df


# ───────────────────────── main TA class ─────────────────────────

class FudstopTA:
    OPEN_ALIASES = OPEN_ALIASES
    HIGH_ALIASES = HIGH_ALIASES
    LOW_ALIASES = LOW_ALIASES
    CLOSE_ALIASES = CLOSE_ALIASES

    # ───────────────────────── ordering helpers ─────────────────────────

    @staticmethod
    def _prep_indicator_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
        """Prepare a candle/indicator DataFrame for calculations.

        Fast path:
          - If a 'ts' column exists and is already sorted ASC, we avoid sorting and
            avoid copying unless the frame is highly fragmented.

        Slow path:
          - Otherwise we copy + sort by ts ASC and record original order for restore.
        """
        if df is None or df.empty:
            return df, False
        if "ts" not in df.columns:
            return df, False

        try:
            ts = df["ts"]
            if getattr(ts, 'is_monotonic_increasing', False):
                # Keep it in-place for speed, but defragment when needed.
                return _consolidate_if_fragmented(df), False
        except Exception:
            pass

        d = df.copy()
        d['__orig_order'] = np.arange(len(d))
        d = d.sort_values('ts').reset_index(drop=True)
        return d, True

    @staticmethod
    def _restore_indicator_df(df: pd.DataFrame, restore: bool) -> pd.DataFrame:
        if restore and df is not None and len(df) > 0 and "__orig_order" in df.columns:
            df = df.sort_values("__orig_order").drop(columns=["__orig_order"])
        return df

    @staticmethod
    def _find_col(df: pd.DataFrame, aliases: tuple) -> Optional[str]:
        col_map = {str(c).lower(): c for c in df.columns}
        for alias in aliases:
            key = alias.lower()
            if key in col_map:
                return col_map[key]
        return None

    @staticmethod
    def _td_points(count: float) -> int:
        if count >= 25:
            return 4
        if count >= 20:
            return 3
        if count >= 13:
            return 2
        if count >= 9:
            return 1
        return 0

    # ───────────────────────── core indicators ─────────────────────────

    @staticmethod
    def compute_wilders_rsi_numba(closes: np.ndarray, window: int) -> np.ndarray:
        return _compute_wilders_rsi_numba(closes.astype(np.float64), window)

    @staticmethod
    def compute_wilders_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Wilder RSI on close column 'c'. Adds column: rsi
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        closes = _to_float64(df["c"])
        df["rsi"] = _compute_wilders_rsi_numba(closes, window)
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def compute_td9_counts(closes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        return _compute_td9_counts(closes.astype(np.float64))

    @staticmethod
    def add_td9_counts(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds td_buy_count and td_sell_count columns using TD Sequential rules.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df
        closes = _to_float64(df["c"])
        td_buy, td_sell = _compute_td9_counts(closes)
        df["td_buy_count"] = td_buy
        df["td_sell_count"] = td_sell
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_macd(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> pd.DataFrame:
        """
        Adds MACD line, signal, histogram + cross flags + histogram slopes.
        Columns:
          macd_line, macd_signal, macd_hist,
          macd_cross_up, macd_cross_dn,
          macd_hist_slope, macd_hist_slope3
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        closes = _to_float64(df["c"])
        macd_line, signal_line, hist = _macd_core(closes, fast_period, slow_period, signal_period)

        df["macd_line"] = macd_line
        df["macd_signal"] = signal_line
        df["macd_hist"] = hist

        prev_val = pd.Series(macd_line, index=df.index).shift(1)
        prev_sig = pd.Series(signal_line, index=df.index).shift(1)
        df["macd_cross_up"] = (prev_val <= prev_sig) & (df["macd_line"] > df["macd_signal"])
        df["macd_cross_dn"] = (prev_val >= prev_sig) & (df["macd_line"] < df["macd_signal"])

        df["macd_hist_slope"] = pd.Series(hist, index=df.index).diff()
        df["macd_hist_slope3"] = df["macd_hist"] - df["macd_hist"].shift(3)

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_ema_pack(
        df: pd.DataFrame,
        periods: tuple = (9, 21, 50),
        slope_lookback: int = 3,
    ) -> pd.DataFrame:
        """
        Adds EMA levels + slopes + stack flags + 9/21 cross flags.

        Uses Numba EMA recursion to avoid pandas ewm overhead in large backfills.
        Mirrors pandas ewm(adjust=False) recursion; applies min_periods mask.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        close = _to_float64(df["c"])

        ema_cols = []
        for p in periods:
            ema = _ema_njit(close, int(p))
            if len(ema) >= p:
                ema[: p - 1] = np.nan  # min_periods behaviour
            else:
                ema[:] = np.nan
            col = f"ema_{p}"
            df[col] = ema
            ema_cols.append(col)

            # slope over lookback
            if slope_lookback and slope_lookback > 0:
                slope = ema - np.roll(ema, slope_lookback)
                slope[:slope_lookback] = np.nan
                df[f"ema_slope_{p}"] = slope
            else:
                df[f"ema_slope_{p}"] = np.nan

        # stack flags (bull: fast > mid > slow)
        if len(periods) >= 2:
            ps = list(periods)
            bull = np.ones(len(df), dtype=bool)
            bear = np.ones(len(df), dtype=bool)
            for i in range(len(ps) - 1):
                a = df[f"ema_{ps[i]}"].to_numpy(dtype=np.float64, copy=False)
                b = df[f"ema_{ps[i+1]}"].to_numpy(dtype=np.float64, copy=False)
                bull = bull & (a > b)
                bear = bear & (a < b)
            # NaNs -> False
            for p in ps:
                bull = bull & ~np.isnan(df[f"ema_{p}"].to_numpy(dtype=np.float64, copy=False))
                bear = bear & ~np.isnan(df[f"ema_{p}"].to_numpy(dtype=np.float64, copy=False))
            df["ema_stack_bull"] = bull
            df["ema_stack_bear"] = bear
        else:
            df["ema_stack_bull"] = False
            df["ema_stack_bear"] = False

        # 9/21 cross flags
        if 9 in periods and 21 in periods:
            fast = df["ema_9"].to_numpy(dtype=np.float64, copy=False)
            slow = df["ema_21"].to_numpy(dtype=np.float64, copy=False)
            fast_prev = np.roll(fast, 1)
            slow_prev = np.roll(slow, 1)
            fast_prev[0] = np.nan
            slow_prev[0] = np.nan
            df["ema_9_21_cross_up"] = (fast_prev <= slow_prev) & (fast > slow)
            df["ema_9_21_cross_dn"] = (fast_prev >= slow_prev) & (fast < slow)

        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── bands / price positioning ─────────────────────────

    @staticmethod
    def compute_trend(
        series_desc: pd.Series,
        threshold: float = 0.001,
        window: int = 5,
    ) -> str:
        """
        Compute trend label from a DESC series (most recent first).
        This is primarily kept for backward compatibility / debugging.
        """
        chronological_data = series_desc.iloc[::-1].copy()
        recent_subset = chronological_data.iloc[-window:]

        if len(recent_subset) < 2:
            return "flattening"

        x = np.arange(len(recent_subset))
        try:
            result = linregress(x, recent_subset.values)
            slope = float(result.slope)
        except Exception:
            return "flattening"

        mean_val = float(np.nanmean(recent_subset.values))
        rel = slope / mean_val if mean_val != 0 else 0.0

        if rel > threshold:
            return "increasing"
        if rel < -threshold:
            return "decreasing"
        return "flattening"

    @staticmethod
    def add_bollinger_bands(
        df: pd.DataFrame,
        window: int = 20,
        num_std: float = 2.0,
        trend_points: int = 13,
        trend_window: int = 5,
        trend_threshold: float = 0.001,
    ) -> pd.DataFrame:
        """
        Adds:
          middle_band, std, upper_band, lower_band,
          upper_bb_trend, lower_bb_trend,
          candle_above_upper, candle_below_lower,
          candle_completely_above_upper, candle_partially_above_upper,
          candle_completely_below_lower, candle_partially_below_lower

        Performance:
          - No merge()
          - Single sort max (via _prep_indicator_df)
          - Trend computed cheaply per-row for the last `trend_window` bars (not per-tick heavy)

        Trend labels:
          upper_bb_trend ∈ {upper_increasing, upper_decreasing, flattening}
          lower_bb_trend ∈ {lower_increasing, lower_decreasing, flattening}
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        mid = close.rolling(window=window, min_periods=window).mean()
        std = close.rolling(window=window, min_periods=window).std(ddof=0)

        df["middle_band"] = mid
        df["std"] = std
        df["upper_band"] = mid + (num_std * std)
        df["lower_band"] = mid - (num_std * std)

        # Candle flags (use high/low when present)
        if {"h", "l"}.issubset(df.columns):
            high = pd.to_numeric(df["h"], errors="coerce").astype(float)
            low = pd.to_numeric(df["l"], errors="coerce").astype(float)

            df["candle_above_upper"] = (high > df["upper_band"]).fillna(False)
            df["candle_below_lower"] = (low < df["lower_band"]).fillna(False)

            comp_above = (low > df["upper_band"])
            part_above = (high > df["upper_band"]) & (low <= df["upper_band"])

            comp_below = (high < df["lower_band"])
            part_below = (low < df["lower_band"]) & (high >= df["lower_band"])
        else:
            df["candle_above_upper"] = (close > df["upper_band"]).fillna(False)
            df["candle_below_lower"] = (close < df["lower_band"]).fillna(False)

            comp_above = close > df["upper_band"]
            part_above = comp_above
            comp_below = close < df["lower_band"]
            part_below = comp_below

        # Shift full-break flags forward by 1 candle (actionable after close)
        df["candle_completely_above_upper"] = comp_above.shift(1, fill_value=False)
        df["candle_completely_below_lower"] = comp_below.shift(1, fill_value=False)

        df["candle_partially_above_upper"] = part_above.fillna(False)
        df["candle_partially_below_lower"] = part_below.fillna(False)

        # Trend labels: computed for each row using last `trend_window` values of the bands.
        # We keep it fast and simple. If you want ultra-fast trend, remove this block.
        df["upper_bb_trend"] = pd.Series([None] * len(df), dtype="object")
        df["lower_bb_trend"] = pd.Series([None] * len(df), dtype="object")

        w = int(max(2, min(trend_window, trend_points)))
        if len(df) >= w:
            # We compute slope over rolling window w on upper_band/lower_band.
            # Using numpy polyfit per row would be slow; instead we approximate using
            # simple linear regression slope formula via rolling sums.

            def _trend_labels(series: pd.Series, prefix: str) -> pd.Series:
                y = series.to_numpy(dtype=np.float64, copy=False)
                n = len(y)
                out = np.array([None] * n, dtype=object)
                if n < w:
                    return pd.Series(out, index=series.index, dtype="object")

                x = np.arange(w, dtype=np.float64)
                sum_x = float(x.sum())
                sum_x2 = float((x * x).sum())
                denom = (w * sum_x2 - sum_x * sum_x)
                if denom == 0.0:
                    return pd.Series(out, index=series.index, dtype="object")

                ones = np.ones(w, dtype=np.float64)
                sum_y = np.convolve(y, ones, mode="valid")
                sum_xy = np.convolve(y, x[::-1], mode="valid")  # aligns window end

                slope = (w * sum_xy - sum_x * sum_y) / denom
                mean = sum_y / w
                rel = np.zeros_like(slope)
                for i in range(len(slope)):
                    m = mean[i]
                    rel[i] = slope[i] / m if m != 0.0 and not np.isnan(m) else 0.0

                # Assign labels at indices [w-1 .. n-1]
                start_idx = w - 1
                for i in range(len(slope)):
                    idx = start_idx + i
                    r = rel[i]
                    if r > trend_threshold:
                        out[idx] = f"{prefix}_increasing"
                    elif r < -trend_threshold:
                        out[idx] = f"{prefix}_decreasing"
                    else:
                        out[idx] = "flattening"
                return pd.Series(out, index=series.index, dtype="object")

            df["upper_bb_trend"] = _trend_labels(df["upper_band"], "upper")
            df["lower_bb_trend"] = _trend_labels(df["lower_band"], "lower")

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_band_position_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Derived from Bollinger outputs:
          - bb_width
          - band_above/below (wick outside)
          - band_above_full/below_full (full candle outside, shifted)
        """
        # This helper is lightweight and runs in-place (copy avoided intentionally)
        if df is None or df.empty:
            return df

        if {"upper_band", "lower_band", "middle_band"}.issubset(df.columns):
            denom = df["middle_band"].replace(0, np.nan)
            df["bb_width"] = ((df["upper_band"] - df["lower_band"]) / denom).replace([np.inf, -np.inf], np.nan).fillna(0.0)
            # BB "outside" helpers (lower/upper) + aliases used by rule_factory / live rules
            close = pd.to_numeric(df["c"], errors="coerce").astype(float)
            high = pd.to_numeric(df["h"], errors="coerce").astype(float)
            low = pd.to_numeric(df["l"], errors="coerce").astype(float)

            lb = pd.to_numeric(df["lower_band"], errors="coerce").astype(float)
            ub = pd.to_numeric(df["upper_band"], errors="coerce").astype(float)

            df["bb_close_outside_lower"] = (close < lb)
            df["bb_close_outside_upper"] = (close > ub)

            df["bb_wick_outside_lower"] = (low < lb) & (close >= lb)
            df["bb_wick_outside_upper"] = (high > ub) & (close <= ub)

            # Back-compat aliases (mostly used by bullish rules)
            df["bb_close_outside"] = df["bb_close_outside_lower"]
            df["bb_wick_outside"] = df["bb_wick_outside_lower"]

        else:
            df["bb_width"] = 0.0

        df["band_above"] = df["candle_above_upper"].fillna(False) if "candle_above_upper" in df.columns else False
        df["band_below"] = df["candle_below_lower"].fillna(False) if "candle_below_lower" in df.columns else False

        df["band_above_full"] = df["candle_completely_above_upper"].fillna(False) if "candle_completely_above_upper" in df.columns else False
        df["band_below_full"] = df["candle_completely_below_lower"].fillna(False) if "candle_completely_below_lower" in df.columns else False

        return df

    # ───────────────────────── volume / price action ─────────────────────────

    @staticmethod
    def add_volume_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds:
          volume_diff
          volume_pct_change (percent, x100)
          volume_increasing_streak
          volume_decreasing_streak

        Implemented with a small Numba kernel for streaks (fast).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        v = pd.to_numeric(df.get("v", 0), errors="coerce").fillna(0.0).astype(float)
        diff = v.diff().fillna(0.0)
        df["volume_diff"] = diff
        df["volume_pct_change"] = v.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.0) * 100.0

        diffs = diff.to_numpy(dtype=np.float64, copy=False)
        inc, dec = _volume_streaks_from_diffs(diffs)
        df["volume_increasing_streak"] = inc
        df["volume_decreasing_streak"] = dec

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_obv(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds standard OBV (vectorized).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        close = _to_float64(df["c"])
        vol = pd.to_numeric(df.get("v", 0), errors="coerce").fillna(0.0).to_numpy(dtype=np.float64, copy=False)

        # direction: +1, -1, or 0 based on close vs prev close
        prev = np.roll(close, 1)
        prev[0] = close[0]
        direction = np.sign(close - prev)
        df["obv"] = np.cumsum(direction * vol)
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_engulfing_patterns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Flags bullish_engulfing / bearish_engulfing (vectorized).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        o = pd.to_numeric(df["o"], errors="coerce").astype(float)
        c = pd.to_numeric(df["c"], errors="coerce").astype(float)
        h = pd.to_numeric(df["h"], errors="coerce").astype(float)
        l = pd.to_numeric(df["l"], errors="coerce").astype(float)

        p_o = o.shift(1)
        p_c = c.shift(1)
        p_h = h.shift(1)
        p_l = l.shift(1)

        prev_red = p_c < p_o
        prev_green = p_c > p_o
        cur_green = c > o
        cur_red = c < o
        range_engulf = (h > p_h) & (l < p_l)

        df["bullish_engulfing"] = (prev_red & cur_green & range_engulf & (o < p_c) & (c > p_o)).fillna(False)
        df["bearish_engulfing"] = (prev_green & cur_red & range_engulf & (o > p_c) & (c < p_o)).fillna(False)

        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── classic indicators (fast-ish) ─────────────────────────

    @staticmethod
    def add_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Average True Range (ATR) using Wilder smoothing.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = _to_float64(df["h"])
        low = _to_float64(df["l"])
        close = _to_float64(df["c"])

        tr = _true_range_numba(high, low, close)
        atr = _wilder_smooth_njit(tr, window)
        df["atr"] = atr
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_cci(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Commodity Channel Index (CCI) with Numba core.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = _to_float64(df["h"])
        low = _to_float64(df["l"])
        close = _to_float64(df["c"])
        df["cci"] = _cci_numba(high, low, close, window)
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_cmo(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Chande Momentum Oscillator (CMO).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        diff = pd.to_numeric(df["c"], errors="coerce").astype(float).diff()
        gains = diff.where(diff > 0, 0.0)
        losses = (-diff).where(diff < 0, 0.0)

        sum_gains = gains.rolling(window=window, min_periods=window).sum()
        sum_losses = losses.rolling(window=window, min_periods=window).sum()
        denom = (sum_gains + sum_losses).replace(0, np.nan)
        df["cmo"] = 100.0 * (sum_gains - sum_losses) / denom

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_stochastic_oscillator(df: pd.DataFrame, window: int = 14, smooth_window: int = 3) -> pd.DataFrame:
        """
        Adds Stochastic Oscillator (%K and %D).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)

        lowest_low = low.rolling(window=window, min_periods=window).min()
        highest_high = high.rolling(window=window, min_periods=window).max()
        denom = (highest_high - lowest_low).replace(0, np.nan)

        df["stoch_k"] = 100.0 * ((close - lowest_low) / denom)
        df["stoch_d"] = df["stoch_k"].rolling(window=smooth_window, min_periods=smooth_window).mean()

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_awesome_oscillator(df: pd.DataFrame, short: int = 5, long: int = 34) -> pd.DataFrame:
        """
        Awesome Oscillator (AO).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        median = (pd.to_numeric(df["h"], errors="coerce").astype(float) + pd.to_numeric(df["l"], errors="coerce").astype(float)) / 2.0
        short_sma = median.rolling(window=short, min_periods=short).mean()
        long_sma = median.rolling(window=long, min_periods=long).mean()
        df["ao"] = short_sma - long_sma
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_donchian_channels(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Donchian channels.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)

        upper = high.rolling(window=window, min_periods=window).max()
        lower = low.rolling(window=window, min_periods=window).min()
        df["donchian_upper"] = upper
        df["donchian_lower"] = lower
        df["donchian_middle"] = (upper + lower) / 2.0
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_aroon(df: pd.DataFrame, window: int = 25) -> pd.DataFrame:
        """
        Aroon up/down/osc using a Numba kernel.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = _to_float64(df["h"])
        low = _to_float64(df["l"])
        up, dn, osc = _aroon_numba(high, low, window)
        df["aroon_up"] = up
        df["aroon_down"] = dn
        df["aroon_osc"] = osc
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_mfi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Money Flow Index (MFI).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        vol = pd.to_numeric(df.get("v", 0), errors="coerce").fillna(0.0).astype(float)

        tp = (high + low + close) / 3.0
        raw = tp * vol
        tp_diff = tp.diff()

        pos = raw.where(tp_diff > 0, 0.0)
        neg = raw.where(tp_diff < 0, 0.0)

        pos_sum = pos.rolling(window=window, min_periods=window).sum()
        neg_sum = neg.rolling(window=window, min_periods=window).sum()

        ratio = pos_sum / neg_sum.replace(0, np.nan)
        mfi = 100.0 - (100.0 / (1.0 + ratio))
        mfi = mfi.mask((neg_sum == 0) & (pos_sum > 0), 100.0)
        mfi = mfi.mask((pos_sum == 0) & (neg_sum > 0), 0.0)

        df["mfi"] = mfi
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_williams_r(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Williams %R.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)

        hh = high.rolling(window=window, min_periods=window).max()
        ll = low.rolling(window=window, min_periods=window).min()
        rng = (hh - ll).replace(0, np.nan)
        df["williams_r"] = -100.0 * (hh - close) / rng
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_vortex_indicator(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Vortex Indicator (VI+ and VI-).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)

        prev_high = high.shift(1)
        prev_low = low.shift(1)

        vm_plus = (high - prev_low).abs()
        vm_minus = (low - prev_high).abs()

        tr = pd.Series(_true_range_numba(high.to_numpy(dtype=np.float64, copy=False),
                                         low.to_numpy(dtype=np.float64, copy=False),
                                         close.to_numpy(dtype=np.float64, copy=False)),
                       index=df.index)

        tr_sum = tr.rolling(window=window, min_periods=window).sum().replace(0, np.nan)
        df["vortex_plus"] = vm_plus.rolling(window=window, min_periods=window).sum() / tr_sum
        df["vortex_minus"] = vm_minus.rolling(window=window, min_periods=window).sum() / tr_sum
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_roc(df: pd.DataFrame, window: int = 12) -> pd.DataFrame:
        """
        Rate of Change (ROC) in percent.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        shifted = close.shift(window)
        denom = shifted.replace(0, np.nan)
        df["roc"] = ((close - shifted) / denom) * 100.0
        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── channel/volatility indicators ─────────────────────────

    @staticmethod
    def add_keltner_channels(
        df: pd.DataFrame,
        window: int = 20,
        atr_window: int = 10,
        atr_multiplier: float = 2.0,
        use_typical_price: bool = True,
        use_ema: bool = True,
    ) -> pd.DataFrame:
        """
        Keltner channels middle/upper/lower.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)

        price = (high + low + close) / 3.0 if use_typical_price else close
        if use_ema:
            middle = price.ewm(span=window, adjust=False, min_periods=window).mean()
        else:
            middle = price.rolling(window=window, min_periods=window).mean()

        tr = pd.Series(_true_range_numba(high.to_numpy(dtype=np.float64, copy=False),
                                         low.to_numpy(dtype=np.float64, copy=False),
                                         close.to_numpy(dtype=np.float64, copy=False)),
                       index=df.index)
        atr = pd.Series(_wilder_smooth_njit(tr.to_numpy(dtype=np.float64, copy=False), atr_window), index=df.index)

        df["keltner_middle"] = middle
        df["keltner_upper"] = middle + (atr_multiplier * atr)
        df["keltner_lower"] = middle - (atr_multiplier * atr)

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_chaikin_money_flow(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Chaikin Money Flow (CMF).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        vol = pd.to_numeric(df.get("v", 0), errors="coerce").fillna(0.0).astype(float)

        pr = (high - low).replace(0, np.nan)
        mfm = ((close - low) - (high - close)) / pr
        mfm = mfm.fillna(0.0)
        mfv = mfm * vol

        mfv_sum = mfv.rolling(window=window, min_periods=window).sum()
        vol_sum = vol.rolling(window=window, min_periods=window).sum().replace(0, np.nan)
        df["cmf"] = mfv_sum / vol_sum

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_choppiness_index(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        CHOP (0-100): higher = choppy, lower = trending.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = _to_float64(df["h"])
        low = _to_float64(df["l"])
        close = _to_float64(df["c"])

        tr = pd.Series(_true_range_numba(high, low, close), index=df.index)
        tr_sum = tr.rolling(window=window, min_periods=window).sum()

        hh = pd.Series(high, index=df.index).rolling(window=window, min_periods=window).max()
        ll = pd.Series(low, index=df.index).rolling(window=window, min_periods=window).min()
        denom = (hh - ll).replace(0, np.nan)

        df["chop"] = 100.0 * (np.log10(tr_sum / denom) / np.log10(window))
        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── VWAP / session features ─────────────────────────

    @staticmethod
    def add_vwap_features(
        df: pd.DataFrame,
        reset_daily: bool = True,
        tz: str = "US/Eastern",
    ) -> pd.DataFrame:
        """
        Computes session VWAP (vwap_sess) + distance fraction (vwap_dist_pct) + cross flags.

        vwap_dist_pct is a DECIMAL FRACTION:
          (close - vwap_sess) / vwap_sess
        so:
          0.02  => +2%
         -0.02  => -2%
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        vol = pd.to_numeric(df.get("v", 0.0), errors="coerce").fillna(0.0).astype(float)
        tp = (pd.to_numeric(df["h"], errors="coerce").astype(float) +
              pd.to_numeric(df["l"], errors="coerce").astype(float) +
              pd.to_numeric(df["c"], errors="coerce").astype(float)) / 3.0

        pv = tp * vol

        is_dt = "ts" in df.columns and pd.api.types.is_datetime64_any_dtype(df["ts"])
        if reset_daily and is_dt:
            ts = df["ts"]
            try:
                ts_local = ts.dt.tz_convert(tz) if getattr(ts.dt, "tz", None) is not None else ts
                sess = ts_local.dt.date
            except Exception:
                sess = ts.dt.date

            pv_cum = pv.groupby(sess).cumsum()
            v_cum = vol.groupby(sess).cumsum()
        else:
            pv_cum = pv.cumsum()
            v_cum = vol.cumsum()

        denom = v_cum.replace(0, np.nan)
        df["vwap_sess"] = (pv_cum / denom).astype(float)

        base = df["vwap_sess"].replace(0, np.nan)
        # IMPORTANT: fraction, not percent
        df["vwap_dist_pct"] = ((pd.to_numeric(df["c"], errors="coerce").astype(float) - df["vwap_sess"]) / base).astype(float)

        prev_delta = (pd.to_numeric(df["c"], errors="coerce").astype(float).shift(1) - df["vwap_sess"].shift(1))
        curr_delta = (pd.to_numeric(df["c"], errors="coerce").astype(float) - df["vwap_sess"])
        df["vwap_cross_up"] = (prev_delta <= 0) & (curr_delta > 0)
        df["vwap_cross_dn"] = (prev_delta >= 0) & (curr_delta < 0)

        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── TSI / Stoch RSI / Force / RVOL ─────────────────────────

    @staticmethod
    def add_tsi(
        df: pd.DataFrame,
        long: int = 25,
        short: int = 13,
        signal: int = 7,
    ) -> pd.DataFrame:
        """
        True Strength Index (TSI) + signal + crosses.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        mom = close.diff()

        ema1 = mom.ewm(span=long, adjust=False, min_periods=long).mean()
        ema2 = ema1.ewm(span=short, adjust=False, min_periods=short).mean()

        ema1_abs = mom.abs().ewm(span=long, adjust=False, min_periods=long).mean()
        ema2_abs = ema1_abs.ewm(span=short, adjust=False, min_periods=short).mean()

        denom = ema2_abs.replace(0, np.nan)
        df["tsi"] = 100.0 * (ema2 / denom)

        if signal and signal > 0:
            df["tsi_signal"] = df["tsi"].ewm(span=signal, adjust=False, min_periods=signal).mean()
            df["tsi_cross_up"] = (df["tsi"].shift(1) <= df["tsi_signal"].shift(1)) & (df["tsi"] > df["tsi_signal"])
            df["tsi_cross_dn"] = (df["tsi"].shift(1) >= df["tsi_signal"].shift(1)) & (df["tsi"] < df["tsi_signal"])
        else:
            df["tsi_signal"] = np.nan
            df["tsi_cross_up"] = False
            df["tsi_cross_dn"] = False

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_stoch_rsi(
        df: pd.DataFrame,
        rsi_window: int = 14,
        stoch_window: int = 14,
        k_smooth: int = 3,
        d_smooth: int = 3,
    ) -> pd.DataFrame:
        """
        Stoch RSI (%K/%D) + crosses.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        if "rsi" not in df.columns:
            df = FudstopTA.compute_wilders_rsi(df, window=rsi_window)

        rsi = pd.to_numeric(df["rsi"], errors="coerce").astype(float)
        rsi_min = rsi.rolling(window=stoch_window, min_periods=stoch_window).min()
        rsi_max = rsi.rolling(window=stoch_window, min_periods=stoch_window).max()
        denom = (rsi_max - rsi_min).replace(0, np.nan)

        stoch_rsi = 100.0 * (rsi - rsi_min) / denom
        df["stoch_rsi"] = stoch_rsi
        df["stoch_rsi_k"] = stoch_rsi.rolling(window=k_smooth, min_periods=k_smooth).mean()
        df["stoch_rsi_d"] = df["stoch_rsi_k"].rolling(window=d_smooth, min_periods=d_smooth).mean()

        df["stoch_rsi_cross_up"] = (df["stoch_rsi_k"].shift(1) <= df["stoch_rsi_d"].shift(1)) & (df["stoch_rsi_k"] > df["stoch_rsi_d"])
        df["stoch_rsi_cross_dn"] = (df["stoch_rsi_k"].shift(1) >= df["stoch_rsi_d"].shift(1)) & (df["stoch_rsi_k"] < df["stoch_rsi_d"])

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_force_index(df: pd.DataFrame, ema_period: int = 13) -> pd.DataFrame:
        """
        Force Index + EMA smoothing.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        vol = pd.to_numeric(df.get("v", 0.0), errors="coerce").fillna(0.0).astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        df["force_index"] = (close.diff() * vol).fillna(0.0)

        if ema_period and ema_period > 1:
            df["force_index_ema"] = df["force_index"].ewm(span=ema_period, adjust=False, min_periods=ema_period).mean()
        else:
            df["force_index_ema"] = np.nan

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_relative_volume(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        RVOL = v / SMA(v, window)
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        vol = pd.to_numeric(df.get("v", 0.0), errors="coerce").fillna(0.0).astype(float)
        vol_ma = vol.rolling(window=window, min_periods=max(5, window // 4)).mean()
        denom = vol_ma.replace(0, np.nan)

        df["rvol"] = (vol / denom).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── squeeze / candle geometry / ADX / momentum flags ─────────────────────────

    @staticmethod
    def add_squeeze_flags(df: pd.DataFrame) -> pd.DataFrame:
        """
        Squeeze flags using:
          upper_band/lower_band (Bollinger)
          keltner_upper/keltner_lower (Keltner)
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        needed = {"upper_band", "lower_band", "keltner_upper", "keltner_lower"}
        if needed.issubset(df.columns):
            squeeze_on = (df["lower_band"] > df["keltner_lower"]) & (df["upper_band"] < df["keltner_upper"])
            squeeze_off = (df["lower_band"] < df["keltner_lower"]) & (df["upper_band"] > df["keltner_upper"])
            df["squeeze_on"] = squeeze_on.fillna(False).astype(bool)
            df["squeeze_off"] = squeeze_off.fillna(False).astype(bool)
            so = df["squeeze_on"]
            df["squeeze_release"] = so.shift(1, fill_value=False) & (~so)
        else:
            df["squeeze_on"] = False
            df["squeeze_off"] = False
            df["squeeze_release"] = False

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_candle_shape_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Wick/body features: hammer/shooting-star/doji + candle color.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        h = pd.to_numeric(df["h"], errors="coerce").astype(float)
        l = pd.to_numeric(df["l"], errors="coerce").astype(float)
        o = pd.to_numeric(df["o"], errors="coerce").astype(float)
        c = pd.to_numeric(df["c"], errors="coerce").astype(float)

        rng = (h - l)
        denom = rng.replace(0, np.nan)

        body = (c - o)
        body_abs = body.abs()

        df["candle_range"] = rng
        df["candle_body"] = body
        df["candle_body_ratio"] = (body_abs / denom).fillna(0.0)

        top = pd.concat([o, c], axis=1).max(axis=1)
        bot = pd.concat([o, c], axis=1).min(axis=1)

        df["upper_wick"] = (h - top)
        df["lower_wick"] = (bot - l)

        df["upper_wick_ratio"] = (df["upper_wick"] / denom).fillna(0.0)
        df["lower_wick_ratio"] = (df["lower_wick"] / denom).fillna(0.0)

        df["is_doji"] = df["candle_body_ratio"] <= 0.10
        df["is_hammer"] = (df["lower_wick_ratio"] >= 0.60) & (df["upper_wick_ratio"] <= 0.20) & (df["candle_body_ratio"] <= 0.30)
        df["is_shooting_star"] = (df["upper_wick_ratio"] >= 0.60) & (df["lower_wick_ratio"] <= 0.20) & (df["candle_body_ratio"] <= 0.30)

        df["candle_green"] = c > o
        df["candle_red"] = c < o

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_adx_clean(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        ADX + DI columns with SQL-friendly names:
          adx, di_plus, di_minus
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = _to_float64(df["h"])
        low = _to_float64(df["l"])
        close = _to_float64(df["c"])

        adx, di_plus, di_minus = _adx_numba(high, low, close, window)
        df["adx"] = adx
        df["di_plus"] = di_plus
        df["di_minus"] = di_minus
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_momentum_flags(df: pd.DataFrame) -> pd.DataFrame:
        """
        Pre-mined booleans that make reversal/momentum mining cleaner:
          adx_strong, di_bull, di_bear,
          macd_bull, macd_bear,
          tsi_bull, tsi_bear,
          trend_regime,
          volume_confirm,
          momentum_confirm_bull, momentum_confirm_bear
        """
        if df is None or df.empty:
            return df

        adx = pd.to_numeric(df.get("adx"), errors="coerce") if "adx" in df.columns else None
        di_plus = pd.to_numeric(df.get("di_plus"), errors="coerce") if "di_plus" in df.columns else None
        di_minus = pd.to_numeric(df.get("di_minus"), errors="coerce") if "di_minus" in df.columns else None

        df["adx_strong"] = (adx >= 25.0) if adx is not None else False
        df["di_bull"] = (di_plus > di_minus) if (di_plus is not None and di_minus is not None) else False
        df["di_bear"] = (di_minus > di_plus) if (di_plus is not None and di_minus is not None) else False

        if "macd_hist" in df.columns:
            mh = pd.to_numeric(df["macd_hist"], errors="coerce").fillna(0.0)
            df["macd_bull"] = mh > 0.0
            df["macd_bear"] = mh < 0.0
        else:
            df["macd_bull"] = False
            df["macd_bear"] = False

        if "tsi" in df.columns:
            tsi = pd.to_numeric(df["tsi"], errors="coerce").fillna(0.0)
            if "tsi_signal" in df.columns:
                sig = pd.to_numeric(df["tsi_signal"], errors="coerce").fillna(0.0)
                df["tsi_bull"] = tsi > sig
                df["tsi_bear"] = tsi < sig
            else:
                df["tsi_bull"] = tsi > 0.0
                df["tsi_bear"] = tsi < 0.0
        else:
            df["tsi_bull"] = False
            df["tsi_bear"] = False

        # Regime: trending when CHOP is low
        if "chop" in df.columns:
            df["trend_regime"] = pd.to_numeric(df["chop"], errors="coerce").fillna(100.0) <= 38.0
        else:
            df["trend_regime"] = False

        # Participation
        if "rvol" in df.columns:
            df["volume_confirm"] = pd.to_numeric(df["rvol"], errors="coerce").fillna(0.0) >= 1.3
        else:
            df["volume_confirm"] = False

        df["momentum_confirm_bull"] = (
            df["trend_regime"].fillna(False)
            & df["adx_strong"].fillna(False)
            & df["di_bull"].fillna(False)
            & df["macd_bull"].fillna(False)
            & df["tsi_bull"].fillna(False)
            & df["volume_confirm"].fillna(False)
        )
        df["momentum_confirm_bear"] = (
            df["trend_regime"].fillna(False)
            & df["adx_strong"].fillna(False)
            & df["di_bear"].fillna(False)
            & df["macd_bear"].fillna(False)
            & df["tsi_bear"].fillna(False)
            & df["volume_confirm"].fillna(False)
        )

        return df

    # ───────────────────────── PPO / TRIX / SDC ─────────────────────────

    @staticmethod
    def add_ppo(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> pd.DataFrame:
        """
        Percentage Price Oscillator (PPO).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        ema_fast = close.ewm(span=fast_period, adjust=False, min_periods=fast_period).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False, min_periods=slow_period).mean()
        denom = ema_slow.replace(0, np.nan)
        df["ppo"] = ((ema_fast - ema_slow) / denom) * 100.0

        df["ppo_signal"] = df["ppo"].ewm(span=signal_period, adjust=False, min_periods=signal_period).mean()
        df["ppo_hist"] = df["ppo"] - df["ppo_signal"]

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_trix(df: pd.DataFrame, window: int = 15, signal_period: int = 9) -> pd.DataFrame:
        """
        TRIX and optional signal line.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        ema1 = close.ewm(span=window, adjust=False, min_periods=window).mean()
        ema2 = ema1.ewm(span=window, adjust=False, min_periods=window).mean()
        ema3 = ema2.ewm(span=window, adjust=False, min_periods=window).mean()
        df["trix"] = ema3.pct_change(fill_method=None) * 100.0

        if signal_period and signal_period > 0:
            df["trix_signal"] = df["trix"].ewm(span=signal_period, adjust=False, min_periods=signal_period).mean()
        else:
            df["trix_signal"] = np.nan

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_sdc_indicator(
        df: pd.DataFrame,
        window: int = 50,
        dev_up: float = 1.5,
        dev_dn: float = 1.5,
    ) -> pd.DataFrame:
        """
        Fast Standard Deviation Channel (SDC) using convolution (no per-row polyfit loops).
        Adds:
          linreg_slope, linreg_intercept, linreg_std, sdc_upper, sdc_lower, sdc_signal
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        n = len(df)
        # pre-create columns
        for col in ("linreg_slope", "linreg_intercept", "linreg_std", "sdc_upper", "sdc_lower"):
            if col not in df.columns:
                df[col] = np.nan
        if "sdc_signal" not in df.columns:
            df["sdc_signal"] = pd.Series([None] * n, dtype="object")

        if n < window:
            return FudstopTA._restore_indicator_df(df, restore)

        y = pd.to_numeric(df["c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64, copy=False)
        y2 = y * y

        w = int(window)
        x = np.arange(w, dtype=np.float64)
        sum_x = x.sum()
        sum_x2 = (x * x).sum()
        denom = (w * sum_x2 - sum_x * sum_x)
        if denom == 0:
            return FudstopTA._restore_indicator_df(df, restore)

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
        df.loc[idx, "linreg_slope"] = slope
        df.loc[idx, "linreg_intercept"] = intercept
        df.loc[idx, "linreg_std"] = std
        df.loc[idx, "sdc_upper"] = upper
        df.loc[idx, "sdc_lower"] = lower

        h = pd.to_numeric(df["h"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64, copy=False)
        l = pd.to_numeric(df["l"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64, copy=False)
        sig_vals = np.where(l[idx] > upper, "above_both", np.where(h[idx] < lower, "below_both", "BETWEEN"))
        sig = np.full(n, None, dtype=object)
        sig[idx] = sig_vals
        df["sdc_signal"] = sig

        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── legacy helpers (kept for compatibility) ─────────────────────────

    @staticmethod
    def compute_angle(series_desc: pd.Series) -> float:
        chronological_data = series_desc.iloc[::-1].copy()
        if len(chronological_data) < 2:
            return 0.0
        x = np.arange(len(chronological_data))
        y = chronological_data.values
        try:
            slope = float(linregress(x, y).slope)
        except Exception:
            return 0.0
        angle_radians = math.atan(slope)
        angle_degrees = math.degrees(angle_radians)
        return 180.0 - angle_degrees

    @staticmethod
    def compute_relative_angle(
        band_series_desc: pd.Series,
        price_series_desc: pd.Series,
        points: int = 4,
    ) -> float:
        if len(band_series_desc) < points or len(price_series_desc) < points:
            return 0.0
        band_chron = band_series_desc.head(points).iloc[::-1].values
        price_chron = price_series_desc.head(points).iloc[::-1].values
        x = np.arange(points)
        try:
            slope_band = float(linregress(x, band_chron).slope)
            slope_price = float(linregress(x, price_chron).slope)
        except Exception:
            return 0.0
        angle_band = 180.0 - math.degrees(math.atan(slope_band))
        angle_price = 180.0 - math.degrees(math.atan(slope_price))
        return angle_band - angle_price



    # ───────────────────────── MACD curvature (optional) ─────────────────────────

    @staticmethod
    def compute_macd_histogram(prices: np.ndarray) -> np.ndarray:
        return _compute_macd_histogram(np.asarray(prices, dtype=np.float64))

    @staticmethod
    def determine_macd_curvature_code(prices: np.ndarray) -> int:
        return int(_determine_macd_curvature_code(np.asarray(prices, dtype=np.float64)))

    @staticmethod
    def macd_curvature_label(prices: np.ndarray) -> str:
        code = int(_determine_macd_curvature_code(np.asarray(prices, dtype=np.float64)))
        mapping = {
            0: "insufficient data",
            1: "diverging bull",
            2: "diverging bear",
            3: "arching bull",
            4: "arching bear",
            5: "converging bull",
            6: "converging bear",
            7: "imminent bullish cross",
            8: "imminent bearish cross",
        }
        return mapping.get(code, "unknown")

    @staticmethod
    def macd_from_close(
        closes: Sequence[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ):
        closes_arr = np.asarray(closes, dtype=np.float64)
        return _macd_core(closes_arr, fast_period, slow_period, signal_period)

    # ───────────────────────── legacy compute_* wrappers ─────────────────────────

    @staticmethod
    def compute_bollinger_bands(
        df: pd.DataFrame,
        window: int = 20,
        num_std: float = 2.0,
    ) -> pd.DataFrame:
        """
        Legacy helper (kept for compatibility): computes bb_mid/bb_upper/bb_lower.
        Prefer add_bollinger_bands() for the full feature set.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        rolling_mean = close.rolling(window=window, min_periods=window).mean()
        rolling_std = close.rolling(window=window, min_periods=window).std(ddof=0)

        df["bb_mid"] = rolling_mean
        df["bb_upper"] = rolling_mean + (rolling_std * num_std)
        df["bb_lower"] = rolling_mean - (rolling_std * num_std)
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def compute_stochastic_oscillator(
        df: pd.DataFrame,
        k_window: int = 14,
        d_window: int = 3,
    ) -> pd.DataFrame:
        """
        Legacy helper (kept for compatibility). Prefer add_stochastic_oscillator().
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)

        low_min = low.rolling(window=k_window, min_periods=k_window).min()
        high_max = high.rolling(window=k_window, min_periods=k_window).max()
        denom = (high_max - low_min).replace(0, np.nan)

        df["stoch_k"] = ((close - low_min) / denom) * 100.0
        df["stoch_d"] = df["stoch_k"].rolling(window=d_window, min_periods=d_window).mean()
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def compute_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Legacy ATR (simple rolling mean of true range).
        Prefer add_atr() for Wilder ATR.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)

        hl = (high - low).abs()
        h_pc = (high - close.shift(1)).abs()
        l_pc = (low - close.shift(1)).abs()

        tr = pd.concat([hl, h_pc, l_pc], axis=1).max(axis=1)
        df["atr"] = tr.rolling(window=window, min_periods=window).mean()
        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def compute_supertrend(
        df: pd.DataFrame,
        atr_multiplier: float = 3.0,
        atr_period: int = 10,
    ) -> pd.DataFrame:
        """
        Supertrend (legacy implementation).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        # Ensure ATR
        if "atr" not in df.columns:
            df = FudstopTA.compute_atr(df, atr_period)

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        atr = pd.to_numeric(df["atr"], errors="coerce").astype(float)

        hl2 = (high + low) / 2.0
        basic_ub = hl2 + (atr_multiplier * atr)
        basic_lb = hl2 - (atr_multiplier * atr)

        final_ub = basic_ub.copy()
        final_lb = basic_lb.copy()

        for i in range(1, len(df)):
            if (basic_ub.iloc[i] < final_ub.iloc[i - 1]) or (close.iloc[i - 1] > final_ub.iloc[i - 1]):
                final_ub.iloc[i] = basic_ub.iloc[i]
            else:
                final_ub.iloc[i] = final_ub.iloc[i - 1]

            if (basic_lb.iloc[i] > final_lb.iloc[i - 1]) or (close.iloc[i - 1] < final_lb.iloc[i - 1]):
                final_lb.iloc[i] = basic_lb.iloc[i]
            else:
                final_lb.iloc[i] = final_lb.iloc[i - 1]

        supertrend = pd.Series(0.0, index=df.index)
        direction = pd.Series(1, index=df.index, dtype=int)

        for i in range(1, len(df)):
            if close.iloc[i] <= final_ub.iloc[i]:
                supertrend.iloc[i] = final_ub.iloc[i]
                direction.iloc[i] = -1
            else:
                supertrend.iloc[i] = final_lb.iloc[i]
                direction.iloc[i] = 1

        df["supertrend"] = supertrend
        df["supertrend_direction"] = direction

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def compute_adx(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """
        Legacy ADX that produces +DI / -DI columns (for compatibility).
        Prefer add_adx_clean() for SQL-friendly names.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        df = FudstopTA.add_adx_clean(df, window=window)
        # Compatibility columns:
        df["+DI"] = df["di_plus"]
        df["-DI"] = df["di_minus"]
        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── Parabolic SAR & volume profile ─────────────────────────

    @staticmethod
    def add_parabolic_sar_signals(
        df: pd.DataFrame,
        af_initial: float = 0.23,
        af_max: float = 0.75,
        bb_period: int = 20,
        bb_mult: float = 2.0,
    ) -> pd.DataFrame:
        """
        Parabolic SAR + comparison to Bollinger Bands.
        Adds:
          psar, psar_direction, psar_long_below_lower_band, psar_short_above_upper_band
        Also adds:
          bb_middle, bb_upper, bb_lower (used only by this PSAR helper)
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        # BB for PSAR context (separate from add_bollinger_bands naming)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        df["bb_middle"] = close.rolling(bb_period, min_periods=bb_period).mean()
        bb_std = close.rolling(bb_period, min_periods=bb_period).std(ddof=0)
        df["bb_upper"] = df["bb_middle"] + bb_mult * bb_std
        df["bb_lower"] = df["bb_middle"] - bb_mult * bb_std

        high = pd.to_numeric(df["h"], errors="coerce").astype(float).to_numpy()
        low = pd.to_numeric(df["l"], errors="coerce").astype(float).to_numpy()
        close_arr = close.to_numpy()

        n = len(df)
        psar = np.full(n, np.nan, dtype=float)
        direction = np.array([None] * n, dtype=object)

        if n < 2:
            df["psar"] = psar
            df["psar_direction"] = direction
            df["psar_long_below_lower_band"] = False
            df["psar_short_above_upper_band"] = False
            return FudstopTA._restore_indicator_df(df, restore)

        # initialize
        if close_arr[1] > close_arr[0]:
            cur_dir = "long"
            psar[0] = low[0]
            ep = max(high[0], high[1])
        else:
            cur_dir = "short"
            psar[0] = high[0]
            ep = min(low[0], low[1])

        psar[1] = psar[0]
        af = af_initial
        direction[0] = cur_dir
        direction[1] = cur_dir

        for i in range(2, n):
            prev_psar = psar[i - 1]
            prev_dir = direction[i - 1]

            if prev_dir == "long":
                new_psar = prev_psar + af * (ep - prev_psar)
                # constrain
                new_psar = min(new_psar, low[i - 1], low[i - 2])
                if low[i] > new_psar:
                    cur_dir = "long"
                    psar[i] = new_psar
                    if high[i] > ep:
                        ep = high[i]
                        af = min(af + af_initial, af_max)
                else:
                    cur_dir = "short"
                    psar[i] = ep
                    ep = low[i]
                    af = af_initial
            else:
                new_psar = prev_psar - af * (prev_psar - ep)
                new_psar = max(new_psar, high[i - 1], high[i - 2])
                if high[i] < new_psar:
                    cur_dir = "short"
                    psar[i] = new_psar
                    if low[i] < ep:
                        ep = low[i]
                        af = min(af + af_initial, af_max)
                else:
                    cur_dir = "long"
                    psar[i] = ep
                    ep = high[i]
                    af = af_initial

            direction[i] = cur_dir

        df["psar"] = psar
        df["psar_direction"] = direction
        df["psar_long_below_lower_band"] = (df["psar_direction"] == "long") & (df["psar"] < df["bb_lower"])
        df["psar_short_above_upper_band"] = (df["psar_direction"] == "short") & (df["psar"] > df["bb_upper"])

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def compute_volume_profile(df_intraday: pd.DataFrame, num_bins: int = 100):
        """
        Compute POC, VAH, VAL from intraday data using a simple volume profile.
        """
        if df_intraday is None or df_intraday.empty:
            return (np.nan, np.nan, np.nan)

        period_low = float(pd.to_numeric(df_intraday["l"], errors="coerce").min())
        period_high = float(pd.to_numeric(df_intraday["h"], errors="coerce").max())
        total_volume = float(pd.to_numeric(df_intraday.get("v", 0), errors="coerce").fillna(0.0).sum())

        if period_low == period_high:
            return (period_low, period_low, period_low)

        bin_edges = np.linspace(period_low, period_high, num_bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        volume_profile = np.zeros(num_bins, dtype=float)

        # lightweight python loop (num_bins=100 => fine)
        for _, row in df_intraday.iterrows():
            bar_low = float(row["l"])
            bar_high = float(row["h"])
            bar_volume = float(row.get("v", 0.0))
            bar_mid = (bar_low + bar_high) / 2.0
            closest_bin = int(np.argmin(np.abs(bin_centers - bar_mid)))
            volume_profile[closest_bin] += bar_volume

        poc_index = int(np.argmax(volume_profile))
        poc_price = float(bin_centers[poc_index])

        cum_volume = float(volume_profile[poc_index])
        lower_idx = poc_index
        upper_idx = poc_index
        target_volume = 0.70 * total_volume

        while cum_volume < target_volume:
            down_vol = volume_profile[lower_idx - 1] if lower_idx > 0 else -1.0
            up_vol = volume_profile[upper_idx + 1] if upper_idx < num_bins - 1 else -1.0

            if down_vol > up_vol:
                if lower_idx > 0:
                    lower_idx -= 1
                    cum_volume += float(volume_profile[lower_idx])
            else:
                if upper_idx < num_bins - 1:
                    upper_idx += 1
                    cum_volume += float(volume_profile[upper_idx])

            if down_vol == -1.0 and up_vol == -1.0:
                break

        vah_price = float(bin_centers[upper_idx])
        val_price = float(bin_centers[lower_idx])
        return (poc_price, vah_price, val_price)

    # ───────────────────────── accumulation/distribution & oscillators ─────────────────────────

    @staticmethod
    def add_accumulation_distribution(df: pd.DataFrame) -> pd.DataFrame:
        """
        Accumulation/Distribution Line (ADL).
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        vol = pd.to_numeric(df.get("v", 0), errors="coerce").fillna(0.0).astype(float)

        pr = (high - low).replace(0, np.nan)
        mfm = ((close - low) - (high - close)) / pr
        mfm = mfm.fillna(0.0)
        df["adl"] = (mfm * vol).cumsum()

        return FudstopTA._restore_indicator_df(df, restore)

    @staticmethod
    def add_ultimate_oscillator(
        df: pd.DataFrame,
        short: int = 7,
        medium: int = 14,
        long: int = 28,
    ) -> pd.DataFrame:
        """
        Ultimate Oscillator.
        """
        df, restore = FudstopTA._prep_indicator_df(df)
        if df is None or df.empty:
            return df

        high = pd.to_numeric(df["h"], errors="coerce").astype(float)
        low = pd.to_numeric(df["l"], errors="coerce").astype(float)
        close = pd.to_numeric(df["c"], errors="coerce").astype(float)
        prev_close = close.shift(1)

        min_low_close = pd.concat([low, prev_close], axis=1).min(axis=1)
        max_high_close = pd.concat([high, prev_close], axis=1).max(axis=1)

        bp = close - min_low_close
        tr = max_high_close - min_low_close

        tr_short = tr.rolling(window=short, min_periods=short).sum().replace(0, np.nan)
        tr_medium = tr.rolling(window=medium, min_periods=medium).sum().replace(0, np.nan)
        tr_long = tr.rolling(window=long, min_periods=long).sum().replace(0, np.nan)

        avg_short = bp.rolling(window=short, min_periods=short).sum() / tr_short
        avg_medium = bp.rolling(window=medium, min_periods=medium).sum() / tr_medium
        avg_long = bp.rolling(window=long, min_periods=long).sum() / tr_long

        df["ultimate_osc"] = 100.0 * ((4.0 * avg_short) + (2.0 * avg_medium) + avg_long) / 7.0

        return FudstopTA._restore_indicator_df(df, restore)

    # ───────────────────────── confluence score (optional) ─────────────────────────

    @staticmethod
    def add_confluence_score(df: pd.DataFrame, macd_sentiment: str) -> pd.DataFrame:
        """
        Multi-factor confluence score. Kept for compatibility with existing callers.
        This is not used by the rule-mining pipeline unless you explicitly enable it.

        Adds:
          score_td9, score_rsi, score_macd, score_bbands, score_volume, score_sdc, confluence_score
        """
        df = df.copy()

        if "ts" in df.columns:
            df = df.sort_values("ts").reset_index(drop=True)

        lower_cols = {c.lower(): c for c in df.columns}

        for col in ("score_td9", "score_rsi", "score_macd", "score_bbands", "score_volume", "score_sdc"):
            if col not in df.columns:
                df[col] = 0

        td_buy_candidates = [
            "td9_buy",
            "td9_buy_count",
            "td_buy",
            "td_buy_count",
            "tdsequential_buy",
            "td_buy_setup",
            "td9buy",
            "td_buycount",
        ]
        td_sell_candidates = [
            "td9_sell",
            "td9_sell_count",
            "td_sell",
            "td_sell_count",
            "tdsequential_sell",
            "td_sell_setup",
            "td9sell",
            "td_sellcount",
        ]

        buy_col = next((lower_cols[n] for n in td_buy_candidates if n in lower_cols), None)
        sell_col = next((lower_cols[n] for n in td_sell_candidates if n in lower_cols), None)

        buy_series = df[buy_col] if buy_col else pd.Series(0, index=df.index, dtype=float)
        sell_series = df[sell_col] if sell_col else pd.Series(0, index=df.index, dtype=float)

        df["score_td9"] = buy_series.apply(FudstopTA._td_points) - sell_series.apply(FudstopTA._td_points)

        rsi_candidates = ["rsi", "rsi_14", "rsi_wilders", "wilders_rsi"]
        rsi_col = next((lower_cols[n] for n in rsi_candidates if n in lower_cols), None)
        rsi = df[rsi_col] if rsi_col else pd.Series(np.nan, index=df.index, dtype=float)

        base_rsi_score = np.select(
            [
                rsi < 20,
                (rsi >= 20) & (rsi < 30),
                rsi > 80,
                (rsi > 70) & (rsi <= 80),
            ],
            [4, 2, -4, -2],
            default=0,
        )

        rsi_cross = pd.Series(0, index=df.index, dtype=int)
        if rsi_col:
            prev_rsi = rsi.shift(1)
            cross_up = (prev_rsi <= 50) & (rsi > 50)
            cross_dn = (prev_rsi >= 50) & (rsi < 50)
            rsi_cross[cross_up] = 1
            rsi_cross[cross_dn] = -1

        df["score_rsi"] = base_rsi_score + rsi_cross

        sent = (macd_sentiment or "").strip().lower()
        macd_points = 3 if sent == "bullish" else (-3 if sent == "bearish" else 0)

        macd_cross = pd.Series(0, index=df.index, dtype=int)
        hist_score = pd.Series(0, index=df.index, dtype=int)

        macd_val = df.get("macd_line")
        macd_sig = df.get("macd_signal")
        macd_hist = df.get("macd_hist")

        if macd_val is not None and macd_sig is not None:
            cross_up = (macd_val.shift(1) < macd_sig.shift(1)) & (macd_val > macd_sig)
            cross_dn = (macd_val.shift(1) > macd_sig.shift(1)) & (macd_val < macd_sig)
            macd_cross = pd.Series(
                np.where(cross_up, 2, np.where(cross_dn, -2, 0)),
                index=df.index,
                dtype=int,
            )

        if macd_hist is not None:
            hist_std = macd_hist.rolling(15, min_periods=5).std()
            hist_z = np.where(hist_std > 0, macd_hist / hist_std, 0)
            hist_score = pd.Series(
                np.select(
                    [hist_z >= 1.0, hist_z <= -1.0],
                    [1, -1],
                    default=0,
                ),
                index=df.index,
                dtype=int,
            )

        df["score_macd"] = macd_points + macd_cross + hist_score

        if {"middle_band", "std"}.issubset(df.columns):
            std = df["std"].replace(0, np.nan)
            bb_z = (df["c"] - df["middle_band"]) / std
            df["score_bbands"] = np.select(
                [
                    bb_z <= -2.0,
                    (bb_z > -2.0) & (bb_z <= -1.0),
                    bb_z >= 2.0,
                    (bb_z < 2.0) & (bb_z >= 1.0),
                ],
                [3, 1, -3, -1],
                default=0,
            ).astype(int)

        open_col = FudstopTA._find_col(df, FudstopTA.OPEN_ALIASES)

        if open_col:
            price_up = (df["c"] > df[open_col])
            price_down = (df["c"] < df[open_col])
        else:
            prev_c = df["c"].shift(1)
            price_up = (df["c"] > prev_c)
            price_down = (df["c"] < prev_c)

        vol = pd.to_numeric(df.get("v", 0), errors="coerce").fillna(0.0)

        vol_ma20 = vol.rolling(20, min_periods=5).mean()
        vol_std20 = vol.rolling(20, min_periods=5).std()

        vol_ratio = pd.Series(np.where(vol_ma20 > 0, vol / vol_ma20, 0.0), index=df.index)
        vol_z = pd.Series(np.where(vol_std20 > 0, (vol - vol_ma20) / vol_std20, 0.0), index=df.index)

        vol_ma5 = vol.rolling(5, min_periods=3).mean()
        vol_trend_ratio = pd.Series(np.where(vol_ma20 > 0, vol_ma5 / vol_ma20, 1.0), index=df.index)

        base_vol_score = pd.Series(
            np.select(
                [
                    (vol_ratio >= 1.8) & price_up,
                    (vol_ratio >= 1.3) & price_up,
                    (vol_ratio >= 1.8) & price_down,
                    (vol_ratio >= 1.3) & price_down,
                ],
                [2, 1, -2, -1],
                default=0,
            ),
            index=df.index,
            dtype=int,
        )

        streak_score = pd.Series(0, index=df.index, dtype=int)
        if "volume_streak" in df.columns:
            streak_score = pd.Series(
                np.select(
                    [
                        (df["volume_streak"] >= 3) & price_up,
                        (df["volume_streak"] <= -3) & price_down,
                    ],
                    [1, -1],
                    default=0,
                ),
                index=df.index,
                dtype=int,
            )

        trend_score = pd.Series(
            np.select(
                [
                    (vol_trend_ratio >= 1.15) & price_up,
                    (vol_trend_ratio >= 1.15) & price_down,
                    (vol_trend_ratio <= 0.85) & price_up,
                    (vol_trend_ratio <= 0.85) & price_down,
                ],
                [1, -1, -1, 1],
                default=0,
            ),
            index=df.index,
            dtype=int,
        )

        vol_z_score = pd.Series(
            np.select(
                [
                    (vol_z >= 2.0) & price_up,
                    (vol_z >= 2.0) & price_down,
                    (vol_z <= -1.0) & price_up,
                    (vol_z <= -1.0) & price_down,
                ],
                [1, -1, -1, 1],
                default=0,
            ),
            index=df.index,
            dtype=int,
        )

        signed_vol = np.where(price_up, vol, np.where(price_down, -vol, 0.0))
        pressure_sum = pd.Series(signed_vol, index=df.index).rolling(10, min_periods=5).sum()
        pressure_ratio = pd.Series(
            np.where(vol_ma20 > 0, pressure_sum / (vol_ma20 * 10.0), 0.0),
            index=df.index,
        )
        pressure_score = pd.Series(
            np.select(
                [pressure_ratio >= 0.15, pressure_ratio <= -0.15],
                [1, -1],
                default=0,
            ),
            index=df.index,
            dtype=int,
        )

        ret = df["c"].pct_change().fillna(0.0)
        abs_ret = ret.abs()
        abs_ret_ma20 = abs_ret.rolling(20, min_periods=5).mean()
        abs_ret_std20 = abs_ret.rolling(20, min_periods=5).std()
        ret_z = pd.Series(
            np.where(abs_ret_std20 > 0, (abs_ret - abs_ret_ma20) / abs_ret_std20, 0.0),
            index=df.index,
        )

        impulse_score = pd.Series(
            np.select(
                [
                    (ret_z >= 1.5) & (vol_z >= 1.0) & (ret > 0),
                    (ret_z >= 1.5) & (vol_z >= 1.0) & (ret < 0),
                ],
                [1, -1],
                default=0,
            ),
            index=df.index,
            dtype=int,
        )

        raw_volume_score = (
            base_vol_score
            + streak_score
            + trend_score
            + vol_z_score
            + pressure_score
            + impulse_score
        ).clip(-6, 6)

        df["score_volume"] = raw_volume_score.shift(1).fillna(0).astype(int)

        vol_confirm = ((vol_ratio >= 1.3) | (vol_z >= 1.0) | (vol_trend_ratio >= 1.15)).shift(1).fillna(False)

        if "candle_completely_below_lower" in df.columns:
            df["score_bbands"] = df["score_bbands"] + np.where(
                df["candle_completely_below_lower"] & vol_confirm,
                1,
                0,
            ).astype(int)

        if "candle_completely_above_upper" in df.columns:
            df["score_bbands"] = df["score_bbands"] + np.where(
                df["candle_completely_above_upper"] & vol_confirm,
                -1,
                0,
            ).astype(int)

        if "sdc_signal" in df.columns:
            df["score_sdc"] = np.select(
                [
                    df["sdc_signal"] == "above_both",
                    df["sdc_signal"] == "below_both",
                ],
                [2, -2],
                default=0,
            )

        components = ["score_td9", "score_rsi", "score_macd", "score_bbands", "score_volume", "score_sdc"]
        df["confluence_score"] = df[components].sum(axis=1)

        return df


# ───────────────────────── MACD curvature helpers ─────────────────────────

@njit(cache=True)
def _compute_macd_histogram(prices: np.ndarray) -> np.ndarray:
    """
    Convenience wrapper returning MACD histogram using default (12,26,9).
    """
    _macd_line, _signal, hist = _macd_core(prices, 12, 26, 9)
    return hist


@njit(cache=True)
def _determine_macd_curvature_code(prices: np.ndarray) -> int:
    """
    Determine a MACD histogram curvature code using refined momentum logic.

    Codes:
      0: insufficient data
      1: diverging bull
      2: diverging bear
      3: arching bull
      4: arching bear
      5: converging bull
      6: converging bear
      7: imminent bullish cross
      8: imminent bearish cross
    """
    hist = _compute_macd_histogram(prices)
    n = len(hist)

    if n < 4:
        return 0

    h1, h2, h3, h4 = hist[n - 4], hist[n - 3], hist[n - 2], hist[n - 1]
    d1 = h2 - h1
    d2 = h3 - h2
    d3 = h4 - h3

    avg_hist_vol = (abs(d1) + abs(d2) + abs(d3)) / 3.0 + 1e-9
    strong_slope_thresh = avg_hist_vol * 0.8
    small_slope_thresh = avg_hist_vol * 0.2

    last = h4
    prev = h3
    slope = last - prev

    # Near-zero histogram, near-zero slope => "imminent" type
    if abs(last) < avg_hist_vol * 0.5 and abs(slope) < small_slope_thresh:
        if last < 0:
            return 7  # imminent bullish cross
        return 8      # imminent bearish cross

    if last > 0:
        if slope > strong_slope_thresh:
            return 1  # diverging bull
        if slope < -strong_slope_thresh:
            return 3  # arching bull
        return 5      # converging bull

    # last < 0
    if slope < -strong_slope_thresh:
        return 2  # diverging bear
    if slope > strong_slope_thresh:
        return 4  # arching bear
    return 6      # converging bear
