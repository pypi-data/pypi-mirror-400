from imports import *
import asyncio
import sys
from pathlib import Path
from datetime import datetime, time
import pytz
import aiohttp
import pandas as pd
from UTILS.db_tables import ContractsTable
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import os
from dotenv import load_dotenv
load_dotenv()
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from fudstop4._markets.list_sets.dicts import hex_color_dict

contracts_dict = { 
    "buy": f"{os.environ.get('contracts')}" + "?thread_id=1392555374376124457",
    "sell": f"{os.environ.get('contracts')}" + "?thread_id="
}

processed = set()

async def contracts(contract_type: str) -> None:
    """
    Fetch the most recent contract record of the given type ("buy" or
    "sell"), build a rich embed describing the contract, and send it
    via Discord.  The database connection must already be established
    prior to calling this function.

    Args:
        contract_type: Either ``"buy"`` or ``"sell"``.  Any other value will
            result in a neutral embed color.
    """
    query = f"SELECT * FROM {contract_type}_contracts ORDER BY insertion_timestamp DESC LIMIT 1"
    # Determine embed color based on contract type
    if contract_type == 'sell':
        color = hex_color_dict.get('red')
    elif contract_type == 'buy':
        color = hex_color_dict.get('green')
    else:
        color = hex_color_dict.get('grey')

    results = await db.fetch(query)
    if not results:
        print(f"[WARNING] No {contract_type} contracts found in database.")
        return
    results = ContractsTable(results)

    # Build the embed describing the contract
    embed = DiscordEmbed(
        title=(
            f"{contract_type} contracts | {results.ticker[0]} ${results.strike[0]}"
            f" {results.call_put} {results.expiry}"
        ),
        description=(
            f"```py\nThis contract is classified as a {contract_type} contract "
            f"because it has the most {contract_type} volume. Details below.```"
        ),
        color=color,
    )
    embed.add_embed_field(
        name="Contract:",
        value=(
            f"> {results.ticker[0]} ${results.strike[0]} {results.call_put} {results.expiry}"
        ),
    )
    embed.add_embed_field(
        name="Volume:",
        value=(
            f"> Total: **{results.total_vol}**\n"
            f"> Buy: **{results.buy_vol}**\n"
            f"> Neutral: **{results.neut_vol}**\n"
            f"> Sell: **{results.sell_vol}**"
        ),
    )
    embed.add_embed_field(
        name="Trades:",
        value=(
            f"> Total: **{results.total_trades}**\n> OI: **{results.oi}**"
        ),
    )
    embed.set_timestamp()
    embed.set_footer(
        text=(
            f"{contract_type} contracts, {results.ticker[0]} {results.strike[0]} {results.call_put} {results.expiry}"
        )
    )

    # Send the embed to the appropriate Discord webhook thread
    hook_url = contracts_dict.get(contract_type)
    if not hook_url:
        print(f"[ERROR] No webhook URL configured for contract type {contract_type}")
        return
    webhook = AsyncDiscordWebhook(url=hook_url)
    webhook.add_embed(embed)
    await webhook.execute()

async def run_contracts() -> None:
    """
    Continuously monitor and report the most recent buy and sell
    contracts.  A single database connection is opened and reused for
    each cycle.  Between iterations the coroutine sleeps briefly to
    avoid spamming Discord with rapid updates.
    """
    await db.connect()
    try:
        while True:
            # Process both buy and sell contracts
            await asyncio.gather(contracts('buy'), contracts('sell'))
            # Sleep for a few minutes before checking again
            await asyncio.sleep(300)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(run_contracts())