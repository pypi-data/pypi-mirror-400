import asyncio
import sys
from pathlib import Path
from datetime import datetime
import aiohttp
import pandas as pd

from fudstop4.apis.occ.occ_sdk import occSDK
occ = occSDK()


from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
SLEEP_SECONDS = 900  # 15 minutes
MAX_CONCURRENT_TASKS = 8  # Adjust as needed for performance/API limits

sem = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
async def stock_info(ticker):
    async with sem:
        try:
            info = await occ.stock_info(ticker)

            if info is not None and hasattr(info, 'as_dataframe'):
                df = info.as_dataframe

                # ✅ Normalize date fields before upserting
                date_columns = [
                    'latest_dividend_date',
                    'latest_split_date',
                    'latest_earnings_date',
                    'estimate_earnings_date',
                    'next_earning_day',
                    'dividend_date',  # New field in ISO format with T00:00:00
                ]

                for col in date_columns:
                    if col in df.columns:
                        malformed = df[~df[col].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$', na=False)]
                        if not malformed.empty:
                            print(f"[!] {ticker}: Malformed values in `{col}` — setting to NULL:\n{malformed[[col]]}")

                        # Cast ISO datetime strings to date safely
                        df[col] = pd.to_datetime(df[col], errors='coerce').dt.date

                await db.batch_upsert_dataframe(
                    df,
                    table_name='info',
                    unique_columns=['ticker'],
                )
                print(f"[✓] Updated: {ticker} at {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            print(f"[!] Error for {ticker}: {e}")

async def main_loop():
    await db.connect()
    try:
        while True:
            try:
                tasks = [stock_info(ticker) for ticker in most_active_tickers]
                await asyncio.gather(*tasks)
            except Exception as e:
                print(f"[!] Main loop error: {e}")
            print(f"[⏰] Sleeping for {SLEEP_SECONDS // 60} minutes...")
            await asyncio.sleep(SLEEP_SECONDS)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main_loop())