import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import math
from datetime import datetime, time
import pytz
import aiohttp
import pandas as pd
from _webull.models.financials import IncomeStatement
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf
from imports import *

processed = set()

async def income_statement(
    ticker: str,
    session: aiohttp.ClientSession,
) -> None:
    """
    Fetch and store the income statement for a single ticker.  This
    function does not open or close the database connection or the
    HTTP session; these must be managed by the caller.

    Args:
        ticker: The stock ticker symbol.
        session: A shared aiohttp ClientSession used for making HTTP requests.
    """
    ticker_id = wbt.ticker_to_id_map.get(ticker)
    if not ticker_id:
        return
    url = (
        "https://quotes-gw.webullfintech.com/api/information/financial/incomestatement"
        f"?tickerId={ticker_id}&type=102&fiscalPeriod=1,2,3,4&limit=11"
    )
    try:
        async with session.get(url) as resp:
            data = await resp.json()
        records = data.get('data', [])
        if not records:
            return
        stmt = IncomeStatement(records)
        df = stmt.as_dataframe
        df['ticker'] = ticker
        await db.batch_upsert_dataframe(
            df,
            table_name='income_statement',
            unique_columns=['ticker', 'fiscal_year', 'fiscal_period'],
        )
    except Exception as e:
        print(f"[ERROR] {e} - {ticker}")

BATCH_SIZE = 7
RUNS_PER_DAY = 2
PERIOD = 86400 // RUNS_PER_DAY  # Seconds between runs (43200 for 2/day)

async def run_income_statement():
    """
    Periodically fetch and store income statements for the most active non‑ETF
    tickers.  A single database connection and HTTP session are used
    throughout the lifetime of the coroutine.
    """
    tickers = most_active_nonetf  # list of tickers
    await db.connect()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                print("Starting income statement run...")
                for i in range(0, len(tickers), BATCH_SIZE):
                    batch = tickers[i : i + BATCH_SIZE]
                    tasks = [income_statement(tkr, session) for tkr in batch]
                    await asyncio.gather(*tasks)
                    print(
                        f"Completed batch {i//BATCH_SIZE + 1} of {math.ceil(len(tickers)/BATCH_SIZE)}"
                    )
                print(
                    f"All batches done. Sleeping for {PERIOD/3600:.2f} hours."
                )
                await asyncio.sleep(PERIOD)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(run_income_statement())