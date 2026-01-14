import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
from UTILS.db_tables import AMBSLast2Weeks, CentralBankLiquiditySwaps, RepoOperations, SecuritiesLendingOperations, SomaSummary


async def agency_mbs():
    await db.connect()
    url = f"https://markets.newyorkfed.org/api/ambs/all/results/details/lastTwoWeeks.json"


    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()


            ambs = data['ambs']

            auctions = ambs['auctions']

            data = AMBSLast2Weeks(auctions)

            await db.batch_upsert_dataframe(data.as_dataframe, table_name='agency_mbs', unique_columns=['operation_date', 'cusip'])



async def  central_bank_liquidity_swaps():
    await db.connect()
    url = f"https://markets.newyorkfed.org/api/fxs/usdollar/last/10.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            fxSwaps = data['fxSwaps']
            operations = fxSwaps['operations']

            data = CentralBankLiquiditySwaps(operations)

            await db.batch_upsert_dataframe(data.as_dataframe, table_name='liquidity_swaps', unique_columns=['trade_date', 'counterparty'])



async def rep_operations():

    await db.connect()
    url = f"https://markets.newyorkfed.org/api/rp/all/all/results/lastTwoWeeks.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

            data = RepoOperations(data)

            await db.batch_upsert_dataframe(data.to_dataframe(), table_name='repo_operations', unique_columns=['operation_id', 'release_time'])




async def securities_lending():

    await db.connect()

    url = f"https://markets.newyorkfed.org/api/seclending/all/results/details/lastTwoWeeks.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

            data = SecuritiesLendingOperations(data)

            await db.batch_upsert_dataframe(data.as_dataframe, table_name='securities_lending', unique_columns=['operation_id', 'soma_holdings'])


async def soma_holdings():
    await db.connect()

    url = f"https://markets.newyorkfed.org/api/soma/summary.json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

            data = SomaSummary(data)

            data = data.as_dataframe[::-1]

            await db.batch_upsert_dataframe(data, table_name='soma_holdings', unique_columns=['as_of_date'])

import asyncio
from datetime import datetime, timedelta
import pytz



eastern = pytz.timezone("US/Eastern")


async def run_all_tasks():
    await asyncio.gather(
        agency_mbs(),
        central_bank_liquidity_swaps(),
        rep_operations(),
        securities_lending(),
        soma_holdings()
    )


async def wait_until_12_15_est():
    now_utc = datetime.now(tz=pytz.utc)
    now_est = now_utc.astimezone(eastern)

    target_time_est = now_est.replace(hour=12, minute=15, second=0, microsecond=0)

    if now_est >= target_time_est:
        # target time today has passed, schedule for tomorrow
        target_time_est += timedelta(days=1)

    target_time_utc = target_time_est.astimezone(pytz.utc)
    seconds_to_wait = (target_time_utc - now_utc).total_seconds()
    print(f"[Scheduler] Waiting {int(seconds_to_wait)} seconds until 12:15 PM EST...")

    await asyncio.sleep(seconds_to_wait)


async def main():
    while True:
        await wait_until_12_15_est()
        print(f"[Scheduler] Running NYFed data tasks at {datetime.now(tz=eastern).strftime('%Y-%m-%d %H:%M:%S')} EST")
        try:
            await run_all_tasks()
            print(f"[Scheduler] All tasks complete.")
        except Exception as e:
            print(f"[Scheduler] Task failed with error: {e}")
        print("[Scheduler] Sleeping until next 12:15 PM EST...\n")


if __name__ == "__main__":
    asyncio.run(main())
