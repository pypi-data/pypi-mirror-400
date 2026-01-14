import asyncio
import sys
from pathlib import Path
from datetime import datetime
import aiohttp
import pandas as pd

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



async def earnings_estimate(ticker):
    await db.connect()

    try:
        data = yf.Ticker(ticker)
        df = data.earnings_estimate

        if df is None or df.empty:
            print(f"[{ticker}] No earnings data.")
            return

        df = df.reset_index()
        df['ticker'] = ticker

        rename_map = {
            '0q': 'Current Quarter',
            '+1q': 'Next Quarter',
            '0y': 'Current Fiscal Year',
            '+1y': 'Next Fiscal Year'
        }

        df['period'] = df['period'].replace(rename_map)
        df['ticker'] = ticker
        await db.batch_upsert_dataframe(df, table_name='yf_earnings_estimate', unique_columns=['ticker', 'period'])

        print(f"[{ticker}] Upserted successfully.")

    except Exception as e:
        print(f"[{ticker}] Error: {e}")


async def run_estimate():
    while True:
        print(f"🔄 Starting full run at {datetime.now().isoformat()}")
        for batch in chunked(most_active_nonetf, 7):
            print(f"🚀 Running batch: {batch}")
            tasks = [earnings_estimate(ticker) for ticker in batch]
            await asyncio.gather(*tasks)
        print(f"✅ All batches done. Sleeping 6 hours...\n")
        await asyncio.sleep(6 * 60 * 60)  # 6 hours


asyncio.run(run_estimate())