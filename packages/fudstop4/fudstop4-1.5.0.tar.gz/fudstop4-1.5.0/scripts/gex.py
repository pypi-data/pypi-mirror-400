#!/usr/bin/env python3
import sys
from pathlib import Path

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
import asyncio
from UTILS import exposure
from UTILS.confluence import score_gex
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
SEM = asyncio.Semaphore(6)          # six‑wide concurrency

async def process_one_ticker(db, ticker: str):
    async with SEM:
        q = f"SELECT * FROM wb_opts WHERE ticker = '{ticker}'"
        raw = await db.fetch(q)
        cols = await db.get_table_columns('wb_opts')
        df = pd.DataFrame(raw, columns=cols)

        if df.empty:
            return None  # Skip

        # Get spot price (use open if that's your convention)
        spot_q = f"SELECT open FROM multi_quote WHERE ticker = '{ticker}'"
        spot_result = await db.fetch(spot_q)
        opens = [i.get('open') for i in spot_result]
        spot = float(opens[0])
        print(spot)
        enriched, summary = exposure.compute_exposures(df, spot)

        # Add ticker to summary
        summary = pd.DataFrame(summary, index=[0])
        summary["ticker"] = ticker

        gex_score = score_gex(
            total_gex=summary["total_gex"].iloc[0],
            spot_price=summary.get("spot_price", pd.Series([spot])).iloc[0],
            flip_strike=summary.get("max_neg_gamma_strike", pd.Series([None])).iloc[0],
        )
        for col, value in gex_score.to_columns("gex").items():
            summary[col] = value
        await db.batch_upsert_dataframe(df=summary, table_name='gex', unique_columns=['ticker'])
        print(f"Inserted {ticker}.")
        return summary  # just return summary dict per ticker


async def pump_most_active(db, tickers) -> None:
    """
    Continuously compute option exposures (GEX) for a list of tickers.
    A single database connection is opened and reused for the duration of
    this coroutine.  After each full cycle of processing all tickers, the
    coroutine sleeps for a short interval to avoid hammering the database.

    Args:
        db: A database object with asynchronous connect/fetch/upsert methods.
        tickers: A list of ticker symbols to process.
    """
    await db.connect()
    try:
        while True:
            # Create tasks for each ticker; results are gathered concurrently
            tasks = [process_one_ticker(db, t) for t in tickers]
            _ = await asyncio.gather(*tasks)
            # Optional: process the summaries returned by tasks if needed
            # Sleep to avoid running continuously without pause
            await asyncio.sleep(600)  # 10 minutes between runs
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(pump_most_active(db=db, tickers=most_active_tickers))
