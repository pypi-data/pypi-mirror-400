import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

import pandas as pd
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
from tabulate import tabulate

# Make sure project directory is in path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Import your internal modules
from fudstop4.apis.ultimate.ultimate_sdk import UltimateSDK  # noqa: E402
from fudstop4.apis.polygonio.polygon_options import PolygonOptions  # noqa: E402
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf  # noqa: E402
from fudstop4._markets.list_sets.dicts import hex_color_dict  # noqa: E402
from UTILS.confluence import score_analyst_ratings  # noqa: E402

load_dotenv()

ultimate = UltimateSDK()
db = PolygonOptions(database="fudstop3")

DEFAULT_FETCH_SLEEP = 86_400
DEFAULT_PRODUCER_SLEEP = 86_400

logger = logging.getLogger(__name__)

# Discord Webhooks
strongbuy_hook = os.environ.get("strongbuy_rating")
buy_hook = os.environ.get("buy_rating")
hold_hook = os.environ.get("hold_rating")
sell_hook = os.environ.get("sell_rating")
underperform_hook = os.environ.get("underperform_rating")


def configure_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


async def send_embed(df: pd.DataFrame, rating: str) -> None:
    """
    Send an embed to the Discord channel corresponding to a given rating.
    """
    ticker = df["ticker"].to_list()[0]
    webhook_url = None
    if rating == "sell":
        color = hex_color_dict.get("red")
        webhook_url = sell_hook
        title_text = "Sell Ratings"
        footer_text = "Analysts Sell"
    elif rating == "underperform":
        color = hex_color_dict.get("orange")
        webhook_url = underperform_hook
        title_text = "Underperform Ratings"
        footer_text = "Analysts Underperform"
    elif rating == "hold":
        color = hex_color_dict.get("yellow")
        webhook_url = hold_hook
        title_text = "Hold Ratings"
        footer_text = "Analysts Hold"
    elif rating == "buy":
        color = hex_color_dict.get("green")
        webhook_url = buy_hook
        title_text = "Buy Ratings"
        footer_text = "Analysts Buy"
    elif rating == "strong_buy":
        color = hex_color_dict.get("green")
        webhook_url = strongbuy_hook
        title_text = "Strong Buy Ratings"
        footer_text = "Analysts Strong Buy"
    else:
        color = hex_color_dict.get("blue")
        webhook_url = buy_hook
        title_text = "Unknown Rating"
        footer_text = "Analysts Unknown"

    if not webhook_url:
        logger.debug("No webhook configured for rating '%s'; skipping send", rating)
        return

    table = tabulate(
        df.values.tolist(),
        headers=list(df.columns),
        tablefmt="heavy_rounded",
        showindex=False,
    )

    webhook = AsyncDiscordWebhook(webhook_url)
    embed = DiscordEmbed(
        title=title_text,
        description=f"```py\n{table}```",
        color=color,
    )
    embed.set_timestamp()
    embed.set_footer(text=f"{ticker},{rating}, Implemented by F.U.D.STOP")

    webhook.add_embed(embed)
    await webhook.execute()


async def producer(
    sleep_seconds: int = DEFAULT_PRODUCER_SLEEP, max_cycles: int | None = None
) -> None:
    """
    Continuously queries the 'analysts' table for each rating category and sends Discord alerts.
    """
    cycle = 0
    while True:
        queries = {
            "strong_buy": (
                "SELECT ticker, strong_buy "
                "FROM analysts "
                "WHERE strong_buy > buy "
                "  AND strong_buy > sell "
                "  AND strong_buy > underperform "
                "  AND strong_buy > hold",
                ["ticker", "strong_buy"],
            ),
            "sell": (
                "SELECT ticker, sell "
                "FROM analysts "
                "WHERE sell > buy "
                "  AND sell > strong_buy "
                "  AND sell > underperform "
                "  AND sell > hold",
                ["ticker", "sell"],
            ),
            "hold": (
                "SELECT ticker, hold "
                "FROM analysts "
                "WHERE hold > buy "
                "  AND hold > strong_buy "
                "  AND hold > underperform "
                "  AND hold > sell",
                ["ticker", "hold"],
            ),
            "underperform": (
                "SELECT ticker, underperform "
                "FROM analysts "
                "WHERE underperform > hold "
                "  AND underperform > sell "
                "  AND underperform > strong_buy "
                "  AND underperform > buy",
                ["ticker", "underperform"],
            ),
            "buy": (
                "SELECT ticker, buy "
                "FROM analysts "
                "WHERE buy > underperform "
                "  AND buy > strong_buy "
                "  AND buy > sell "
                "  AND buy > hold",
                ["ticker", "buy"],
            ),
        }
        fetch_tasks = [db.fetch(query) for (query, _cols) in queries.values()]
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        dataframes: dict[str, pd.DataFrame] = {}
        for (rating, (_query, cols)), result in zip(queries.items(), results):
            if isinstance(result, Exception):
                logger.warning("Failed to fetch %s: %s", rating, result)
                dataframes[rating] = pd.DataFrame(columns=cols)
            else:
                dataframes[rating] = pd.DataFrame(result, columns=cols)

        send_tasks = [
            send_embed(df, rating=rating) for rating, df in dataframes.items() if not df.empty
        ]
        if send_tasks:
            await asyncio.gather(*send_tasks)

        logger.info("Producer cycle complete; sleeping for %s seconds", sleep_seconds)
        cycle += 1
        if max_cycles is not None and cycle >= max_cycles:
            break
        await asyncio.sleep(sleep_seconds)


async def main(
    fetch_sleep_seconds: int = DEFAULT_FETCH_SLEEP, max_cycles: int | None = None
) -> None:
    """
    Continuously fetches the latest analyst ratings for the most active tickers and upserts them.
    """
    cycle = 0
    while True:
        all_ratings = await ultimate.analyst_ratings_for_tickers(most_active_nonetf)

        for ticker, rating_obj in all_ratings.items():
            try:
                if rating_obj is not None and getattr(rating_obj, "df", None) is not None:
                    rating_obj.df["ticker"] = ticker
                    try:
                        row = rating_obj.df.iloc[0].to_dict()
                        score = score_analyst_ratings(
                            row.get("strong_buy"),
                            row.get("buy"),
                            row.get("hold"),
                            row.get("underperform"),
                            row.get("sell"),
                        )
                        rating_obj.df = rating_obj.df.assign(
                            **score.to_columns("analyst"),
                            confluence_score=score.points,
                            analyst_asof=pd.Timestamp.utcnow(),
                        )
                    except Exception as exc:
                        logger.warning("Failed scoring analysts for %s: %s", ticker, exc)
                    await db.batch_upsert_dataframe(
                        rating_obj.df,
                        table_name="analysts",
                        unique_columns=["ticker"],
                    )
                    # Confluence layer (light weight to avoid double-counting)
                    layer_df = pd.DataFrame(
                        [
                            {
                                "ticker": ticker,
                                "source": "analyst_ratings",
                                "points": score.points,
                                "signal": score.signal,
                                "reason": score.reason,
                                "weight": 0.3,
                            }
                        ]
                    )
                    await db.batch_upsert_dataframe(
                        layer_df,
                        table_name="confluence_layers",
                        unique_columns=["ticker", "source"],
                    )
                else:
                    logger.debug("Skipped upsert for %s: no analyst dataframe", ticker)
            except Exception as exc:
                logger.warning("Failed upsert for %s: %s", ticker, exc)

        logger.info("Fetch cycle completed; sleeping for %s seconds", fetch_sleep_seconds)
        cycle += 1
        if max_cycles is not None and cycle >= max_cycles:
            break
        await asyncio.sleep(fetch_sleep_seconds)


async def run_concurrent_tasks(
    fetch_sleep_seconds: int,
    producer_sleep_seconds: int,
    run_once: bool = False,
) -> None:
    """Run the fetch and producer loops concurrently."""
    await db.connect()
    try:
        max_cycles = 1 if run_once else None
        await asyncio.gather(
            main(fetch_sleep_seconds=fetch_sleep_seconds, max_cycles=max_cycles),
            producer(sleep_seconds=producer_sleep_seconds, max_cycles=max_cycles),
        )
    finally:
        await db.disconnect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch analyst ratings and push Discord alerts.")
    parser.add_argument(
        "--fetch-sleep",
        type=int,
        default=DEFAULT_FETCH_SLEEP,
        help="Seconds to sleep between fetch cycles (default: %(default)s).",
    )
    parser.add_argument(
        "--producer-sleep",
        type=int,
        default=DEFAULT_PRODUCER_SLEEP,
        help="Seconds to sleep between notification cycles (default: %(default)s).",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run a single cycle for both fetch and producer then exit.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    cli_args = parse_args()
    asyncio.run(
        run_concurrent_tasks(
            fetch_sleep_seconds=cli_args.fetch_sleep,
            producer_sleep_seconds=cli_args.producer_sleep,
            run_once=cli_args.run_once,
        )
    )
