import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from datetime import datetime
import aiohttp
import pandas as pd
from _webull.models.etf_holdings import ETFHoldings
from more_itertools import chunked
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf
from imports import *




async def etf_holdings(ticker: str, size: str = '50', session: aiohttp.ClientSession | None = None) -> None:
    """
    Fetch and store the holdings of an ETF for a given ticker.  A reusable
    HTTP session may be provided; if not, a temporary one will be created.

    Args:
        ticker: The stock ticker for which to fetch ETF holdings.
        size: Number of holdings records to request from the API. Defaults to '50'.
        session: An optional aiohttp ClientSession.  When provided, it will
            be reused for the API call.  Otherwise, a new session is created
            and closed within this function.
    """
    try:
        ticker_id = wbt.ticker_to_id_map.get(ticker)
        if not ticker_id:
            print(f"[ERROR] Unknown ticker id for {ticker}")
            return
        url = (
            "https://quotes-gw.webullfintech.com/api/information/company/queryEtfList"
            f"?tickerId={ticker_id}&pageIndex=1&pageSize={size}"
        )
        own_session = False
        if session is None:
            session = aiohttp.ClientSession(headers=generate_webull_headers())
            own_session = True
        try:
            async with session.get(url) as resp:
                data = await resp.json()
            data_list = data.get('dataList')
            if not data_list:
                return
            results = ETFHoldings(data_list)
            df = results.as_dataframe
            await db.batch_upsert_dataframe(
                df,
                table_name='etf_holdings',
                unique_columns=['fund_id', 'ticker_id'],
            )
        finally:
            if own_session:
                await session.close()
    except Exception as e:
        print(f"[ERROR] {e} - {ticker}")

async def run_etf_holdings() -> None:
    """
    Periodically update ETF holdings for all non-ETF tickers.  A single
    database connection and HTTP session are created and reused for all
    requests.  After processing all tickers, the coroutine sleeps for
    10 minutes before starting over.
    """
    await db.connect()
    try:
        # Create one session with the required headers for all requests
        async with aiohttp.ClientSession(headers=generate_webull_headers()) as session:
            while True:
                for batch in chunked(most_active_nonetf, 7):
                    tasks = [etf_holdings(ticker, session=session) for ticker in batch]
                    await asyncio.gather(*tasks)
                print("All ETF holdings processed. Waiting 10 minutes before next cycle...")
                await asyncio.sleep(600)  # 10 minutes
    finally:
        await db.disconnect()

# Entry point
if __name__ == "__main__":
    asyncio.run(run_etf_holdings())