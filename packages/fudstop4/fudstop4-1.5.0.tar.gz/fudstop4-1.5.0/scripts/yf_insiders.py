import asyncio
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import yfinance as yf

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from imports import *
from _yfinance.models.price_target import yfPriceTarget
from more_itertools import chunked
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
# 📦 Helper to chunk the list
def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

BATCH_SIZE = 7
SLEEP_SECONDS = 43200  # 12 hours

# 🧽 Normalize and structure insider summary
def normalize_insider_summary(ticker):
    try:
        tickers_obj = yf.Ticker(ticker)
        raw = tickers_obj.get_insider_purchases(as_dict=True)
        if not raw or 'Shares' not in raw:  # type: ignore
            return None

        shares = raw.get('Shares', {})
        trans = raw.get('Trans', {})

        data = {
            'ticker': ticker,
            'shares_purchased': shares.get(0),
            'shares_sold': shares.get(1),
            'net_shares_purchased': shares.get(2),
            'total_shares_held': shares.get(3),
            'pct_net_shares_purchased': shares.get(4),
            'pct_buy_shares': shares.get(5),
            'pct_sell_shares': shares.get(6),
            'purchases_trans': trans.get(0),
            'sales_trans': trans.get(1),
            'net_trans': trans.get(2),
        }

        df = pd.DataFrame([data])
        return df

    except Exception as e:
        print(f"[x] Failed to normalize insider data for {ticker}: {e}")
        return None

# 🔁 Fetch + insert per-ticker
async def yf_insiders(ticker):
    await db.connect()
    df = normalize_insider_summary(ticker)
    if df is None or df.empty:
        print(f"[!] No insider data for {ticker}")
        return

    await db.batch_upsert_dataframe(df, table_name='yf_insiders', unique_columns=['ticker'])
    print(f"[+] Inserted insider summary for {ticker}")

# 🚀 Runner
async def run_all_insiders():
    for batch in chunk_list(most_active_tickers, BATCH_SIZE):
        tasks = [yf_insiders(tkr) for tkr in batch]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1)

# 🔁 Infinite loop every 12 hours
async def main_loop():
    while True:
        print(f"\n[*] Starting insider scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await run_all_insiders()
        print("[*] Sleeping for 12 hours...\n")
        await asyncio.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    asyncio.run(main_loop())
