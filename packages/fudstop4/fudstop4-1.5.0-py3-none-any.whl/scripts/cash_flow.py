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
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf
from _webull.models.financials import CashFlow
import math
processed = set()
async def cash_flow(ticker: str, limit: str = '11', session: aiohttp.ClientSession | None = None) -> None:
    """
    Retrieve cash flow data for a single ticker and write it to the database.
    A pre-existing HTTP session should be provided; this function does not
    establish its own database connection.  The ``limit`` parameter is
    currently unused but kept for backwards compatibility.

    Args:
        ticker: The stock ticker to fetch cash flow data for.
        limit: The number of records to request from the API.  Defaults to '11'.
        session: An aiohttp ClientSession to use for HTTP requests.  If ``None``
            is provided, a temporary session will be created and closed within
            this call.
    """
    # Determine the ticker ID used by the Webull API
    ticker_id = wbt.ticker_to_id_map.get(ticker)
    if not ticker_id:
        print(f"[ERROR] Unknown ticker id for {ticker}")
        return

    # Ensure we have a session to use.  If none is provided, create one
    own_session = False
    if session is None:
        session = aiohttp.ClientSession()
        own_session = True
    try:
        url = (
            "https://quotes-gw.webullfintech.com/api/information/financial/cashflow"
            f"?tickerId={ticker_id}&type=102&fiscalPeriod=1,2,3,4&limit={limit}"
        )
        async with session.get(url) as resp:
            data = await resp.json()
        data = data.get('data', [])
        if not data:
            return
        cash = CashFlow(data)
        df = cash.as_dataframe
        df['ticker'] = ticker
        await db.batch_upsert_dataframe(
            df,
            table_name='cash_flow',
            unique_columns=['ticker', 'fiscal_year', 'fiscal_period'],
        )
    except Exception as e:
        print(f"[ERROR] {e} - {ticker}")
    finally:
        if own_session:
            await session.close()

BATCH_SIZE = 7
RUNS_PER_DAY = 2
PERIOD = 86400 // RUNS_PER_DAY  # Seconds between runs (43200 for 2/day)

async def run_cash_flow() -> None:
    """
    Continuously fetch cash flow data for the most active non-ETF tickers.
    A single database connection and HTTP session are created and reused
    throughout the lifetime of this coroutine.  Tickers are processed in
    batches with a configurable delay between cycles.
    """
    tickers = most_active_nonetf  # list of tickers
    await db.connect()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                print("Starting cash flow run...")
                for i in range(0, len(tickers), BATCH_SIZE):
                    batch = tickers[i : i + BATCH_SIZE]
                    tasks = [cash_flow(tkr, session=session) for tkr in batch]
                    await asyncio.gather(*tasks)
                    print(
                        f"Completed batch {i // BATCH_SIZE + 1} of {math.ceil(len(tickers) / BATCH_SIZE)}"
                    )
                print(
                    f"All batches done. Sleeping for {PERIOD/3600:.2f} hours."
                )
                await asyncio.sleep(PERIOD)
    finally:
        # Ensure the database connection is properly closed when the loop exits
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(run_cash_flow())