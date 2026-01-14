import sys
from pathlib import Path

# Ensure the project directory is on the Python path so internal modules can be imported
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

import aiohttp
import asyncio
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.helpers import format_large_numbers_in_dataframe2
opts = PolygonOptions()
import pandas as pd
from fudstop4._markets.list_sets.dicts import hex_color_dict
from discord_webhook import DiscordEmbed, AsyncDiscordWebhook
import os
from dotenv import load_dotenv

load_dotenv()
import datetime
from datetime import timedelta, datetime, date

# Import database and helper functions from the shared imports
from imports import *
from UTILS.confluence import score_earnings_setup


def get_next_trading_day(start_date=None) -> str:
    """
    Returns the next trading day, skipping weekends.  Accepts a date, datetime,
    or ISO date string.  If ``start_date`` is None, the current date is used.

    Args:
        start_date: Optional starting date.  May be a str, datetime, or date.
    Returns:
        A string in 'YYYY-MM-DD' format representing the next trading day.
    """
    if start_date is None:
        d = datetime.now().date()
    elif isinstance(start_date, str):
        # Try to parse string to date
        try:
            d = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            # Try parsing as datetime string
            try:
                d = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S").date()
            except ValueError:
                raise ValueError("start_date string format not recognized")
    elif isinstance(start_date, datetime):
        d = start_date.date()
    elif isinstance(start_date, date):
        d = start_date
    else:
        raise ValueError(
            "start_date must be None, str, datetime.date, or datetime.datetime"
        )
    # Move to next day if today is not a trading day
    while d.weekday() >= 5:  # 5=Saturday, 6=Sunday
        d += timedelta(days=1)
    return d.strftime("%Y-%m-%d")


def safe_float(value):
    """Safely cast a value to float, returning None if casting fails."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_webull_datetime(iso_str: str, tz: str = 'UTC') -> str:
    """
    Converts a Webull ISO date string to 'YYYY-MM-DD HH:MM:SS AM/PM' format.
    Args:
        iso_str: The ISO formatted string with timezone information.
        tz: 'UTC' (default) or 'local' to output the time in the system local timezone.
    Returns:
        The formatted datetime string.
    """
    from datetime import timezone, datetime as dt
    dt_obj = dt.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    if tz.lower() == 'local':
        dt_obj = dt_obj.astimezone()
    else:
        dt_obj = dt_obj.astimezone(timezone.utc)
    return dt_obj.strftime("%Y-%m-%d %I:%M:%S %p")


async def fetch_earnings(session: aiohttp.ClientSession) -> None:
    """
    Fetch earnings data for the next trading day and write it to the
    ``earnings_soon`` table.  This function assumes that the database
    connection has already been established via ``opts.connect()``.

    Args:
        session: An aiohttp ClientSession to use for the HTTP request.
    """
    trading_day = get_next_trading_day()
    url = (
        "https://quotes-gw.webullfintech.com/api/market/calendar/earnings"
        f"?regionIds=6&supportBroker=8&pageIndex=1&pageSize=100"
        f"&startDate={trading_day}&endDate={trading_day}"
        "&timeZone=America%2FNew_York&timePeriods=1%2C2%2C3%2C4"
    )
    try:
        async with session.get(url, headers=generate_webull_headers()) as resp:
            data = await resp.json()
        if not data:
            print("[!] No earnings data returned.")
            return
        # The API returns a list of dicts; extract relevant fields
        tickers = [item.get('ticker') for item in data]
        symbols = [i.get('symbol') for i in tickers]
        names = [i.get('name') for i in tickers]
        volumes = [float(i.get('volume') or 0) for i in tickers]
        prices = [float(i.get('close') or 0) for i in tickers]
        change_ratio = [round(float(i.get('changeRatio') or 0) * 100, 2) for i in tickers]
        start_dates = [item.get('startDate') for item in data]
        years = [int(item.get('year') or 0) for item in data]
        quarters = [int(item.get('quarter') or 0) for item in data]
        eps_estimates = [
            float(item.get('epsEstimate')) if item.get('epsEstimate') not in (None, '') else None
            for item in data
        ]
        eps_last_year = [
            float(item.get('epsLastYear')) if item.get('epsLastYear') not in (None, '') else None
            for item in data
        ]
        revenue_estimates = [
            float(item.get('revenueEstimate')) if item.get('revenueEstimate') not in (None, '') else None
            for item in data
        ]
        revenue_last_year = [
            float(item.get('revenueLastYear')) if item.get('revenueLastYear') not in (None, '') else None
            for item in data
        ]
        last_release = [item.get('lastReleaseDate') for item in data]
        eps_estimate_date = [item.get('epsEstimateDate') for item in data]
        earnings_dict = {
            'ticker': symbols,
            'name': names,
            'price': prices,
            'volume': volumes,
            'change_ratio': change_ratio,
            'start_date': start_dates,
            'year': years,
            'quarter': quarters,
            'last_release': last_release,
            'eps_last': eps_last_year,
            'eps_estimate': eps_estimates,
            'eps_estimate_date': eps_estimate_date,
            'revenue_estimate': revenue_estimates,
            'revenue_last': revenue_last_year,
        }
        df = pd.DataFrame(earnings_dict)
        scores = df.apply(
            lambda row: score_earnings_setup(
                row.get('eps_estimate'),
                row.get('eps_last'),
                row.get('revenue_estimate'),
                row.get('revenue_last'),
            ),
            axis=1,
        )
        df['earnings_signal'] = [s.signal for s in scores]
        df['earnings_points'] = [s.points for s in scores]
        df['earnings_reason'] = [s.reason for s in scores]
        df['confluence_score'] = df['earnings_points']
        df['earnings_asof'] = pd.Timestamp.utcnow()
        await opts.batch_upsert_dataframe(
            df, table_name='earnings_soon', unique_columns=['ticker']
        )
        print(f"[✓] Upserted {len(df)} earnings records for {trading_day}")
    except Exception as e:
        print(f"[ERROR] Error fetching earnings: {e}")


async def notify_earnings() -> None:
    """
    Retrieve upcoming earnings from the database and send a summary embed to
    Discord.  Assumes the ``earnings_soon`` table has already been
    populated and that ``opts.connect()`` has been called.
    """
    query = (
        "SELECT ticker, name, price, volume, change_ratio, start_date, "
        "last_release, eps_last, eps_estimate, revenue_estimate, revenue_last "
        "FROM earnings_soon"
    )
    try:
        results = await opts.fetch(query)
        if not results:
            print("[!] No earnings data available to notify.")
            return
        df = pd.DataFrame(
            results,
            columns=[
                'ticker',
                'name',
                'price',
                'volume',
                'change_ratio',
                'start_date',
                'last_release',
                'eps_last',
                'eps_estimate',
                'revenue_estimate',
                'revenue_last',
            ],
        )
        # Format large numbers for readability
        df = format_large_numbers_in_dataframe2(df)
        embed = DiscordEmbed(
            title='Earnings Soon!',
            description="```py\nThe tickers below have earnings soon.```",
            color=hex_color_dict.get('gold'),
        )
        for _, row in df.iterrows():
            embed.add_embed_field(
                name=f"{row.get('name')} | {row.get('ticker')}",
                value=(
                    f"> Price: ${row.get('price')}\n"
                    f"> Volume: {row.get('volume')}\n"
                    f"> Change: {row.get('change_ratio')}%\n"
                    f"> Start: {row.get('start_date')}\n"
                    f"> Last release: {row.get('last_release')}\n"
                    f"> Revenue (Est/Last): {row.get('revenue_estimate')} / {row.get('revenue_last')}\n"
                    f"> EPS (Est/Last): {row.get('eps_estimate')} / {row.get('eps_last')}"
                ),
                inline=False,
            )
        # Send the embed via the configured webhook
        hook_url = os.environ.get('earnings_today')
        if not hook_url:
            print("[ERROR] Earnings webhook URL not configured in environment variables.")
            return
        hook = AsyncDiscordWebhook(hook_url)
        embed.set_timestamp()
        hook.add_embed(embed)
        await hook.execute()
    except Exception as e:
        print(f"[ERROR] Error sending earnings notification: {e}")


async def run_earnings() -> None:
    """
    Entry point for periodically fetching upcoming earnings and sending
    notifications.  A single database connection and HTTP session are
    created and reused.
    """
    await opts.connect()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                # Fetch and upsert earnings for the next trading day
                await fetch_earnings(session)
                # Notify of upcoming earnings
                await notify_earnings()
                # Sleep before the next cycle (approx. 2.2 hours)
                await asyncio.sleep(8000)
    finally:
        await opts.disconnect()


if __name__ == "__main__":
    asyncio.run(run_earnings())
