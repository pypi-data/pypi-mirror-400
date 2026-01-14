#!/usr/bin/env python3
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, Iterable, List
from fudstop4.apis.helpers import check_macd_sentiment
import aiohttp
import asyncpg
import numpy as np
import pandas as pd
from fudstop4.apis.polygonio.polygon_options import PolygonOptions

db = PolygonOptions()
# ── Project imports (adjust paths as needed)
project_dir = str(Path(__file__).resolve().parents[2])
if project_dir not in sys.path:
    sys.path.append(project_dir)



from discord_webhook import AsyncDiscordWebhook,DiscordEmbed
from tabulate import tabulate
from fudstop4._markets.list_sets.dicts import hex_color_dict

LAST_SENT_FINGERPRINT = None

async def run_signal_scan():
    global LAST_SENT_FINGERPRINT

    await db.connect()

    while True:
        query = """
          SELECT ticker, timespan, side, est_hit_rate as prob
          FROM reversal_signals
          ORDER BY insertion_timestamp DESC
          LIMIT 1
        """

        results = await db.fetch(query)
        if not results:
            await asyncio.sleep(1)
            continue

        result = results[0]

        # ---- SIMPLE DEDUPE ----
        fingerprint = (
            f"{result['ticker']}|"
            f"{result['timespan']}|"
            f"{result['side']}|"
            f"{float(result['prob']):.6f}"
        )

        if fingerprint == LAST_SENT_FINGERPRINT:
            await asyncio.sleep(1)
            continue

        LAST_SENT_FINGERPRINT = fingerprint
        # ----------------------

        color = hex_color_dict.get('red') if result['side'] == 'short' else hex_color_dict.get('green')

        df = pd.DataFrame([result], columns=['ticker', 'timespan', 'side', 'prob'])
        table = tabulate(df, headers='keys', tablefmt='heavy_rounded', showindex=False)

        embed = DiscordEmbed(
            title='Reversal Signals',
            description=f"```py\n{table}```",
            color=color
        )

        embed.set_timestamp()
        embed.add_embed_field(
            name="Test feed.",
            value="Implemented by FUDSTOP.",
            inline=False
        )

        webhook = AsyncDiscordWebhook(
            "https://discord.com/api/webhooks/1370438351752003675/UtRTbhuO3HkFTyGbylG4JYqWPQGc9IURKnIkzBNZ20C_T-YHSXqJVKI0WOH_lyLgX8YW"
        )
        webhook.add_embed(embed)
        await webhook.execute()

        # small pause so we don't instantly re-post if DB lags
        await asyncio.sleep(1)

asyncio.run(run_signal_scan())