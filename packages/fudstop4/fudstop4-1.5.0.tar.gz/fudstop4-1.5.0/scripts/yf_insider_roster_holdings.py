import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
from _yfinance.models.price_target import yfPriceTarget
from more_itertools import chunked  # or use manual chunking if you prefer
from typing import Tuple, List, Any

from datetime import datetime
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf
import yfinance as yf



async def insider_roster_holdings(ticker):
    await db.connect()

    try:
        data = yf.Ticker(ticker)
        df = data.get_insider_roster_holders()

        if df is None or df.empty: #type: ignore
            print(f"[{ticker}] No insider holdings data.")
            return

        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_') #type: ignore
        df['ticker'] = ticker

        # Example upsert (adjust table/columns as needed)
        await db.batch_upsert_dataframe(df, table_name='yf_insider_roster_holdings', unique_columns=['ticker', 'name']) #type: ignore

        print(f"[{ticker}] Insider holdings saved.")
    except Exception as e:
        print(f"[{ticker}] Error: {e}")


async def run_insider_holdings():
    while True:
        print(f"🔄 Starting insider holdings run at {datetime.now().isoformat()}")
        
        for batch in chunked(most_active_nonetf, 7):
            print(f"🚀 Processing batch: {batch}")
            tasks = [insider_roster_holdings(ticker) for ticker in batch]
            await asyncio.gather(*tasks)

        print("✅ All batches complete. Sleeping for 12 hours.\n")
        await asyncio.sleep(12 * 60 * 60)  # 12 hours = 43,200 seconds



asyncio.run(run_insider_holdings())