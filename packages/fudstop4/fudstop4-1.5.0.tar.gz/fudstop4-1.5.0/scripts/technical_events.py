from pathlib import Path
import sys
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import aiohttp
import pandas as pd
from config import SIGNAL_HOOKS, indicator_abbreviations
from discord_webhook import AsyncDiscordWebhook,DiscordEmbed
import asyncio
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.helpers import generate_webull_headers
from typing import Dict
db = PolygonOptions()
from _webull.models.technical_events import TechnicalTicker,TechnicalValues

types = ['bullish', 'bearish']
times = ['short', 'middle', 'long']
SENT_CACHE: Dict[tuple, datetime] = {}
CACHE_TTL_MINUTES = int(os.getenv("TECHNICAL_EVENTS_CACHE_MINUTES", "360"))


def _prune_cache(now: datetime) -> None:
    if CACHE_TTL_MINUTES <= 0:
        return
    cutoff = now - timedelta(minutes=CACHE_TTL_MINUTES)
    stale = [key for key, ts in SENT_CACHE.items() if ts < cutoff]
    for key in stale:
        SENT_CACHE.pop(key, None)


def _build_cache_key(row: dict, type_name: str, time_horizon: str) -> tuple:
    return (
        str(row.get("ticker") or ""),
        str(row.get("signal") or ""),
        str(type_name),
        str(time_horizon),
        str(row.get("trade_time") or ""),
    )


async def technical_alerts(type, time_horizon, size):
    try:
        """
        >>> Types:
            bullish or bearish


        >>> Time horizons:
            short, middle, or long
        """
        type_dict = { 
            'bullish': '1',
            'bearish': '2',
        }
        time_dict = { 
            'short': 'Short',
            'middle': 'Middle',
            'long': 'Long'
        }
        url = f"https://quotes-gw.webullfintech.com/api/wlas/ranking/tc-rank?regionId=6&supportBroker=8&type={type_dict.get(type)}&rankType=technicalEvents.tc{time_dict.get(time_horizon)}&pageIndex=1&pageSize={size}"


        async with aiohttp.ClientSession(headers=generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))) as session:
            async with session.get(url) as resp:
                data = await resp.json()


                data = data['data']
                ticker = [i.get('ticker') for i in data]
                values = [i.get('values') for i in data]

                ticker_obj = TechnicalTicker(ticker, type=type, time_horizon=time_horizon)
                values_obj = TechnicalValues(values)

                ticker_df = ticker_obj.as_dataframe
                values_df = values_obj.as_dataframe

                merged_df = pd.merge(ticker_df, values_df, on='ticker_id')
                print(merged_df)
                await db.batch_upsert_dataframe(merged_df, table_name='technical_events', unique_columns=['ticker', 'type', 'time_horizon'])

                now = datetime.now(timezone.utc)
                _prune_cache(now)

                async def send_signal(row: dict):
                    latest_signal = row.get("signal")
                    if not latest_signal:
                        return
                    abbreviated_signal = indicator_abbreviations.get(latest_signal)
                    if abbreviated_signal is None:
                        return
                    hook = SIGNAL_HOOKS.get(abbreviated_signal)
                    if not hook:
                        return

                    ticker = row.get("ticker")
                    cache_key = _build_cache_key(row, type, time_horizon)
                    if cache_key in SENT_CACHE:
                        return
                    embed = DiscordEmbed(title=f"{latest_signal} - {ticker}")
                    embed.add_embed_field(name="Type", value=type, inline=True)
                    embed.add_embed_field(name="Horizon", value=time_horizon, inline=True)

                    webhook = AsyncDiscordWebhook(hook)
                    webhook.add_embed(embed)
                    await webhook.execute()
                    SENT_CACHE[cache_key] = now

                records = merged_df.to_dict(orient="records")
                tasks = [send_signal(r) for r in records]
                if tasks:
                    await asyncio.gather(*tasks)

    except Exception as e:
        print(e)

async def run_events():
    await db.connect()
    while True:
        tasks = [technical_alerts(t, th, size=10) for t in types for th in times]
        await asyncio.gather(*tasks)
        await asyncio.sleep(30)  # Run every 30 seconds

# To launch
asyncio.run(run_events())
