#!/usr/bin/env python3
import sys
from pathlib import Path

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *




async def main() -> None:
    """
    Periodically fetch government spending data and print each transaction.
    A single HTTP session is reused for all requests and a delay is
    introduced between iterations to avoid overwhelming the upstream
    service.  This function can be extended to upsert data into a
    database if desired.
    """
    url = "https://www.quiverquant.com/get_gov_spending_data/"
    # If you wish to persist the data, uncomment the following lines to
    # connect to the database
    # await db.connect()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(url) as resp:
                        data = await resp.json()
                    transactions = data.get('gov_transactions', [])
                    if transactions:
                        print(
                            f"[✓] Fetched {len(transactions)} government spending transactions."
                        )
                        for item in transactions:
                            print(item)
                    else:
                        print("[!] No government transactions returned.")
                except Exception as e:
                    print(f"[!] Error fetching government spending data: {e}")
                # Wait for an hour before the next fetch
                await asyncio.sleep(3600)
    finally:
        # If you connected to the database above, disconnect here
        # await db.disconnect()
        pass

if __name__ == "__main__":
    asyncio.run(main())