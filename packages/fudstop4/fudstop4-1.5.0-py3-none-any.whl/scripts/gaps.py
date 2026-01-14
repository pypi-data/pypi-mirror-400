#!/usr/bin/env python3
import sys
from pathlib import Path

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
import aiohttp
import asyncio
from asyncio import Semaphore, Lock
import numpy as np
import pandas as pd
import time
from numba import njit
import logging
from typing import Dict, Tuple, Any, Union, Optional

# ─── SETUP LOGGING ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ─── IMPORT MARKET HOURS FILTER (YOUR LOCAL MODULE) ──────────────────────────



# ─── ADJUST PROJECT DIRECTORY IMPORTS ─────────────────────────────────────────
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

# ─── IMPORT PROJECT MODULES ───────────────────────────────────────────────────
# Make sure these exist in your environment.

from fudstop4.apis.webull.webull_ta import WebullTA
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers



# ─── GLOBAL OBJECTS AND CONSTANTS ─────────────────────────────────────────────
SEM = Semaphore(50)
ticker_id_cache: Dict[str, int] = {}
ticker_cache_lock = Lock()

# Initialize DB & TA
db = PolygonOptions()
ta = WebullTA()


import pandas as pd

def infer_timespan(df):
    """
    Infers the timespan string (e.g., 'm1', 'm5', 'm15', etc.) from a DataFrame with a 'ts' column.
    Returns a string like 'm1', 'm5', 'm15', 'm30', 'm60', 'm120', 'm240', 'd1', 'w1'.
    Falls back to seconds (e.g., '9000s') if not a standard interval.
    """
    df = df.sort_values('ts')
    # Ensure 'ts' is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['ts']):
        df['ts'] = pd.to_datetime(df['ts'])
    # Compute time deltas in seconds, drop 0s
    time_deltas = df['ts'].diff().dropna().dt.total_seconds()
    # Use the most common nonzero delta
    delta = int(time_deltas[time_deltas > 0].mode()[0])

    # Standard mapping
    mapping = {
        60: 'm1',
        300: 'm5',
        900: 'm15',
        1800: 'm30',
        3600: 'm60',
        7200: 'm120',
        14400: 'm240',
        86400: 'd1',
        604800: 'w1'
    }

    # Try to match standard timespans
    if delta in mapping:
        return mapping[delta]

    # Try to match multiples of standard timespans (e.g., 9000 = 15*600)
    for base, label in [(60, 'm'), (300, 'm'), (900, 'm'), (1800, 'm'), (3600, 'm'), (86400, 'd'), (604800, 'w')]:
        if delta % base == 0 and delta // base > 1 and base < 86400:
            return f"{label}{int(delta // base * (base // 60 if label == 'm' else 1))}"

    # If delta is a multiple of 60, return as 'mX'
    if delta % 60 == 0 and delta < 3600:
        return f"m{delta // 60}"
    # If delta is a multiple of 3600, return as 'hX'
    if delta % 3600 == 0 and delta < 86400:
        return f"h{delta // 3600}"
    # Otherwise, return as seconds
    return f"{delta}s"
def find_price_gaps(df, min_gap=0.001, only_unfilled=True, timespan=None):
    """
    Finds price gaps in OHLCV data, including timestamps and timeframe.
    Adds percent distance from current price to gap_low and gap_high.
    Also includes the close price at the gap.
    :param df: DataFrame with columns ['ts','o','h','l','c']
    :param min_gap: Minimum gap size to detect
    :param only_unfilled: Only return gaps not yet filled
    :param timespan: Optionally specify timespan string (e.g., 'm1', 'm5'). If None, auto-detect.
    :return: List of dicts with gap info including timestamps, timespan, close price, and percent distances
    """
    df = df.copy()
    df['ts'] = pd.to_datetime(df['ts'])
    timespan = timespan or infer_timespan(df)

    # Use the latest close as current price
    current_price = df['c'].iloc[-1] if 'c' in df.columns else None

    gaps = []
    for i in range(1, len(df)):
        prev_high = df.iloc[i-1]['h']
        prev_low  = df.iloc[i-1]['l']
        curr_high = df.iloc[i]['h']
        curr_low  = df.iloc[i]['l']
        curr_close = df.iloc[i]['c']

        # Upward gap (void below)
        if curr_low - prev_high > min_gap:
            gap_low = prev_high
            gap_high = curr_low
            gap = {
                'type': 'up',
                'from_ts': df.iloc[i-1]['ts'],
                'to_ts':   df.iloc[i]['ts'],
                'gap_low': gap_low,
                'gap_high': gap_high,
                'gap_range': (gap_low, gap_high),
                'gap_size': gap_high - gap_low,
                'timespan': timespan,
                'c': curr_close
            }
            if current_price and current_price != 0:
                gap['gap_low_pct'] = 100 * (gap_low - current_price) / current_price
                gap['gap_high_pct'] = 100 * (gap_high - current_price) / current_price
            else:
                gap['gap_low_pct'] = None
                gap['gap_high_pct'] = None
            gaps.append(gap)
        # Downward gap (void above)
        elif prev_low - curr_high > min_gap:
            gap_low = curr_high
            gap_high = prev_low
            gap = {
                'type': 'down',
                'from_ts': df.iloc[i-1]['ts'],
                'to_ts':   df.iloc[i]['ts'],
                'gap_low': gap_low,
                'gap_high': gap_high,
                'gap_range': (gap_low, gap_high),
                'gap_size': gap_high - gap_low,
                'timespan': timespan,
                'c': curr_close
            }
            if current_price and current_price != 0:
                gap['gap_low_pct'] = 100 * (gap_low - current_price) / current_price
                gap['gap_high_pct'] = 100 * (gap_high - current_price) / current_price
            else:
                gap['gap_low_pct'] = None
                gap['gap_high_pct'] = None
            gaps.append(gap)

    # Filter for only unfilled gaps if requested
    if only_unfilled:
        unfilled = []
        for gap in gaps:
            filled = False
            to_idx = df.index.get_loc(df[df['ts'] == gap['to_ts']].index[0])
            for j in range(to_idx + 1, len(df)):
                if gap['type'] == 'up':
                    if df.iloc[j]['l'] <= gap['gap_low']:
                        filled = True
                        break
                elif gap['type'] == 'down':
                    if df.iloc[j]['h'] >= gap['gap_high']:
                        filled = True
                        break
            if not filled:
                unfilled.append(gap)
        gaps = unfilled

    return gaps


# ─── UTILITY: RETRY AIOHTTP REQUESTS ─────────────────────────────────────────
async def fetch_with_retries(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict,
    retries: int = 3,
    delay: float = 1.0
) -> Optional[dict]:
    """
    Fetch a URL with retries upon failure.
    """
    for attempt in range(retries):
        try:
            # Use the provided headers instead of regenerating on each call
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logging.warning(
                "Attempt %d/%d failed for URL %s: %s",
                attempt + 1,
                retries,
                url,
                e,
            )
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise



# ─── ASYNC FETCH & PROCESS ────────────────────────────────────────────────────
async def fetch_data_for_timespan(
    session: aiohttp.ClientSession,
    ticker: str,
    timespan: str,
    rsi_window: int = 14
) -> Optional[pd.DataFrame]:
    """
    Fetch data for a given ticker/timespan, compute RSI, MACD, TD9, etc.
    Keeping final DataFrame in ascending order so columns line up properly.
    """
    try:
        async with SEM:
            # Check the cache for ticker -> ticker_id
            async with ticker_cache_lock:
                if ticker in ticker_id_cache:
                    ticker_id = ticker_id_cache[ticker]
                else:
                    ticker_id = ta.ticker_to_id_map.get(ticker)
                    if ticker_id is not None:
                        ticker_id_cache[ticker] = ticker_id
                    else:
                        logging.warning("No ticker_id found for %s", ticker)

            # Increase `count=` so we have enough bars for TD9
            url = (
                "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
                f"?type={timespan}&count=120&restorationType=1&loadFactor=1"
                f"&extendTrading=0&tickerId={ticker_id}"
            )
            data_json = await fetch_with_retries(session, url, headers=generate_webull_headers())

        if not data_json or not isinstance(data_json, list) or len(data_json) == 0:
            logging.warning("No data returned for %s %s", ticker, timespan)
            return None

        raw_data = data_json[0].get('data', [])
        if not raw_data:
            logging.warning("Empty 'data' field for %s %s", ticker, timespan)
            return None

        # Parse
        split_data = [row.split(",") for row in raw_data]
        df = pd.DataFrame(split_data, columns=['ts','o','c','h','l','a','v','vwap'])

        # Convert timestamp
        df['ts'] = pd.to_numeric(df['ts'], errors='coerce')
        df['ts'] = pd.to_datetime(df['ts'], unit='s', utc=True)
       
        # Webull often returns newest first => reverse to ascending
        df = df.iloc[::-1].reset_index(drop=True)

        print(df)
        for col in ['o','c','h','l','v','vwap','a']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        # Clip volume to int32 range to match DB schema
        max_int32 = 2_147_000_000
        df['v'] = df['v'].clip(lower=0, upper=max_int32).astype(int)
        
        # We don't need 'a' column
        df.drop(columns=['a'], inplace=True, errors='ignore')
        
        # Ensure 'ts' is string for DB insert
        df['ts'] = df['ts'].astype(str)

        df['timespan'] = timespan
        df['ticker'] = ticker
        await db.batch_upsert_dataframe(
            df,
            table_name='candles',
            unique_columns=['ticker', 'ts'],
        )
        return df

    except Exception as e:
        logging.error("Error fetching data for %s %s: %s", ticker, timespan, e)
        return None

async def fetch_and_store(
    session: aiohttp.ClientSession,
    ticker: str,
    timespan: str,
    results: Dict[Tuple[str, str], Optional[pd.DataFrame]]
) -> None:
    df = await fetch_data_for_timespan(session, ticker, timespan)
    results[(ticker, timespan)] = df

async def fetch_all_tickers(
    tickers: list,
    timespans: list,
    session: aiohttp.ClientSession,
) -> Dict[Tuple[str, str], Optional[pd.DataFrame]]:
    """
    Fetch and store candle data for all combinations of tickers and timespans
    using the provided HTTP session.  Returns a dictionary mapping
    (ticker, timespan) tuples to DataFrames or ``None`` if the fetch
    failed.
    """
    results: Dict[Tuple[str, str], Optional[pd.DataFrame]] = {}
    tasks = [
        asyncio.create_task(fetch_and_store(session, t, ts, results))
        for t in tickers
        for ts in timespans
    ]
    await asyncio.gather(*tasks)
    return results

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
async def main() -> None:
    try:
        await db.connect()
        cycle = 0
        # Choose whichever timespans you prefer
        timespans = [
            'm1',
            'm5',
            'm30',
            'm15',
            'm60',
            'd1',
            'w1',
            'm120',
            'm240',
        ]
        sleep_interval = 6  # seconds between cycles
        # Create a single session reused across all cycles
        async with aiohttp.ClientSession() as session:
            while True:
                cycle += 1
                cycle_start = time.time()
                logging.info("Starting cycle %d", cycle)
                # Fetch all data for tickers and timespans
                all_data = await fetch_all_tickers(
                    most_active_tickers, timespans, session
                )
                gaps_by_ticker: Dict[str, list[pd.DataFrame]] = {}
                for (ticker, tspan), df in all_data.items():
                    if df is None or df.empty:
                        continue
                    gaps = find_price_gaps(df, min_gap=0.01, only_unfilled=True)
                    query = f"SELECT close from multi_quote where ticker = '{ticker}'"
                    results = await db.fetch(query)
                    current_price = None
                    if results:
                        try:
                            current_price = float([i.get('close') for i in results][0])
                        except Exception:
                            current_price = None
                    gaps_df = pd.DataFrame(gaps)
                    if gaps_df.empty:
                        continue
                    gaps_df['ticker'] = ticker
                    gaps_df['current_price'] = current_price
                    # Ensure numeric gap fields to avoid type errors when calculating sizes
                    for col in ['gap_low', 'gap_high', 'gap_low_pct', 'gap_high_pct']:
                        if col in gaps_df.columns:
                            gaps_df[col] = pd.to_numeric(gaps_df[col], errors='coerce')
                    # Split the tuple column 'gap_range' into two new columns
                    if 'gap_range' in gaps_df.columns:
                        gaps_df[['gap_low', 'gap_high']] = pd.DataFrame(
                            gaps_df['gap_range'].tolist(), index=gaps_df.index
                        )
                        gaps_df.drop('gap_range', axis=1, inplace=True)
                    # Convert any Timestamp columns to string for DB compatibility
                    for col in ['from_ts', 'to_ts']:
                        if col in gaps_df.columns:
                            gaps_df[col] = gaps_df[col].astype(str)
                    # Upsert gaps using a list for unique_columns
                    await db.batch_upsert_dataframe(
                        gaps_df,
                        table_name='gaps',
                        unique_columns=['ticker', 'timespan', 'gap_low', 'gap_high'],
                    )
                    gaps_by_ticker.setdefault(ticker, []).append(gaps_df)

                # Build per-ticker support/resistance summaries
                for ticker, frames in gaps_by_ticker.items():
                    try:
                        full_df = pd.concat(frames, ignore_index=True)
                    except ValueError:
                        continue
                    if full_df.empty:
                        continue
                    # Choose nearest boundary (low/high) in pct terms with sign preserved
                    def nearest_pct_row(row: pd.Series) -> Optional[float]:
                        vals = [v for v in (row.get('gap_low_pct'), row.get('gap_high_pct')) if pd.notnull(v)]
                        if not vals:
                            return None
                        return min(vals, key=lambda x: abs(x))

                    full_df['nearest_pct'] = full_df.apply(nearest_pct_row, axis=1)
                    support_pct = full_df.loc[full_df['nearest_pct'] < 0, 'nearest_pct'].max() if any(full_df['nearest_pct'] < 0) else None
                    resistance_pct = full_df.loc[full_df['nearest_pct'] > 0, 'nearest_pct'].min() if any(full_df['nearest_pct'] > 0) else None

                    # Pick the absolutely nearest gap for context fields
                    nearest_row = full_df.loc[full_df['nearest_pct'].abs().idxmin()] if full_df['nearest_pct'].notna().any() else None
                    points = 0
                    reasons = []
                    if support_pct is not None and pd.notnull(support_pct):
                        if abs(support_pct) <= 2:
                            points += 2
                            reasons.append(f"support gap {support_pct:+.2f}% from price")
                        elif abs(support_pct) <= 5:
                            points += 1
                            reasons.append(f"support gap {support_pct:+.2f}%")
                        else:
                            reasons.append(f"support gap {support_pct:+.2f}% (far)")
                    if resistance_pct is not None and pd.notnull(resistance_pct):
                        if resistance_pct <= 2:
                            points -= 2
                            reasons.append(f"resistance gap {resistance_pct:+.2f}% from price")
                        elif resistance_pct <= 5:
                            points -= 1
                            reasons.append(f"resistance gap {resistance_pct:+.2f}%")
                        else:
                            reasons.append(f"resistance gap {resistance_pct:+.2f}% (far)")

                    gap_signal = "bullish" if points > 0 else "bearish" if points < 0 else "neutral"
                    summary_df = pd.DataFrame([{
                        "ticker": ticker,
                        "timespan": nearest_row.get('timespan') if nearest_row is not None else None,
                        "gap_from_ts": nearest_row.get('from_ts') if isinstance(nearest_row, pd.Series) else None,
                        "gap_to_ts": nearest_row.get('to_ts') if isinstance(nearest_row, pd.Series) else None,
                        "gap_type": nearest_row.get('type') if isinstance(nearest_row, pd.Series) else None,
                        "gap_low_pct": nearest_row.get('gap_low_pct') if isinstance(nearest_row, pd.Series) else None,
                        "gap_high_pct": nearest_row.get('gap_high_pct') if isinstance(nearest_row, pd.Series) else None,
                        "current_price": nearest_row.get('current_price') if isinstance(nearest_row, pd.Series) else None,
                        "support_pct": support_pct,
                        "resistance_pct": resistance_pct,
                        "gap_signal": gap_signal,
                        "gap_points": points,
                        "gap_reason": "; ".join(reasons) if reasons else "no nearby gaps",
                        "gap_confluence_score": points,
                        "confluence_score": points,
                        "asof": pd.Timestamp.utcnow(),
                    }])
                    await db.batch_upsert_dataframe(
                        summary_df,
                        table_name='gap_signals',
                        unique_columns=['ticker'],
                    )
                # Sleep for a short interval before the next cycle
                await asyncio.sleep(sleep_interval)
    except asyncio.CancelledError:
        logging.info("Main loop cancelled.")
    except Exception as e:
        logging.error("Unexpected error in main loop: %s", e)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program terminated by user.")
