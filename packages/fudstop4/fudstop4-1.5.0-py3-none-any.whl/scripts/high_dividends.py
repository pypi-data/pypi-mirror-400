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
from _webull.models.dividends import DividendsValues, HighDividendTicker

SLEEP_SECONDS = 86400  # 24 hours

async def high_dividends(session: aiohttp.ClientSession) -> None:
    """
    Fetch and store high dividend information.  This function relies on an
    existing database connection and HTTP session.  It does not connect
    or disconnect from the database itself.

    Args:
        session: An aiohttp ClientSession used to perform the HTTP request.
    """
    url = (
        "https://quotes-gw.webullfintech.com/api/wlas/ranking/dividend"
        "?regionId=6&rankType=dividend&pageIndex=1&pageSize=50&order=yield&direction=-1"
    )
    async with session.get(url) as resp:
        data = await resp.json()
    entries = data.get('data', [])
    if not entries:
        print(
            f"[!] No dividend data returned at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return
    tickers = [item.get('ticker') for item in entries]
    values = [item.get('values') for item in entries]
    ticker_obj = HighDividendTicker(tickers)
    values_obj = DividendsValues(values)
    ticker_df = ticker_obj.as_dataframe
    values_df = values_obj.as_dataframe
    merged_df = pd.merge(ticker_df, values_df, on='ticker_id')
    await db.batch_upsert_dataframe(
        merged_df,
        table_name='high_dividends',
        unique_columns=['ticker_id', 'ex_date'],
    )
    print(
        f"[+] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Upserted {len(merged_df)} high dividend entries."
    )

async def main_loop() -> None:
    """
    Execute the high dividends update once per day.  A single database
    connection and HTTP session are opened and reused for the lifetime of
    this loop.  Any errors encountered during the update are caught and
    logged without breaking the loop.
    """
    await db.connect()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    print(
                        f"[*] Starting daily high_dividends run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    await high_dividends(session)
                except Exception as e:
                    print(f"[!] Error during high_dividends: {e}")
                print(f"[*] Sleeping for 24 hours...\n")
                await asyncio.sleep(SLEEP_SECONDS)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main_loop())
