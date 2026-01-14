import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from imports import *
from collections import defaultdict
from UTILS.confluence import score_iv_skew




import pandas as pd

async def iv_skew():
    await db.connect()
    try:


        opts_query = f"""
           WITH base AS (
  SELECT *
  FROM wb_opts
  WHERE expiry > CURRENT_DATE
    AND iv IS NOT NULL
),
next2 AS (
  -- one row per (ticker, expiry), ranked by nearest expiry per ticker
  SELECT
    ticker,
    expiry,
    ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY expiry) AS rn_exp
  FROM (SELECT DISTINCT ticker, expiry FROM base) d
),
ranked AS (
  -- lowest-IV strike per expiry, but only for the next 2 expiries
  SELECT
    w.ticker,
    w.expiry,
    w.strike AS skew_strike,
    w.iv,
    ROW_NUMBER() OVER (
      PARTITION BY w.ticker, w.expiry
      ORDER BY w.iv ASC, w.strike ASC
    ) AS rn
  FROM base w
  JOIN next2 n
    ON n.ticker = w.ticker
   AND n.expiry = w.expiry
  WHERE n.rn_exp <= 2
),
latest_mq AS (
  -- latest underlying close per ticker
  SELECT DISTINCT ON (ticker)
    ticker, close
  FROM multi_quote
  ORDER BY ticker, insertion_timestamp DESC
)
SELECT
  r.ticker,
  r.expiry,
  r.skew_strike,
  r.iv,
  mq.close,
  (r.skew_strike - mq.close) AS skew_diff
FROM ranked r
JOIN latest_mq mq
  ON mq.ticker = r.ticker
WHERE r.rn = 1
ORDER BY r.ticker, r.expiry;

;

        """
        results = await db.fetch(opts_query)
        df = pd.DataFrame(results, columns=['ticker', 'expiry', 'skew_strike', 'iv', 'close', 'skew_diff'])

        df['expiry'] = pd.to_datetime(df['expiry'])

        # >>> FILTER OUT EXPIRATIONS BEFORE TODAY <<<
        today = pd.to_datetime(datetime.now().date())
        df = df[df['expiry'] >= today]
        df['skew_type'] = df['skew_diff'].apply(lambda x: 'put_skew' if x < 0 else 'call_skew')
        df = df.sort_values('expiry').reset_index(drop=True)

        score_df = df.apply(
            lambda row: pd.Series(
                score_iv_skew(
                    skew_type=row['skew_type'],
                    skew_diff=row['skew_diff'],
                    close_price=row['close'],
                    iv=row['iv'],
                ).to_columns('skew')
            ),
            axis=1,
        )
        df = pd.concat([df, score_df], axis=1)

        await db.batch_upsert_dataframe(df, table_name='iv_skew', unique_columns=['ticker', 'expiry'])
    except Exception as e:
        print(e)
# Usage
import asyncio



# BATCH_SIZE = 7
# SLEEP_SECONDS = 3

# async def run_iv_skew():
#     await db.connect()
#     while True:
#         # Break tickers into batches of 7
#         batches = [most_active_tickers[i:i+BATCH_SIZE] for i in range(0, len(most_active_tickers), BATCH_SIZE)]

#         for batch in batches:
#             tasks = [iv_skew(ticker) for ticker in batch]
#             await asyncio.gather(*tasks)
#         await asyncio.sleep(SLEEP_SECONDS)


async def run_skew():
    while True:
        await iv_skew()

        print(f"Done..sleeping 5 seconds.")

        await asyncio.sleep(5)
# Run the continuous loop
asyncio.run(run_skew())
