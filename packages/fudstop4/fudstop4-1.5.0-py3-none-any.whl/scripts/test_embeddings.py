"""Smoke tests for the embed builders.

Run this to push one embed for each feed to the configured webhooks.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

project_dir = Path(__file__).resolve().parents[1]
if str(project_dir) not in sys.path:
    sys.path.append(str(project_dir))

maybe_fudstop_pkg = project_dir.parent / "fudstop"
if maybe_fudstop_pkg.exists() and str(maybe_fudstop_pkg) not in sys.path:
    sys.path.append(str(maybe_fudstop_pkg))

from fudstop4.apis.polygonio.polygon_options import PolygonOptions  # noqa: E402

from scripts.embeddings import (  # noqa: E402
    HOOKS,
    send_active_embed,
    send_alert_embed,
    send_info_embed,
    send_volume_analysis_embed,
    send_volume_summary_embed,
)


async def _pick_ticker(db_client: PolygonOptions, table: str, column: str = "ticker", order_by: Optional[str] = "insertion_timestamp") -> Optional[str]:
    await db_client.connect()
    order_clause = f" ORDER BY {order_by} DESC" if order_by else ""
    rows = await db_client.fetch(
        f"SELECT {column} FROM {table} WHERE {column} IS NOT NULL{order_clause} LIMIT 1"
    )
    if not rows:
        return None
    row = rows[0]
    return row.get(column) or (row[column] if isinstance(row, dict) else None)


async def main() -> None:
    load_dotenv()
    db_client = PolygonOptions()

    info_ticker = await _pick_ticker(db_client, "info")
    volume_summary_ticker = await _pick_ticker(db_client, "volume_summary")
    volume_analysis_ticker = await _pick_ticker(db_client, "volume_analysis")

    tasks = []
    if info_ticker:
        print(f"[test] sending info embed for {info_ticker}")
        tasks.append(send_info_embed(info_ticker, db_client=db_client))
    else:
        print("[test] no info ticker found")

    print("[test] sending active embed (turnoverratio)")
    tasks.append(send_active_embed("turnoverRatio", 5, hook_override=HOOKS.active, db_client=db_client))

    if volume_summary_ticker:
        print(f"[test] sending volume summary embed for {volume_summary_ticker}")
        tasks.append(send_volume_summary_embed(volume_summary_ticker, hook_override=HOOKS.volume_summary, db_client=db_client))
    else:
        print("[test] no volume summary ticker found")

    if volume_analysis_ticker:
        print(f"[test] sending volume analysis embed for {volume_analysis_ticker}")
        tasks.append(send_volume_analysis_embed(volume_analysis_ticker, hook_override=HOOKS.volume_analysis, db_client=db_client))
    else:
        print("[test] no volume analysis ticker found")

    print("[test] sending sample alert embed")
    tasks.append(
        send_alert_embed(
            "TEST",
            "Large Volume (Rising)",
            volume=12345,
            hook_override=os.environ.get("large_volume_rising") or HOOKS.alerts,
        )
    )

    if tasks:
        await asyncio.gather(*tasks)
    else:
        print("[test] nothing to send")


if __name__ == "__main__":
    asyncio.run(main())
