import asyncio
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import aiohttp

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from UTILS.db_tables import USBonds
from imports import *





async def us_bonds():

    url = f"https://quotes-gw.webullfintech.com/api/wlas/bonds/list?regionId=6&supportBroker=8&direction=-1&pageIndex=1&pageSize=100&securitySubTypes=1601&oddLotFlag=1&order=expDate"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:

            data = await resp.json()
            data = data.get('data', [])
            data = USBonds(data)

            await db.batch_upsert_dataframe(data.as_dataframe, table_name='us_bonds', unique_columns=['symbol'])



async def treasury_strips():

    url = f"https://quotes-gw.webullfintech.com/api/wlas/bonds/list?regionId=6&supportBroker=8&direction=-1&pageIndex=1&pageSize=30&securitySubTypes=1601&order=askYieldYTW&treasuryType=4"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:

            data = await resp.json()
            data = data.get('data', [])
            data = USBonds(data)

            await db.batch_upsert_dataframe(data.as_dataframe, table_name='treasury_strips', unique_columns=['symbol'])



async def scheduler():
    await db.connect()
    while True:
        await asyncio.gather(
            us_bonds(),
            treasury_strips()
        )
        await asyncio.sleep(900)  # Sleep for 15 minutes (900 seconds)

if __name__ == "__main__":
    asyncio.run(scheduler())