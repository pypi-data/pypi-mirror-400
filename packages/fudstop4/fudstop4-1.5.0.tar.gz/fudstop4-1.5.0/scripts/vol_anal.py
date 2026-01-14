import sys
from pathlib import Path

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import pandas as pd
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
import os
from dotenv import load_dotenv
load_dotenv()
neutral_zone_hook = os.environ.get('neutral_zone')
fire_sale_hook = os.environ.get('fire_sale')
accumulation_hook = os.environ.get('accumulation')
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
opts = PolygonOptions()
from fudstop4.apis.ultimate.ultimate_sdk import UltimateSDK
from fudstop4._markets.list_sets.dicts import hex_color_dict
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
ultim = UltimateSDK()
from imports import *
import asyncio



async def main():

    
    vol_anal = await ultim.volume_analysis_for_tickers(most_active_tickers)

    for tick, volanal in vol_anal.items():
        try:
            if volanal is None:
                continue
            df = volanal.df
            print(df)
            df['ticker'] = tick
            await db.batch_upsert_dataframe(df, table_name='volume_analysis', unique_columns=['ticker'])
        except Exception as e:
            print(e)
async def run():
    await db.connect()
    while True:
        await main()
        print(f"Done. SLeeping")
        await asyncio.sleep(120)

         

asyncio.run(run())