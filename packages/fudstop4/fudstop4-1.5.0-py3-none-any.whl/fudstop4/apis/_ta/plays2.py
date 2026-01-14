#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
import inspect
from pathlib import Path
from typing import Dict, Tuple, Optional, Iterable, List
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import numpy as np
import pandas as pd

# ── Project imports (adjust if needed)
project_dir = str(Path(__file__).resolve().parents[2])
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Optional dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from fudstop4.apis._ta.ta_sdk import FudstopTA
from fudstop4.apis.helpers import generate_webull_headers
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_ta import WebullTA
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers


# ───────────────────────── header helper ─────────────────────────
def _make_webull_headers(access_token: Optional[str] = None) -> dict:
    """
    Your repo shows generate_webull_headers() used in two ways:
      - generate_webull_headers()
      - generate_webull_headers(access_token=...)
    This wrapper supports both safely.
    """
    try:
        sig = inspect.signature(generate_webull_headers)
        if "access_token" in sig.parameters:
            return generate_webull_headers(access_token=access_token)
        return generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))
    except Exception:
        # Fallback if signature inspection fails
        try:
            return generate_webull_headers(access_token=access_token)
        except TypeError:
            return generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))


# ───────────────────────── ta_sdk speed patches (same as get_candle_data) ─────────────────────────
def _patch_ta_sdk_for_speed() -> None:
    """
    Same core patches you had in get_candle_data (kept for parity + fewer surprises).
    """
    # 1) Fast _prep: no copy, no sort if ts already monotonic increasing
    def _prep_indicator_df_fast(df: pd.DataFrame):
        if df is None or df.empty:
            return df, False
        if "ts" not in df.columns:
            return df, False
        try:
            ts = df["ts"]
            if getattr(ts, "is_monotonic_increasing", False):
                return df, False
        except Exception:
            pass

        d = df.copy()
        d["__orig_order"] = np.arange(len(d))
        d = d.sort_values("ts").reset_index(drop=True)
        return d, True

    FudstopTA._prep_indicator_df = staticmethod(_prep_indicator_df_fast)

    # 2) Fast Bollinger bands
    def add_bollinger_bands_fast(
        df: pd.DataFrame,
        window: int = 20,
        num_std: float = 2.0,
        trend_points: int = 13,
    ) -> pd.DataFrame:
        d, restore = FudstopTA._prep_indicator_df(df)
        close = pd.to_numeric(d["c"], errors="coerce").astype(float)

        mid = close.rolling(window=window, min_periods=window).mean()
        std = close.rolling(window=window, min_periods=window).std(ddof=0)

        d["middle_band"] = mid
        d["std"] = std
        d["upper_band"] = mid + (num_std * std)
        d["lower_band"] = mid - (num_std * std)

        d["upper_bb_trend"] = pd.Series([None] * len(d), dtype="object")
        d["lower_bb_trend"] = pd.Series([None] * len(d), dtype="object")

        if len(d) >= max(2, trend_points):
            sub_u = d["upper_band"].iloc[-trend_points:][::-1]
            sub_l = d["lower_band"].iloc[-trend_points:][::-1]
            try:
                ut = FudstopTA.compute_trend(sub_u)
            except Exception:
                ut = "flattening"
            try:
                lt = FudstopTA.compute_trend(sub_l)
            except Exception:
                lt = "flattening"

            last_idx = d.index[-1]
            d.at[last_idx, "upper_bb_trend"] = (
                "upper_increasing" if ut == "increasing" else
                "upper_decreasing" if ut == "decreasing" else
                "flattening"
            )
            d.at[last_idx, "lower_bb_trend"] = (
                "lower_increasing" if lt == "increasing" else
                "lower_decreasing" if lt == "decreasing" else
                "flattening"
            )

        if {"h", "l"}.issubset(d.columns):
            h = pd.to_numeric(d["h"], errors="coerce").fillna(0.0)
            l = pd.to_numeric(d["l"], errors="coerce").fillna(0.0)
            d["candle_above_upper"] = (h > d["upper_band"])
            d["candle_below_lower"] = (l < d["lower_band"])

            comp_above = (l > d["upper_band"])
            comp_below = (h < d["lower_band"])
            part_above = (h > d["upper_band"]) & (l <= d["upper_band"])
            part_below = (l < d["lower_band"]) & (h >= d["lower_band"])
        else:
            d["candle_above_upper"] = close > d["upper_band"]
            d["candle_below_lower"] = close < d["lower_band"]
            comp_above = close > d["upper_band"]
            comp_below = close < d["lower_band"]
            part_above = comp_above
            part_below = comp_below

        # match your historical shift behavior
        d["candle_completely_above_upper"] = comp_above.shift(1, fill_value=False)
        d["candle_completely_below_lower"] = comp_below.shift(1, fill_value=False)
        d["candle_partially_above_upper"] = part_above.fillna(False)
        d["candle_partially_below_lower"] = part_below.fillna(False)

        return FudstopTA._restore_indicator_df(d, restore)

    FudstopTA.add_bollinger_bands = staticmethod(add_bollinger_bands_fast)

    # 3) Fast volume metrics
    def add_volume_metrics_fast(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        d, restore = FudstopTA._prep_indicator_df(df)
        v = pd.to_numeric(d.get("v", 0), errors="coerce").fillna(0.0)

        d["volume_diff"] = v.diff().fillna(0.0)
        d["volume_pct_change"] = v.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.0) * 100.0

        inc = v.diff() > 0
        grp = (~inc).cumsum()
        inc_streak = inc.groupby(grp).cumcount() + 1
        d["volume_increasing_streak"] = inc_streak.where(inc, 0).astype(int)

        dec = v.diff() < 0
        grp2 = (~dec).cumsum()
        dec_streak = dec.groupby(grp2).cumcount() + 1
        d["volume_decreasing_streak"] = dec_streak.where(dec, 0).astype(int)

        return FudstopTA._restore_indicator_df(d, restore)

    FudstopTA.add_volume_metrics = staticmethod(add_volume_metrics_fast)

    # 4) TD9 counts
    def add_td9_counts_fast(df: pd.DataFrame) -> pd.DataFrame:
        d, restore = FudstopTA._prep_indicator_df(df)
        closes = pd.to_numeric(d["c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
        td_buy, td_sell = FudstopTA.compute_td9_counts(closes)
        d["td_buy_count"] = td_buy
        d["td_sell_count"] = td_sell
        return FudstopTA._restore_indicator_df(d, restore)

    FudstopTA.add_td9_counts = staticmethod(add_td9_counts_fast)


_patch_ta_sdk_for_speed()


# ───────────────────────── local fast helpers (same as get_candle_data) ─────────────────────────
def _add_obv_fast(df: pd.DataFrame) -> pd.DataFrame:
    d = df
    close = pd.to_numeric(d["c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    vol = pd.to_numeric(d.get("v", 0), errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    direction = np.sign(np.diff(close, prepend=close[0]))
    d["obv"] = np.cumsum(direction * vol)
    return d


def _add_engulfing_fast(df: pd.DataFrame) -> pd.DataFrame:
    d = df
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
    d = df
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


def _drop_bad_cols(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["+DI", "-DI", "__orig_order"], errors="ignore")


# ───────────────────────── indicator pipeline (same pack as get_candle_data) ─────────────────────────
def _indicator_pipeline(
    df_in: pd.DataFrame,
    ticker: str,
    *,
    enable_psar: bool = False,
    enable_sdc: bool = True,
) -> pd.DataFrame:
    if df_in is None or df_in.empty:
        return df_in

    d = df_in

    # Ensure ASC ts
    if "ts" in d.columns:
        d = d.sort_values("ts").reset_index(drop=True)

    ta = FudstopTA()

    steps = [
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

    if enable_psar:
        steps.append(("psar", lambda x: ta.add_parabolic_sar_signals(x)))

    steps.extend([
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
    ])

    if enable_sdc:
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

    if "ts" in d.columns:
        d = d.sort_values("ts").reset_index(drop=True)

    return _drop_bad_cols(d)


# ───────────────────────────────────────────────────────────────────────────────
# Ingestor
# ───────────────────────────────────────────────────────────────────────────────
class Plays2TechnicalsIngestor:
    """
    Webull mini-chart ingestor that computes the *full* get_candle_data indicator pack,
    then upserts ONLY the latest row into table 'plays2' with unique constraint (ticker, timespan).
    """

    DEFAULT_TIMESPANS = ["m1", "m5", "m15", "m30", "m60", "m120", "m240", "d1"]
    TIMESPAN_MAP = {
        "m1": "1min",
        "m5": "5min",
        "m15": "15min",
        "m30": "30min",
        "m60": "1hr",
        "m120": "2hr",
        "m240": "4hr",
        "d1": "day",
        "w1": "week",
        "mth1": "month",
    }

    def __init__(
        self,
        db_client,
        id_client,
        tickers_provider: Iterable[str],
        *,
        sem_limit: int = 60,
        connector_limit: int = 120,
        retries: int = 3,
        retry_delay: float = 0.7,
        sleep_interval: int = 6,
        timespans: Optional[List[str]] = None,
        count: int = 600,
        restoration_type: int = 1,
        extend_trading: int = 0,
        enable_psar: bool = False,
        enable_sdc: bool = True,
        indicators_in_threads: bool = True,
        indicator_workers: Optional[int] = None,
        access_token: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.db = db_client
        self.id_client = id_client
        self.tickers = list(tickers_provider)

        self.sem = asyncio.Semaphore(sem_limit)
        self.connector_limit = connector_limit
        self.retries = retries
        self.retry_delay = retry_delay
        self.sleep_interval = sleep_interval

        self.timespans = timespans or list(self.DEFAULT_TIMESPANS)
        self.count = int(count)
        self.restoration_type = int(restoration_type)
        self.extend_trading = int(extend_trading)

        self.enable_psar = bool(enable_psar)
        self.enable_sdc = bool(enable_sdc)

        self.access_token = access_token or os.getenv("ACCESS_TOKEN")

        self._ticker_id_cache: Dict[str, int] = {}
        self._ticker_lock = asyncio.Lock()
        self._session: Optional[aiohttp.ClientSession] = None

        self._executor: Optional[ThreadPoolExecutor] = None
        if indicators_in_threads:
            workers = indicator_workers or min(8, (os.cpu_count() or 4))
            self._executor = ThreadPoolExecutor(max_workers=max(1, int(workers)))

        self.log = logger or logging.getLogger(__name__)
        if not self.log.handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    async def __aenter__(self):
        await self.db.connect()
        connector = aiohttp.TCPConnector(limit=self.connector_limit, ttl_dns_cache=300)
        self._session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()
            self._session = None
        await self.db.disconnect()
        if self._executor:
            self._executor.shutdown(wait=False)
            self._executor = None

    async def run_forever(self):
        cycle = 0
        try:
            while True:
                cycle += 1
                self.log.info("plays2 cycle %d start", cycle)
                await self.process_cycle()
                self.log.info("plays2 sleeping %d seconds", self.sleep_interval)
                await asyncio.sleep(self.sleep_interval)
        except asyncio.CancelledError:
            self.log.info("run_forever cancelled.")
        except Exception as e:
            self.log.exception("Unexpected error in run_forever: %s", e)

    async def run_once(self):
        async with self:
            await self.process_cycle()

    async def process_cycle(self):
        results = await self._fetch_all()

        # Upsert only the latest row per ticker/timespan
        for (ticker, tspan), df in results.items():
            if df is None or df.empty:
                continue

            normalized = self.TIMESPAN_MAP.get(tspan, tspan)

            latest = df.iloc[-1:].copy()
            latest["ticker"] = ticker
            latest["timespan"] = normalized

            # store ticker_id if you want it
            tid = await self._get_ticker_id(ticker)
            if tid:
                latest["ticker_id"] = tid

            # stringify ts for DB safety
            if "ts" in latest.columns:
                latest["ts"] = latest["ts"].astype(str)

            # replace NaN with None (helps asyncpg)
            latest = latest.replace({np.nan: None})

            # Optional preview
            try:
                cols = [c for c in ["ts", "o", "h", "l", "c", "v", "td_buy_count", "td_sell_count", "rsi", "macd", "macd_signal"] if c in latest.columns]
                if cols:
                    self.log.info("Ticker=%s Timespan=%s latest:\n%s", ticker, normalized, latest[cols].tail(1))
            except Exception:
                pass

            await self.db.batch_upsert_dataframe(
                latest,
                table_name="plays3",
                unique_columns=["ticker", "timespan"],
            )

    async def _fetch_all(self) -> Dict[Tuple[str, str], Optional[pd.DataFrame]]:
        tasks = [
            asyncio.create_task(self._fetch_one(ticker, tspan))
            for ticker in self.tickers
            for tspan in self.timespans
        ]
        out: Dict[Tuple[str, str], Optional[pd.DataFrame]] = {}

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for item in results:
            if isinstance(item, Exception):
                self.log.warning("fetch task failed: %s", item)
                continue
            (ticker, tspan, df) = item
            out[(ticker, tspan)] = df
        return out

    async def _fetch_one(self, ticker: str, timespan: str) -> Tuple[str, str, Optional[pd.DataFrame]]:
        df = await self._fetch_data_for_timespan(ticker, timespan)
        return ticker, timespan, df

    async def _fetch_data_for_timespan(self, ticker: str, timespan: str) -> Optional[pd.DataFrame]:
        assert self._session is not None, "Call inside async context (__aenter__)."

        try:
            async with self.sem:
                ticker_id = await self._get_ticker_id(ticker)
                if not ticker_id:
                    self.log.warning("No Webull ID found for %s", ticker)
                    return None

                url = (
                    "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
                    f"?type={timespan}&count={self.count}"
                    f"&restorationType={self.restoration_type}"
                    f"&extendTrading={self.extend_trading}"
                    f"&loadFactor=1&tickerId={ticker_id}"
                )

                data_json = await self._fetch_with_retries(url)

            if not data_json or not isinstance(data_json, list) or not data_json[0].get("data"):
                self.log.warning("Invalid/empty chart data for %s [%s]", ticker, timespan)
                return None

            raw_data = data_json[0]["data"]

            # Parse to DataFrame
            df = pd.DataFrame(
                [row.split(",") for row in raw_data],
                columns=["ts", "o", "c", "h", "l", "a", "v", "vwap"],
            )
            df.drop(columns=["a"], errors="ignore", inplace=True)

            # Add base identity cols (ta_sdk expects these around)
            df["ticker"] = ticker
            df["timespan"] = self.TIMESPAN_MAP.get(timespan, timespan)

            # Convert/clean
            df["ts"] = pd.to_datetime(pd.to_numeric(df["ts"], errors="coerce"), unit="s", utc=True)
            df = df.dropna(subset=["ts"])
            if df.empty:
                return None

            for col in ["o", "c", "h", "l", "v", "vwap"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

            df = df.sort_values("ts").reset_index(drop=True)

            # Run the full indicator pack (threaded if enabled)
            df_out = await self._apply_indicators(df, ticker)
            return df_out

        except Exception as e:
            self.log.error("Fetch failed for %s [%s]: %s", ticker, timespan, e)
            return None

    async def _apply_indicators(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        if self._executor is None:
            return _indicator_pipeline(df, ticker, enable_psar=self.enable_psar, enable_sdc=self.enable_sdc)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor,
            _indicator_pipeline,
            df,
            ticker,
            # keyword-only args need wrapping; easiest is lambda-less by using functools.partial,
            # but keep it simple: pipeline reads these from defaults unless passed.
            # We'll call a tiny wrapper here.
        )

    async def _get_ticker_id(self, ticker: str) -> Optional[int]:
        async with self._ticker_lock:
            if ticker in self._ticker_id_cache:
                return self._ticker_id_cache[ticker]

            mapping = getattr(self.id_client, "ticker_to_id_map", {}) or {}
            tid = mapping.get(ticker)
            if tid:
                self._ticker_id_cache[ticker] = tid
                return tid
            return None

    async def _fetch_with_retries(self, url: str) -> dict:
        assert self._session is not None

        last_exc: Optional[Exception] = None
        for attempt in range(self.retries):
            try:
                headers = _make_webull_headers(self.access_token)
                async with self._session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=12),
                ) as resp:
                    if resp.status == 429:
                        # basic backoff on rate limit
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                        continue
                    resp.raise_for_status()
                    return await resp.json()
            except Exception as exc:
                last_exc = exc
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise

        raise last_exc if last_exc else RuntimeError("request failed")


# ───────────────────────────────────────────────────────────────────────────────
# Fix for threaded indicator call keyword-only args:
# We'll override _apply_indicators with a proper executor wrapper.
# (Kept outside class definition for readability)
# ───────────────────────────────────────────────────────────────────────────────
from functools import partial

async def _apply_indicators_threaded(self: Plays2TechnicalsIngestor, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if self._executor is None:
        return _indicator_pipeline(df, ticker, enable_psar=self.enable_psar, enable_sdc=self.enable_sdc)

    loop = asyncio.get_running_loop()
    fn = partial(_indicator_pipeline, ticker=ticker, enable_psar=self.enable_psar, enable_sdc=self.enable_sdc)
    # partial expects df as the first positional arg
    return await loop.run_in_executor(self._executor, fn, df)

Plays2TechnicalsIngestor._apply_indicators = _apply_indicators_threaded


# ───────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ───────────────────────────────────────────────────────────────────────────────
async def main():
    db = PolygonOptions()
    wb = WebullTA()

    ingestor = Plays2TechnicalsIngestor(
        db_client=db,
        id_client=wb,
        tickers_provider=most_active_tickers,
        # knobs:
        sem_limit=30,
        connector_limit=160,
        count=300,                 # enough for SDC(50) + EMA/VWAP warmup
        sleep_interval=6,
        enable_psar=False,         # heavy; match your get_candle_data defaults
        enable_sdc=True,
        indicators_in_threads=True,
        indicator_workers=min(8, (os.cpu_count() or 4)),
    )

    async with ingestor:
        await ingestor.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
