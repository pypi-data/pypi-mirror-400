from pathlib import Path
import sys
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
from _yfinance.models.price_target import yfPriceTarget
from more_itertools import chunked  # or use manual chunking if you prefer
from typing import Tuple, List, Any
from datetime import datetime, time as dtime
from datetime import datetime
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
import yfinance as yf
import pytz
from fudstop4.apis.helpers import generate_webull_headers
import os
from dotenv import load_dotenv
load_dotenv()

async def factors(ticker, timespan:str='m1'):
    timespan_dict = { 
        'm1': '1min',
        'm5': '5min',
        'm15': '15min',
        'm20': '20min',
        'm30': '30min',
        'm60': '1h',
        'm120': '2h',
        'm240': '4h',
        'w': 'week',
        'd': 'day',
        'm': 'month'
    }
    ticker_id = wbt.ticker_to_id_map.get(ticker)
    url = f"https://quotes-gw.webullfintech.com/api/quote/charts/query-mini?type={timespan}&count=800&restorationType=1&loadFactor=1&extendTrading=1&tickerId={ticker_id}"


    async with aiohttp.ClientSession(headers=generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))) as session:
        async with session.get(url) as resp:

            data = await resp.json()

            try:
                factors = [i.get('factors', []) for i in data]
                print(factors)
                factors = [i for sublist in factors for i in sublist]

                effective_dates = [
                    datetime.utcfromtimestamp(f.get('effectiveDate')).strftime('%Y-%m-%d')
                    if f.get('effectiveDate') is not None else None
                    for f in factors
                ]
                factorPricePre = [i.get('factorPricePre') for i in factors]
                factorPricePost = [i.get('factorPricePost') for i in factors]
                factorVolumePre = [i.get('factorVolumePre') for i in factors]
                factorVolumePost = [i.get('factorVolumePost') for i in factors]

                dict = { 
                    'dates': effective_dates,
                    'factor_price_pre': factorPricePre,
                    'factor_price_post': factorPricePost,
                    'factor_volume_pre': factorVolumePre,
                    'factor_volume_post': factorVolumePost
                }

                df = pd.DataFrame(dict)
                df['timespan'] = timespan_dict.get(timespan)
                df['ticker'] = ticker
                df = df[::-1]

                await db.batch_upsert_dataframe(df, table_name='factors', unique_columns=['ticker', 'timespan'])
            except Exception as e:
                print(e)

timespans = ['m1', 'm5', 'm15', 'm20', 'm30', 'm60', 'm120', 'm240']
EST = pytz.timezone("US/Eastern")

def within_market_hours():
    now = datetime.now(EST).time()
    return dtime(9, 30) <= now <= dtime(16, 0)

async def run_factors():
    await db.connect()
    from more_itertools import chunked  # pip install more-itertools if needed

    while True:

        print("Within market hours. Running tasks...")

        tasks = [
            factors(ticker, timespan)
            for ticker in most_active_tickers
            for timespan in timespans
        ]

        # Batch in groups of 7, run each batch concurrently
        for batch in chunked(tasks, 7):
            await asyncio.gather(*batch)
            print(f"Completed batch of {len(batch)} tasks.")

        print("All batches complete for this run. Sleeping until next run.")

        # Sleep until next day, or set to your desired frequency (e.g., every 1 hour)
        await asyncio.sleep(60 * 60)  # Check every hour


asyncio.run(run_factors())