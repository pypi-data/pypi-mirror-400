import asyncio
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import aiohttp

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from imports import *
from _webull.models.top_followed import FollowedTicker, FollowedValues
from typing import Tuple, List, Any

type_dict = { 
    '1': '1d',
    '2': '7d',
    '3': 'all'
}
types = ['1', '2', '3']
SLEEP_SECONDS = 1800  # 30 minutes

async def top_followed(type):
    url = f"https://quotes-gw.webullfintech.com/api/wlas/ranking/watchlist-followers?regionId=6&supportBroker=8&type={type}&pageIndex=1&pageSize=50"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            data = data.get('data', [])

            ticker = [i.get('ticker') for i in data]
            values = [i.get('values') for i in data]

            ticker_obj = FollowedTicker(ticker)
            values_obj = FollowedValues(values)

            return ticker_obj, values_obj, type

async def run_top_followed():
    await db.connect()
    tasks = [top_followed(i) for i in types]
    results = await asyncio.gather(*tasks)

    for ticker_ob, value_ob, type in results:
        ticker_df = ticker_ob.as_dataframe
        values_df = value_ob.as_dataframe

        merged_df = pd.merge(ticker_df, values_df, on='ticker_id')
        merged_df['type'] = type_dict.get(type)

        await db.batch_upsert_dataframe(
            merged_df,
            table_name='top_followed',
            unique_columns=['ticker_id', 'type']
        )
        print(f"[+] Upserted {len(merged_df)} rows for type: {type_dict.get(type)}")

async def main_loop():
    while True:
        print(f"[*] Running top_followed scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            await run_top_followed()
        except Exception as e:
            print(f"[!] Error in top_followed: {e}")
        print(f"[*] Sleeping for 30 minutes...\n")
        await asyncio.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    asyncio.run(main_loop())
