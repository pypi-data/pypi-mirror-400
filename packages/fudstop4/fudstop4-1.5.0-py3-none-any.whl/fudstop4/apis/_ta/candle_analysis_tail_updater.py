#!/usr/bin/env python3
"""
candle_analysis_tail_updater.py

Continuous tail ingestor for candle_analysis:
- Seeds (and periodically repairs) the last WINDOW_DAYS of candles per ticker×timespan
- Polls the latest candles frequently and upserts only new bars (+ overlap bars)
- Keeps a small rolling window in memory per ticker×timespan (raw OHLCV+vwap)
- Computes indicators (including your newer momentum metrics) before upsert
- Uses a DB write queue to overlap fetch/compute with upserts

It upserts into the SAME candle_analysis table.
"""

import os
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any

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

ta = FudstopTA()
trading = WebullTrading()
db = PolygonOptions()

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# ───────────────────────── config knobs ─────────────────────────
MAX_INFLIGHT_REQUESTS = int(os.getenv("MAX_INFLIGHT_REQUESTS", "120"))
CONNECTOR_LIMIT = int(os.getenv("CONNECTOR_LIMIT", "200"))
SLEEP_INTERVAL = float(os.getenv("SLEEP_INTERVAL", "10"))

WINDOW_DAYS = float(os.getenv("WINDOW_DAYS", "2"))  # tail horizon
SEED_MAX_PAGES = int(os.getenv("SEED_MAX_PAGES", "6"))         # seed/repair paging
SEED_PAGE_COUNT = int(os.getenv("SEED_PAGE_COUNT", "1000"))    # count per seed/repair page

POLL_COUNT = int(os.getenv("POLL_COUNT", "120"))               # quick pull each cycle
WINDOW_ROWS = int(os.getenv("WINDOW_ROWS", "3500"))            # raw bars kept in memory per ticker×timespan

# indicator compute sizes
APPLY_INDICATORS = os.getenv("APPLY_INDICATORS", "true").lower() in ("1", "true", "yes")
INDICATOR_TAIL_ROWS = int(os.getenv("INDICATOR_TAIL_ROWS", "700"))  # compute this many most-recent rows on incremental
OVERLAP_UPSERT_BARS = int(os.getenv("OVERLAP_UPSERT_BARS", "3"))    # re-upsert last N bars (fix shift(-1) features)

# closed candle filtering (prevents rewriting live-forming candle every poll)
ONLY_CLOSED_CANDLES = os.getenv("ONLY_CLOSED_CANDLES", "true").lower() in ("1", "true", "yes")

# periodic repair of last WINDOW_DAYS (fills gaps / vendor corrections)
REPAIR_INTERVAL_SECONDS = float(os.getenv("REPAIR_INTERVAL_SECONDS", "1800"))  # 30 minutes

# DB batching
UPSERT_BATCH_ROWS = int(os.getenv("UPSERT_BATCH_ROWS", "20000"))
DB_QUEUE_MAXSIZE = int(os.getenv("DB_QUEUE_MAXSIZE", "50"))
DB_WRITE_WORKERS = int(os.getenv("DB_WRITE_WORKERS", "1"))

# heavy indicator toggles
ENABLE_PSAR = os.getenv("ENABLE_PSAR", "true").lower() in ("1", "true", "yes")
ENABLE_SDC = os.getenv("ENABLE_SDC", "true").lower() in ("1", "true", "yes")

# Timespans to maintain
TIMESPANS = [t.strip() for t in os.getenv("TIMESPANS", "m1").split(",") if t.strip()]

SPAN_SECONDS = {
    "m1": 60,
    "m5": 300,
    "m15": 900,
    "m30": 1800,
    "m60": 3600,
    "m120": 7200,
    "m240": 14400,
    "d1": 86400,
    "w1": 604800,
}

# Optional fast JSON parsing
try:
    import orjson  # type: ignore
    def _json_loads(b: bytes):
        return orjson.loads(b)
except Exception:
    import json
    def _json_loads(b: bytes):
        return json.loads(b)


def _drop_bad_cols(df: pd.DataFrame) -> pd.DataFrame:
    # Never let invalid/temporary columns hit Postgres
    return df.drop(columns=["+DI", "-DI", "__orig_order"], errors="ignore")


def _closed_cutoff(timespan: str, now_utc: pd.Timestamp) -> Optional[pd.Timestamp]:
    sec = SPAN_SECONDS.get(timespan)
    if not sec:
        return None
    epoch = int(now_utc.timestamp())
    floored = epoch - (epoch % sec)
    cutoff = floored - sec
    return pd.to_datetime(cutoff, unit="s", utc=True)


def _parse_webull_rows(raw_rows: List[str]) -> pd.DataFrame:
    df = pd.DataFrame(
        [r.split(",") for r in raw_rows],
        columns=["ts", "o", "c", "h", "l", "a", "v", "vwap"],
    )
    df = df.drop(columns=["a"], errors="ignore")
    df["ts"] = pd.to_numeric(df["ts"], errors="coerce")
    df = df.dropna(subset=["ts"])
    if df.empty:
        return df
    df["ts"] = pd.to_datetime(df["ts"].astype("int64"), unit="s", utc=True)

    for col in ["o", "c", "h", "l", "v", "vwap"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Normalize to ascending by ts
    df = df.sort_values("ts").reset_index(drop=True)
    return df[["ts", "o", "h", "l", "c", "v", "vwap"]]


def _add_obv_fast(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy().sort_values("ts").reset_index(drop=True)
    close = pd.to_numeric(d["c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    vol = pd.to_numeric(d.get("v", 0), errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    sign = np.sign(np.diff(close, prepend=close[0]))
    d["obv"] = np.cumsum(sign * vol)
    return d


def _add_engulfing_fast(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy().sort_values("ts").reset_index(drop=True)

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

    bullish = prev_red & cur_green & range_engulf & (o < p_c) & (c > p_o)
    bearish = prev_green & cur_red & range_engulf & (o > p_c) & (c < p_o)

    d["bullish_engulfing"] = bullish.fillna(False)
    d["bearish_engulfing"] = bearish.fillna(False)
    return d


def _add_sdc_fast(df: pd.DataFrame, window: int = 50, dev_up: float = 1.5, dev_dn: float = 1.5) -> pd.DataFrame:
    """
    Vectorized replacement for ta.add_sdc_indicator().

    Produces:
      linreg_slope, linreg_intercept, linreg_std, sdc_upper, sdc_lower, sdc_signal
    """
    d = df.copy().sort_values("ts").reset_index(drop=True)
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

    sig_vals = np.where(
        l[idx] > upper,
        "above_both",
        np.where(h[idx] < lower, "below_both", "BETWEEN"),
    )
    sig = np.full(n, None, dtype=object)
    sig[idx] = sig_vals
    d["sdc_signal"] = sig
    return d


class RollingWindow:
    __slots__ = ("raw", "max_rows")

    def __init__(self, max_rows: int):
        self.max_rows = int(max_rows)
        self.raw = pd.DataFrame(columns=["ts", "o", "h", "l", "c", "v", "vwap"])

    @property
    def last_ts(self) -> Optional[pd.Timestamp]:
        if self.raw.empty:
            return None
        return self.raw["ts"].iloc[-1]

    def merge(self, new_df: pd.DataFrame) -> bool:
        if new_df is None or new_df.empty:
            return False

        new_df = new_df[["ts", "o", "h", "l", "c", "v", "vwap"]].copy()
        new_df = new_df.dropna(subset=["ts"])
        if new_df.empty:
            return False

        prev_max = self.last_ts
        has_new = True if prev_max is None else (new_df["ts"].max() > prev_max)

        if self.raw.empty:
            merged = new_df
        else:
            merged = pd.concat([self.raw, new_df], ignore_index=True)

        merged = (
            merged.drop_duplicates(subset=["ts"], keep="last")
            .sort_values("ts")
            .reset_index(drop=True)
        )

        if len(merged) > self.max_rows:
            merged = merged.iloc[-self.max_rows :].reset_index(drop=True)

        self.raw = merged
        return bool(has_new)


async def _db_writer_worker(q: asyncio.Queue, worker_id: int):
    while True:
        item = await q.get()
        if item is None:
            q.task_done()
            return

        df, meta = item
        try:
            df = _drop_bad_cols(df)
            await db.batch_upsert_dataframe(
                df,
                table_name="candle_analysis",
                unique_columns=["ticker", "timespan", "ts"],
            )
            if meta:
                ticker, timespan, tmin, tmax, rows = meta
                print(f"[upsert] {ticker} {timespan} rows={rows} ({tmin} -> {tmax})")
        except Exception as exc:
            print(f"[db-writer-{worker_id}] upsert failed: {repr(exc)}")
        finally:
            q.task_done()


class TailCandleUpdater:
    def __init__(self, *, tickers: List[str], timespans: List[str]):
        self.tickers = list(tickers)
        self.timespans = list(timespans)

        self.sem = asyncio.Semaphore(MAX_INFLIGHT_REQUESTS)
        self._session: Optional[aiohttp.ClientSession] = None

        self._windows: Dict[Tuple[str, str], RollingWindow] = {
            (t, ts): RollingWindow(max_rows=WINDOW_ROWS)
            for t in self.tickers
            for ts in self.timespans
        }

        self._last_repair_epoch: Dict[Tuple[str, str], float] = {}

        self._write_q: Optional[asyncio.Queue] = None
        self._writer_tasks: List[asyncio.Task] = []

    async def __aenter__(self):
        await db.connect()

        self._write_q = asyncio.Queue(maxsize=DB_QUEUE_MAXSIZE)
        for wid in range(max(1, DB_WRITE_WORKERS)):
            self._writer_tasks.append(asyncio.create_task(_db_writer_worker(self._write_q, wid)))

        headers = generate_webull_headers(access_token=ACCESS_TOKEN)
        connector = aiohttp.TCPConnector(
            limit=CONNECTOR_LIMIT,
            limit_per_host=CONNECTOR_LIMIT,
            ttl_dns_cache=300,
        )
        self._session = aiohttp.ClientSession(headers=headers, connector=connector)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._write_q is not None:
            await self._write_q.join()
            for _ in self._writer_tasks:
                await self._write_q.put(None)
            await asyncio.gather(*self._writer_tasks, return_exceptions=True)
            self._writer_tasks.clear()
            self._write_q = None

        if self._session is not None:
            await self._session.close()
            self._session = None

        await db.disconnect()

    async def run_forever(self):
        await self.seed_all()

        while True:
            cycle_start = time.time()
            await self.process_cycle()

            elapsed = time.time() - cycle_start
            sleep_for = max(0.0, SLEEP_INTERVAL - elapsed)
            await asyncio.sleep(sleep_for)

    async def seed_all(self):
        print(f"[seed] last {WINDOW_DAYS} days for {len(self.tickers)} tickers × {len(self.timespans)} spans")
        tasks = [
            asyncio.create_task(self._tick(ticker=t, timespan=ts, force_repair=True))
            for t in self.tickers
            for ts in self.timespans
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def process_cycle(self):
        tasks = [
            asyncio.create_task(self._tick(ticker=t, timespan=ts, force_repair=False))
            for t in self.tickers
            for ts in self.timespans
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _http_get_json(self, url: str) -> Any:
        assert self._session is not None
        for attempt in range(3):
            try:
                async with self.sem:
                    async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        resp.raise_for_status()
                        raw = await resp.read()
                        return _json_loads(raw)
            except Exception:
                await asyncio.sleep(0.35 * (2 ** attempt))
        return None

    async def _fetch_latest(self, *, ticker_id: int, timespan: str, count: int) -> Optional[pd.DataFrame]:
        now_ts = int(time.time())
        url = (
            "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
            f"?type={timespan}&count={int(count)}&timestamp={now_ts}"
            f"&restorationType=0&tickerId={ticker_id}&hasMore=true"
        )

        data = await self._http_get_json(url)
        raw_rows = (data[0] or {}).get("data") if isinstance(data, list) and data else None
        if not raw_rows:
            return None

        df = _parse_webull_rows(raw_rows)
        if df.empty:
            return df

        if ONLY_CLOSED_CANDLES:
            cutoff = _closed_cutoff(timespan, pd.Timestamp.utcnow().tz_localize("UTC"))
            if cutoff is not None:
                df = df[df["ts"] <= cutoff].copy()

        return df

    async def _fetch_window_days(self, *, ticker_id: int, timespan: str) -> Optional[pd.DataFrame]:
        """
        Seed/repair pull: pages backward until ts reaches WINDOW_DAYS cutoff.
        """
        now_epoch = int(time.time())
        cutoff_epoch = now_epoch - int(WINDOW_DAYS * 86400)

        anchor = now_epoch
        rows: List[str] = []
        last_oldest: Optional[int] = None

        for _ in range(max(1, SEED_MAX_PAGES)):
            url = (
                "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
                f"?type={timespan}&count={int(SEED_PAGE_COUNT)}&timestamp={int(anchor)}"
                f"&restorationType=0&tickerId={ticker_id}&hasMore=true"
            )

            data = await self._http_get_json(url)
            raw_rows = (data[0] or {}).get("data") if isinstance(data, list) and data else None
            if not raw_rows:
                break

            page_oldest: Optional[int] = None
            for r in raw_rows:
                parts = r.split(",")
                if not parts:
                    continue
                try:
                    ts_val = int(parts[0])
                except Exception:
                    continue
                if page_oldest is None or ts_val < page_oldest:
                    page_oldest = ts_val

            rows.extend(raw_rows)

            if page_oldest is None:
                break
            if page_oldest <= cutoff_epoch:
                break
            if last_oldest is not None and page_oldest >= last_oldest:
                break

            last_oldest = page_oldest
            anchor = page_oldest - 1

        if not rows:
            return None

        df = _parse_webull_rows(rows)
        if df.empty:
            return df

        cutoff_ts = pd.to_datetime(cutoff_epoch, unit="s", utc=True)
        df = df[df["ts"] >= cutoff_ts].copy()

        if ONLY_CLOSED_CANDLES:
            cutoff = _closed_cutoff(timespan, pd.Timestamp.utcnow().tz_localize("UTC"))
            if cutoff is not None:
                df = df[df["ts"] <= cutoff].copy()

        return df

    def _compute_indicators(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        if df is None or df.empty:
            return df

        d = df.copy()

        # Keep your existing order, then append new metrics.
        steps = [
            ("bollinger_bands", ta.add_bollinger_bands),
            ("aroon", ta.add_aroon),
            ("atr", ta.add_atr),
            ("cci", ta.add_cci),
            ("cmo", ta.add_cmo),
            ("td9_counts", ta.add_td9_counts),
            ("mfi", ta.add_mfi),
            ("stochastic", ta.add_stochastic_oscillator),
            ("awesome_oscillator", ta.add_awesome_oscillator),
            ("donchian", ta.add_donchian_channels),
            ("volume_metrics", ta.add_volume_metrics),
            ("keltner", ta.add_keltner_channels),
            ("chaikin_money_flow", ta.add_chaikin_money_flow),

            # faster vectorized versions
            ("engulfing_patterns_fast", _add_engulfing_fast),
            ("obv_fast", _add_obv_fast),

            ("roc", ta.add_roc),
            ("rsi", ta.compute_wilders_rsi),
            ("williams_r", ta.add_williams_r),
            ("vortex", ta.add_vortex_indicator),
            ("ppo", ta.add_ppo),
            ("trix", ta.add_trix),
        ]

        if ENABLE_PSAR:
            steps.insert(steps.index(("roc", ta.add_roc)), ("parabolic_sar", ta.add_parabolic_sar_signals))

        for name, func in steps:
            try:
                out = func(d)
                if out is not None and not out.empty:
                    d = out
            except Exception as exc:
                print(f"[{ticker}] indicator {name} failed: {exc}")

        # New momentum/confirmation metrics (safe calls; no hard dependency)
        for name, fn in [
            ("stoch_rsi", lambda x: ta.add_stoch_rsi(x)),
            ("macd", lambda x: ta.add_macd(x)),
            ("ema_pack", lambda x: ta.add_ema_pack(x, periods=(9, 21, 50), slope_lookback=3)),
            ("vwap_features", lambda x: ta.add_vwap_features(x, reset_daily=True, tz="US/Eastern")),
            ("tsi", lambda x: ta.add_tsi(x, long=25, short=13, signal=7)),
            ("force_index", lambda x: ta.add_force_index(x, ema_period=13)),
            ("rvol", lambda x: ta.add_relative_volume(x, window=20)),
            ("chop", lambda x: ta.add_choppiness_index(x, window=14)),
            ("band_position_metrics", lambda x: ta.add_band_position_metrics(x)),
            ("squeeze_flags", lambda x: ta.add_squeeze_flags(x)),
            ("candle_shape_metrics", lambda x: ta.add_candle_shape_metrics(x)),
            ("adx_clean", lambda x: ta.add_adx_clean(x, window=14)),
            ("momentum_flags", lambda x: ta.add_momentum_flags(x)),
        ]:
            try:
                out = fn(d)
                if out is not None and not out.empty:
                    d = out
            except Exception as exc:
                print(f"[{ticker}] indicator {name} failed: {exc}")

        if ENABLE_SDC:
            try:
                d = _add_sdc_fast(d, window=50, dev_up=1.5, dev_dn=1.5)
            except Exception as exc:
                print(f"[{ticker}] indicator sdc_fast failed: {exc}")

        d = _drop_bad_cols(d)
        return d

    async def _tick(self, *, ticker: str, timespan: str, force_repair: bool):
        ticker_id = trading.ticker_to_id_map.get(ticker)
        if not ticker_id:
            return

        key = (ticker, timespan)
        win = self._windows[key]
        prev_last_ts = win.last_ts

        now = time.time()
        last_rep = self._last_repair_epoch.get(key, 0.0)
        need_repair = force_repair or ((now - last_rep) >= REPAIR_INTERVAL_SECONDS)

        if win.raw.empty or need_repair:
            df_new = await self._fetch_window_days(ticker_id=ticker_id, timespan=timespan)
            self._last_repair_epoch[key] = now
        else:
            df_new = await self._fetch_latest(ticker_id=ticker_id, timespan=timespan, count=POLL_COUNT)

        if df_new is None or df_new.empty:
            return

        has_new = win.merge(df_new)
        if (not has_new) and (not need_repair):
            return

        raw = win.raw.copy()

        # incremental: compute indicators only on a tail slice
        if not need_repair and prev_last_ts is not None and len(raw) > INDICATOR_TAIL_ROWS:
            raw = raw.iloc[-INDICATOR_TAIL_ROWS:].copy()

        if APPLY_INDICATORS:
            ind_df = self._compute_indicators(raw, ticker)
            if ind_df is None or ind_df.empty:
                return
        else:
            ind_df = raw

        ind_df["ticker"] = ticker
        ind_df["timespan"] = timespan

        # Decide upsert slice
        if prev_last_ts is None or need_repair:
            upsert_df = ind_df.copy()
        else:
            new_rows = ind_df[ind_df["ts"] > prev_last_ts]
            if new_rows.empty:
                return
            min_new_ts = new_rows["ts"].min()

            span = SPAN_SECONDS.get(timespan, 60)
            overlap_sec = span * max(1, OVERLAP_UPSERT_BARS)
            start_ts = min_new_ts - pd.Timedelta(seconds=overlap_sec)

            upsert_df = ind_df[ind_df["ts"] >= start_ts].copy()

        # Restrict writes to last WINDOW_DAYS
        cutoff_ts = pd.Timestamp.utcnow().tz_localize("UTC") - pd.Timedelta(days=WINDOW_DAYS)
        upsert_df = upsert_df[upsert_df["ts"] >= cutoff_ts].copy()
        if upsert_df.empty:
            return

        upsert_df = _drop_bad_cols(upsert_df)

        assert self._write_q is not None
        for start in range(0, len(upsert_df), UPSERT_BATCH_ROWS):
            chunk = upsert_df.iloc[start:start + UPSERT_BATCH_ROWS].copy()
            meta = (ticker, timespan, chunk["ts"].min(), chunk["ts"].max(), len(chunk))
            await self._write_q.put((chunk, meta))


async def main():
    # Optional override: export TICKERS="AAPL,TSLA,MSFT"
    env_tickers = os.getenv("TICKERS", "").strip()
    if env_tickers:
        tickers = [t.strip().upper() for t in env_tickers.split(",") if t.strip()]
    else:
        tickers = list(most_active_tickers)

    async with TailCandleUpdater(tickers=tickers, timespans=TIMESPANS) as runner:
        await runner.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
