#!/usr/bin/env python3
import sys
from pathlib import Path

project_dir = str(Path(__file__).resolve().parents[2])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from script_helpers import add_td9_counts, add_bollinger_bands, compute_wilders_rsi, macd_curvature_label, add_obv, add_volume_metrics, generate_webull_headers, add_parabolic_sar_signals,add_sdc_indicator
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
SEM = Semaphore(75)
ticker_id_cache: Dict[str, int] = {}
ticker_cache_lock = Lock()

# Initialize DB & TA
db = PolygonOptions()
ta = WebullTA()


import matplotlib.pyplot as plt
from io import BytesIO
import base64
import asyncpg




async def init_db_pool():
    return await asyncpg.create_pool(
        user='chuck',
        password='fud',
        database='fudstop3',
        host='localhost',   # or the appropriate host/IP
        port=5432,          # default PostgreSQL port
        min_size=1,
        max_size=10,
        command_timeout=60
    )




# ─── UTILITY: RETRY AIOHTTP REQUESTS ─────────────────────────────────────────
async def fetch_with_retries(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict,
    retries: int = 3,
    delay: float = 1.0
) -> dict: #type: ignore
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



async def fetch_data_for_timespan(
    session: aiohttp.ClientSession,
    ticker: str,
    timespan: str,
    rsi_window: int = 14,
    charting: bool = False,
    db_pool: Optional[asyncpg.Pool] = None,
    headers: Optional[dict] = None
) -> Optional[pd.DataFrame]:
    """
    Fetch Webull chart data for a given ticker/timespan and apply technical indicators.
    Optionally generate and store a chart to the database.
    """
    try:
        async with SEM:
            # ─── Ticker ID Cache ─────────────────────────────
            async with ticker_cache_lock:
                ticker_id = ticker_id_cache.get(ticker) or ta.ticker_to_id_map.get(ticker)
                if not ticker_id:
                    logging.warning("No Webull ID found for %s", ticker)
                    return None
                ticker_id_cache[ticker] = ticker_id  # memoize it

            # ─── Fetch Historical Data ───────────────────────
            url = (
                "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
                f"?type={timespan}&count=800&restorationType=1&loadFactor=1"
                f"&extendTrading=0&tickerId={ticker_id}"
            )
            headers = headers or generate_webull_headers()
            data_json = await fetch_with_retries(session, url, headers=headers)

        # ─── Validate JSON Structure ─────────────────────────
        if not data_json or not isinstance(data_json, list) or not data_json[0].get('data'):
            logging.warning("Invalid or empty chart data for %s [%s]", ticker, timespan)
            return None

        # ─── Parse DataFrame ────────────────────────────────
        raw_data = data_json[0]['data']
        df = pd.DataFrame(
            [row.split(",") for row in raw_data],
            columns=['ts', 'o', 'c', 'h', 'l', 'a', 'v', 'vwap']
        )

        df['ts'] = pd.to_datetime(pd.to_numeric(df['ts'], errors='coerce'), unit='s', utc=True)
        df = df.iloc[::-1].reset_index(drop=True)  # ascending order

        numeric_cols = ['o', 'c', 'h', 'l', 'v', 'vwap']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
        df = df.drop(columns=['a'])

        df['timespan'] = timespan
        df['ticker'] = ticker


        return df

    except Exception as e:
        logging.error("Data fetch failed for %s [%s]: %s", ticker, timespan, e)
        return None

async def fetch_and_store(
    session: aiohttp.ClientSession,
    ticker: str,
    timespan: str,
    results: Dict[Tuple[str, str], Optional[pd.DataFrame]]
) -> None:
    df = await fetch_data_for_timespan(session, ticker, timespan)
    results[(ticker, timespan)] = df

async def fetch_all_tickers(tickers: list, timespans: list) -> Dict[Tuple[str, str], Optional[pd.DataFrame]]:
    results: Dict[Tuple[str, str], Optional[pd.DataFrame]] = {}
    connector = aiohttp.TCPConnector(limit=105)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            asyncio.create_task(fetch_and_store(session, t, ts, results))
            for t in tickers for ts in timespans
        ]
        await asyncio.gather(*tasks)
    return results

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
async def main() -> None:
    try:
        await db.connect()
        cycle = 0
        # You can choose whichever timespans you prefer
        timespans = ['m1','m5','m30','m15', 'm60','d1', 'm120','m240']
        sleep_interval = 6  # in seconds
        timespan_mapping = {
            'm1': '1min',
            'm5': '5min',
            'm15': '15min',
            'm30': '30min',
            'm60': '1hr',
            'm120': '2hr',
            'm240': '4hr',
            'd1': 'day',
            'w1': 'week',
            'mth1': 'month'
        }

        # Convert timespan keys in all_data to human-readable format
        normalized_data = {}
        while True:
            cycle += 1
            cycle_start = time.time()
            logging.info("Starting cycle %d", cycle)

            all_data = await fetch_all_tickers(most_active_tickers, timespans)

            for (ticker, tspan), df in all_data.items():
                if df is None or df.empty:
                    continue

                normalized_timespan = timespan_mapping.get(tspan, tspan)

                if ticker not in normalized_data:
                    normalized_data[ticker] = {}

                normalized_data[ticker][normalized_timespan] = df
                # Add human-readable timespan to row


                # The very last row is your newest bar
                newest_row = df.iloc[-1:].copy()
                newest_row["timespan"] = normalized_timespan
                newest_row["ts"] = newest_row["ts"].astype(str)


                # Convert ts to string for DB
                newest_row["ts"] = newest_row["ts"].astype(str)


            cycle_end = time.time()
            total_time = cycle_end - cycle_start
            logging.info("Cycle %d done in %.2f seconds.", cycle, total_time)
            logging.info("Sleeping %d seconds...\n", sleep_interval)
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
