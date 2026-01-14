from fudstop4.apis.webull.webull_options.webull_options import WebullOptions
from fudstop4.apis.webull.webull_trading import WebullTrading
from fudstop4.apis.webull.trade_models.stock_quote import MultiQuote
wb_opts = WebullOptions()
trading = WebullTrading()
from fudstop4.apis.webull.webull_crypto import WebullCrypto
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
crypto = WebullCrypto()
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
opts = PolygonOptions()


import asyncio
import pandas as pd
import time


import requests


import asyncio
import requests

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def fetch_chart_data_batch(tickers, ticker_ids):
    loop = asyncio.get_running_loop()
    ticker_ids_str = ",".join(str(tid) for tid in ticker_ids)
    url = f"https://quotes-gw.webullfintech.com/api/bgw/quote/realtime?ids={ticker_ids_str}&includeSecu=1&delay=0&more=1"
    result = await loop.run_in_executor(None, requests.get, url)
    data = result.json()
    
    data = MultiQuote(data)
    data = data.as_dataframe
    data['ticker_id'] = data['ticker_id'].astype(int)
    data = data.rename(columns={'symbol': 'ticker'})
    data['ticker'] = data['ticker'].str.replace(r'USD$', '', regex=True)
    await opts.batch_upsert_dataframe(data, table_name='crypto', unique_columns=['ticker_id'])
    # return data

async def main():
    await opts.connect()
    while True:
        items = list(crypto.coin_to_id_map.items())
        batch_size = 50

        batch_tasks = []
        for batch in chunks(items, batch_size):
            tickers, ticker_ids = zip(*batch)
            batch_tasks.append(fetch_chart_data_batch(tickers, ticker_ids))

        await asyncio.gather(*batch_tasks)

asyncio.run(main())