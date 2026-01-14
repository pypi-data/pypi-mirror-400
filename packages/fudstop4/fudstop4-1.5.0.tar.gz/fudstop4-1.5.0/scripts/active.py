import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime, time
from pathlib import Path
from typing import Iterable, Tuple
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.helpers import generate_webull_headers
db = PolygonOptions()
import aiohttp
import pandas as pd
import pytz

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)


from _webull.models.most_active import Ticker, Values

DEFAULT_SLEEP_SECONDS = 600  # 10 minutes
DEFAULT_RANK_TYPES = ("turnoverRatio", "rvol10d", "range", "volume")
EST = pytz.timezone("US/Eastern")

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure a basic console logger if the application has not already configured logging."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


def within_market_hours(now: datetime) -> bool:
    est_now = now.astimezone(EST)
    t = est_now.time()
    return time(9, 30) <= t <= time(16, 0)


async def top_active(rank_type: str, session: aiohttp.ClientSession) -> Tuple[list, list, str]:
    """
    Retrieve the top active tickers for the specified rank type.

    A shared HTTP session is passed to avoid the overhead of creating a new
    session on each call. The request headers are generated on demand to
    ensure freshness.
    """
    payload = {
        "regionId": 6,
        "rankType": rank_type,
        "pageIndex": 1,
        "pageSize": 50,
        "order": rank_type,
        "direction": -1,
    }
    url = "https://quotes-gw.webullfintech.com/api/wlas/ranking/topActive"
    async with session.post(url, headers=generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN')), json=payload) as resp:
        resp.raise_for_status()
        data = await resp.json()
        data = data.get("data", [])
        ticker = [i.get("ticker") for i in data]
        values = [i.get("values") for i in data]
        return ticker, values, rank_type


async def run_top_active(session: aiohttp.ClientSession, rank_types: Iterable[str]) -> None:
    """
    Fetch and store rankings for multiple rank types concurrently using a
    shared HTTP session. Assumes a database connection has already been
    established.
    """
    tasks = [top_active(rt, session) for rt in rank_types]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            logger.warning("rank fetch failed: %s", result)
            continue
        ticker, values, rank_type = result

        ticker_df = Ticker(ticker).as_dataframe
        values_df = Values(values).as_dataframe

        merged_df = pd.merge(ticker_df, values_df, on="ticker_id")
        merged_df["rank_type"] = rank_type
        merged_df = merged_df.rename(columns={"symbol": "ticker"})
        merged_df["rank_idx"] = range(1, len(merged_df) + 1)

        await db.batch_upsert_dataframe(
            merged_df,
            table_name="active",
            unique_columns=["ticker", "rank_type"],
        )
        logger.info(
            "Upserted %s rows to active (%s)",
            len(merged_df),
            rank_type,
        )

        # Confluence layer: reward top-ranked momentum names
        layer_df = merged_df[["ticker", "rank_idx"]].copy()
        layer_df["points"] = layer_df["rank_idx"].apply(
            lambda r: 3 if r <= 5 else 2 if r <= 15 else 1 if r <= 30 else 0
        )
        layer_df = layer_df[layer_df["points"] > 0]
        if not layer_df.empty:
            layer_df["signal"] = "bullish"
            layer_df["reason"] = layer_df["rank_idx"].apply(
                lambda r: f"{rank_type} rank {r}"
            )
            layer_df["source"] = f"active_{rank_type}"
            layer_df["weight"] = 0.5
            await db.batch_upsert_dataframe(
                layer_df,
                table_name="confluence_layers",
                unique_columns=["ticker", "source"],
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and store Webull top-active rankings.")
    parser.add_argument(
        "--sleep-seconds",
        type=int,
        default=int(os.getenv("ACTIVE_SLEEP_SECONDS", DEFAULT_SLEEP_SECONDS)),
        help="Delay between polling cycles (default: %(default)s seconds)",
    )
    parser.add_argument(
        "--rank-type",
        action="append",
        dest="rank_types",
        help="Specific rank types to request (can be supplied multiple times). Defaults to all.",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run a single fetch cycle instead of looping indefinitely.",
    )
    return parser.parse_args()


async def main_loop(args: argparse.Namespace) -> None:
    """
    Main scheduler loop for fetching the top active rankings. Ensures a
    single database connection and a single aiohttp session are reused
    across iterations, and only runs during market hours.
    """
    rank_types = tuple(args.rank_types) if args.rank_types else DEFAULT_RANK_TYPES
    await db.connect()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                now = datetime.now(EST)
                if within_market_hours(now):
                    logger.info("Running top_active at %s", now.strftime("%Y-%m-%d %I:%M:%S %p EST"))
                    try:
                        await run_top_active(session, rank_types)
                    except Exception:
                        logger.exception("top_active run failed")
                else:
                    logger.info(
                        "Skipping outside market hours: %s",
                        now.strftime("%I:%M:%S %p EST"),
                    )
                if args.run_once:
                    break
                await asyncio.sleep(args.sleep_seconds)
    finally:
        await db.disconnect()


if __name__ == "__main__":
    configure_logging()
    cli_args = parse_args()
    asyncio.run(main_loop(cli_args))
