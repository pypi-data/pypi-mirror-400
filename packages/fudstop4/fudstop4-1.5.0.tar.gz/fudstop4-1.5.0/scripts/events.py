import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import os
from dotenv import load_dotenv
load_dotenv()
from fudstop4.apis.nasdaq.nasdaq_sdk import Nasdaq
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
db = PolygonOptions()
sdk = Nasdaq()

import asyncio
from datetime import date, timedelta
import pandas as pd


async def fetch_day(d):
    x = await sdk.economic_events(date=d.isoformat())
    df = x.as_dataframe

    if df is not None and not df.empty:
        df["event_date"] = d.isoformat()
        return df

    return None

async def events():
    start = date.today()
    days = [start + timedelta(days=i) for i in range(15)]

    results = await asyncio.gather(
        *(fetch_day(d) for d in days)
    )

    frames = [df for df in results if df is not None]

    if frames:
        full_df = pd.concat(frames, ignore_index=True)
        await db.batch_upsert_dataframe(full_df, table_name='economic_events', unique_columns=['country', 'event', 'description', 'event_date'])
        print(f"Econ events stored.")
    else:
        print("No economic events found in the next two weeks.")

async def scheduler():
    await db.connect()
    while True:
        print("⏰ Running economic events scan...")
        try:
            await events()
        except Exception as e:
            print("⚠️ Error during events scan:", e)

        # sleep for 3 hours
        await asyncio.sleep(60 * 60 * 3)

asyncio.run(scheduler())