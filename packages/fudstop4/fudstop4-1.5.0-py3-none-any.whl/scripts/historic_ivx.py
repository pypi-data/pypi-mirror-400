import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, time
import pytz
from dotenv import load_dotenv
import pandas as pd
import aiohttp
from fudstop4.apis.webull.webull_options.webull_options import WebullOptions
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
# Add project path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from more_itertools import chunked  # pip install more-itertools if needed
from imports import *
async def historic_ivx(ticker: str) -> None:
    """
    Fetch and store the historic implied volatility index (IVX) for a given
    ticker.  Assumes the database connection is already open.  Handles
    any exceptions internally by logging.

    Args:
        ticker: The stock ticker symbol.
    """
    try:
        monitor = await occ.historic_ivx(symbol=ticker)
        await db.batch_upsert_dataframe(
            monitor.as_dataframe,
            table_name='historic_ivx',
            unique_columns=['ticker', 'date'],
        )
    except Exception as e:
        print(f"[ERROR] Failed to fetch historic IVX for {ticker}: {e}")

async def run_historic_ivx():
    """
    Continuously fetch historic IVX data for the most active tickers.  A
    single database connection is opened and reused.  After each full
    iteration through all tickers, the function sleeps for 10 minutes.
    """
    await db.connect()
    try:
        while True:
            for batch in chunked(most_active_tickers, 7):
                tasks = [historic_ivx(ticker) for ticker in batch]
                try:
                    await asyncio.gather(*tasks)
                except Exception as e:
                    print(f"[ERROR] Batch failed: {e}")
            print("[INFO] Waiting 10 minutes before next cycle.")
            await asyncio.sleep(600)  # 10 minutes
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(run_historic_ivx())