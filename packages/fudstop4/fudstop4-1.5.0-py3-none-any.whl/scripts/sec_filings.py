

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import aiohttp
import pandas as pd
import time
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from fudstop4.apis.sec.sec_sdk import SECSDK
from fudstop4.apis.polygonio.polygon_options import PolygonOptions

db = PolygonOptions()
sec = SECSDK()
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf
class RateLimiter:
    def __init__(self, rate_per_sec: int):
        self._interval = 1 / rate_per_sec
        self._last_call = 0
        self._lock = asyncio.Lock()

    async def wait(self):
        async with self._lock:
            now = time.monotonic()
            delta = now - self._last_call
            if delta < self._interval:
                await asyncio.sleep(self._interval - delta)
            self._last_call = time.monotonic()


sec = SECSDK()
rate_limiter = RateLimiter(rate_per_sec=10)


async def fetch_form4(ticker: str):
    await rate_limiter.wait()
    try:
        data = await sec.get_latest_form_4(ticker)
        await db.batch_upsert_dataframe(data, table_name="form_4", unique_columns=['ticker', 'transaction_date'])
    except Exception as e:
        print(f"{ticker} failed:", e)


async def run_once():
    tasks = [
        asyncio.create_task(fetch_form4(ticker))
        for ticker in most_active_nonetf
    ]
    await asyncio.gather(*tasks)


async def main():
    await db.connect()
    while True:
        start = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n=== SEC scan started @ {start} ===")
        await run_once()
        print("=== Scan complete. Sleeping 1 hour. ===\n")
        await asyncio.sleep(3600)


asyncio.run(main())