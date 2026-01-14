

import asyncio
import sys
from pathlib import Path
from discord_webhook import DiscordEmbed, AsyncDiscordWebhook
from datetime import datetime
import aiohttp
import pandas as pd
from fudstop4._markets.list_sets.dicts import hex_color_dict
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
db = PolygonOptions()
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)



seen_ids = set()

top_gainers_hook = "https://discordapp.com/api/webhooks/1420460070373949473/SVvjbyb11h4gXZ3L7UYGMiRO1i7qsD8l-jGWUDHNoanf9tDH58LE0KumtdiEjbTGcVh-"
test_hook = "https://discord.com/api/webhooks/1370438351752003675/UtRTbhuO3HkFTyGbylG4JYqWPQGc9IURKnIkzBNZ20C_T-YHSXqJVKI0WOH_lyLgX8YW"


async def run_top_gainers():
    rank_types = ['premarket', 'aftermarket', '5min', '1d', '1m', '3m']
    await db.connect()

    queries = [
        f"""SELECT ticker, change_pct 
            FROM rise_{i} 
            ORDER BY change_pct DESC 
            LIMIT 10"""
        for i in rank_types
    ]

    results = await asyncio.gather(*[db.fetch(query) for query in queries])

    embed = DiscordEmbed(
        title="📈 Top Gainers",
        description="```Viewing Top Gainers by Rank Type```",
        color = hex_color_dict.get('green')
    )  
    embed.set_timestamp()
    embed.set_footer(text='Implemented by FUDSTOP.')
    for rank_type, result in zip(rank_types, results):
        lines = [f"{row['ticker']:<6} {row['change_pct']:>8.2f}%" for row in result]
        block = "```" + "\n".join(lines) + "```"

        embed.add_embed_field(
            name=f"Top 10 ({rank_type})",
            value=block,
            inline=True
        )

    hook = AsyncDiscordWebhook(test_hook)
    hook.add_embed(embed)
    await hook.execute()


async def main_loop():
    while True:
        try:
            await run_top_gainers()
        except Exception as e:
            print(f"Error in run_top_gainers: {e}")
        await asyncio.sleep(300)  # wait 5 minutes


if __name__ == "__main__":
    asyncio.run(main_loop())