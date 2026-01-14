


import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from imports import *

from discord_webhook import AsyncDiscordWebhook,DiscordEmbed

from fudstop4._markets.list_sets.dicts import hex_color_dict
# Global cache: ticker -> timestamp of last alert
seen_tickers = {}

# Time window in seconds (5 minutes)
FRESH_SECONDS = 5 * 60

async def bull_scan():


    await db.connect()
    try:
        query = f"""SELECT ticker, timespan from plays where rsi <= 26 and td_buy_count >= 8"""

        results = await db.fetch(query)


        tickers = [i.get('ticker') for i in results]
        timespans = [i.get('timespan') for i in results]

        for ticker, timespan in zip(tickers, timespans):

            query = f"""SELECT * from atm_vol_anal where ticker = '{ticker}'"""

            results = await db.fetch(query)

            buy_vol = [i.get('buy_vol') for i in results]
            sell_vol = [i.get('sell_vol') for i in results]
            neut_vol = [i.get('neut_vol') for i in results]
            
            strikes = [i.get('strike') for i in results]
            call_puts = [i.get('call_put') for i in results]
            expiries = [i.get('expiry') for i in results]
            embed = DiscordEmbed()
            hook = AsyncDiscordWebhook("https://discord.com/api/webhooks/1370438351752003675/UtRTbhuO3HkFTyGbylG4JYqWPQGc9IURKnIkzBNZ20C_T-YHSXqJVKI0WOH_lyLgX8YW",content=f"@everyone")
            for b,s,n,strike, call_put, expiry in zip(buy_vol,sell_vol,neut_vol,strikes,call_puts,expiries):
        

                if b >= (s + n) and b >= 150:

                    embed.title='Scalp Feed'
                    embed.description=f"```py\n{ticker} has flagged a TD9 / RSI setup on the {timespan} timespan.```\n\n> This feed also has more buy volume than sell volume in the options chain, and flags the following contracts:```\n> **{ticker} | {strike} | {call_put} | {expiry}```"
                    green_hex = hex_color_dict.get('green')
                    embed.color = int(green_hex.lstrip('#'), 16) if green_hex else None
                    embed.add_embed_field(name=f"Contract:", value=f"```py\n{ticker} has flagged a TD9 / RSI setup on the {timespan} timespan.```\n\n> This feed also has more buy volume than sell volume in the options chain, and flags the following contracts:```\n> **{ticker} | {strike} | {call_put} | {expiry} with **{b}** buy volume, **{n}** neutral volume, and **{s}** sell volume.")
    
                    embed.set_timestamp()
            
            hook.add_embed(embed)
            await hook.execute()
    except Exception as e:
        print(e)
asyncio.run(bull_scan())