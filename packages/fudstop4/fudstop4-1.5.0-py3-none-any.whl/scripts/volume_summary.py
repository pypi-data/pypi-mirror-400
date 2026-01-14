import sys
from pathlib import Path
import asyncio
import aiohttp
import pandas as pd
import numpy as np
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
CONCURRENCY = 15  # Number of concurrent requests

CONCURRENCY = 15  # max concurrent requests
UPDATE_INTERVAL = 20  # seconds

async def volume_summary(ticker, semaphore):
    async with semaphore:
        x = await wb_opts.multi_options(
            ticker=ticker,
            headers=generate_webull_headers()
        )

        df = x.as_dataframe
        df['ticker'] = ticker
        print(df)
        calls_df = df[df['call_put'] == 'call']
        puts_df  = df[df['call_put'] == 'put']

        call_volume = (
            calls_df.groupby('expiry')['volume']
            .sum()
            .rename('call_volume')
        )

        put_volume = (
            puts_df.groupby('expiry')['volume']
            .sum()
            .rename('put_volume')
        )

        volume_summary = (
            pd.concat([call_volume, put_volume], axis=1)
            .fillna(0)
            .reset_index()
        )

        volume_summary["expiry"] = pd.to_datetime(volume_summary["expiry"], errors="coerce").dt.date
        volume_summary['ticker'] = ticker
        await db.batch_upsert_dataframe(
            volume_summary,
            table_name='volume_summary',
            unique_columns=['ticker', 'expiry']
        )

        return volume_summary.to_dict("records")
async def run_summary():
    await db.connect()
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession():
        while True:
            start = time.monotonic()

            tasks = [
                volume_summary(ticker, semaphore)
                for ticker in most_active_tickers
            ]

            await asyncio.gather(*tasks)
            print("Done batch")

            elapsed = time.monotonic() - start
            sleep_for = max(0, UPDATE_INTERVAL - elapsed)

            await asyncio.sleep(sleep_for)
# Example entrypoint
if __name__ == "__main__":
    asyncio.run(run_summary())