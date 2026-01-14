import asyncio
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
from imports import *
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
from UTILS.confluence import score_options_flow
from fudstop4.apis.occ.occ_sdk import occSDK
occ = occSDK()
async def options_monitor(ticker):
    
    monitor = await occ.options_monitor(symbol=ticker)
    if monitor is not None and hasattr(monitor, 'as_dataframe'):
        monitor_df = monitor.as_dataframe.rename(columns={'expirationdate': 'expiry'})
        try:
            cols = set(monitor_df.columns)
            call_vol = float(monitor_df["call_volume"].sum()) if "call_volume" in cols else 0.0
            put_vol = float(monitor_df["put_volume"].sum()) if "put_volume" in cols else 0.0
            call_oi = float(monitor_df["call_openinterest_eod"].sum()) if "call_openinterest_eod" in cols else 0.0
            put_oi = float(monitor_df["put_openinterest_eod"].sum()) if "put_openinterest_eod" in cols else 0.0
            flow_score = score_options_flow(call_vol, put_vol, call_oi, put_oi, label="options_monitor")
            monitor_df = monitor_df.assign(
                **flow_score.to_columns("options_monitor"),
                confluence_score=flow_score.points,
            )
        except Exception as e:
            print(f"[!] Scoring options monitor failed for {ticker}: {e}")
        await db.batch_upsert_dataframe(monitor_df, table_name='options_monitor', unique_columns=['ticker', 'strike', 'expiry', 'call_openinterest_eod', 'put_openinterest_eod'])
    else:
        print(f"[ERROR] Monitor object for {ticker} is None or missing 'as_dataframe' attribute.")

async def run_options_monitor():
    await db.connect()
    while True:
        for batch in chunked(most_active_tickers, 7):
            tasks = [options_monitor(ticker) for ticker in batch]
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                print(f"[ERROR] Batch failed: {e}")
        print("[INFO] Waiting 10 minutes before next cycle.")
        await asyncio.sleep(600)  # 10 minutes

if __name__ == "__main__":
    asyncio.run(run_options_monitor())
