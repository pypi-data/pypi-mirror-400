from fudstop4.apis.polygonio.polygon_options import PolygonOptions
import asyncio
import pandas as pd
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed

db = PolygonOptions()
from tabulate import tabulate



async def main():


    await db.connect()

    bull_query = f"""select ticker, timespan, rsi from plays where candle_completely_below_lower = 't';"""
    bear_query = f"""select ticker, timespan, rsi from plays where candle_completely_above_upper = 't';"""


    bull_results = await db.fetch(bull_query)

    bear_results = await db.fetch(bear_query)

    bull_df = pd.DataFrame(bull_results, columns=['ticker', 'timespan', 'rsi'])
    bear_df = pd.DataFrame(bear_results, columns=['ticker', 'timespan', 'rsi'])

    #round rsi to two decimal points

    bull_table = tabulate(bull_df, headers='keys', tablefmt='heavy_rounded', showindex=False)
    bear_table = tabulate(bear_df, headers='keys', tablefmt='heavy_rounded', showindex=False)


    embed = DiscordEmbed(title='MONEY PLAYS', description=f"# > CALLS:\n```py\n{bull_table}```\n# > PUTS:\n```py\n{bear_table}```")

    embed.add_embed_field(name='Info:', value='Viewing confirmed setup where the latest candle on the timespan has closed above or below the upper or lower bollinger band.')


    embed.set_timestamp()

    hook = AsyncDiscordWebhook()