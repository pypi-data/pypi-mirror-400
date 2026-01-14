#!/usr/bin/env python3
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, Iterable, List
from fudstop4.apis.helpers import check_macd_sentiment
import aiohttp
import asyncpg
import numpy as np
import pandas as pd

# ── Project imports (adjust paths as needed)
project_dir = str(Path(__file__).resolve().parents[2])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from script_helpers import (
    add_td9_counts, add_bollinger_bands, compute_wilders_rsi, macd_curvature_label,
    add_obv, add_volume_metrics, add_parabolic_sar_signals, add_sdc_indicator,
    generate_webull_headers, macd_from_close, OPEN_ALIASES, LOW_ALIASES, CLOSE_ALIASES, HIGH_ALIASES, _find_col
)

# Example deps:
# from fudstop4.apis.webull.webull_ta import WebullTA
# from fudstop4.apis.polygonio.polygon_options import PolygonOptions
# from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
def add_volume_streaks(
    df: pd.DataFrame,
    return_mode: str = "multi",   # "multi" => adds vol_delta, vol_rise_streak, vol_fall_streak, vol_run
                                  # "single" => returns a 1-D Series for one column (signed run)
    colname: str = "volume_streak"
):
    """
    Computes volume streaks (rising/falling run lengths).
    Assumes df is sorted ascending by time and has numeric 'v' (volume).
    - vol_rise_streak: consecutive candles volume increased
    - vol_fall_streak: consecutive candles volume decreased
    - vol_run: signed run length (+rise, -fall, 0 if flat)
    If return_mode == "multi": mutate df in place and return df.
    If return_mode == "single": return a 1-D Series (signed run), suitable for df[colname] = series.
    """
    import numpy as np

    if df is None or df.empty or 'v' not in df.columns:
        # Return compatible shapes for both modes
        if return_mode == "single":
            return pd.Series([], dtype=int)
        return df

    v = pd.to_numeric(df['v'], errors='coerce').fillna(0).to_numpy(copy=False)
    n = len(v)

    rise = np.zeros(n, dtype=np.int32)
    fall = np.zeros(n, dtype=np.int32)
    delta = np.zeros(n, dtype=np.float64)

    for i in range(1, n):
        d = v[i] - v[i-1]
        delta[i] = d
        if d > 0:
            rise[i] = rise[i-1] + 1
            fall[i] = 0
        elif d < 0:
            fall[i] = fall[i-1] + 1
            rise[i] = 0
        else:
            # flat resets both; change if you prefer to carry previous run
            rise[i] = 0
            fall[i] = 0

    signed = rise.copy()
    neg_idx = fall > 0
    signed[neg_idx] = -fall[neg_idx]

    if return_mode == "single":
        # Return a 1-D Series (no shape mismatch)
        return pd.Series(signed, index=df.index, name=colname, dtype="int32")

    # "multi" mode: attach columns and return df
    # Drop preexisting to avoid dtype/assignment warnings
    for c in ("vol_delta", "vol_rise_streak", "vol_fall_streak", "vol_run"):
        if c in df.columns:
            df.drop(columns=c, inplace=True, errors="ignore")

    df['vol_delta'] = delta
    df['vol_rise_streak'] = rise
    df['vol_fall_streak'] = fall
    df['vol_run'] = signed.astype('int32')
    return df

def _td_points(count: float) -> int:
    """Map TD count to points."""
    if count >= 25:
        return 4
    if count >= 20:
        return 3
    if count >= 13:
        return 2
    if count >= 9:
        return 1
    return 0

def add_confluence_score(df: pd.DataFrame, macd_sentiment: str) -> pd.DataFrame:
    """
    Add a multi-factor confluence score using researched, widely used thresholds.

    Signals/points (all ASCII for clarity):
      - TD9: classic 9/13/20/25 thresholds mapped to 1/2/3/4 points (buy minus sell).
      - RSI: <20 +4, 20-30 +2, cross above 50 +1; >80 -4, 70-80 -2, cross below 50 -1.
      - MACD: sentiment +3/-3, fresh line cross +2/-2, histogram z-score >1/-1 adds +1/-1.
      - Bollinger: z <= -2 +3, -2 to -1 +1; z >= 2 -3, 1 to 2 -1.
      - Volume/Momentum: vol_ratio (v / 20-bar mean) >=1.8 with green candle +2 (red -1),
        >=1.3 with green +1 (red -1); volume streak >=3 with green +1, <=-3 with red -1.
      - SDC channel: close above upper band +2, below lower band -2.
    """
    df = df.copy()
    lower_cols = {c.lower(): c for c in df.columns}

    # Initialize all component scores to 0
    for col in ("score_td9", "score_rsi", "score_macd", "score_bbands", "score_volume", "score_sdc"):
        if col not in df.columns:
            df[col] = 0

    # --- TD9 buy/sell counts (robust column detection) ---
    td_buy_candidates  = ['td9_buy', 'td9_buy_count', 'td_buy', 'td_buy_count',
                          'tdsequential_buy', 'td_buy_setup', 'td9buy', 'td_buycount']
    td_sell_candidates = ['td9_sell', 'td9_sell_count', 'td_sell', 'td_sell_count',
                          'tdsequential_sell', 'td_sell_setup', 'td9sell', 'td_sellcount']

    buy_col  = next((lower_cols[n] for n in td_buy_candidates  if n in lower_cols), None)
    sell_col = next((lower_cols[n] for n in td_sell_candidates if n in lower_cols), None)

    buy_series  = df[buy_col]  if buy_col  else pd.Series(0, index=df.index, dtype=float)
    sell_series = df[sell_col] if sell_col else pd.Series(0, index=df.index, dtype=float)

    df['score_td9'] = buy_series.apply(_td_points) - sell_series.apply(_td_points)

    # --- RSI scoring (assumes Wilder's RSI column named 'rsi' or variants) ---
    rsi_candidates = ['rsi', 'rsi_14', 'rsi_wilders', 'wilders_rsi']
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
        default=0
    )
    # cross of RSI 50 threshold
    rsi_cross = pd.Series(0, index=df.index, dtype=int)
    if rsi_col:
        prev_rsi = rsi.shift(1)
        cross_up = (prev_rsi <= 50) & (rsi > 50)
        cross_dn = (prev_rsi >= 50) & (rsi < 50)
        rsi_cross[cross_up] = 1
        rsi_cross[cross_dn] = -1

    df['score_rsi'] = base_rsi_score + rsi_cross

    # --- MACD sentiment (+3 bullish / -3 bearish) plus cross/hist strength ---
    sent = (macd_sentiment or '').strip().lower()
    macd_points = 3 if sent == 'bullish' else (-3 if sent == 'bearish' else 0)

    macd_cross = pd.Series(0, index=df.index, dtype=int)
    hist_score = pd.Series(0, index=df.index, dtype=int)
    macd_val = df.get('macd_value')
    macd_sig = df.get('macd_signal')
    macd_hist = df.get('macd_hist')
    if macd_val is not None and macd_sig is not None:
        cross_up = (macd_val.shift(1) < macd_sig.shift(1)) & (macd_val > macd_sig)
        cross_dn = (macd_val.shift(1) > macd_sig.shift(1)) & (macd_val < macd_sig)
        macd_cross = pd.Series(
            np.where(cross_up, 2, np.where(cross_dn, -2, 0)),
            index=df.index,
            dtype=int
        )
    if macd_hist is not None:
        hist_std = macd_hist.rolling(15, min_periods=5).std()
        hist_z = pd.Series(0, index=df.index, dtype=float)
        hist_z = np.where(hist_std > 0, macd_hist / hist_std, 0)
        hist_score = pd.Series(
            np.select(
                [hist_z >= 1.0, hist_z <= -1.0],
                [1, -1],
                default=0
            ),
            index=df.index,
            dtype=int
        )
    df['score_macd'] = macd_points + macd_cross + hist_score

    # --- Bollinger bands z-score ---
    if {'middle_band', 'std'}.issubset(df.columns):
        std = df['std'].replace(0, np.nan)
        bb_z = (df['c'] - df['middle_band']) / std
        df['score_bbands'] = np.select(
            [
                bb_z <= -2.0,
                (bb_z > -2.0) & (bb_z <= -1.0),
                bb_z >= 2.0,
                (bb_z < 2.0) & (bb_z >= 1.0)
            ],
            [3, 1, -3, -1],
            default=0
        ).astype(int)

    # --- Volume / momentum confirmation ---
    open_col = _find_col(df, OPEN_ALIASES)
    price_up = pd.Series(False, index=df.index)
    price_down = pd.Series(False, index=df.index)
    if open_col:
        price_up = df['c'] > df[open_col]
        price_down = df['c'] < df[open_col]

    vol_ma = df['v'].rolling(20, min_periods=5).mean()
    vol_ratio = np.where(vol_ma > 0, df['v'] / vol_ma, 0)
    vol_score = pd.Series(
        np.select(
            [
                (vol_ratio >= 1.8) & price_up,
                (vol_ratio >= 1.3) & price_up,
                (vol_ratio >= 1.8) & price_down,
                (vol_ratio >= 1.3) & price_down,
            ],
            [2, 1, -1, -1],
            default=0
        ),
        index=df.index,
        dtype=int
    )

    streak_col = 'volume_streak'
    streak_score = pd.Series(0, index=df.index, dtype=int)
    if streak_col in df.columns:
        streak_score = pd.Series(
            np.select(
                [
                    (df[streak_col] >= 3) & price_up,
                    (df[streak_col] <= -3) & price_down
                ],
                [1, -1],
                default=0
            ),
            index=df.index,
            dtype=int
        )
    df['score_volume'] = vol_score + streak_score

    # --- SDC regression channel breaks ---
    if 'sdc_signal' in df.columns:
        df['score_sdc'] = np.select(
            [
                df['sdc_signal'] == 'above_both',
                df['sdc_signal'] == 'below_both'
            ],
            [2, -2],
            default=0
        )

    # --- Total ---
    components = ['score_td9', 'score_rsi', 'score_macd', 'score_bbands', 'score_volume', 'score_sdc']
    df['confluence_score'] = df[components].sum(axis=1)
    return df


class ConfluencePlaysIngestor:
    """
    Reusable async ingestor for pulling Webull mini-charts across many tickers × timespans,
    computing indicators, and upserting the latest row into a 'plays' table.

    Key features:
      - Batching/concurrency controls via Semaphore and aiohttp connector limit
      - Shared session reuse
      - Ticker-id caching
      - Retry-on-failure for HTTP calls
      - Pluggable DB client with `batch_upsert_dataframe(...)`
      - Pluggable TA/ID mapping dependency (WebullTA)
    """

    DEFAULT_TIMESPANS = ['m1', 'm5', 'm30', 'm15', 'm60', 'd1', 'm120', 'm240']
    TIMESPAN_MAP = {
        'm1': '1min', 'm5': '5min', 'm15': '15min', 'm30': '30min',
        'm60': '1hr', 'm120': '2hr', 'm240': '4hr', 'd1': 'day',
        'w1': 'week', 'mth1': 'month'
    }

    def __init__(
        self,
        db_client,                     # expects .connect(), .disconnect(), .batch_upsert_dataframe(df, table_name, unique_columns)
        ta_client,                     # expects .ticker_to_id_map (dict[str,int])
        tickers_provider: Iterable[str],
        *,
        sem_limit: int = 75,
        connector_limit: int = 105,
        retries: int = 3,
        retry_delay: float = 1.0,
        sleep_interval: int = 6,
        timespans: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.db = db_client
        self.ta = ta_client
        self.tickers_provider = list(tickers_provider)

        self.sem = asyncio.Semaphore(sem_limit)
        self.connector_limit = connector_limit
        self.retries = retries
        self.retry_delay = retry_delay
        self.sleep_interval = sleep_interval
        self.timespans = timespans or list(self.DEFAULT_TIMESPANS)

        self._ticker_id_cache: Dict[str, int] = {}
        self._ticker_lock = asyncio.Lock()
        self._session: Optional[aiohttp.ClientSession] = None

        self.log = logger or logging.getLogger(__name__)
        if not self.log.handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # ──────────────────────────────────────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────────────────────────────────────
    async def __aenter__(self):
        await self.db.connect()
        connector = aiohttp.TCPConnector(limit=self.connector_limit)
        self._session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()
            self._session = None
        await self.db.disconnect()

    # ──────────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────────
    async def run_forever(self):
        """Continuous loop: fetch, compute, upsert, sleep."""
        cycle = 0
        try:
            while True:
                cycle += 1
                self.log.info("Starting cycle %d", cycle)
                await self.process_cycle()
                self.log.info("Sleeping %d seconds...", self.sleep_interval)
                await asyncio.sleep(self.sleep_interval)
        except asyncio.CancelledError:
            self.log.info("run_forever cancelled.")
        except Exception as e:
            self.log.exception("Unexpected error in run_forever: %s", e)

    async def process_cycle(self):
        """Fetch all tickers × timespans, compute indicators, upsert newest row per combo."""
        results = await self._fetch_all()
        for (ticker, tspan), df in results.items():
            if df is None or df.empty:
                continue

            normalized_timespan = self.TIMESPAN_MAP.get(tspan, tspan)
            # Log a tiny tail preview
            try:
                preview = df.tail(3)[['ts', 'o', 'h', 'l', 'c', 'td_buy_count', 'td_sell_count', 'macd_curvature']]
                self.log.info("Ticker=%s  Timespan=%s  (tail):\n%s", ticker, tspan, preview)
            except Exception:
                pass

            newest_row = df.iloc[-1:].copy()
            newest_row["timespan"] = normalized_timespan
            # stringify ts for DB
            newest_row["ts"] = newest_row["ts"].astype(str)

            await self.db.batch_upsert_dataframe(
                newest_row,
                table_name='plays',
                unique_columns=['ticker', 'timespan']
            )

    # ──────────────────────────────────────────────────────────────────────────
    # Internal: fetching & processing
    # ──────────────────────────────────────────────────────────────────────────
    async def _fetch_all(self) -> Dict[Tuple[str, str], Optional[pd.DataFrame]]:
        assert self._session is not None, "Call within async context or __aenter__."
        results: Dict[Tuple[str, str], Optional[pd.DataFrame]] = {}
        tasks = [
            asyncio.create_task(self._fetch_and_store(t, ts, results))
            for t in self.tickers_provider for ts in self.timespans
        ]
        await asyncio.gather(*tasks)
        return results

    async def _fetch_and_store(
        self,
        ticker: str,
        timespan: str,
        results: Dict[Tuple[str, str], Optional[pd.DataFrame]],
    ) -> None:
        df = await self._fetch_data_for_timespan(ticker, timespan)
        results[(ticker, timespan)] = df

    async def _fetch_data_for_timespan(
        self,
        ticker: str,
        timespan: str,
        rsi_window: int = 14,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch Webull chart data for a given ticker/timespan and apply technical indicators.
        """
        assert self._session is not None, "Session not initialized"
        try:
            async with self.sem:
                # Ticker id lookup with memoization
                ticker_id = await self._get_ticker_id(ticker)
                if not ticker_id:
                    self.log.warning("No Webull ID found for %s", ticker)
                    return None

                url = (
                    "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
                    f"?type={timespan}&count=50&restorationType=1&extendTrading=0&loadFactor=1"
                    f"&tickerId={ticker_id}"
                )
                data_json = await self._fetch_with_retries(url)

            # Validate JSON shape
            if not data_json or not isinstance(data_json, list) or not data_json[0].get('data'):
                self.log.warning("Invalid/empty chart data for %s [%s]", ticker, timespan)
                return None

            # Parse to DataFrame (ascending)
            raw_data = data_json[0]['data']

            df = pd.DataFrame(
                [row.split(",") for row in raw_data],
                columns=['ts', 'o', 'c', 'h', 'l', 'a', 'v', 'vwap']
            )
            df['ticker'] = ticker
            df['timespan'] = timespan
            df['ts'] = pd.to_datetime(pd.to_numeric(df['ts'], errors='coerce'), unit='s', utc=True)
            df = df.iloc[::-1].reset_index(drop=True)

            df = df.drop(columns=['a'], errors='ignore')
            numeric_cols = ['o', 'c', 'h', 'l', 'v', 'vwap']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
            await db.batch_upsert_dataframe(df, table_name='candle_charts', unique_columns=['ticker','timespan', 'ts'])

            closes = df['c'].to_list()
            # Technical indicators
            df = compute_wilders_rsi(df, window=rsi_window)
            df = add_bollinger_bands(df, window=30, num_std=1.5)
            df = add_td9_counts(df)
            df = add_sdc_indicator(df)
            df['timespan'] = timespan
            df['ticker'] = ticker
            # Compute MACD
            macd_line, signal_line, hist = macd_from_close(closes)

            # Attach to DataFrame
            df["macd_value"] = macd_line
            df["macd_signal"] = signal_line
            df["macd_hist"] = hist
            hist_ = df['macd_hist'].to_list()
            macd_sent = await check_macd_sentiment(ticker=ticker, timespan=timespan, hist=hist_)
            print(macd_sent)
            df['macd_sentiment'] = macd_sent
            df['volume_streak'] = add_volume_streaks(df, return_mode="single", colname="volume_streak")
            df['ticker_id'] = ticker_id
            # ⬇️ NEW: add confluence scoring
            df = add_confluence_score(df, macd_sent)

            return df

        except Exception as e:
            self.log.error("Fetch failed for %s [%s]: %s", ticker, timespan, e)
            return None

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────
    async def _get_ticker_id(self, ticker: str) -> Optional[int]:
        async with self._ticker_lock:
            if ticker in self._ticker_id_cache:
                return self._ticker_id_cache[ticker]
            # from TA client mapping
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

    # ──────────────────────────────────────────────────────────────────────────
    # Convenience single-shot
    # ──────────────────────────────────────────────────────────────────────────
    async def run_once(self):
        """Run a single cycle (useful for cron or tests)."""
        async with self:
            await self.process_cycle()


from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_ta import WebullTA
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
db = PolygonOptions()
ta = WebullTA()

ingestor = ConfluencePlaysIngestor(db_client=db, ta_client=ta,tickers_provider=most_active_tickers)

async def main():
    async with ingestor:            # <-- ensures DB connect + aiohttp session
        await ingestor.run_forever()

asyncio.run(main())
