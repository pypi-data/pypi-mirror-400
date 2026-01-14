from pathlib import Path
import sys
import asyncio

# Set up project directory for imports
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from imports import *

async def stock_monitor():
    try:
        monitor = await occ.stock_monitor()
        df = monitor
        df = df.rename(columns={'symbol': 'ticker'})
        await db.batch_upsert_dataframe(df, table_name='stock_monitor', unique_columns=['ticker'])
    except Exception as e:
        print(e)
async def run_loop():
    await db.connect()
    while True:
        try:
            await stock_monitor()
            print(f"Done")
        except Exception as e:
            print(f"[ERROR] confluence failed: {e}")
        await asyncio.sleep(900)  # 15 minutes

if __name__ == "__main__":
    asyncio.run(run_loop())
