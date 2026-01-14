"""
Fetch option chains for a list of tickers and store them in ``wb_opts``.

This version adds structured logging, safer header generation, and CLI flags
so you can run a single cycle for testing or tune concurrency without
touching the source. Failed tickers no longer abort the batch; they are
logged and the loop keeps going.
"""
import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4.apis.helpers import generate_webull_headers  # noqa: E402
from fudstop4.apis.webull.webull_options.webull_options import WebullOptions  # noqa: E402
from fudstop4.apis.polygonio.polygon_options import PolygonOptions  # noqa: E402
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers  # noqa: E402
from UTILS.confluence import score_options_flow  # noqa: E402

load_dotenv()

opts = WebullOptions()
db = PolygonOptions()

DEFAULT_BATCH_SIZE = 10
DEFAULT_CONCURRENCY = 10
DEFAULT_SLEEP_SECONDS = 60

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


def build_headers() -> dict:
    """Generate Webull headers, including an access token if available."""
    token = os.getenv("ACCESS_TOKEN")
    headers = generate_webull_headers(access_token=token) if token else generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))
    if not token:
        logger.debug("ACCESS_TOKEN not set; using anonymous header generation.")
    return headers


async def process_ticker(
    ticker: str, semaphore: asyncio.Semaphore, headers: dict
) -> None:
    """
    Fetch options for a single ticker and upsert them into the database.

    Parameters
    ----------
    ticker:
        The ticker symbol to process.
    semaphore:
        Concurrency limiter to respect upstream API rate limits.
    headers:
        Precomputed Webull request headers.
    """
    async with semaphore:
        try:
            opts_data = await opts.get_all_options_for_ticker(
                tickers=[ticker], headers=headers
            )
            if not opts_data or ticker not in opts_data:
                logger.debug("No options data returned for %s", ticker)
                return
            df = opts_data[ticker].as_dataframe
            if df.empty:
                logger.debug("Empty options dataframe for %s", ticker)
                return

            if "expiry" in df.columns:
                df["expiry"] = pd.to_datetime(df["expiry"], errors="coerce").dt.date
            if "trade_time" in df.columns:
                df = df.drop(columns=["trade_time"])

            df = df.dropna(subset=["expiry", "option_id"])
            if df.empty:
                logger.debug("No valid options after cleaning for %s", ticker)
                return
            df = df.drop_duplicates(subset=["option_id"])

            call_mask = df["call_put"].astype(str).str.lower() == "call"
            put_mask = df["call_put"].astype(str).str.lower() == "put"
            call_volume = pd.to_numeric(df.loc[call_mask, "volume"], errors="coerce").fillna(0).sum()
            put_volume = pd.to_numeric(df.loc[put_mask, "volume"], errors="coerce").fillna(0).sum()
            call_oi = pd.to_numeric(df.loc[call_mask, "oi"], errors="coerce").fillna(0).sum()
            put_oi = pd.to_numeric(df.loc[put_mask, "oi"], errors="coerce").fillna(0).sum()

            flow_score = score_options_flow(
                call_volume=call_volume,
                put_volume=put_volume,
                call_oi=call_oi,
                put_oi=put_oi,
                label="all_options",
            )
            for col, value in flow_score.to_columns("options_flow").items():
                df[col] = value

            await db.batch_upsert_dataframe(
                df, table_name="wb_opts", unique_columns=["option_id"]
            )
            logger.info(
                "Upserted %s options for %s at %s",
                len(df),
                ticker,
                datetime.now().strftime("%H:%M:%S"),
            )
            # Confluence layer contribution for options flow
            layer_df = pd.DataFrame(
                [
                    {
                        "ticker": ticker,
                        "source": "options_flow_all",
                        "points": flow_score.points,
                        "signal": flow_score.signal,
                        "reason": flow_score.reason,
                        "weight": 1.0,
                    }
                ]
            )
            await db.batch_upsert_dataframe(
                layer_df,
                table_name="confluence_layers",
                unique_columns=["ticker", "source"],
            )
        except Exception as exc:
            logger.warning("[%s] options ingestion failed: %s", ticker, exc)


async def batched_execution(
    tickers: Iterable[str], batch_size: int, max_concurrency: int, headers: dict
) -> None:
    """
    Run ``process_ticker`` over a list of tickers in batches.

    A semaphore is used to ensure that at most ``max_concurrency`` requests
    execute concurrently. The list of tickers is chunked into ``batch_size``
    segments to avoid spawning too many tasks at once.
    """
    semaphore = asyncio.Semaphore(max_concurrency)
    tickers_list = list(tickers)
    for i in range(0, len(tickers_list), batch_size):
        batch = tickers_list[i : i + batch_size]
        tasks = [process_ticker(ticker, semaphore, headers) for ticker in batch]
        await asyncio.gather(*tasks)


async def run_main(
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_concurrency: int = DEFAULT_CONCURRENCY,
    sleep_seconds: int = DEFAULT_SLEEP_SECONDS,
    tickers: Iterable[str] | None = None,
    run_once: bool = False,
) -> None:
    """
    Main loop to continuously fetch and persist options data.

    Parameters
    ----------
    batch_size:
        Number of tickers to process concurrently in a single batch.
    max_concurrency:
        Maximum number of concurrent API calls allowed.
    sleep_seconds:
        Number of seconds to wait between full fetch cycles.
    tickers:
        Iterable of tickers to process; defaults to most_active_tickers.
    run_once:
        When True, execute a single cycle and exit (useful for testing).
    """
    tickers = tickers or most_active_tickers
    await db.connect()
    try:
        while True:
            headers = build_headers()
            await batched_execution(
                tickers,
                batch_size=batch_size,
                max_concurrency=max_concurrency,
                headers=headers,
            )
            if run_once:
                break
            logger.info("Cycle complete. Sleeping for %s seconds.", sleep_seconds)
            await asyncio.sleep(sleep_seconds)
    finally:
        await db.disconnect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Webull options for a set of tickers.")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(os.getenv("ALL_OPTIONS_BATCH_SIZE", DEFAULT_BATCH_SIZE)),
        help="Tickers to launch per batch (default: %(default)s).",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=int(os.getenv("ALL_OPTIONS_CONCURRENCY", DEFAULT_CONCURRENCY)),
        help="Maximum concurrent API calls (default: %(default)s).",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=int,
        default=int(os.getenv("ALL_OPTIONS_SLEEP_SECONDS", DEFAULT_SLEEP_SECONDS)),
        help="Delay between cycles (default: %(default)s).",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run a single cycle then exit.",
    )
    parser.add_argument(
        "--ticker",
        action="append",
        dest="tickers",
        help="Limit ingestion to specific tickers (can be provided multiple times).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    asyncio.run(
        run_main(
            batch_size=args.batch_size,
            max_concurrency=args.concurrency,
            sleep_seconds=args.sleep_seconds,
            tickers=args.tickers,
            run_once=args.run_once,
        )
    )
