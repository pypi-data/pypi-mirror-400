"""Discord webhook embed builders for multiple data feeds.

This module centralizes embed construction so webhook services can
combine the rich data gathered by the scripts in this repository.
Each feed uses the underlying database records populated by the
corresponding script and formats a concise Discord embed.
"""
from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
from tabulate import tabulate

project_dir = Path(__file__).resolve().parents[1]
if str(project_dir) not in sys.path:
    sys.path.append(str(project_dir))

# Enable access to the shared fudstop4 package that lives alongside this repo.
maybe_fudstop_pkg = project_dir.parent / "fudstop"
if maybe_fudstop_pkg.exists() and str(maybe_fudstop_pkg) not in sys.path:
    sys.path.append(str(maybe_fudstop_pkg))

from UTILS.confluence import score_volatility_profile  # noqa: E402
from UTILS.db_tables import InfoTable  # noqa: E402
from fudstop4._markets.list_sets.dicts import hex_color_dict  # noqa: E402
from fudstop4.apis.polygonio.polygon_options import PolygonOptions  # noqa: E402
from scripts.config import alerts_webhook_dict  # noqa: E402

load_dotenv()

db = PolygonOptions()

VOLATILITY_HOOKS = {
    "Absolutely still": os.environ.get("still_volatility"),
    "Quiet": os.environ.get("quiet_volatility"),
    "Volatile": os.environ.get("volatile_volatility"),
    "Slightly volatile": os.environ.get("slightly_volatile"),
    "Extremely volatile": os.environ.get("extreme_volatility"),
    "Volatility unclear": os.environ.get("unclear_volatility"),
}


ANALYST_HOOKS = { 

    'sell': os.environ.get('sell_rating'),
    'underperform': os.environ.get('underperform_rating'),
    'buy': os.environ.get('buy_rating'),
    'strong_buy': os.environ.get('strongbuy_rating'),
    'hold': os.environ.get('hold_rating')
}


@dataclass(frozen=True)
class FeedHooks:
    """Environment-driven webhook endpoints used by the feeds."""

    info: Optional[str] = os.environ.get("info_webhook")
    active: Optional[str] = os.environ.get("active_webhook") or os.environ.get("active_alerts")
    alerts: Optional[str] = os.environ.get("alerts_webhook")
    volume_summary: Optional[str] = os.environ.get("volume_summary_webhook") or os.environ.get("volume_surge")
    volume_analysis: Optional[str] = os.environ.get("volume_analysis_webhook") or os.environ.get("volume_surge")
    extreme_rsi: Optional[str] = os.environ.get("extreme_rsi_webhook")


HOOKS = FeedHooks()


def classify_color(alert_label: str | None) -> str:
    """Return a hex color for the alert; defaults to neutral yellow."""
    if not alert_label:
        return hex_color_dict.get("gold", "FFFF00")
    alert_label = alert_label.lower()
    bearish_terms = ("sell", "falling", "decrease", "reversal", "down")
    bullish_terms = ("buy", "rising", "increase", "rebound", "rise", "up")
    if any(term in alert_label for term in bearish_terms):
        return hex_color_dict.get("red", "FF0000")
    if any(term in alert_label for term in bullish_terms):
        return hex_color_dict.get("green", "00FF00")
    return hex_color_dict.get("gold", "FFFF00")


def _extract_value(value):
    """Extract scalar value from list if needed."""
    return value[0] if isinstance(value, list) else value


def _percent(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def _number(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.0f}" if abs(value) >= 1 else f"{value:.2f}"


async def _upsert_volume_signal(ticker: str, vol_score, results: InfoTable, *, db_client: PolygonOptions) -> None:
    """Persist a volatility signal produced from :mod:`feeds.info`."""
    vol_columns = vol_score.to_columns("info")
    vol_df = pd.DataFrame(
        [
            {
                "ticker": ticker,
                "asof": pd.Timestamp.utcnow(),
                "info_signal": vol_columns.get("info_signal"),
                "info_points": vol_columns.get("info_points"),
                "info_reason": vol_columns.get("info_reason"),
                "info_confluence_score": vol_columns.get("info_confluence_score"),
                "info_call_put_volume_ratio": vol_columns.get("info_call_put_volume_ratio"),
                "confluence_score": vol_score.points,
                "volatile_rank": _extract_value(results.volatile_rank),
                "call_volume": _extract_value(results.call_vol),
                "put_volume": _extract_value(results.put_vol),
            }
        ]
    )
    await db_client.batch_upsert_dataframe(
        vol_df,
        table_name="info_signals",
        unique_columns=["ticker"],
    )


async def send_info_embed(ticker: str, *, hook_override: str | None = None, db_client: PolygonOptions | None = None) -> None:
    """Send a volatility-centric embed for a ticker.

    Data source: :mod:`feeds.info` (``info`` table).
    """

    db_local = db_client or db
    await db_local.connect()
    query = (
        "SELECT * FROM info "
        f"WHERE ticker = '{ticker}' "
        "ORDER BY insertion_timestamp DESC LIMIT 1"
    )
    rows = await db_local.fetch(query)
    if not rows:
        print(f"[!] No info rows found for {ticker}")
        return

    info = InfoTable(rows)

    volatile_rank = _extract_value(info.volatile_rank)
    call_vol = _extract_value(info.call_vol)
    put_vol = _extract_value(info.put_vol)

    try:
        vol_score = score_volatility_profile(volatile_rank, call_vol, put_vol)
        await _upsert_volume_signal(ticker, vol_score, info, db_client=db_local)
    except Exception as exc:  # noqa: BLE001
        print(f"[!] Failed to store info signal for {ticker}: {exc}")

    hook_url = hook_override or VOLATILITY_HOOKS.get(volatile_rank) or HOOKS.info
    if not hook_url:
        print(f"[!] No info webhook configured for volatility rank '{volatile_rank}'; skipping embed")
        return

    hook = AsyncDiscordWebhook(hook_url)
    embed = DiscordEmbed(
        title=f"Volatility - {ticker}",
        description=(
            "```py\n"
            f"{ticker} is currently {volatile_rank} and is trading at {_extract_value(info.price)}."
            "```"
        ),
        color=hex_color_dict.get("gold"),
    )
    embed.set_timestamp()

    embed.add_embed_field(
        name="52w Stats",
        value=(
            f"> Low: **${_extract_value(info.low_price_52wk):.2f}**\n"
            f"> Now: **${_extract_value(info.price):.2f}**\n"
            f"> High: **${_extract_value(info.high_price_52wk):.2f}**"
        ),
    )
    embed.add_embed_field(
        name="Activity",
        value=(
            f"> Option Volume: **{_number(_extract_value(info.opt_vol))}**\n"
            f"> Stock Volume: **{_number(_extract_value(info.stock_vol))}**\n"
            f"> Options OI: **{_number(_extract_value(info.open_interest))}**"
        ),
    )
    embed.add_embed_field(
        name="Calls vs Puts",
        value=(
            f"> Calls: **{_number(call_vol)}**\n"
            f"> Puts: **{_number(put_vol)}**"
        ),
    )
    embed.add_embed_field(
        name="IV Rank",
        value=(
            f"> 30D: **{_extract_value(info.ivr30):.2f}**\n"
            f"> 60D: **{_extract_value(info.ivr60):.2f}**\n"
            f"> 90D: **{_extract_value(info.ivr90):.2f}**\n"
            f"> 150D: **{_extract_value(info.ivr150):.2f}**\n"
            f"> 180D: **{_extract_value(info.ivr180):.2f}**"
        ),
    )
    embed.add_embed_field(
        name="Historical Volatility",
        value=(
            f"> 10D: **{_extract_value(info.hv10):.2f}**\n"
            f"> 30D: **{_extract_value(info.hv30):.2f}**\n"
            f"> 60D: **{_extract_value(info.hv60):.2f}**\n"
            f"> 90D: **{_extract_value(info.hv90):.2f}**\n"
            f"> 180D: **{_extract_value(info.hv180):.2f}**"
        ),
    )
    embed.add_embed_field(
        name="Company",
        value=(
            f"> Market Cap: **{_number(_extract_value(info.market_cap))}**\n"
            f"> EPS: **{_extract_value(info.eps)}**\n"
            f"> P.E.: **{_extract_value(info.pe)}**\n"
            f"> Industry: **{_extract_value(info.industry)}**"
        ),
    )
    embed.set_footer(text=f"{ticker},{volatile_rank},Info Feed")

    hook.add_embed(embed)
    await hook.execute()


async def send_active_embed(
    rank_type: str = "turnoverRatio",
    limit: int = 5,
    *,
    hook_override: str | None = None,
    db_client: PolygonOptions | None = None,
) -> None:
    """Send the most recent Webull *active* leaderboard.

    Data source: :mod:`scripts.active` (``active_<rank_type>`` tables).
    """

    db_local = db_client or db
    await db_local.connect()
    query = (
        "SELECT * FROM active "
        f"WHERE rank_type = '{rank_type}' "
        "ORDER BY insertion_timestamp DESC "
        f"LIMIT {limit}"
    )
    rows = await db_local.fetch(query)
    if not rows:
        print(f"[!] No rows found in active for rank_type={rank_type}; skipping embed")
        return

    embed = DiscordEmbed(
        title=f"Top {limit} Active ({rank_type})",
        description="Latest leaderboard snapshot.",
        color=hex_color_dict.get("blue"),
    )
    embed.set_timestamp()

    for idx, row in enumerate(rows, 1):
        ticker = row.get("ticker") or row.get("symbol")
        metric_value = row.get("rank_value") or row.get(rank_type) or row.get("value")
        change_ratio = row.get("change_ratio")
        volume = row.get("volume")
        embed.add_embed_field(
            name=f"{idx}. {ticker}",
            value=(
                f"> Rank Value: **{_number(metric_value)}**\n"
                f"> Change: **{_percent(change_ratio)}**\n"
                f"> Volume: **{_number(volume)}**"
            ),
        )

    hook_url = hook_override or HOOKS.active
    if not hook_url:
        print("[!] No active webhook configured; skipping embed")
        return

    hook = AsyncDiscordWebhook(hook_url)
    hook.add_embed(embed)
    await hook.execute()


async def send_alert_embed(
    ticker: str,
    alert_type: str,
    *,
    volume: float | None = None,
    change_ratio: float | None = None,
    hook_override: str | None = None,
) -> None:
    """Send a real-time alert embed using the same styling as :mod:`scripts.alerts`."""

    hook_url = hook_override or alerts_webhook_dict.get(alert_type) or HOOKS.alerts
    if not hook_url:
        print(f"[!] No alert webhook configured for {alert_type}; skipping embed")
        return

    hook = AsyncDiscordWebhook(hook_url)
    color = classify_color(alert_type)

    description = f"```py\n{ticker} has triggered a {alert_type} alert.```"
    embed = DiscordEmbed(title=f"Alert: {ticker}", description=description, color=color)

    if volume is not None:
        embed.add_embed_field(name="Volume", value=f"> **{_number(volume)}**", inline=False)
    if change_ratio is not None:
        direction = "Up" if change_ratio > 0 else "Down"
        embed.add_embed_field(
            name="Price Change",
            value=f"> **{direction} {abs(change_ratio):.2f}%**",
            inline=False,
        )

    embed.set_timestamp()
    embed.set_footer(text=f"{ticker},{alert_type},Alerts Feed")
    hook.add_embed(embed)
    await hook.execute()


async def send_volume_summary_embed(
    ticker: str,
    *,
    expiry_limit: int = 3,
    hook_override: str | None = None,
    db_client: PolygonOptions | None = None,
) -> None:
    """Send a summarized open interest/volume snapshot.

    Data source: :mod:`scripts.volume_summary` (``volume_summary`` table).
    """

    db_local = db_client or db
    await db_local.connect()
    query = (
        "SELECT * FROM volume_summary "
        f"WHERE ticker = '{ticker}' ORDER BY expiry ASC LIMIT {expiry_limit}"
    )
    rows = await db_local.fetch(query)
    if not rows:
        print(f"[!] No volume_summary data for {ticker}")
        return

    embed = DiscordEmbed(
        title=f"Options Volume Summary - {ticker}",
        description=f"Nearest {expiry_limit} expirations for {ticker}.",
        color=hex_color_dict.get("teal"),
    )
    embed.set_timestamp()

    for row in rows:
        expiry = row.get("expiry")
        calls = row.get("call_volume")
        puts = row.get("put_volume")
        total = calls + puts if calls is not None and puts is not None else None
        embed.add_embed_field(
            name=str(expiry),
            value=(
                f"> Calls Vol: **{_number(calls)}**\n"
                f"> Puts Vol: **{_number(puts)}**\n"
                f"> Total Vol: **{_number(total)}**"
            ),
        )

    hook_url = hook_override or HOOKS.volume_summary
    if not hook_url:
        print("[!] No volume summary webhook configured; skipping embed")
        return

    hook = AsyncDiscordWebhook(hook_url)
    hook.add_embed(embed)
    await hook.execute()


async def send_volume_analysis_embed(
    ticker: str,
    *,
    hook_override: str | None = None,
    db_client: PolygonOptions | None = None,
) -> None:
    """Send the latest volume analysis snapshot.

    Data source: :mod:`scripts.vol_anal` (``volume_analysis`` table).
    """

    db_local = db_client or db
    await db_local.connect()
    query = (
        "SELECT * FROM volume_analysis "
        f"WHERE ticker = '{ticker}' "
        "ORDER BY insertion_timestamp DESC LIMIT 1"
    )
    rows = await db_local.fetch(query)
    if not rows:
        print(f"[!] No volume analysis for {ticker}")
        return

    row = rows[0]
    embed = DiscordEmbed(
        title=f"Volume Analysis - {ticker}",
        description="Latest Ultimate volume analytics snapshot.",
        color=hex_color_dict.get("purple"),
    )
    embed.set_timestamp()

    try:
        avg_price = float(row.get("avg_price")) if row.get("avg_price") not in (None, "") else None
    except (TypeError, ValueError):
        avg_price = None

    embed.add_embed_field(
        name="Totals",
        value=(
            f"> Volume: **{_number(row.get('total_volume'))}**\n"
            f"> Trades: **{_number(row.get('total_num'))}**\n"
            f"> Avg Price: **{avg_price or 'N/A'}**"
        ),
    )
    embed.add_embed_field(
        name="Breakdown",
        value=(
            f"> Buy: **{_number(row.get('buy_volume'))} ({_percent(row.get('buy_pct'))})**\n"
            f"> Sell: **{_number(row.get('sell_volume'))} ({_percent(row.get('sell_pct'))})**\n"
            f"> Neutral: **{_number(row.get('neut_volume'))} ({_percent(row.get('neut_pct'))})**"
        ),
    )
    if row.get("volume_signal") or row.get("volume_reason"):
        embed.add_embed_field(
            name="Signal",
            value=(
                f"> Signal: **{row.get('volume_signal') or 'N/A'}**\n"
                f"> Points: **{row.get('volume_points') or 'N/A'}**\n"
                f"> Reason: **{row.get('volume_reason') or 'N/A'}**"
            ),
            inline=False,
        )

    hook_url = hook_override or HOOKS.volume_analysis
    if not hook_url:
        print("[!] No volume analysis webhook configured; skipping embed")
        return

    hook = AsyncDiscordWebhook(hook_url)
    hook.add_embed(embed)
    await hook.execute()


async def send_batch(feed_fn, tickers: Iterable[str]) -> None:
    """Helper to fan out a feed coroutine across tickers."""

    tasks = [feed_fn(tkr) for tkr in tickers]
    await asyncio.gather(*tasks)








async def analyst_rating_embed(df: pd.DataFrame, rating: str) -> None:
    """
    Sends an embed to the Discord channel corresponding to a given rating.
    
    :param df: The DataFrame to be embedded in the message.
    :param rating: The rating string (e.g., 'sell', 'underperform', 'hold', 'buy', 'strong_buy').
    """
    # Match rating with color and webhook
    ticker = df['ticker'].to_list()[0]
    if rating == 'sell':
        color = hex_color_dict.get('red')
        webhook_url = ANALYST_HOOKS.get(rating)
        title_text = "Sell Ratings"
        footer_text = "Analysts Sell"

    elif rating == 'underperform':
        color = hex_color_dict.get('orange')
        webhook_url = ANALYST_HOOKS.get(rating)
        title_text = "Underperform Ratings"
        footer_text = "Analysts Underperform"

    elif rating == 'hold':
        color = hex_color_dict.get('yellow')
        webhook_url = ANALYST_HOOKS.get(rating)
        title_text = "Hold Ratings"
        footer_text = "Analysts Hold"

    elif rating == 'buy':
        color = hex_color_dict.get('green')
        ANALYST_HOOKS.get(rating)
        title_text = "Buy Ratings"
        footer_text = "Analysts Buy"

    elif rating == 'strong_buy':
        color = hex_color_dict.get('green')
        webhook_url = ANALYST_HOOKS.get(rating)
        title_text = "Strong Buy Ratings"
        footer_text = "Analysts Strong Buy"
    else:
        # Fallback (in case rating is not recognized)
        color = hex_color_dict.get('blue')
        webhook_url = ANALYST_HOOKS.get(rating)
        title_text = "Unknown Rating"
        footer_text = "Analysts Unknown"

    # Build the table from the DataFrame
    table = tabulate(df.values.tolist(), headers=list(df.columns), tablefmt='heavy_rounded', showindex=False)

    # Create the webhook + embed
    webhook = AsyncDiscordWebhook(webhook_url)
    embed = DiscordEmbed(
        title=title_text,
        description=f"```py\n{table}```",
        color=color
    )
    embed.set_timestamp()
    embed.set_footer(text=f"{ticker},{footer_text}, Implemented by F.U.D.STOP")

    webhook.add_embed(embed)

    # Execute the webhook
    await webhook.execute()




async def extreme_rsi_embed(
    webhook_url: str | None = None,
    *,
    lookback_minutes: int = 5,
    limit: int = 10,
    db_client: PolygonOptions | None = None,
) -> None:
    """
    Send an embed summarizing extreme RSI conditions (1m/5m) for the last N minutes.
    Produces two tabulated sections: oversold (bullish) and overbought (bearish).
    """

    db_local = db_client or db
    await db_local.connect()
    lookback_clause = f"NOW() - INTERVAL '{int(lookback_minutes)} minutes'"

    bull_query = f"""
        SELECT ticker, timespan, rsi
        FROM plays
        WHERE timespan IN ('1min', '5min')
          AND insertion_timestamp >= {lookback_clause}
          AND (candle_completely_below_lower = TRUE OR rsi <= 30)
        ORDER BY rsi ASC
        LIMIT {int(limit)}
    """
    bear_query = f"""
        SELECT ticker, timespan, rsi
        FROM plays
        WHERE timespan IN ('1min', '5min')
          AND insertion_timestamp >= {lookback_clause}
          AND (candle_completely_above_upper = TRUE OR rsi >= 70)
        ORDER BY rsi DESC
        LIMIT {int(limit)}
    """

    bulls = pd.DataFrame(await db_local.fetch(bull_query), columns=["ticker", "timespan", "rsi"])
    bears = pd.DataFrame(await db_local.fetch(bear_query), columns=["ticker", "timespan", "rsi"])

    for df in (bulls, bears):
        if not df.empty:
            df["rsi"] = df["rsi"].astype(float).round(2)

    def _section(label: str, df: pd.DataFrame) -> str:
        if df.empty:
            return f"{label}:\n  none in last {lookback_minutes}m"
        table = tabulate(df.values.tolist(), headers=list(df.columns), tablefmt="heavy_rounded", showindex=False)
        return f"{label}:\n{table}"

    desc = "```py\n" + "\n\n".join(
        [
            _section("BULLISH (oversold)", bulls),
            _section("BEARISH (overbought)", bears),
        ]
    ) + "\n```"

    hook_url = webhook_url or HOOKS.extreme_rsi
    if not hook_url:
        print("[!] No extreme RSI webhook configured; skipping embed")
        return

    embed = DiscordEmbed(
        title="Extreme RSI Scan (1m/5m)",
        description=desc,
        color=hex_color_dict.get("teal"),
    )
    embed.set_timestamp()
    embed.set_footer(text=f"extreme_rsi, lookback {lookback_minutes}m")

    hook = AsyncDiscordWebhook(hook_url)
    hook.add_embed(embed)
    await hook.execute()


async def run_extreme_rsi_loop(
    *,
    interval_seconds: int = 300,
    webhook_url: str | None = None,
    lookback_minutes: int = 5,
    limit: int = 10,
    db_client: PolygonOptions | None = None,
) -> None:
    """Continuously send the extreme RSI embed on a fixed cadence."""
    while True:
        try:
            await extreme_rsi_embed(
                webhook_url=webhook_url,
                lookback_minutes=lookback_minutes,
                limit=limit,
                db_client=db_client,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[!] extreme_rsi_embed loop error: {exc}")
        await asyncio.sleep(interval_seconds)


__all__: List[str] = [
    "send_info_embed",
    "send_active_embed",
    "send_alert_embed",
    "send_volume_summary_embed",
    "send_volume_analysis_embed",
    "extreme_rsi_embed",
    "send_batch",
    "FeedHooks",
    "HOOKS",
]
