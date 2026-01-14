from datetime import timedelta
import datetime
#!/usr/bin/env python3
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
import datetime
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
def get_next_trading_day(start_date=None):
    """
    Returns the next trading day (skips Saturday/Sunday).
    Args:
        start_date: datetime.date, datetime.datetime, or str (optional). If None, uses today.
    Returns:
        str: 'YYYY-MM-DD' for the next trading day.
    """
    if start_date is None:
        d = datetime.datetime.now().date()
    elif isinstance(start_date, str):
        # Try to parse string to date
        try:
            d = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            # Try parsing as datetime string
            d = datetime.datetime.fromisoformat(start_date).date()
    elif isinstance(start_date, datetime.datetime):
        d = start_date.date()
    elif isinstance(start_date, datetime.date):
        d = start_date
    else:
        raise ValueError("start_date must be None, str, datetime.date, or datetime.datetime")

    # Move to next day if today is not a trading day
    while d.weekday() >= 5:  # 5=Saturday, 6=Sunday
        d += timedelta(days=1)
    return d.strftime("%Y-%m-%d")

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
    


def format_webull_datetime(iso_str, tz='UTC'):
    """
    Converts Webull ISO date string to 'YYYY-MM-DD HH:MM:SS AM/PM' format.
    tz: 'UTC' (default) or 'local'
    """
    # Parse ISO string to datetime (aware)
    from datetime import timezone
    dt = datetime.datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    if tz.lower() == 'local':
        # Convert to system local time
        dt = dt.astimezone()
    else:
        # Keep as UTC
        dt = dt.astimezone(timezone.utc)
    # Format as required
    return dt.strftime("%Y-%m-%d %I:%M:%S %p")



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
            async with session.get(url, headers=generate_webull_headers(), timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logging.warning(
                "Attempt %d/%d failed for URL %s: %s",
                attempt + 1, retries, url, e
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
    limit:str='1',
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
                f"?type={timespan}&count={limit}&restorationType=1&loadFactor=1"
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

  
        for col in ['o','c','h','l','v','vwap','a']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # We don't need 'a' column
        df.drop(columns=['a'], inplace=True, errors='ignore')
        
        # Ensure 'ts' is string for DB insert
        df['ts'] = df['ts'].astype(str)

        df['timespan'] = timespan
        df['ticker'] = ticker
        return df

    except Exception as e:
        logging.error("Error fetching data for %s %s: %s", ticker, timespan, e)
        return None

async def fetch_and_store(
    session: aiohttp.ClientSession,
    ticker: str,
    timespan: str,
    results: Dict[Tuple[str, str], Optional[pd.DataFrame]],
    limit:str='1'
) -> None:
    df = await fetch_data_for_timespan(session, ticker, timespan, limit=limit)
    results[(ticker, timespan)] = df

async def fetch_all_tickers(tickers: list, timespans: list) -> Dict[Tuple[str, str], Optional[pd.DataFrame]]:
    results: Dict[Tuple[str, str], Optional[pd.DataFrame]] = {}
    connector = aiohttp.TCPConnector(limit=105)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            asyncio.create_task(fetch_and_store(session, t, ts, results, limit='1'))
            for t in tickers for ts in timespans
        ]
        await asyncio.gather(*tasks)
    return results
