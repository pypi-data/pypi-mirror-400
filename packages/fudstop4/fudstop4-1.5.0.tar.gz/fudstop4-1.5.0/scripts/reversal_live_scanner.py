#!/usr/bin/env python3
"""
reversal_live_scanner_true.py

Live ingestion + reversal scanner that:
- pulls latest Webull mini-chart candles per ticker × timespan
- keeps only a rolling window in memory
- computes indicators via FudstopTA (ta_sdk)
- scans ONLY CLOSED candles (prevents "forming candle" noise)
- emits ONLY ONE best signal per (ticker,timespan,candle) to avoid spam
- optional DB upserts to snapshot/signals tables

Key fixes vs prior version:
1) Bollinger "band" flags align with ta_sdk.add_bollinger_bands (which shifts full-band flags to the NEXT bar).
   This matters a lot for "instant reversal" correctness.
2) Rule set is intentionally smaller + more confirmatory (trigger required) to reduce false positives.
3) Side-level cooldown prevents repeat firing while oversold/overbought persists.
"""
from __future__ import annotations

import os
import asyncio
import logging
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import aiohttp
import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# --- project deps (same pattern as plays.py / get_candle_data.py) ---
from fudstop4.apis.helpers import generate_webull_headers
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_ta import WebullTA
from fudstop4.apis._ta.ta_sdk import FudstopTA


@dataclass(frozen=True)
class ReversalRule:
    name: str
    side: str               # "long" or "short"
    est_hit_rate: float     # ranking hint
    predicate: Callable[[pd.Series], bool]


class RollingWindow:
    __slots__ = ("raw", "max_rows")

    def __init__(self, max_rows: int):
        self.max_rows = int(max_rows)
        self.raw: pd.DataFrame = pd.DataFrame(columns=["ts", "o", "h", "l", "c", "v", "vwap"])

    def append_new(self, new_rows: pd.DataFrame) -> bool:
        if new_rows is None or new_rows.empty:
            return False

        new_rows = new_rows[["ts", "o", "h", "l", "c", "v", "vwap"]].copy()
        new_rows = new_rows.dropna(subset=["ts"])
        if new_rows.empty:
            return False

        prev_max = self.raw["ts"].max() if not self.raw.empty else None
        has_new = True if prev_max is None else (new_rows["ts"].max() > prev_max)

        merged = new_rows if self.raw.empty else pd.concat([self.raw, new_rows], ignore_index=True)
        merged = (
            merged.drop_duplicates(subset=["ts"], keep="last")
            .sort_values("ts")
            .reset_index(drop=True)
        )

        if len(merged) > self.max_rows:
            merged = merged.iloc[-self.max_rows :].reset_index(drop=True)

        self.raw = merged
        return bool(has_new)

    @property
    def last_ts(self) -> Optional[pd.Timestamp]:
        if self.raw.empty:
            return None
        return self.raw["ts"].iloc[-1]


class LiveReversalScanner:
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
    }
    TIMESPAN_SECONDS = {
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

    def __init__(
        self,
        *,
        tickers: Iterable[str],
        timespans: List[str],
        db_client: Optional[PolygonOptions] = None,
        ta_client: Optional[WebullTA] = None,
        sem_limit: int = 75,
        connector_limit: int = 105,
        retries: int = 3,
        retry_delay: float = 1.0,
        sleep_interval: float = 6.0,
        seed_count: int = 120,
        poll_count: int = 25,
        window_rows: int = 160,
        scan_only_closed_candles: bool = True,
        signal_cooldown_bars: int = 5,
        log_signals: bool = True,
        upsert_snapshot_table: Optional[str] = None,
        upsert_signals_table: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.tickers = list(tickers)
        self.timespans = list(timespans)

        self.db = db_client
        self.ta = ta_client or WebullTA()
        self.ta_ind = FudstopTA()

        self.sem = asyncio.Semaphore(int(sem_limit))
        self.connector_limit = int(connector_limit)
        self.retries = int(retries)
        self.retry_delay = float(retry_delay)
        self.sleep_interval = float(sleep_interval)

        self.seed_count = int(seed_count)
        self.poll_count = int(poll_count)
        self.window_rows = int(window_rows)

        self.scan_only_closed_candles = bool(scan_only_closed_candles)
        self.signal_cooldown_bars = int(signal_cooldown_bars)

        self.log_signals = bool(log_signals)
        self.upsert_snapshot_table = upsert_snapshot_table
        self.upsert_signals_table = upsert_signals_table

        self._ticker_id_cache: Dict[str, int] = {}
        self._ticker_lock = asyncio.Lock()

        self._session: Optional[aiohttp.ClientSession] = None

        self._windows: Dict[Tuple[str, str], RollingWindow] = {
            (t, ts): RollingWindow(max_rows=self.window_rows)
            for t in self.tickers
            for ts in self.timespans
        }

        # Last scanned CLOSED candle per (ticker,timespan) to avoid missing bars
        self._last_scanned_ts: Dict[Tuple[str, str], pd.Timestamp] = {}

        # Side-level cooldown: last fired ts per (ticker,timespan,side)
        self._last_fired_side_ts: Dict[Tuple[str, str, str], pd.Timestamp] = {}

        self.rules: List[ReversalRule] = self._build_rules()

        self.log = logger or logging.getLogger(__name__)
        if not self.log.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
            )

    async def __aenter__(self):
        if self.db is not None:
            await self.db.connect()
        connector = aiohttp.TCPConnector(limit=self.connector_limit)
        self._session = aiohttp.ClientSession(
            connector=connector,
            headers=generate_webull_headers(access_token=os.environ.get("ACCESS_TOKEN")),
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()
            self._session = None
        if self.db is not None:
            await self.db.disconnect()

    async def run_forever(self):
        cycle = 0
        while True:
            cycle += 1
            await self.process_cycle(cycle=cycle)
            await asyncio.sleep(self.sleep_interval)

    async def process_cycle(self, *, cycle: int):
        assert self._session is not None, "Use within async context manager"
        tasks = [
            asyncio.create_task(self._tick(ticker=t, timespan=ts, cycle=cycle))
            for t in self.tickers
            for ts in self.timespans
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _tick(self, *, ticker: str, timespan: str, cycle: int):
        key = (ticker, timespan)
        win = self._windows[key]

        count = self.seed_count if win.last_ts is None else self.poll_count
        df_raw = await self._fetch_chart_raw(ticker=ticker, timespan=timespan, count=count)
        if df_raw is None or df_raw.empty:
            return

        has_new = win.append_new(df_raw)
        if not has_new and win.last_ts is not None:
            return

        ind_df = self._compute_reversal_indicators(win.raw)
        if ind_df is None or ind_df.empty:
            return

        ind_df = ind_df.sort_values("ts").reset_index(drop=True)

        # Determine which timestamps are SAFE to scan (closed candles only).
        cutoff_ts = None
        if not self.scan_only_closed_candles:
            cutoff_ts = ind_df["ts"].iloc[-1]
        else:
            bar_secs = self.TIMESPAN_SECONDS.get(timespan, 60)
            now_utc = pd.Timestamp.now(tz="UTC")
            last_ts = ind_df["ts"].iloc[-1]

            # if the most recent bar is still forming, use the prior bar as the latest closed bar
            if now_utc < (last_ts + pd.Timedelta(seconds=bar_secs)):
                if len(ind_df) < 2:
                    return
                cutoff_ts = ind_df["ts"].iloc[-2]
            else:
                cutoff_ts = last_ts

        prev_scanned = self._last_scanned_ts.get(key)
        if prev_scanned is None:
            # on first cycle, only scan the latest closed candle (avoids historical spam)
            candidates = ind_df[ind_df["ts"] == cutoff_ts]
        else:
            candidates = ind_df[(ind_df["ts"] > prev_scanned) & (ind_df["ts"] <= cutoff_ts)]

        if candidates.empty:
            # still update last scanned if we have a valid cutoff
            if cutoff_ts is not None and (prev_scanned is None or cutoff_ts > prev_scanned):
                self._last_scanned_ts[key] = cutoff_ts
            return

        # Optional snapshot upsert (latest row only)
        if self.db is not None and self.upsert_snapshot_table:
            latest = ind_df[ind_df["ts"] == cutoff_ts].tail(1).copy()
            if not latest.empty:
                latest["ticker"] = ticker
                latest["timespan"] = self.TIMESPAN_MAP.get(timespan, timespan)
                latest["ts"] = latest["ts"].astype(str)
                await self.db.batch_upsert_dataframe(
                    latest,
                    table_name=self.upsert_snapshot_table,
                    unique_columns=["ticker", "timespan"],
                )

        # Evaluate: ONLY 1 best rule per candle (prevents multi-rule spam).
        signals: List[dict] = []
        for _, row in candidates.iterrows():
            # side cooldown check helper
            def _cooldown_ok(side: str) -> bool:
                last_fire = self._last_fired_side_ts.get((ticker, timespan, side))
                if last_fire is None:
                    return True
                bar_secs = self.TIMESPAN_SECONDS.get(timespan, 60)
                cooldown_secs = max(1, self.signal_cooldown_bars) * bar_secs
                return (row["ts"] - last_fire).total_seconds() >= cooldown_secs

            matched: List[ReversalRule] = []
            for rule in self.rules:
                if not _cooldown_ok(rule.side):
                    continue
                try:
                    if rule.predicate(row):
                        matched.append(rule)
                except Exception:
                    continue

            if not matched:
                continue

            best = max(matched, key=lambda r: r.est_hit_rate)

            # stamp cooldown at the candle ts
            self._last_fired_side_ts[(ticker, timespan, best.side)] = row["ts"]

            sig = {
                "ticker": ticker,
                "timespan": self.TIMESPAN_MAP.get(timespan, timespan),
                "ts": str(row["ts"]),
                "side": best.side,
                "rule": best.name,
                "est_hit_rate": float(best.est_hit_rate),
                # core diagnostics (keep small; extend if your DB schema supports it)
                "td_buy_count": int(row.get("td_buy_count", 0) or 0),
                "td_sell_count": int(row.get("td_sell_count", 0) or 0),
                "rsi": float(row.get("rsi", np.nan)),
                "mfi": float(row.get("mfi", np.nan)),
                "stoch_k": float(row.get("stoch_k", np.nan)),
                "williams_r": float(row.get("williams_r", np.nan)),
                "cci": float(row.get("cci", np.nan)),
                "bb_width": float(row.get("bb_width", np.nan)),
                "band_above_full": bool(row.get("band_above_full", False)),
                "band_below_full": bool(row.get("band_below_full", False)),
                "stoch_cross_up": bool(row.get("stoch_cross_up", False)),
                "stoch_cross_dn": bool(row.get("stoch_cross_dn", False)),
                "bullish_engulfing": bool(row.get("bullish_engulfing", False)),
                "bearish_engulfing": bool(row.get("bearish_engulfing", False)),
                "volume_pct_change": float(row.get("volume_pct_change", np.nan)),
            }
            signals.append(sig)

            if self.log_signals:
                self.log.info(
                    "TRUE_REV %s %s %s rule=%s rsi=%.2f mfi=%.2f stoch=%.2f tdB=%s tdS=%s bandFull(%s/%s) bbW=%.3f",
                    ticker,
                    timespan,
                    best.side.upper(),
                    best.name,
                    sig["rsi"],
                    sig["mfi"],
                    sig["stoch_k"],
                    sig["td_buy_count"],
                    sig["td_sell_count"],
                    sig["band_below_full"],
                    sig["band_above_full"],
                    sig["bb_width"] if not np.isnan(sig["bb_width"]) else -1,
                )

        # Persist signals (optional)
        if signals and self.db is not None and self.upsert_signals_table:
            sig_df = pd.DataFrame(signals)
            await self.db.batch_upsert_dataframe(
                sig_df,
                table_name=self.upsert_signals_table,
                unique_columns=["ticker", "timespan", "rule", "ts"],
            )

        # advance last scanned to cutoff (closed candle)
        self._last_scanned_ts[key] = candidates["ts"].max()

    # ───────────────────────────── fetching ─────────────────────────────
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
        last_exc: Optional[Exception] = None
        for attempt in range(self.retries):
            try:
                async with self.sem:
                    async with self._session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        resp.raise_for_status()
                        return await resp.json()
            except Exception as exc:
                last_exc = exc
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.retry_delay)
        raise last_exc if last_exc else RuntimeError("fetch failed")

    async def _fetch_chart_raw(self, *, ticker: str, timespan: str, count: int) -> Optional[pd.DataFrame]:
        ticker_id = await self._get_ticker_id(ticker)
        if not ticker_id:
            return None

        url = (
            "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
            f"?type={timespan}&count={int(count)}&restorationType=1&extendTrading=0&loadFactor=1"
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
        df = df.drop(columns=["a"], errors="ignore")

        num_cols = ["o", "c", "h", "l", "v", "vwap"]
        df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)

        # reverse to ascending time
        df = df.iloc[::-1].reset_index(drop=True)
        return df[["ts", "o", "h", "l", "c", "v", "vwap"]]

    # ───────────────────────────── indicators ─────────────────────────────
    def _compute_reversal_indicators(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        IMPORTANT: uses add_bollinger_bands (not compute_bollinger_bands)
        so that:
          - full-band flags are shifted to the NEXT candle (instant reversal alignment)
          - the band flags match what get_candle_data.py produces
        """
        if raw_df is None or raw_df.empty:
            return raw_df

        df = raw_df.copy().sort_values("ts").reset_index(drop=True)

        # Minimal, high-signal indicators
        steps = [
            ("bollinger_bands", lambda d: self.ta_ind.add_bollinger_bands(d, window=20, num_std=2, trend_points=13)),
            ("td9_counts", self.ta_ind.add_td9_counts),
            ("rsi", lambda d: self.ta_ind.compute_wilders_rsi(d, window=14)),
            ("mfi", lambda d: self.ta_ind.add_mfi(d, window=14)),
            ("stoch", lambda d: self.ta_ind.add_stochastic_oscillator(d, window=14, smooth_window=3)),
            ("williams_r", lambda d: self.ta_ind.add_williams_r(d, window=14)),
            ("cci", lambda d: self.ta_ind.add_cci(d, window=20)),
            ("volume_metrics", lambda d: self.ta_ind.add_volume_metrics(d, window=5)),
            ("engulfing", self.ta_ind.add_engulfing_patterns),
        ]

        for _, func in steps:
            try:
                out = func(df)
                if out is not None:
                    df = out
            except Exception:
                # keep running if an indicator step fails
                pass

        # normalize order
        df = df.sort_values("ts").reset_index(drop=True)

        # --- Bollinger-derived helpers (from add_bollinger_bands outputs) ---
        # add_bollinger_bands outputs: middle_band, upper_band, lower_band
        if {"middle_band", "upper_band", "lower_band"}.issubset(df.columns):
            denom = df["middle_band"].replace(0, np.nan)
            df["bb_width"] = (df["upper_band"] - df["lower_band"]) / denom
            df["bb_width"] = df["bb_width"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        else:
            df["bb_width"] = 0.0

        # band flags: align with ta_sdk naming + shifting behavior
        df["band_above"] = df.get("candle_above_upper", False).fillna(False) if "candle_above_upper" in df.columns else False
        df["band_below"] = df.get("candle_below_lower", False).fillna(False) if "candle_below_lower" in df.columns else False

        # Full-band flags are already shifted by add_bollinger_bands (instant reversal alignment)
        df["band_above_full"] = df.get("candle_completely_above_upper", False).fillna(False) if "candle_completely_above_upper" in df.columns else False
        df["band_below_full"] = df.get("candle_completely_below_lower", False).fillna(False) if "candle_completely_below_lower" in df.columns else False

        df["bb_full_extreme"] = df["band_above_full"] | df["band_below_full"]

        # stoch crosses
        if {"stoch_k", "stoch_d"}.issubset(df.columns):
            df["stoch_cross_up"] = (df["stoch_k"].shift(1) <= df["stoch_d"].shift(1)) & (df["stoch_k"] > df["stoch_d"])
            df["stoch_cross_dn"] = (df["stoch_k"].shift(1) >= df["stoch_d"].shift(1)) & (df["stoch_k"] < df["stoch_d"])
        else:
            df["stoch_cross_up"] = False
            df["stoch_cross_dn"] = False

        return df

    # ───────────────────────────── rules ─────────────────────────────
    def _build_rules(self) -> List[ReversalRule]:
        """
        Smaller, confirmatory rule pack designed for "true" reversals:
        - requires BOTH exhaustion + confirmation trigger
        - avoids extremely broad "one-indicator" rules that spam

        Triggers (at least one):
          long: band_below_full OR stoch_cross_up OR bullish_engulfing
          short: band_above_full OR stoch_cross_dn OR bearish_engulfing
        """
        def f(r: pd.Series, k: str, d: float) -> float:
            try:
                v = r.get(k, d)
                return d if v is None else float(v)
            except Exception:
                return d

        def i(r: pd.Series, k: str) -> int:
            try:
                v = r.get(k, 0)
                return 0 if v is None else int(v)
            except Exception:
                return 0

        def b(r: pd.Series, k: str) -> bool:
            return bool(r.get(k, False))

        def vol_ok(r: pd.Series) -> bool:
            # original mining found "no vol spike / no streak" helped
            vpc = f(r, "volume_pct_change", 0.0)
            inc = i(r, "volume_increasing_streak")
            dec = i(r, "volume_decreasing_streak")
            return (vpc < 50.0) and (inc < 2) and (dec < 2)

        def long_trigger(r: pd.Series) -> bool:
            return b(r, "band_below_full") or b(r, "stoch_cross_up") or b(r, "bullish_engulfing")

        def short_trigger(r: pd.Series) -> bool:
            return b(r, "band_above_full") or b(r, "stoch_cross_dn") or b(r, "bearish_engulfing")

        def long_color_ok(r: pd.Series) -> bool:
            # reversal candle confirmation: green candle or bullish engulfing
            return (f(r, "c", 0.0) > f(r, "o", 0.0)) or b(r, "bullish_engulfing")

        def short_color_ok(r: pd.Series) -> bool:
            # reversal candle confirmation: red candle or bearish engulfing
            return (f(r, "c", 0.0) < f(r, "o", 0.0)) or b(r, "bearish_engulfing")

        def long_extreme_count(r: pd.Series) -> int:
            cnt = 0
            if f(r, "mfi", 999.0) <= 20.0: cnt += 1
            if f(r, "stoch_k", 999.0) <= 20.0: cnt += 1
            if f(r, "williams_r", 0.0) <= -85.0: cnt += 1
            if f(r, "cci", 0.0) <= -150.0: cnt += 1
            return cnt

        def short_extreme_count(r: pd.Series) -> int:
            cnt = 0
            if f(r, "mfi", -999.0) >= 80.0: cnt += 1
            if f(r, "stoch_k", -999.0) >= 80.0: cnt += 1
            if f(r, "williams_r", -100.0) >= -15.0: cnt += 1
            if f(r, "cci", 0.0) >= 150.0: cnt += 1
            return cnt

        # Core "true reversal" consensus rules (generic)
        def true_rev_long(r: pd.Series) -> bool:
            return (
                (i(r, "td_buy_count") >= 9)
                and (f(r, "rsi", 999.0) <= 30.0)
                and (long_extreme_count(r) >= 2)
                and long_trigger(r)
                and long_color_ok(r)
                and (f(r, "bb_width", 0.0) >= 0.02)
                and vol_ok(r)
            )

        def true_rev_short(r: pd.Series) -> bool:
            return (
                (i(r, "td_sell_count") >= 9)
                and (f(r, "rsi", -999.0) >= 70.0)
                and (short_extreme_count(r) >= 2)
                and short_trigger(r)
                and short_color_ok(r)
                and (f(r, "bb_width", 0.0) >= 0.02)
                and vol_ok(r)
            )

        # High-confidence mined families, but add a trigger so they don't fire endlessly while pinned
        def mined_mfi_stoch_long(r: pd.Series) -> bool:
            return (
                (i(r, "td_buy_count") >= 9)
                and (f(r, "rsi", 999.0) <= 24.0)
                and (f(r, "mfi", 999.0) <= 15.0)
                and (f(r, "stoch_k", 999.0) <= 15.0)
                and (f(r, "williams_r", 0.0) > -90.0)
                and (f(r, "cci", 0.0) > -175.0)
                and long_trigger(r)
                and long_color_ok(r)
                and vol_ok(r)
            )

        def mined_mfi_stoch_short(r: pd.Series) -> bool:
            return (
                (i(r, "td_sell_count") >= 9)
                and (f(r, "rsi", -999.0) >= 76.0)
                and (f(r, "mfi", -999.0) >= 85.0)
                and (f(r, "stoch_k", -999.0) >= 85.0)
                and (f(r, "williams_r", -100.0) < -10.0)
                and (f(r, "cci", 0.0) < 175.0)
                and short_trigger(r)
                and short_color_ok(r)
                and vol_ok(r)
            )

        def mined_wr_cci_stoch_long(r: pd.Series) -> bool:
            return (
                (i(r, "td_buy_count") >= 9)
                and (f(r, "rsi", 999.0) <= 24.0)
                and (f(r, "williams_r", 0.0) <= -90.0)
                and (f(r, "cci", 0.0) <= -175.0)
                and (f(r, "stoch_k", 999.0) <= 15.0)
                and (f(r, "mfi", 0.0) > 15.0)
                and long_trigger(r)
                and long_color_ok(r)
                and vol_ok(r)
            )

        def mined_wr_cci_stoch_short(r: pd.Series) -> bool:
            return (
                (i(r, "td_sell_count") >= 9)
                and (f(r, "rsi", -999.0) >= 76.0)
                and (f(r, "williams_r", -100.0) >= -10.0)
                and (f(r, "cci", 0.0) >= 175.0)
                and (f(r, "stoch_k", -999.0) >= 85.0)
                and (f(r, "mfi", 100.0) < 85.0)
                and short_trigger(r)
                and short_color_ok(r)
                and vol_ok(r)
            )

        # Ultra-rare exhaustion spike (td>=20) – not spammy; keep as "top tier"
        def td20_long(r: pd.Series) -> bool:
            return (i(r, "td_buy_count") >= 20) and (f(r, "rsi", 999.0) <= 15.0) and long_trigger(r) and long_color_ok(r)

        def td20_short(r: pd.Series) -> bool:
            return (i(r, "td_sell_count") >= 20) and (f(r, "rsi", -999.0) >= 75.0) and short_trigger(r) and short_color_ok(r)

        return [
            ReversalRule("true_rev_consensus_long", "long", 0.86, true_rev_long),
            ReversalRule("true_rev_consensus_short", "short", 0.86, true_rev_short),

            ReversalRule("rev_mfi_stoch_confirmed_long", "long", 0.82, mined_mfi_stoch_long),
            ReversalRule("rev_mfi_stoch_confirmed_short", "short", 0.82, mined_mfi_stoch_short),

            ReversalRule("rev_wr_cci_stoch_confirmed_long", "long", 0.80, mined_wr_cci_stoch_long),
            ReversalRule("rev_wr_cci_stoch_confirmed_short", "short", 0.80, mined_wr_cci_stoch_short),

            ReversalRule("rev_td20_rsi15_long", "long", 0.85, td20_long),
            ReversalRule("rev_td20_rsi75_short", "short", 0.80, td20_short),
        ]


if __name__ == "__main__":
    from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

    async def main():
        db = PolygonOptions()

        scanner = LiveReversalScanner(
            tickers=most_active_tickers,
            timespans=["m1", "m5", "m15"],
            db_client=db,
            upsert_snapshot_table="candle_analysis_latest",
            upsert_signals_table="reversal_signals",
            sleep_interval=6.0,
            seed_count=120,
            poll_count=25,
            window_rows=160,
            scan_only_closed_candles=True,
            signal_cooldown_bars=5,
            log_signals=True,
        )

        async with scanner:
            await scanner.run_forever()

    asyncio.run(main())
