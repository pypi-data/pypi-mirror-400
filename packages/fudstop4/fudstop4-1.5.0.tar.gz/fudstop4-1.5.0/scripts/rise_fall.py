import asyncio
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import aiohttp

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4.apis.webull.webull_markets import WebullMarkets
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
db = PolygonOptions()
from _webull.models.rise_fall import Ticker, Values
wbm = WebullMarkets()
SLEEP_SECONDS = 60  # 1 minute

async def fetch_data(rise_or_fall: str, rank_type: str):
    direction = -1 if rise_or_fall == "rise" else 1
    url = f"https://quotes-gw.webullfintech.com/api/wlas/ranking/v9/{rise_or_fall}?regionId=6&rankType={rank_type}&pageIndex=1&pageSize=50&order=changeRatio&direction={direction}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            data = data.get('data', [])

            ticker = [i.get('ticker') for i in data]
            values = [i.get('values') for i in data]

            ticker_obj = Ticker(ticker)
            values_obj = Values(values)
            print(f"[DEBUG] Fetching {rise_or_fall=} {rank_type=}")
            return ticker_obj, values_obj, rise_or_fall, rank_type

async def top_gainers_losers():
    await db.connect()

    tasks = [
        fetch_data(rise_or_fall, rt)
        for rise_or_fall in ["rise", "fall"]
        for rt in wbm.top_gainer_loser_types
    ]

    results = await asyncio.gather(*tasks)

    for ticker_obj, values_obj, rise_or_fall, rank_type in results:
        ticker_df = ticker_obj.as_dataframe
        values_df = values_obj.as_dataframe

        merged_df = pd.merge(ticker_df, values_df, on='ticker_id')
        merged_df['rise_or_fall'] = rise_or_fall
        merged_df['rank_type'] = rank_type

        await db.batch_upsert_dataframe(
            merged_df,
            table_name=f"{rise_or_fall}_{rank_type}",
            unique_columns=['ticker_id', 'rank_type']
        )

        print(f"[+] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Upserted {len(merged_df)} rows into {rise_or_fall}_{rank_type}")

async def main_loop():
    while True:
        print(f"[*] Starting top_gainers_losers cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            await top_gainers_losers()
        except Exception as e:
            print(f"[!] Error during fetch: {e}")
        print(f"[*] Sleeping for {SLEEP_SECONDS} seconds...\n")
        await asyncio.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    asyncio.run(main_loop())
