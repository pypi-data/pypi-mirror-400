#!/usr/bin/env python3
"""
Compute the total in-the-money (ITM) dollar value for options on a list of tickers.

This version adds structured logging, CLI flags for batch size and sleep duration,
and optional one-shot execution for testing. Database connections are managed
at the process level so individual computations remain side-effect free.
"""
import json
import argparse
import asyncio
import logging
import sys
from pathlib import Path
import os
import time
import pandas as pd

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from dotenv import load_dotenv
load_dotenv()
from fudstop4.apis.webull.webull_trading import WebullTrading
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
from fudstop4.apis.helpers import generate_webull_headers

db = PolygonOptions()


wbt = WebullTrading()




CONCURRENCY = 10            # overall max concurrent requests
BATCH_SIZE = 5              # tickers per batch
UPDATE_INTERVAL = 300       # 5 minutes

def normalize_related_tickers_col(df: pd.DataFrame) -> pd.DataFrame:
    if "related_tickers" not in df.columns:
        return df

    df["related_tickers"] = df["related_tickers"].apply(
        lambda x: ",".join(
            (i.get("ticker") or i.get("symbol") or str(i)) if isinstance(i, dict) else str(i)
            for i in x
        ) if isinstance(x, (list, tuple)) else (json.dumps(x) if isinstance(x, dict) else x)
    )
    return df

def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]

async def fetch_and_upsert_news(ticker: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            news = await wbt.ai_news(
                symbol=ticker,
                page_size=1,
                headers=generate_webull_headers(access_token=os.environ.get("ACCESS_TOKEN"))
            )

            df = news.as_dataframe
            if df is None or df.empty:
                return 0

            df = df.reset_index(drop=True)
            df = normalize_related_tickers_col(df)
            df["ticker"] = ticker

            # IMPORTANT: don't use only ['ticker'] unless you want overwrites
            await db.batch_upsert_dataframe(df, table_name="ai_news", unique_columns=["ticker", "id"])
            return len(df)

        except Exception as e:
            # keep loop alive even if one ticker fails
            print(f"[ai_news] {ticker} failed: {e}")
            return 0

async def run_ai_news_loop():
    await db.connect()
    semaphore = asyncio.Semaphore(CONCURRENCY)

    while True:
        start = time.monotonic()

        tickers = list(most_active_tickers)
        total_rows = 0

        # run in batches of 5
        for batch in chunked(tickers, BATCH_SIZE):
            tasks = [fetch_and_upsert_news(t, semaphore) for t in batch]
            results = await asyncio.gather(*tasks, return_exceptions=False)
            total_rows += sum(results)

            # tiny pause between batches to be polite (optional)
            await asyncio.sleep(0.25)

        elapsed = time.monotonic() - start
        sleep_for = max(0, UPDATE_INTERVAL - elapsed)
        print(f"[ai_news] done: {len(tickers)} tickers, {total_rows} row(s), elapsed={elapsed:.2f}s, sleep={sleep_for:.2f}s")

        await asyncio.sleep(sleep_for)

if __name__ == "__main__":
    asyncio.run(run_ai_news_loop())