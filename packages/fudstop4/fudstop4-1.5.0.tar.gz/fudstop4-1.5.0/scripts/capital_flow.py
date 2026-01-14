import asyncio
import sys
from pathlib import Path
from datetime import datetime, time
import pytz
import aiohttp
import pandas as pd

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)


from imports import *
from UTILS.charting import generate_capital_flow_image
from UTILS.charting import store_capital_flow_image, reshape_capital_flow_df
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf,most_active_tickers

from _webull.models.capital_flow import CapitalFlowLatest


import asyncio
from more_itertools import chunked
from datetime import datetime

async def capital_flow(ticker):
    try:
        ticker_id = wbt.ticker_to_id_map.get(ticker)
        url = f"https://quotes-gw.webullfintech.com/api/stock/capitalflow/ticker?tickerId={ticker_id}&showHis=true"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                latest = data['latest']
                date_str = latest['date']
                item = latest['item']

                # Parse date string to datetime.date object
                parsed_date = datetime.strptime(date_str, "%Y%m%d").date()

                flow = CapitalFlowLatest(parsed_date, item)
                df = flow.as_dataframe
                df['ticker'] = ticker

                # Ensure 'date' column is string for DB insert
                if 'date' in df.columns:
                    df['date'] = df['date'].astype(str)

                # Store tabular data
                df['latest'] = date_str
                await db.batch_upsert_dataframe(df, table_name='capital_flow', unique_columns=['ticker', 'date'])

                reshaped_df = reshape_capital_flow_df(df.drop(columns=['ticker', 'date', 'insertion_timestamp'], errors='ignore'))

                if reshaped_df.empty:
                    print(f"[ERROR] no numeric data to plot - {ticker}")
                    return

                image_bytes = generate_capital_flow_image(reshaped_df, ticker)
                await store_capital_flow_image(ticker, parsed_date, image_bytes)

    except Exception as e:
        print(f"[ERROR] {e} - {ticker}")
async def run_capital_flow():
    await db.connect()

    while True:
        print(f"[{datetime.now()}] Running capital flow update...")

        for batch in chunked(most_active_tickers, 7):
            tasks = [capital_flow(ticker) for ticker in batch]
            await asyncio.gather(*tasks)
        await asyncio.sleep(20)

if __name__ == "__main__":
    asyncio.run(run_capital_flow())