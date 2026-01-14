import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *

from _webull.models.instutitions import Institutions
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf
from more_itertools import chunked



async def institutions(ticker):
    try:
        ticker_id = wbt.ticker_to_id_map.get(ticker)
        url = f"https://quotes-gw.webullfintech.com/api/information/stock/getInstitutionalHolding?tickerId={ticker_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:

                data = await resp.json()

                institutionHolding = data['institutionHolding']

                stat = institutionHolding.get('stat')

                newPosition = institutionHolding.get('newPosition')
                increase = institutionHolding.get('increase')
                soldOut = institutionHolding.get('soldOut')
                decrease = institutionHolding.get('decrease')

                data = Institutions(stat, newPosition, increase, soldOut, decrease)

                df = data.as_dataframe
                df['ticker'] = ticker

                await db.batch_upsert_dataframe(df, table_name='institutions', unique_columns=['ticker'])
    except Exception as e:
        print(f"{e} - {ticker}")

async def run_institutions():
    await db.connect()
    
    while True:
        print(f"[{datetime.now()}] Starting institutional data refresh...")

        for batch in chunked(most_active_nonetf, 10):
            tasks = [institutions(ticker) for ticker in batch]
            await asyncio.gather(*tasks)
            await asyncio.sleep(10)  # small pause between batches to reduce burst load

        print(f"[{datetime.now()}] Completed institutional refresh. Sleeping for 12 hours...")
        await asyncio.sleep(60 * 60 * 12)  # 12 hours

if __name__ == "__main__":
    asyncio.run(run_institutions())