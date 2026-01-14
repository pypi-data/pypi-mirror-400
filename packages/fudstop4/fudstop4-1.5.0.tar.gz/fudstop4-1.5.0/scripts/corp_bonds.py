import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from datetime import datetime, time
import pytz
import aiohttp
import pandas as pd
from UTILS.db_tables import USBonds

from imports import *


rank_types = ['mag7', 'recently', 'highestYield', 'nonFinancial']





async def corp_bonds(rank_type: str, session: aiohttp.ClientSession) -> None:
    """
    Retrieve corporate bond rankings for the specified rank type and
    upsert the results into the ``corp_bonds`` table.  A pre-existing
    aiohttp session should be provided.

    Args:
        rank_type: The ranking category as defined by Webull (e.g., 'mag7',
            'recently', 'highestYield', or 'nonFinancial').  Certain rank types
            are normalized for storage.
        session: An aiohttp ClientSession to reuse for HTTP requests.
    """
    url = (
        "https://quotes-gw.webullfintech.com/api/wlas/bonds/corp-rank-list"
        "?regionId=6&supportBroker=8&direction=-1&pageIndex=1&pageSize=30"
        "&order=askYieldYTW&rankType=bondsCorp."
        f"{rank_type}"
    )
    # Normalize label for storage
    label = rank_type
    if rank_type == 'highestYield':
        label = 'highest_yield'
    elif rank_type == 'nonFinancial':
        label = 'non_financial'
    try:
        async with session.get(url) as resp:
            data = await resp.json()
        records = data.get('data', [])
        if not records:
            return
        bonds = USBonds(records)
        df = bonds.as_dataframe
        df['rank_type'] = label
        await db.batch_upsert_dataframe(
            df,
            table_name='corp_bonds',
            unique_columns=['rank_type', 'ticker_id'],
        )
    except Exception as e:
        print(f"[ERROR] {e} - {rank_type}")

async def scheduler() -> None:
    """
    Continuously fetch corporate bond rankings for all configured rank types.
    A single database connection and HTTP session are created and reused
    across iterations.  After processing all rank types, the coroutine
    sleeps for 10 minutes before repeating.
    """
    await db.connect()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                await asyncio.gather(
                    *[corp_bonds(rt, session) for rt in rank_types]
                )
                print("Done with corp bonds. Sleeping.")
                await asyncio.sleep(600)  # 10 minutes
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(scheduler())