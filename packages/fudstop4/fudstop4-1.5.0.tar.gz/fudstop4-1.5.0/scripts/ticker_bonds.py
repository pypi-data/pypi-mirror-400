from pathlib import Path
import sys
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
from _webull.models.ticker_bonds import TickerBonds
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers



MAX_CONCURRENT = 5  # Set your concurrency limit here
INTERVAL = 3600     # One hour in seconds

async def ticker_bonds(ticker, size='50'):
    try:
        ticker_id = wbt.ticker_to_id_map.get(ticker)
        url = f"https://quotes-gw.webullfintech.com/api/wlas/bonds/list?belongTickerId={ticker_id}&pageIndex=1&direction=-1&pageSize={size}&regionId=6&supportBroker=8&order=askYieldYTW"
        async with aiohttp.ClientSession(headers=generate_webull_headers()) as session:
            async with session.get(url) as resp:
                data = await resp.json()
                data = data['data']
                data = TickerBonds(data)
                df = data.as_dataframe
                df['ticker'] = ticker
                await db.batch_upsert_dataframe(df, table_name='ticker_bonds', unique_columns=['isin'])
    except Exception as e:
        print(f"No bonds for {ticker} found.")
async def run_bonds():
    await db.connect()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    async def sem_task(ticker):
        async with semaphore:
            await ticker_bonds(ticker)
    while True:
        print(f"Running ticker_bonds for all tickers at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        tasks = [sem_task(i) for i in most_active_tickers]
        await asyncio.gather(*tasks)
        print(f"Completed all requests. Sleeping for {INTERVAL} seconds.")      
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    asyncio.run(run_bonds())