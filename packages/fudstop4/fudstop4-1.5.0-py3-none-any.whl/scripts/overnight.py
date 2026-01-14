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
from _webull.models.overnight import OvernightTicker, OvernightValues
import datetime as dt
SLEEP_SECONDS = 60  # Run every 1 minute
EST = pytz.timezone("US/Eastern")

def within_overnight_hours(now: dt.datetime) -> bool:
    current_time = now.time()
    return current_time >= dt.time(20, 0) or current_time <= dt.time(9, 30)

async def overnight():
    await db.connect()
    url = "https://quotes-gw.webullfintech.com/api/wlas/ranking/overnight?regionId=6&brokerId=8&order=overnightVolume&direction=-1&pageIndex=1&pageSize=50"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            data = data.get('data', [])

            ticker = [i.get('ticker') for i in data]
            values = [i.get('values') for i in data]

            ticker_obj = OvernightTicker(ticker)
            values_obj = OvernightValues(values)

            ticker_df = ticker_obj.as_dataframe
            values_df = values_obj.as_dataframe

            merged_df = pd.merge(ticker_df, values_df, on='ticker_id')

            await db.batch_upsert_dataframe(merged_df, table_name='overnight', unique_columns=['ticker_id'])
            print(f"[+] {datetime.now(EST).strftime('%Y-%m-%d %I:%M:%S %p')} - Upserted {len(merged_df)} overnight tickers")

async def main_loop():
    while True:
        now_est = datetime.now(EST)
        if within_overnight_hours(now_est):
            print(f"[*] Running overnight at {now_est.strftime('%Y-%m-%d %I:%M:%S %p EST')}")
            try:
                await overnight()
            except Exception as e:
                print(f"[!] Error: {e}")
        else:
            print(f"[!] Skipping run outside allowed hours - {now_est.strftime('%I:%M:%S %p EST')}")
        await asyncio.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    asyncio.run(main_loop())
