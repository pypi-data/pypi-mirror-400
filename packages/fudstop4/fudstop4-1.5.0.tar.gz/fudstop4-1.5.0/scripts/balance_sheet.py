import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from datetime import datetime, time
import pytz
import aiohttp
import pandas as pd
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf
from _webull.models.financials import BalanceSheet
import math

from imports import *


processed = set()
async def balance_sheet(
    ticker: str,
    session: aiohttp.ClientSession,
    limit: str = "11",
) -> None:
    """
    Fetch and persist balance sheet information for a single ticker.

    Parameters
    ----------
    ticker:
        The stock ticker symbol to process.
    session:
        A shared aiohttp session used for HTTP requests.
    limit:
        The number of records to retrieve from the upstream API (default: '11').
    """
    ticker_id = wbt.ticker_to_id_map.get(ticker)
    if not ticker_id:
        return
    url = (
        "https://quotes-gw.webullfintech.com/api/information/financial/balancesheet"
        f"?tickerId={ticker_id}&type=102&fiscalPeriod=1,2,3,4&limit={limit}"
    )
    async with session.get(url) as resp:
        data = await resp.json()
        data = data.get("data")
        if not data:
            return
        sheet = BalanceSheet(data)
        df = sheet.as_dataframe
        df["ticker"] = ticker
        await db.batch_upsert_dataframe(
            df,
            table_name="balance_sheet",
            unique_columns=["ticker", "fiscal_year", "fiscal_period"],
        )

            

BATCH_SIZE = 7
RUNS_PER_DAY = 2
PERIOD = 86400 // RUNS_PER_DAY  # Seconds between runs (43200 for 2/day)

async def run_balance_sheet() -> None:
    """
    Periodically fetch and update balance sheets for the most active non‑ETF tickers.
    Establishes a single database connection and reuses a single HTTP session
    across batches to reduce overhead.
    """
    tickers = most_active_nonetf
    await db.connect()
    try:
        while True:
            print("Starting balance sheet run...")
            async with aiohttp.ClientSession() as session:
                for i in range(0, len(tickers), BATCH_SIZE):
                    batch = tickers[i : i + BATCH_SIZE]
                    tasks = [balance_sheet(tkr, session) for tkr in batch]
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
    asyncio.run(run_balance_sheet())
