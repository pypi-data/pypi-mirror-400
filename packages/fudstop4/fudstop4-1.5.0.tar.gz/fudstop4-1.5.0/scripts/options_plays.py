import sys
from pathlib import Path
from datetime import datetime, time
import pytz
import aiohttp
import pandas as pd
from more_itertools import chunked  # pip install more-itertools
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
import asyncio


db = PolygonOptions()


import asyncio




async def run_once():
    await db.connect()

    query = """
    WITH latest AS (
        SELECT
            ticker,
            strike,
            call_put,
            expiry,
            timespan,
            ts,
            candle_completely_below_lower,
            ROW_NUMBER() OVER (
                PARTITION BY ticker, strike, call_put, expiry, timespan
                ORDER BY ts DESC
            ) AS rn
        FROM option_candles
    )
    SELECT
        ticker,
        strike,
        call_put,
        expiry,
        timespan
    FROM latest
    WHERE rn = 1
      AND candle_completely_below_lower = TRUE
    LIMIT 10;
    """

    results = await db.fetch(query)

    df = pd.DataFrame(
        list(results),
        columns=["ticker", "strike", "call_put", "expiry", "timespan"]
    )

    if not df.empty:
        await db.batch_upsert_dataframe(
            df,
            table_name="option_plays",
            unique_columns=["ticker", "strike", "call_put", "expiry"]
        )


async def main():
    while True:
        try:
            await run_once()
        except Exception as e:
            # don’t let one bad tick kill the loop
            print("loop error:", e)

        await asyncio.sleep(15)


asyncio.run(main())