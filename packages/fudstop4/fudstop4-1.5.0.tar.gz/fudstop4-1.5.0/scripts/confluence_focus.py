from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pandas as pd

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4.apis.polygonio.polygon_options import PolygonOptions


GEX_QUERY = """
WITH ranked AS (
    SELECT ticker,
           gex_points,
           gex_signal,
           gex_reason,
           insertion_timestamp,
           ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
    FROM gex
    WHERE gex_points IS NOT NULL
)
SELECT ticker,
       gex_points,
       gex_signal,
       gex_reason,
       insertion_timestamp AS gex_asof
FROM ranked
WHERE rn = 1;
"""

IV_SKEW_QUERY = """
WITH ranked AS (
    SELECT ticker,
           skew_points,
           skew_signal,
           skew_reason,
           expiry,
           insertion_timestamp,
           ROW_NUMBER() OVER (
               PARTITION BY ticker
               ORDER BY expiry ASC NULLS LAST, insertion_timestamp DESC NULLS LAST
           ) AS rn
    FROM iv_skew
    WHERE skew_points IS NOT NULL
)
SELECT ticker,
       skew_points,
       skew_signal,
       skew_reason,
       expiry AS skew_expiry,
       insertion_timestamp AS skew_asof
FROM ranked
WHERE rn = 1;
"""

ATM_QUERY = """
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY option_id ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
    FROM atm_options
    WHERE atm_flow_points IS NOT NULL
),
per_ticker AS (
    SELECT ticker,
           AVG(atm_flow_points)::float AS atm_points,
           COUNT(*) AS atm_sample,
           STRING_AGG(DISTINCT LEFT(atm_flow_reason, 120), ' | ') AS atm_reason,
           MAX(insertion_timestamp) AS atm_asof
    FROM ranked
    WHERE rn = 1
    GROUP BY ticker
)
SELECT ticker,
       atm_points,
       CASE
           WHEN atm_points > 0 THEN 'bullish'
           WHEN atm_points < 0 THEN 'bearish'
           ELSE 'neutral'
       END AS atm_signal,
       atm_reason,
       atm_sample,
       atm_asof
FROM per_ticker;
"""

PRICE_TARGET_QUERY = """
WITH ranked AS (
    SELECT ticker,
           price_target_points,
           price_target_signal,
           price_target_reason,
           insertion_timestamp,
           ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
    FROM yf_pt
    WHERE price_target_points IS NOT NULL
)
SELECT ticker,
       price_target_points,
       price_target_signal,
       price_target_reason,
       insertion_timestamp AS price_target_asof
FROM ranked
WHERE rn = 1;
"""


db = PolygonOptions()


async def fetch_df(query: str) -> pd.DataFrame:
    rows = await db.fetch(query)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def merge_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for frame in frames:
        if frame.empty:
            continue
        merged = frame if merged is None else merged.merge(frame, on="ticker", how="outer")
    return merged if merged is not None else pd.DataFrame()


async def build_confluence() -> pd.DataFrame:
    gex_df, iv_df, atm_df, pt_df = await asyncio.gather(
        fetch_df(GEX_QUERY),
        fetch_df(IV_SKEW_QUERY),
        fetch_df(ATM_QUERY),
        fetch_df(PRICE_TARGET_QUERY),
    )

    merged = merge_frames([gex_df, iv_df, atm_df, pt_df])
    if merged.empty:
        return merged

    point_cols = [
        col for col in merged.columns
        if col.endswith("_points") or col in {"gex_points", "skew_points", "atm_points", "price_target_points"}
    ]
    merged[point_cols] = merged[point_cols].fillna(0.0)
    merged["total_points"] = merged[point_cols].sum(axis=1)
    merged["combined_signal"] = merged["total_points"].apply(
        lambda val: "bullish" if val > 0 else ("bearish" if val < 0 else "neutral")
    )
    merged["asof"] = pd.Timestamp.utcnow()
    return merged.sort_values("total_points", ascending=False)


async def persist(df: pd.DataFrame) -> None:
    if df.empty:
        print("[!] No confluence data to persist")
        return
    await db.batch_upsert_dataframe(
        df,
        table_name="confluence_focus",
        unique_columns=["ticker"],
    )
    print(f"[+] Upserted {len(df)} confluence rows")


async def main():
    await db.connect()
    try:
        df = await build_confluence()
        if df.empty:
            print("[!] Combined dataframe empty; nothing to do")
            return
        await persist(df)
        print(df[["ticker", "total_points", "combined_signal"]].head(20))
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
