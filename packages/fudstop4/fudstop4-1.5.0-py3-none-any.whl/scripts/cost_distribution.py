import asyncio
import sys
import os
from pathlib import Path
# Add project path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from datetime import datetime, time
import pytz
from dotenv import load_dotenv
import pandas as pd
import aiohttp


# Load env
load_dotenv()
cost_hook = os.environ.get('cost_distribution')

# Imports
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from UTILS.ticker_dicts import ticker_hooks_dict
from MODELS.candles import Candles
from fudstop4._markets.list_sets.dicts import hex_color_dict
from fudstop4.apis.webull.webull_trading import WebullTrading
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers, most_active_nonetf
from UTILS.confluence import score_cost_distribution

# Setup
opts = PolygonOptions()
trading = WebullTrading()
candles = Candles()

BATCH_SIZE = 5
EST = pytz.timezone("US/Eastern")
RUN_LIMIT = 2
SLEEP_SECONDS = 60  # check loop every minute

# Chunk utility
def chunked(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]

# Time restriction
def within_market_hours(now: datetime) -> bool:
    t = now.time()
    return time(9, 30) <= t <= time(16, 0)

# Fetch logic
async def fetch(ticker: str) -> None:
    """
    Fetch the latest cost distribution data for a ticker and send a
    notification if the sentiment is strongly bullish or bearish.  The
    database connection is managed by the outer ``main`` coroutine.

    Args:
        ticker: A stock ticker symbol.
    """
    try:
        cost_dict = await trading.new_cost_dist(
            symbol=ticker,
            start_date=trading.eight_days_ago,
            end_date=trading.today,
        )
        # ``new_cost_dist`` returns an object with ``as_dataframe`` attribute
        df = cost_dict.as_dataframe  # type: ignore
        print(df)
        profit_ratio = df['profit_ratio'].to_list()[0]

        score = score_cost_distribution(profit_ratio)
        if abs(score.points) >= 2:
            color = hex_color_dict.get('green') if score.signal == 'bullish' else hex_color_dict.get('red')
            embed = DiscordEmbed(
                title=f"Cost Distribution Alert - {ticker}",
                description=(
                    f"```py\n{ticker} shows {profit_ratio:.1f}% of holders in profit "
                    f"({score.signal.upper()} short-term tilt).```\nReason: {score.reason}"
                ),
                color=color,
            )
            embed.add_embed_field(
                name="Players profiting:",
                value=f"> **{profit_ratio:.1f}%**",
            )
            embed.set_footer(text=f'cost_dist,{ticker},{score.signal}')
            embed.set_timestamp()

            hook = AsyncDiscordWebhook(cost_hook)
            hook.add_embed(embed)
            await hook.execute()

            if ticker_hooks_dict.get(ticker):
                hook2 = AsyncDiscordWebhook(ticker_hooks_dict[ticker])
                hook2.add_embed(embed)
                await hook2.execute()

        df_result = pd.DataFrame({
            'ticker': [ticker],
            'profit_ratio': [profit_ratio],
            'cost_signal': [score.signal],
            'cost_points': [score.points],
            'cost_reason': [score.reason],
            'confluence_score': [score.points],
        })
        await opts.batch_upsert_dataframe(
            df_result,
            table_name='cost_distribution',
            unique_columns=['ticker', 'cost_sentiment'],
        )
    except Exception as e:
        print(f"[!] Error fetching for {ticker}: {e}")

# Main loop
async def main():
    await opts.connect()
    run_count = 0
    last_run_day = None
    try:
        while True:
            now = datetime.now(EST)
            today_str = now.strftime('%Y-%m-%d')

            if last_run_day != today_str:
                # Reset count at the beginning of a new day
                run_count = 0
                last_run_day = today_str
                print(f"[*] Reset run count for {today_str}")

            if within_market_hours(now) and run_count < RUN_LIMIT:
                # Start a run only during market hours and if the daily limit hasn't been reached
                print(
                    f"[*] Starting cost dist run #{run_count + 1} at "
                    f"{now.strftime('%I:%M:%S %p EST')}"
                )
                processed: set[str] = set()
                for batch in chunked(most_active_nonetf, BATCH_SIZE):
                    batch_to_run = [i for i in batch if i not in processed]
                    if not batch_to_run:
                        continue
                    # Launch fetch tasks concurrently
                    tasks = [fetch(i) for i in batch_to_run]
                    await asyncio.gather(*tasks)
                    processed.update(batch_to_run)
                    print(f"[+] Processed batch: {batch_to_run}")
                run_count += 1
                print(
                    f"[✓] Cost distribution run complete. Total runs today: {run_count}"
                )
            else:
                if not within_market_hours(now):
                    print(
                        f"[!] Outside market hours - {now.strftime('%I:%M:%S %p EST')}"
                    )
                elif run_count >= RUN_LIMIT:
                    print(
                        f"[!] Run limit ({RUN_LIMIT}) reached for {today_str}"
                    )

            # Sleep until the next check
            await asyncio.sleep(SLEEP_SECONDS)
    finally:
        await opts.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
