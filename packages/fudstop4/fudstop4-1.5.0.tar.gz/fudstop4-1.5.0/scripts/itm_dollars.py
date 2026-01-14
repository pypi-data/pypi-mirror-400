#!/usr/bin/env python3
"""
Compute the total in-the-money (ITM) dollar value for options on a list of tickers.

This version adds structured logging, CLI flags for batch size and sleep duration,
and optional one-shot execution for testing. Database connections are managed
at the process level so individual computations remain side-effect free.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import pandas as pd

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4.apis.polygonio.polygon_options import PolygonOptions  # noqa: E402
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers  # noqa: E402
from UTILS.confluence import score_itm_balance  # noqa: E402

db = PolygonOptions()

DEFAULT_BATCH_SIZE = 5
DEFAULT_SLEEP_SECONDS = 120

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


def build_itm_query(ticker: str) -> str:
    """Construct the ITM dollars SQL query for a given ticker."""
    safe_ticker = ticker.replace("'", "''")
    return (
        "WITH nearest_expiry AS ("
        " SELECT MIN(expiry::date) AS expiry"
        " FROM wb_opts"
        f" WHERE ticker = '{safe_ticker}'"
        "   AND expiry::date >= CURRENT_DATE"
        ")"
        " SELECT"
        "     o.ticker,"
        "     o.expiry,"
        "     o.call_put,"
        "     o.strike,"
        "     SUM(o.oi) AS total_oi,"
        "     ROUND("
        "         GREATEST("
        "             CASE"
        "                 WHEN o.call_put = 'call' THEN MAX(p.c) - o.strike"
        "                 WHEN o.call_put = 'put'  THEN o.strike - MAX(p.c)"
        "                 ELSE 0"
        "             END,"
        "             0"
        "         )::numeric, 2"
        "     ) AS intrinsic_value,"
        "     ROUND("
        "         ("
        "             GREATEST("
        "                 CASE"
        "                     WHEN o.call_put = 'call' THEN MAX(p.c) - o.strike"
        "                     WHEN o.call_put = 'put'  THEN o.strike - MAX(p.c)"
        "                     ELSE 0"
        "                 END,"
        "                 0"
        "             ) * SUM(o.oi) * 100"
        "         )::numeric, 2"
        "     ) AS total_itm_dollars"
        " FROM wb_opts o"
        " JOIN plays p ON o.ticker = p.ticker"
        " JOIN nearest_expiry ne ON o.expiry::date = ne.expiry"
        " WHERE o.oi IS NOT NULL"
        f"   AND o.ticker = '{safe_ticker}'"
        "   AND ("
        "     (o.call_put = 'call' AND p.c > o.strike) OR"
        "     (o.call_put = 'put' AND p.c < o.strike)"
        "   )"
        " GROUP BY o.ticker, o.expiry, o.call_put, o.strike"
        " ORDER BY total_itm_dollars DESC;"
    )


async def compute_itm_dollars(ticker: str) -> None:
    """Compute and store the in-the-money dollar value for a single ticker."""
    query = build_itm_query(ticker)
    results = await db.fetch(query)
    if not results:
        logger.debug("No ITM rows returned for %s", ticker)
        return

    df = pd.DataFrame(
        results,
        columns=[
            "ticker",
            "expiry",
            "call_put",
            "strike",
            "total_oi",
            "intrinsic_value",
            "total_itm_dollars",
        ],
    )

    safe_ticker = ticker.replace("'", "''")
    price_query = f"SELECT c FROM plays WHERE ticker = '{safe_ticker}'"
    price_results = await db.fetch(price_query)
    price = price_results[0].get("c") if price_results else None

    df["total_oi"] = pd.to_numeric(df["total_oi"], errors="coerce").fillna(0)
    df["intrinsic_value"] = pd.to_numeric(df["intrinsic_value"], errors="coerce").fillna(0)
    df["total_itm_dollars"] = pd.to_numeric(df["total_itm_dollars"], errors="coerce").fillna(0)
    df["price"] = price
    if "expiry" in df.columns:
        df["expiry"] = df["expiry"].astype(str)

    await db.batch_upsert_dataframe(
        df,
        table_name="itm_dollars",
        unique_columns=["ticker", "expiry", "call_put", "strike"],
    )

    try:
        totals = df.groupby("call_put")["total_itm_dollars"].sum()
        call_itm = float(totals.get("call", 0.0))
        put_itm = float(totals.get("put", 0.0))
        score = score_itm_balance(call_itm, put_itm)
        summary_df = pd.DataFrame(
            [
                {
                    "ticker": ticker,
                    "call_itm_dollars": call_itm,
                    "put_itm_dollars": put_itm,
                    **score.to_columns("itm"),
                    "confluence_score": score.points,
                }
            ]
        )
        await db.batch_upsert_dataframe(
            summary_df,
            table_name="itm_dollars_summary",
            unique_columns=["ticker"],
        )
        # Confluence layer: capture ITM balance tilt
        layer_df = pd.DataFrame(
            [
                {
                    "ticker": ticker,
                    "source": "itm_balance",
                    "points": score.points,
                    "signal": score.signal,
                    "reason": score.reason,
                    "weight": 0.8,
                }
            ]
        )
        await db.batch_upsert_dataframe(
            layer_df,
            table_name="confluence_layers",
            unique_columns=["ticker", "source"],
        )
        logger.info(
            "Updated ITM dollars for %s (call: %s, put: %s)",
            ticker,
            f"{call_itm:,.0f}",
            f"{put_itm:,.0f}",
        )
    except Exception as exc:
        logger.warning("Failed to score ITM balance for %s: %s", ticker, exc)


async def run_itm_dollars(
    tickers: list[str],
    batch_size: int = DEFAULT_BATCH_SIZE,
    sleep_seconds: int = DEFAULT_SLEEP_SECONDS,
    run_once: bool = False,
) -> None:
    """
    Main loop for computing ITM dollars on a list of tickers.
    """
    await db.connect()
    try:
        while True:
            for i in range(0, len(tickers), batch_size):
                batch = tickers[i : i + batch_size]
                tasks = [compute_itm_dollars(ticker) for ticker in batch]
                await asyncio.gather(*tasks)
            if run_once:
                break
            logger.info("ITM dollars sleeping for %s seconds", sleep_seconds)
            await asyncio.sleep(sleep_seconds)
    finally:
        await db.disconnect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute ITM dollar values for options.")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Tickers to process concurrently (default: %(default)s).",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=int,
        default=DEFAULT_SLEEP_SECONDS,
        help="Seconds to sleep between full iterations (default: %(default)s).",
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run a single pass then exit.",
    )
    parser.add_argument(
        "--ticker",
        action="append",
        dest="tickers",
        help="Optional tickers to process (can be provided multiple times). Defaults to most_active_tickers.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    asyncio.run(
        run_itm_dollars(
            tickers=args.tickers or list(most_active_tickers),
            batch_size=args.batch_size,
            sleep_seconds=args.sleep_seconds,
            run_once=args.run_once,
        )
    )
