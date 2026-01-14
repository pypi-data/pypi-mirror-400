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
SLEEP_SECONDS = 86400  # 24 hours

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

async def yf_mfholders(ticker):
    await db.connect()
    try:
        tickers_obj = yf.Ticker(ticker)
        df = tickers_obj.get_mutualfund_holders()
        if df is None or df.empty:  # type: ignore
            print(f"[!] No mutual fund holder data for {ticker}")
            return
        df['ticker'] = ticker
        df.columns = ( #type: ignore
            df.columns #type: ignore
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
            .str.replace('%', 'pct')
            .str.replace(r'[^\w_]', '', regex=True)
        )
        await db.batch_upsert_dataframe(
            df, #type: ignore
            table_name='yf_mfholders',
            unique_columns=['ticker']
        )
        print(f"[+] Inserted mutual fund data for {ticker}")
    except Exception as e:
        print(f"[x] Error for {ticker}: {e}")

async def run_all_mfholders():
    BATCH_SIZE = 5
    for batch in chunk_list(most_active_tickers, BATCH_SIZE):
        tasks = [yf_mfholders(tkr) for tkr in batch]
        await asyncio.gather(*tasks)

async def main_loop():
    while True:
        print(f"[*] Running mutual fund scrape: {datetime.now()}")
        await run_all_mfholders()
        print(f"[*] Sleeping for 24 hours...\n")
        await asyncio.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    asyncio.run(main_loop())
