import sys
import asyncio
import time
from pathlib import Path
import pandas as pd
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from tabulate import tabulate

# Make sure project directory is in path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
from imports import *
from UTILS.confluence import score_options_flow


import asyncio
import pandas as pd
from itertools import islice

BATCH_SIZE = 5
DELAY_SECONDS = 60  # Delay between each full batch cycle
# Fix timezone-aware timestamps that break asyncpg
def sanitize_timestamps(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].apply(lambda x: x.to_pydatetime().replace(tzinfo=None) if pd.notnull(x) else None)


def chunked(iterable, size):
    """Yield successive chunks of size `size` from iterable."""
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            break
        yield batch

async def atm_options(ticker: str) -> None:
    """
    Fetch at-the-money options for a single ticker and upsert them into
    the ``atm_options`` table.  Assumes an active database connection.
    """
    try:
        # Note: The ticker is interpolated directly here; if user input is possible,
        # parameterize this query to avoid SQL injection.
        query = f"""
        SELECT wo.*
        FROM wb_opts wo
        JOIN multi_quote mq ON wo.ticker = mq.ticker
        WHERE wo.ticker = '{ticker}'
          AND wo.strike BETWEEN mq.close * 0.96 AND mq.close * 1.04
          AND wo.expiry >= CURRENT_DATE
        ORDER BY ABS(wo.strike - mq.close) ASC;
        """
        results = await db.fetch(query)
        if not results:
            print(f"[{ticker}] No ATM options found.")
            return
        df = pd.DataFrame(
            results, columns=await db.get_table_columns("wb_opts")
        )
        # Drop unused metadata columns
        df = df.drop(
            columns=["insertion_timestamp", "trade_time"],
            errors="ignore",
        )
        # Normalize expiry column to native dates
        if "expiry" in df.columns:
            df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.date
        # Drop rows lacking required identifiers
        df = df.dropna(subset=["expiry", "option_id"])
        if df.empty:
            return
        call_mask = df["call_put"].astype(str).str.lower() == "call"
        put_mask = df["call_put"].astype(str).str.lower() == "put"
        call_volume = pd.to_numeric(df.loc[call_mask, "volume"], errors="coerce").fillna(0).sum()
        put_volume = pd.to_numeric(df.loc[put_mask, "volume"], errors="coerce").fillna(0).sum()
        call_oi = pd.to_numeric(df.loc[call_mask, "oi"], errors="coerce").fillna(0).sum()
        put_oi = pd.to_numeric(df.loc[put_mask, "oi"], errors="coerce").fillna(0).sum()

        flow_score = score_options_flow(
            call_volume=call_volume,
            put_volume=put_volume,
            call_oi=call_oi,
            put_oi=put_oi,
            label="atm",
        )
        for col, value in flow_score.to_columns("atm_flow").items():
            df[col] = value

        await db.batch_upsert_dataframe(
            df,
            table_name="atm_options",
            unique_columns=["option_id"],
        )
        print(f"[{ticker}] Upserted {len(df)} ATM options.")
    except Exception as e:
        print(f"[!] Error in atm_options({ticker}): {e}")

async def run_atm_options() -> None:
    """
    Continuously process ATM options for the most active tickers in batches.
    Establishes a single database connection and sleeps between full cycles
    to avoid overwhelming the database and the API.
    """
    await db.connect()
    try:
        while True:
            for batch in chunked(most_active_tickers, BATCH_SIZE):
                print(f"Processing batch: {batch}")
                tasks = [atm_options(t) for t in batch]
                await asyncio.gather(*tasks)
            # Sleep after processing all tickers
            #await asyncio.sleep(DELAY_SECONDS)
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(run_atm_options())
