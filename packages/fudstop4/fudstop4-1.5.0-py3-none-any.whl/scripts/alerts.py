import argparse
import asyncio
import inspect
import logging
import os
import sys
from collections import deque
from functools import partial
from pathlib import Path
from typing import Iterable, Tuple

import aiohttp
import pandas as pd
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from dotenv import load_dotenv

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from config import alerts_dict, alerts_webhook_dict  # noqa: E402
from fudstop4._markets.list_sets.dicts import hex_color_dict  # noqa: E402
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers  # noqa: E402
from UTILS.imps import *  # noqa: E402,F401,F403

load_dotenv()

DEFAULT_INTERVAL = 5
MAX_SEEN_ALERTS = 10_000

logger = logging.getLogger(__name__)
_seen_keys: deque[str] = deque()
_seen_set: set[str] = set()


def configure_logging() -> None:
    """Configure a basic console logger if the application has not already configured logging."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


def record_seen(alert_key: str, max_seen: int) -> bool:
    """Return True if this alert is new and record it, otherwise False."""
    if alert_key in _seen_set:
        return False
    _seen_keys.append(alert_key)
    _seen_set.add(alert_key)
    while len(_seen_keys) > max_seen:
        expired = _seen_keys.popleft()
        _seen_set.discard(expired)
    return True


def classify_color(alert_label: str | None) -> str:
    """Return a hex color for the alert; defaults to neutral yellow."""
    if not alert_label:
        return "FFFF00"
    alert_label = alert_label.lower()
    bearish_terms = ("sell", "falling", "decrease", "reversal", "down")
    bullish_terms = ("buy", "rising", "increase", "rebound", "rise", "up")
    if any(term in alert_label for term in bearish_terms):
        return hex_color_dict.get("red", "FF0000")
    if any(term in alert_label for term in bullish_terms):
        return hex_color_dict.get("green", "00FF00")
    return "FFFF00"


async def ensure_awaitable(func, *args, **kwargs):
    """Invoke `func` regardless of whether it's sync or async."""
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))


def _alert_type_key(alert_type: object) -> int | None:
    """Return an int alert type key when possible."""
    try:
        return int(alert_type)
    except (TypeError, ValueError):
        return None


async def send_embed(
    ticker: str,
    alert_type_code: object,
    alert_label: str,
    volume: float | None = None,
    change_ratio: float | None = None,
) -> None:
    """Send a formatted alert embed to the appropriate Discord webhook."""
    hook_url = alerts_webhook_dict.get(alert_label)
    if not hook_url and alert_type_code is not None:
        hook_url = alerts_webhook_dict.get(str(alert_type_code))
    if not hook_url:
        logger.warning(
            "No webhook configured for alert %s (%s); skipping",
            alert_type_code,
            alert_label,
        )
        return

    hook = AsyncDiscordWebhook(hook_url)
    color = classify_color(alert_label)
    title = f"Real-Time Alert: {ticker}"
    description = f"```py\n{ticker} triggered: {alert_label}```"
    embed = DiscordEmbed(title=title, description=description, color=color)
    embed.set_footer(text=f"Implemented by F.U.D.STOP • {ticker} • {alert_type_code}")

    if volume is not None:
        embed.add_embed_field(
            name="Volume Alert",
            value=f"> Volume: {volume:,.0f}",
            inline=False,
        )
    elif change_ratio is not None:
        direction = "Up" if change_ratio > 0 else "Down"
        embed.add_embed_field(
            name="Price Change Alert",
            value=f"> Change: {direction} {abs(change_ratio):.2f}%",
            inline=False,
        )

    embed.set_timestamp()
    hook.add_embed(embed)
    await hook.execute()


async def fetch_webull_alerts(
    session: aiohttp.ClientSession, ticker_ids: Iterable[int], max_seen: int
) -> Tuple[list[dict], list[dict]]:
    """Fetch Webull alerts and return volume and change-ratio alerts."""
    url = "https://quotes-gw.webullfintech.com/api/wlas/portfolio/changes"
    payload = {
        "supportBroker": 8,
        "regionId": 6,
        "sId": 0,
        "limit": 150,
        "tickerIds": list(ticker_ids),
    }

    async with session.post(url, json=payload) as response:
        response.raise_for_status()
        data = await response.json()

    volume_alerts: list[dict] = []
    change_alerts: list[dict] = []

    for item in data:
        ticker = item.get("symbol") or "N/A"
        alert_type_code = item.get("alertType")
        alert_key = f"{ticker}-{alert_type_code}"
        if not record_seen(alert_key, max_seen):
            continue

        if item.get("volume") is not None:
            volume_alerts.append(
                {
                    "ticker": ticker,
                    "volume": float(item["volume"]),
                    "alertType": alert_type_code,
                }
            )
        elif item.get("changeRatio") is not None:
            change_alerts.append(
                {
                    "ticker": ticker,
                    "changeRatio": round(float(item["changeRatio"]) * 100, 2),
                    "alertType": alert_type_code,
                }
            )

    return volume_alerts, change_alerts


async def handle_alerts(
    volume_alerts: list[dict], change_alerts: list[dict]
) -> None:
    """Send embeds and persist alerts concurrently."""
    awaitables: list[asyncio.Future] = []
    layer_rows: list[dict] = []

    for alert in volume_alerts:
        alert_type_code = alert["alertType"]
        alert_type_key = _alert_type_key(alert_type_code)
        human_alert = alerts_dict.get(
            alert_type_key,
            alerts_dict.get(alert_type_code, str(alert_type_code)),
        )
        payload = {
            "ticker": alert["ticker"],
            "alert": human_alert,
            "alert_type": alert_type_code,
            "volume": alert["volume"],
        }
        df = pd.DataFrame(payload, index=[0])

        awaitables.append(
            send_embed(
                ticker=alert["ticker"],
                alert_type_code=alert_type_code,
                alert_label=human_alert,
                volume=alert["volume"],
            )
        )
        awaitables.append(
            ensure_awaitable(
                db.batch_upsert_dataframe,
                df,
                table_name="volume_alerts",
                unique_columns=["ticker", "alert_type"],
            )
        )
        layer_rows.append(
            {
                "ticker": alert["ticker"],
                "source": f"alert_volume_{alert_type_code}",
                "points": 1,
                "signal": "bullish",
                "reason": f"Volume alert {human_alert}",
                "asof": pd.Timestamp.utcnow(),
                "weight": 0.4,
            }
        )

    for alert in change_alerts:
        alert_type_code = alert["alertType"]
        alert_type_key = _alert_type_key(alert_type_code)
        human_alert = alerts_dict.get(
            alert_type_key,
            alerts_dict.get(alert_type_code, str(alert_type_code)),
        )
        payload = {
            "ticker": alert["ticker"],
            "alert_type": alert_type_code,
            "alert": human_alert,
            "change_ratio": alert["changeRatio"],
        }
        df = pd.DataFrame(payload, index=[0])

        awaitables.append(
            send_embed(
                ticker=alert["ticker"],
                alert_type_code=alert_type_code,
                alert_label=human_alert,
                change_ratio=alert["changeRatio"],
            )
        )
        awaitables.append(
            ensure_awaitable(
                db.batch_upsert_dataframe,
                df,
                table_name="change_alerts",
                unique_columns=["ticker", "alert_type"],
            )
        )
        change_pts = 2 if abs(alert["changeRatio"]) >= 3 else 1
        signal = "bullish" if alert["changeRatio"] > 0 else "bearish"
        layer_rows.append(
            {
                "ticker": alert["ticker"],
                "source": f"alert_change_{alert_type_code}",
                "points": change_pts,
                "signal": signal,
                "reason": f"Price change {alert['changeRatio']}%",
                "asof": pd.Timestamp.utcnow(),
                "weight": 0.5,
            }
        )

    if awaitables:
        results = await asyncio.gather(*awaitables, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                logger.warning("alert task raised: %s", r)
    if layer_rows:
        layer_df = pd.DataFrame(layer_rows)
        await db.batch_upsert_dataframe(
            layer_df,
            table_name="confluence_layers",
            unique_columns=["ticker", "source"],
        )


async def monitor_alerts(
    interval: int = DEFAULT_INTERVAL,
    max_seen: int = MAX_SEEN_ALERTS,
    ticker_ids: Iterable[int] | None = None,
    run_once: bool = False,
) -> None:
    """Poll the Webull changes endpoint on a fixed interval and send alerts."""
    await db.connect()
    tickers = list(ticker_ids) if ticker_ids is not None else most_active_ticker_ids
    try:
        async with aiohttp.ClientSession() as session:
            logger.info("Monitoring Webull alerts every %s seconds", interval)
            while True:
                try:
                    volume_alerts, change_alerts = await fetch_webull_alerts(
                        session, tickers, max_seen
                    )
                    await handle_alerts(volume_alerts, change_alerts)
                except Exception:
                    logger.exception("Exception while processing alerts")

                if run_once:
                    break
                await asyncio.sleep(interval)
    finally:
        await db.disconnect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor Webull alerts and forward to Discord.")
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv("ALERT_INTERVAL", DEFAULT_INTERVAL)),
        help="Polling interval in seconds (default: %(default)s).",
    )
    parser.add_argument(
        "--max-seen",
        type=int,
        default=int(os.getenv("ALERT_MAX_SEEN", MAX_SEEN_ALERTS)),
        help="Number of recent alerts to remember for deduplication.",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Execute a single poll cycle then exit.",
    )
    parser.add_argument(
        "--ticker-id",
        action="append",
        type=int,
        dest="ticker_ids",
        help="Optional Webull ticker IDs to monitor (can be provided multiple times).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    asyncio.run(
        monitor_alerts(
            interval=args.interval,
            max_seen=args.max_seen,
            ticker_ids=args.ticker_ids,
            run_once=args.run_once,
        )
    )
