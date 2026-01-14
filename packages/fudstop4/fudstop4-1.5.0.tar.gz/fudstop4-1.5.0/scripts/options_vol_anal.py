

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import aiohttp
import pandas as pd

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
db = PolygonOptions()
import os
from dotenv import load_dotenv
load_dotenv()


from fudstop4.apis.helpers import generate_webull_headers
from datetime import date


from fudstop4._markets.list_sets.dicts import hex_color_dict
from discord_webhook import AsyncDiscordWebhook,DiscordEmbed
seen_ids = set()

async def process_option_id(ticker, strike, call_put, expiry, option_id, oi):
    url = f"https://quotes-gw.webullfintech.com/api/statistic/option/queryVolumeAnalysis?count=50&tickerId={option_id}"

    try:
        async with aiohttp.ClientSession(headers=generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"[!] Failed to fetch for {option_id} - Status: {resp.status}")
                    return

                data = await resp.json()
                print(f"[{ticker}] Option Flow: {data}")

                # Extract and validate values
                total_trades = data.get('totalNum')
                total_vol = data.get('totalVolume')
                avg_price = data.get('avgPrice')
                buy_vol = data.get('buyVolume')
                sell_vol = data.get('sellVolume')
                neut_vol = data.get('neutralVolume')
                ticker_id = data.get('tickerId') or option_id

                # Ensure numeric fields are valid
                if not all(isinstance(x, (int, float)) for x in [buy_vol, sell_vol, neut_vol, total_vol]):
                    return

                # Normalize expiry to date object
                if isinstance(expiry, str):
                    expiry = pd.to_datetime(expiry, errors='coerce').date()
                elif isinstance(expiry, pd.Timestamp):
                    expiry = expiry.date()

                payload = {
                    'option_id': ticker_id,
                    'ticker': ticker,
                    'strike': strike,
                    'call_put': call_put,
                    'expiry': expiry,
                    'total_trades': total_trades,
                    'total_vol': total_vol,
                    'oi': oi,
                    'buy_vol': buy_vol,
                    'sell_vol': sell_vol,
                    'neut_vol': neut_vol,
                }

                df = pd.DataFrame(payload, index=[0])

                # 🚀 Buy Surge
                if buy_vol > (sell_vol + neut_vol) and total_vol > 650:
                    await db.batch_upsert_dataframe(df, table_name='buy_contracts', unique_columns=['option_id'])

                    hook_url = os.environ.get('buy_surge')
                    if hook_url:
                        hook = AsyncDiscordWebhook(hook_url, content='@everyone')
                        embed = DiscordEmbed(
                            title=f"Buy Surge - {ticker} ${strike} {call_put} {expiry}",
                            description=f"> **Buy Surge Detected!** Total trades: **{total_trades}**, OI: **{oi}**.",
                            color=hex_color_dict.get('green')
                        )
                        embed.add_embed_field(
                            name="Volume Breakdown:",
                            value=f"> Buy: **{buy_vol}**\n> Sell: **{sell_vol}**\n> Neut: **{neut_vol}**"
                        )
                        hook.add_embed(embed)
                        await hook.execute()

                # 🔻 Sell Surge
                if sell_vol > (buy_vol + neut_vol) and total_vol > 650:
                    await db.batch_upsert_dataframe(df, table_name='sell_contracts', unique_columns=['option_id'])

                    hook_url = os.environ.get('sell_surge')
                    if hook_url:
                        hook = AsyncDiscordWebhook(hook_url, content='@everyone')
                        embed = DiscordEmbed(
                            title=f"Sell Surge - {ticker} ${strike} {call_put} {expiry}",
                            description=f"> **Sell Surge Detected!** Total trades: **{total_trades}**, OI: **{oi}**.",
                            color=hex_color_dict.get('red')
                        )
                        embed.add_embed_field(
                            name="Volume Breakdown:",
                            value=f"> Buy: **{buy_vol}**\n> Sell: **{sell_vol}**\n> Neut: **{neut_vol}**"
                        )
                        hook.add_embed(embed)
                        await hook.execute()

                # ⚪ Neutral Surge
                if neut_vol > (buy_vol + sell_vol) and total_vol > 650:
                    await db.batch_upsert_dataframe(df, table_name='neut_contracts', unique_columns=['option_id'])

                    hook_url = os.environ.get('neut_surge')
                    if hook_url:
                        hook = AsyncDiscordWebhook(hook_url)
                        embed = DiscordEmbed(
                            title=f"Neutral Surge - {ticker} ${strike} {call_put} {expiry}",
                            description=f"> **Neutral Surge Detected.** Total trades: **{total_trades}**, OI: **{oi}**.",
                            color=hex_color_dict.get('gray')
                        )
                        embed.add_embed_field(
                            name="Volume Breakdown:",
                            value=f"> Buy: **{buy_vol}**\n> Sell: **{sell_vol}**\n> Neut: **{neut_vol}**"
                        )
                        hook.add_embed(embed)
                        await hook.execute()

    except Exception as e:
        import traceback
        print(f"[x] Error processing {option_id} ({ticker}): {e}")
        traceback.print_exc()
# 🔁 Main polling loop
async def get_options_data():
    await db.connect()
    global seen_ids

    while True:
        query = f"""
            SELECT ticker, strike, call_put, expiry, option_id, oi
            FROM atm_options where expiry >= '{db.today}'
            ORDER BY insertion_timestamp DESC LIMIT 40
        """
        results = await db.fetch(query)
        print(results)
        df = pd.DataFrame(results, columns=['ticker', 'strike', 'call_put', 'expiry', 'option_id', 'oi'])

        if df.empty:
            print("[!] No data returned.")
        else:
            df_new = df[~df['option_id'].isin(seen_ids)]
            if not df_new.empty:
                ids = df_new['option_id'].tolist()
                tickers = df_new['ticker'].tolist()
                strikes = df_new['strike'].tolist()
                call_puts = df_new['call_put'].tolist()
                expiries = df_new['expiry'].tolist()
                ois = df_new['oi'].tolist()
                seen_ids.update(ids)
                print(f"[+] New option IDs: {ids}")

                today = date.today()

                # Run tasks only if expiry is in the future
                tasks = [
                    process_option_id(ticker, strike, call_put, expiry, opt_id, oi)
                    for ticker, strike, call_put, expiry, opt_id, oi in zip(
                        tickers, strikes, call_puts, expiries, ids, ois
                    )
                    if pd.to_datetime(expiry).date() > today
                ]
                await asyncio.gather(*tasks)
            else:
                print("[✓] No new option IDs.")

        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(get_options_data())
