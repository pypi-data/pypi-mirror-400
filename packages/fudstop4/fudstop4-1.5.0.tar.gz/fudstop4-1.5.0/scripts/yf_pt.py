import asyncio
import sys
from pathlib import Path
from datetime import datetime

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
from imports import *
from _yfinance.models.price_target import yfPriceTarget
from more_itertools import chunked
from typing import Tuple, List, Any
import yfinance as yf

BATCH_SIZE = 7
SLEEP_SECONDS = 43200  # 12 hours

async def yf_pricetarget(ticker):
    await db.connect()
    try:
        tickers_obj = yf.Ticker(ticker)
        price_targets = tickers_obj.analyst_price_targets
        if not price_targets:
            print(f"[!] No price target data for {ticker}")
            return

        data = yfPriceTarget(price_targets)
        df = data.as_dataframe
        df['ticker'] = ticker

        await db.batch_upsert_dataframe(df, table_name='yf_pt', unique_columns=['ticker'])
        print(f"[+] Updated price target for {ticker}")
    except Exception as e:
        print(f"[x] Error processing {ticker}: {e}")

async def run_pricetarget():
    for batch in chunked(most_active_tickers, BATCH_SIZE):
        tasks = [yf_pricetarget(ticker) for ticker in batch]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1)

async def main_loop():
    while True:
        print(f"[*] Running price target update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await run_pricetarget()
        print(f"[*] Sleeping 12 hours...\n")
        await asyncio.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    asyncio.run(main_loop())
