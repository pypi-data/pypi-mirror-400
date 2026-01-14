import numpy as np
from numba import njit
import pandas as pd
import sys
from pathlib import Path
import math
from datetime import time
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()
from fudstop4.apis.webull.webull_trading import WebullTrading
import aiohttp
from fudstop4.apis.helpers import generate_webull_headers
wbt = WebullTrading()


async def main(ticker):
    ticker_id = wbt.ticker_to_id_map.get(ticker)
    url = (
        f"https://quotes-gw.webullfintech.com/api/quote/charts/seconds-mini?"
        f"type=s1&count=800&restorationType=0&extendTrading=1&tickerId={ticker_id}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))) as resp:
            json_data = await resp.json()

            # Extract list of second bars
            raw_data = [i.get('data') for i in json_data if i.get('data') is not None]
            
            print(raw_data)
          
            

asyncio.run(main('AAPL'))