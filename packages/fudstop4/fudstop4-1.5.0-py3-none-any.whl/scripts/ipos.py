import datetime
import asyncio
import sys
from pathlib import Path
import pytz
import aiohttp
import pandas as pd
from time import time
# Adjust sys.path for project imports
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from imports import time, db
from _webull.models.ipos import IPOsUpcoming
from typing import List, Optional

# Configuration constants
TIMEZONE = pytz.timezone("US/Eastern")
STATUSES: List[str] = ['upcoming', 'filing']
RUN_LIMIT = 4  # number of IPO fetches allowed per day
SLEEP_SECONDS = 60  # loop interval in seconds (1 minute)


def within_market_hours(now=None):
    now = now or datetime.datetime.now()

    start = datetime.time(20, 0)
    end   = datetime.time(9, 30)

    t = now.time()
    return t >= start or t <= end

async def fetch_ipos_for_status(status: str, session: aiohttp.ClientSession) -> Optional[str]:
    """
    Fetch IPO data for a given status and upsert it into the database.
    This function assumes the database connection is already open and
    uses the provided HTTP session to avoid creating a new session on
    each call.

    Args:
        status: One of 'upcoming' or 'filing'.  Other statuses are ignored.
        session: An aiohttp ClientSession reused across calls.

    Returns:
        A status message or None if no data was found.
    """
    if status not in {'upcoming', 'filing'}:
        return None
    url = (
        "https://quotes-gw.webullfintech.com/api/bgw/ipo/listIpo"
        f"?regionId=6&status={status}"
    )
    async with session.get(url) as resp:
        data = await resp.json()
    items = data.get('items', [])
    if not items:
        print(f"[!] No IPO data for {status}")
        return f"{status} - no data"

    items_obj = IPOsUpcoming(items)
    df = items_obj.as_dataframe
    df['status'] = status
    await db.batch_upsert_dataframe(
        df,
        table_name=f'ipos_{status}',
        unique_columns=['ticker', 'status'],
    )
    print(f"[+] {status.upper()} IPOs upserted: {len(df)}")
    return f"{status} stored successfully."


async def run_ipos(session: aiohttp.ClientSession) -> List[Optional[str]]:
    """
    Launch concurrent fetches of IPO data for all configured statuses.
    Assumes that the database connection is open and uses the provided
    session for HTTP requests.

    Args:
        session: An aiohttp ClientSession reused across calls.

    Returns:
        A list of results from each status fetch.
    """
    tasks = [fetch_ipos_for_status(status, session) for status in STATUSES]
    return await asyncio.gather(*tasks)


async def main_loop() -> None:
    """
    Main loop for periodically fetching IPO data.  The loop runs
    indefinitely, checking market hours and run count to decide whether
    to fetch IPO data.  A single database connection and HTTP session
    are opened and reused for the lifetime of the loop.  The run
    history is tracked to enforce a daily limit on the number of fetches.
    """
    run_times: List[str] = []
    # Open database connection once for the duration of the loop
    await db.connect()
    try:
        # Create a single HTTP session to be reused for all network calls
        async with aiohttp.ClientSession() as session:
            while True:
                now = datetime.datetime.now(TIMEZONE)
                current_str = now.strftime('%Y-%m-%d %H:%M')
                # Reset daily run history at midnight
                if run_times and run_times[0][:10] != current_str[:10]:
                    run_times.clear()

                if within_market_hours(now) and len(run_times) < RUN_LIMIT:
                    timestamp = now.strftime('%Y-%m-%d %I:%M:%S %p %Z')
                    print(f"[*] {timestamp} - Running IPO fetch...")
                    try:
                        await run_ipos(session)
                        run_times.append(current_str)
                        print(f"[*] Runs today: {len(run_times)} / {RUN_LIMIT}")
                    except Exception as e:
                        print(f"[!] Error during IPO fetch: {e}")
                else:
                    if not within_market_hours(now):
                        print(
                            f"[!] Skipping: Outside market hours - "
                            f"{now.strftime('%I:%M:%S %p %Z')}"
                        )
                    elif len(run_times) >= RUN_LIMIT:
                        print(
                            f"[!] Skipping: Daily IPO fetch limit ({RUN_LIMIT}) reached."
                        )
                # Wait before next iteration
                await asyncio.sleep(SLEEP_SECONDS)
    finally:
        # Ensure database connection is closed upon exit
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main_loop())
