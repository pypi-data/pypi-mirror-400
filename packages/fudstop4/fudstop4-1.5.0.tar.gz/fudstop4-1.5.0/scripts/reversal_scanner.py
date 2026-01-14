#!/usr/bin/env python3
import asyncio
import logging
import os
from datetime import datetime, time as dt_time
from typing import Dict, Iterable, List, Optional
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from fudstop4.apis.helpers import generate_webull_headers
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_ta import WebullTA
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

load_dotenv()

ET_ZONE = ZoneInfo("America/New_York")

PATTERNS = [
    {
        "name": "A_mfi_stoch_extreme",
        "signal": "long",
        "hit_rate": 0.812121,
        "wilson_low_95": 0.745673,
        "where": (
            "td_buy_count >= 9 AND rsi <= 24 "
            "AND mfi_extreme = true AND stoch_extreme = true "
            "AND bb_full_extreme = false AND wr_extreme = false "
            "AND cci_extreme = false AND stoch_cross = false "
            "AND ppo_cross = false AND vol_spike = false AND vol_streak = false"
        ),
    },
    {
        "name": "A_mfi_stoch_extreme",
        "signal": "short",
        "hit_rate": 0.816568,
        "wilson_low_95": 0.751406,
        "where": (
            "td_sell_count >= 9 AND rsi >= 76 "
            "AND mfi_extreme = true AND stoch_extreme = true "
            "AND bb_full_extreme = false AND wr_extreme = false "
            "AND cci_extreme = false AND stoch_cross = false "
            "AND ppo_cross = false AND vol_spike = false AND vol_streak = false"
        ),
    },
    {
        "name": "B_wr_cci_stoch_extreme",
        "signal": "long",
        "hit_rate": 0.789855,
        "wilson_low_95": 0.748035,
        "where": (
            "td_buy_count >= 9 AND rsi <= 24 "
            "AND wr_extreme = true AND cci_extreme = true "
            "AND stoch_extreme = true AND mfi_extreme = false "
            "AND bb_full_extreme = false AND stoch_cross = false "
            "AND ppo_cross = false AND vol_spike = false AND vol_streak = false"
        ),
    },
    {
        "name": "B_wr_cci_stoch_extreme",
        "signal": "short",
        "hit_rate": 0.801653,
        "wilson_low_95": 0.757566,
        "where": (
            "td_sell_count >= 9 AND rsi >= 76 "
            "AND wr_extreme = true AND cci_extreme = true "
            "AND stoch_extreme = true AND mfi_extreme = false "
            "AND bb_full_extreme = false AND stoch_cross = false "
            "AND ppo_cross = false AND vol_spike = false AND vol_streak = false"
        ),
    },
    {
        "name": "C_short_stoch_cross",
        "signal": "short",
        "hit_rate": 0.790698,
        "wilson_low_95": 0.751767,
        "where": (
            "td_sell_count >= 9 AND rsi >= 76 "
            "AND mfi_extreme = true AND wr_extreme = true "
            "AND stoch_extreme = true AND stoch_cross = true "
            "AND cci_extreme = false AND bb_full_extreme = false "
            "AND ppo_cross = false AND vol_spike = false AND vol_streak = false"
        ),
    },
]


def _env_list(name: str, default: Iterable[str]) -> List[str]:
    raw = os.environ.get(name)
    if not raw:
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _is_missing(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str):
        stripped = val.strip()
        if stripped in ("", "--"):
            return True
        if stripped.lower() in ("nan", "na", "none", "null"):
            return True
        return False
    try:
        return bool(pd.isna(val))
    except Exception:
        return False


def _safe_float(val, default: float) -> float:
    try:
        if _is_missing(val):
            return default
        return float(str(val).replace("%", "").strip())
    except (TypeError, ValueError):
        return default


def _safe_int(val, default: int) -> int:
    try:
        if _is_missing(val):
            return default
        return int(float(str(val).strip()))
    except (TypeError, ValueError):
        return default


def _safe_bool(val, default: bool = False) -> bool:
    if _is_missing(val):
        return default
    if isinstance(val, str):
        normalized = val.strip().lower()
        if normalized in ("true", "t", "1", "yes", "y"):
            return True
        if normalized in ("false", "f", "0", "no", "n"):
            return False
    return bool(val)


def _is_market_open(now_et: datetime) -> bool:
    if now_et.weekday() >= 5:
        return False
    t = now_et.time()
    return dt_time(9, 30) <= t < dt_time(16, 0)


def _prep_candle_df(df: pd.DataFrame, ticker: str, timespan: str) -> Optional[pd.DataFrame]:
    if df is None or df.empty:
        return None
    df = df.copy()
    df.columns = [str(c).lower() for c in df.columns]
    df = df.rename(
        columns={
            "timestamp": "ts",
            "open": "o",
            "close": "c",
            "high": "h",
            "low": "l",
            "volume": "v",
        }
    )
    df["ticker"] = ticker
    df["timespan"] = timespan
    if "ts" not in df.columns:
        return None
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df = df.dropna(subset=["ts"])
    df = df.sort_values("ts").reset_index(drop=True)
    for col in ("o", "h", "l", "c", "v", "vwap"):
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    return df


def _add_td_counts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["td_buy_count"] = 0
    df["td_sell_count"] = 0
    for i in range(4, len(df)):
        c_now = df.at[i, "c"]
        c_4 = df.at[i - 4, "c"]
        if c_now < c_4:
            prev = df.at[i - 1, "td_buy_count"]
            df.at[i, "td_buy_count"] = prev + 1 if prev > 0 else 1
        else:
            df.at[i, "td_buy_count"] = 0
        if c_now > c_4:
            prev = df.at[i - 1, "td_sell_count"]
            df.at[i, "td_sell_count"] = prev + 1 if prev > 0 else 1
        else:
            df.at[i, "td_sell_count"] = 0
    return df


def _add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    delta = df["c"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100.0 - (100.0 / (1.0 + rs))
    return df


def _add_mfi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    raw_mf = tp * df["v"]
    pos = raw_mf.where(tp > tp.shift(1), 0.0)
    neg = raw_mf.where(tp < tp.shift(1), 0.0)
    pos_sum = pos.rolling(window=window).sum()
    neg_sum = neg.rolling(window=window).sum()
    ratio = pos_sum / neg_sum.replace(0, np.nan)
    mfi = 100.0 - (100.0 / (1.0 + ratio))
    mfi = mfi.mask((neg_sum == 0) & (pos_sum > 0), 100.0)
    mfi = mfi.mask((pos_sum == 0) & (neg_sum > 0), 0.0)
    df["mfi"] = mfi
    return df


def _add_stoch(df: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> pd.DataFrame:
    low_min = df["l"].rolling(window=k_window).min()
    high_max = df["h"].rolling(window=k_window).max()
    denom = high_max - low_min
    stoch_k = np.where(denom != 0, ((df["c"] - low_min) / denom) * 100.0, 0.0)
    df["stoch_k"] = stoch_k
    df["stoch_d"] = pd.Series(stoch_k, index=df.index).rolling(window=d_window).mean()
    return df


def _add_williams_r(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    high_max = df["h"].rolling(window=window).max()
    low_min = df["l"].rolling(window=window).min()
    rng = high_max - low_min
    willr = np.where(rng != 0, -100.0 * (high_max - df["c"]) / rng, 0.0)
    df["williams_r"] = willr
    return df


def _add_cci(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    tp_ma = tp.rolling(window=window).mean()
    mad = tp.rolling(window=window).apply(
        lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
    )
    denom = 0.015 * mad
    cci = np.where(denom != 0, (tp - tp_ma) / denom, 0.0)
    df["cci"] = cci
    return df


def _add_volume_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df["volume_pct_change"] = df["v"].pct_change().fillna(0.0) * 100.0
    n_inc = [0] * len(df)
    n_dec = [0] * len(df)
    for i in range(1, len(df)):
        if df.at[i, "v"] > df.at[i - 1, "v"]:
            n_inc[i] = n_inc[i - 1] + 1
        else:
            n_inc[i] = 0
        if df.at[i, "v"] < df.at[i - 1, "v"]:
            n_dec[i] = n_dec[i - 1] + 1
        else:
            n_dec[i] = 0
    df["volume_increasing_streak"] = n_inc
    df["volume_decreasing_streak"] = n_dec
    return df


def _add_ppo(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = df["c"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["c"].ewm(span=slow, adjust=False).mean()
    denom = ema_slow.replace(0, np.nan)
    df["ppo"] = ((ema_fast - ema_slow) / denom) * 100.0
    df["ppo_signal"] = df["ppo"].ewm(span=signal, adjust=False).mean()
    return df


def _add_bollinger_flags(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    middle = df["c"].rolling(window=window).mean()
    std = df["c"].rolling(window=window).std()
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    df["bb_full_extreme"] = (df["l"] > upper) | (df["h"] < lower)
    return df


def _add_cross_flags(df: pd.DataFrame) -> pd.DataFrame:
    prev_k = df["stoch_k"].shift(1)
    prev_d = df["stoch_d"].shift(1)
    stoch_cross = ((prev_k <= prev_d) & (df["stoch_k"] > df["stoch_d"])) | (
        (prev_k >= prev_d) & (df["stoch_k"] < df["stoch_d"])
    )
    df["stoch_cross"] = stoch_cross.fillna(False)

    prev_ppo = df["ppo"].shift(1)
    prev_sig = df["ppo_signal"].shift(1)
    ppo_cross = ((prev_ppo <= prev_sig) & (df["ppo"] > df["ppo_signal"])) | (
        (prev_ppo >= prev_sig) & (df["ppo"] < df["ppo_signal"])
    )
    df["ppo_cross"] = ppo_cross.fillna(False)
    return df


def _add_extreme_flags(df: pd.DataFrame) -> pd.DataFrame:
    df["mfi_extreme"] = (df["mfi"] <= 15) | (df["mfi"] >= 85)
    df["stoch_extreme"] = (df["stoch_k"] <= 15) | (df["stoch_k"] >= 85)
    df["wr_extreme"] = (df["williams_r"] <= -90) | (df["williams_r"] >= -10)
    df["cci_extreme"] = (df["cci"] <= -175) | (df["cci"] >= 175)
    df["vol_spike"] = df["volume_pct_change"] >= 50
    df["vol_streak"] = df["volume_increasing_streak"] >= 2
    return df


class CandleAnalysisModel:
    def __init__(self, data: List[Dict[str, object]]):
        self.ticker = [i.get("ticker") for i in data]
        self.timespan = [i.get("timespan") for i in data]
        self.ts = [i.get("ts") for i in data]

        self.o = [_safe_float(i.get("o"), 0.0) for i in data]
        self.h = [_safe_float(i.get("h"), 0.0) for i in data]
        self.l = [_safe_float(i.get("l"), 0.0) for i in data]
        self.c = [_safe_float(i.get("c"), 0.0) for i in data]
        self.v = [_safe_float(i.get("v"), 0.0) for i in data]
        self.vwap = [_safe_float(i.get("vwap"), 0.0) for i in data]

        self.td_buy_count = [_safe_int(i.get("td_buy_count"), 0) for i in data]
        self.td_sell_count = [_safe_int(i.get("td_sell_count"), 0) for i in data]

        self.rsi = [_safe_float(i.get("rsi"), 50.0) for i in data]
        self.mfi = [_safe_float(i.get("mfi"), 50.0) for i in data]
        self.stoch_k = [_safe_float(i.get("stoch_k"), 50.0) for i in data]
        self.stoch_d = [_safe_float(i.get("stoch_d"), 50.0) for i in data]
        self.williams_r = [_safe_float(i.get("williams_r"), -50.0) for i in data]
        self.cci = [_safe_float(i.get("cci"), 0.0) for i in data]

        self.volume_pct_change = [_safe_float(i.get("volume_pct_change"), 0.0) for i in data]
        self.volume_increasing_streak = [_safe_int(i.get("volume_increasing_streak"), 0) for i in data]
        self.volume_decreasing_streak = [_safe_int(i.get("volume_decreasing_streak"), 0) for i in data]

        self.mfi_extreme = [_safe_bool(i.get("mfi_extreme")) for i in data]
        self.stoch_extreme = [_safe_bool(i.get("stoch_extreme")) for i in data]
        self.wr_extreme = [_safe_bool(i.get("wr_extreme")) for i in data]
        self.cci_extreme = [_safe_bool(i.get("cci_extreme")) for i in data]
        self.bb_full_extreme = [_safe_bool(i.get("bb_full_extreme")) for i in data]
        self.stoch_cross = [_safe_bool(i.get("stoch_cross")) for i in data]
        self.ppo_cross = [_safe_bool(i.get("ppo_cross")) for i in data]
        self.vol_spike = [_safe_bool(i.get("vol_spike")) for i in data]
        self.vol_streak = [_safe_bool(i.get("vol_streak")) for i in data]

        self.data_dict = {
            "ticker": self.ticker,
            "timespan": self.timespan,
            "ts": self.ts,
            "o": self.o,
            "h": self.h,
            "l": self.l,
            "c": self.c,
            "v": self.v,
            "vwap": self.vwap,
            "td_buy_count": self.td_buy_count,
            "td_sell_count": self.td_sell_count,
            "rsi": self.rsi,
            "mfi": self.mfi,
            "stoch_k": self.stoch_k,
            "stoch_d": self.stoch_d,
            "williams_r": self.williams_r,
            "cci": self.cci,
            "volume_pct_change": self.volume_pct_change,
            "volume_increasing_streak": self.volume_increasing_streak,
            "volume_decreasing_streak": self.volume_decreasing_streak,
            "mfi_extreme": self.mfi_extreme,
            "stoch_extreme": self.stoch_extreme,
            "wr_extreme": self.wr_extreme,
            "cci_extreme": self.cci_extreme,
            "bb_full_extreme": self.bb_full_extreme,
            "stoch_cross": self.stoch_cross,
            "ppo_cross": self.ppo_cross,
            "vol_spike": self.vol_spike,
            "vol_streak": self.vol_streak,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class ReversalSignalModel:
    def __init__(self, data: List[Dict[str, object]]):
        self.ticker = [i.get("ticker") for i in data]
        self.timespan = [i.get("timespan") for i in data]
        self.ts = [i.get("ts") for i in data]
        self.signal = [i.get("signal") for i in data]
        self.pattern = [i.get("pattern") for i in data]
        self.hit_rate = [_safe_float(i.get("hit_rate"), 0.0) for i in data]
        self.wilson_low_95 = [_safe_float(i.get("wilson_low_95"), 0.0) for i in data]

        self.data_dict = {
            "ticker": self.ticker,
            "timespan": self.timespan,
            "ts": self.ts,
            "signal": self.signal,
            "pattern": self.pattern,
            "hit_rate": self.hit_rate,
            "wilson_low_95": self.wilson_low_95,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class ReversalScannerIngestor:
    def __init__(
        self,
        db: PolygonOptions,
        ta: WebullTA,
        tickers: Iterable[str],
        timespans: Iterable[str],
        *,
        candle_count: int = 200,
        concurrency: int = 10,
        sleep_seconds: int = 60,
        market_hours_enabled: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        self.db = db
        self.ta = ta
        self.tickers = list(tickers)
        self.timespans = list(timespans)
        self.candle_count = candle_count
        self.sem = asyncio.Semaphore(concurrency)
        self.sleep_seconds = sleep_seconds
        self.market_hours_enabled = market_hours_enabled
        self.log = logger or logging.getLogger("reversal_scanner")
        if not self.log.handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    async def run_forever(self):
        await self.db.connect()
        try:
            while True:
                now_et = datetime.now(ET_ZONE)
                if self.market_hours_enabled and not _is_market_open(now_et):
                    self.log.info("Market closed (ET). Sleeping %ds", self.sleep_seconds)
                    await asyncio.sleep(self.sleep_seconds)
                    continue
                await self.process_cycle()
                await asyncio.sleep(self.sleep_seconds)
        finally:
            await self.db.close()

    async def process_cycle(self):
        headers = generate_webull_headers(access_token=os.environ.get("ACCESS_TOKEN"))
        tasks = [
            asyncio.create_task(self._fetch_latest(ticker, span, headers))
            for ticker in self.tickers
            for span in self.timespans
        ]
        results = await asyncio.gather(*tasks)
        rows = [r for r in results if r is not None]

        if rows:
            model = CandleAnalysisModel(rows)
            await self.db.batch_upsert_dataframe(
                model.as_dataframe,
                table_name="candle_analysis",
                unique_columns=["ticker", "timespan"],
            )
            self.log.info("Upserted %d candle_analysis rows", len(rows))
        else:
            self.log.info("No candle data rows to upsert")

        signals = await self._scan_signals()
        if signals:
            model = ReversalSignalModel(signals)
            await self.db.batch_upsert_dataframe(
                model.as_dataframe,
                table_name="reversal_scanner_signals",
                unique_columns=["ticker", "timespan", "ts", "signal", "pattern"],
            )
            self.log.info("Upserted %d reversal signals", len(signals))
        else:
            self.log.info("No reversal signals found")

    async def _fetch_latest(self, ticker: str, timespan: str, headers: Dict[str, str]):
        async with self.sem:
            df = await self.ta.get_candle_data(
                ticker=ticker,
                interval=timespan,
                headers=headers,
                count=str(self.candle_count),
            )
        df = _prep_candle_df(df, ticker, timespan)
        if df is None or df.empty:
            return None

        df = _add_td_counts(df)
        df = _add_rsi(df)
        df = _add_mfi(df)
        df = _add_stoch(df)
        df = _add_williams_r(df)
        df = _add_cci(df)
        df = _add_volume_metrics(df)
        df = _add_ppo(df)
        df = _add_bollinger_flags(df)
        df = _add_cross_flags(df)
        df = _add_extreme_flags(df)

        latest = df.iloc[-1]
        return {
            "ticker": latest.get("ticker"),
            "timespan": latest.get("timespan"),
            "ts": latest.get("ts"),
            "o": latest.get("o"),
            "h": latest.get("h"),
            "l": latest.get("l"),
            "c": latest.get("c"),
            "v": latest.get("v"),
            "vwap": latest.get("vwap"),
            "td_buy_count": latest.get("td_buy_count"),
            "td_sell_count": latest.get("td_sell_count"),
            "rsi": latest.get("rsi"),
            "mfi": latest.get("mfi"),
            "stoch_k": latest.get("stoch_k"),
            "stoch_d": latest.get("stoch_d"),
            "williams_r": latest.get("williams_r"),
            "cci": latest.get("cci"),
            "volume_pct_change": latest.get("volume_pct_change"),
            "volume_increasing_streak": latest.get("volume_increasing_streak"),
            "volume_decreasing_streak": latest.get("volume_decreasing_streak"),
            "mfi_extreme": latest.get("mfi_extreme"),
            "stoch_extreme": latest.get("stoch_extreme"),
            "wr_extreme": latest.get("wr_extreme"),
            "cci_extreme": latest.get("cci_extreme"),
            "bb_full_extreme": latest.get("bb_full_extreme"),
            "stoch_cross": latest.get("stoch_cross"),
            "ppo_cross": latest.get("ppo_cross"),
            "vol_spike": latest.get("vol_spike"),
            "vol_streak": latest.get("vol_streak"),
        }

    async def _scan_signals(self) -> List[Dict[str, object]]:
        signals: List[Dict[str, object]] = []
        for pattern in PATTERNS:
            sql = f"""
            WITH latest AS (
                SELECT DISTINCT ON (ticker, timespan) *
                FROM candle_analysis
                ORDER BY ticker, timespan, ts DESC
            )
            SELECT ticker, timespan, ts
            FROM latest
            WHERE {pattern["where"]};
            """
            records = await self.db.fetch(sql)
            if records:
                self.log.info(
                    "Pattern %s (%s) matches: %d",
                    pattern["name"],
                    pattern["signal"],
                    len(records),
                )
            for rec in records:
                signals.append(
                    {
                        "ticker": rec.get("ticker"),
                        "timespan": rec.get("timespan"),
                        "ts": rec.get("ts"),
                        "signal": pattern["signal"],
                        "pattern": pattern["name"],
                        "hit_rate": pattern["hit_rate"],
                        "wilson_low_95": pattern["wilson_low_95"],
                    }
                )
        return signals


async def main():
    tickers = _env_list("REVERSAL_TICKERS", most_active_tickers)
    timespans = _env_list("REVERSAL_TIMESPANS", ["m5"])
    candle_count = _safe_int(os.environ.get("REVERSAL_CANDLE_COUNT"), 200)
    concurrency = _safe_int(os.environ.get("REVERSAL_CONCURRENCY"), 10)
    sleep_seconds = _safe_int(os.environ.get("REVERSAL_SLEEP_SECONDS"), 60)
    market_hours_enabled = os.environ.get("MARKET_HOURS_ENABLED", "1") != "0"

    db = PolygonOptions()
    ta = WebullTA()
    ingestor = ReversalScannerIngestor(
        db=db,
        ta=ta,
        tickers=tickers,
        timespans=timespans,
        candle_count=candle_count,
        concurrency=concurrency,
        sleep_seconds=sleep_seconds,
        market_hours_enabled=market_hours_enabled,
    )
    await ingestor.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
