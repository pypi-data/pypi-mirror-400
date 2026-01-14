from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4.apis.polygonio.polygon_options import PolygonOptions


@dataclass
class SourceDef:
    name: str
    query: str
    weight: float = 1.0


SOURCES: List[SourceDef] = [
    SourceDef(
        name="plays",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   timespan,
                   confluence_score AS points,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY ticker, timespan ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM plays
            WHERE confluence_score IS NOT NULL
        )
        SELECT ticker,
               timespan,
               'plays' AS source,
               points,
               CASE WHEN points > 0 THEN 'bullish'
                    WHEN points < 0 THEN 'bearish'
                    ELSE 'neutral' END AS signal,
               'TD/RSI/MACD blend' AS reason,
               insertion_timestamp AS asof
        FROM ranked
        WHERE rn = 1;
        """,
        weight=1.2,
    ),
    SourceDef(
        name="cp_profiles",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   strike,
                   cp_flow_points,
                   cp_flow_reason,
                   last_timestamp::timestamptz AS last_ts,
                   ROW_NUMBER() OVER (PARTITION BY ticker, strike ORDER BY last_timestamp DESC NULLS LAST) AS rn
            FROM cp_profiles
            WHERE cp_flow_points IS NOT NULL
        ),
        agg AS (
            SELECT ticker,
                   AVG(cp_flow_points)::float AS points,
                   STRING_AGG(DISTINCT LEFT(COALESCE(cp_flow_reason, ''), 120), ' | ') AS reason,
                   MAX(last_ts) AS asof
            FROM ranked
            WHERE rn = 1
            GROUP BY ticker
        )
        SELECT ticker,
               NULL::text AS timespan,
               'cp_profiles' AS source,
               points,
               CASE WHEN points > 0 THEN 'bullish'
                    WHEN points < 0 THEN 'bearish'
                    ELSE 'neutral' END AS signal,
               reason,
               asof
        FROM agg;
        """,
        weight=1.0,
    ),
    SourceDef(
        name="atm_options",
        query="""
        WITH ranked AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY option_id ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM atm_options
            WHERE atm_flow_points IS NOT NULL
        ),
        agg AS (
            SELECT ticker,
                   AVG(atm_flow_points)::float AS points,
                   STRING_AGG(DISTINCT LEFT(COALESCE(atm_flow_reason, ''), 120), ' | ') AS reason,
                   MAX(insertion_timestamp) AS asof
            FROM ranked
            WHERE rn = 1
            GROUP BY ticker
        )
        SELECT ticker,
               NULL::text AS timespan,
               'atm_options' AS source,
               points,
               CASE WHEN points > 0 THEN 'bullish'
                    WHEN points < 0 THEN 'bearish'
                    ELSE 'neutral' END AS signal,
               reason,
               asof
        FROM agg;
        """,
        weight=1.0,
    ),
    SourceDef(
        name="wb_opts",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   option_id,
                   options_flow_points,
                   options_flow_reason,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY option_id ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM wb_opts
            WHERE options_flow_points IS NOT NULL
        ),
        agg AS (
            SELECT ticker,
                   AVG(options_flow_points)::float AS points,
                   STRING_AGG(DISTINCT LEFT(COALESCE(options_flow_reason, ''), 120), ' | ') AS reason,
                   MAX(insertion_timestamp) AS asof
            FROM ranked
            WHERE rn = 1
            GROUP BY ticker
        )
        SELECT ticker,
               NULL::text AS timespan,
               'wb_opts' AS source,
               points,
               CASE WHEN points > 0 THEN 'bullish'
                    WHEN points < 0 THEN 'bearish'
                    ELSE 'neutral' END AS signal,
               reason,
               asof
        FROM agg;
        """,
        weight=1.0,
    ),
    SourceDef(
        name="wb_trades",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   option_id,
                   trade_flow_points,
                   trade_flow_reason,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY option_id ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM wb_trades
            WHERE trade_flow_points IS NOT NULL
        ),
        agg AS (
            SELECT ticker,
                   AVG(trade_flow_points)::float AS points,
                   STRING_AGG(DISTINCT LEFT(COALESCE(trade_flow_reason, ''), 120), ' | ') AS reason,
                   MAX(insertion_timestamp) AS asof
            FROM ranked
            WHERE rn = 1
            GROUP BY ticker
        )
        SELECT ticker,
               NULL::text AS timespan,
               'wb_trades' AS source,
               points,
               CASE WHEN points > 0 THEN 'bullish'
                    WHEN points < 0 THEN 'bearish'
                    ELSE 'neutral' END AS signal,
               reason,
               asof
        FROM agg;
        """,
        weight=1.0,
    ),
    SourceDef(
        name="gex",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   gex_points AS points,
                   gex_signal AS signal,
                   gex_reason AS reason,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM gex
            WHERE gex_points IS NOT NULL
        )
        SELECT ticker,
               NULL::text AS timespan,
               'gex' AS source,
               points,
               signal,
               reason,
               insertion_timestamp AS asof
        FROM ranked
        WHERE rn = 1;
        """,
        weight=1.0,
    ),
    SourceDef(
        name="iv_skew",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   skew_points AS points,
                   skew_signal AS signal,
                   skew_reason AS reason,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM iv_skew
            WHERE skew_points IS NOT NULL
        )
        SELECT ticker,
               NULL::text AS timespan,
               'iv_skew' AS source,
               points,
               signal,
               reason,
               insertion_timestamp AS asof
        FROM ranked
        WHERE rn = 1;
        """,
        weight=0.9,
    ),
    SourceDef(
        name="volume_analysis",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   volume_points AS points,
                   volume_signal AS signal,
                   volume_reason AS reason,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM volume_analysis
            WHERE volume_points IS NOT NULL
        )
        SELECT ticker,
               NULL::text AS timespan,
               'volume_analysis' AS source,
               points,
               signal,
               reason,
               insertion_timestamp AS asof
        FROM ranked
        WHERE rn = 1;
        """,
        weight=0.8,
    ),
    SourceDef(
        name="cost_distribution",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   cost_points AS points,
                   cost_signal AS signal,
                   cost_reason AS reason,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM cost_distribution
            WHERE cost_points IS NOT NULL
        )
        SELECT ticker,
               NULL::text AS timespan,
               'cost_distribution' AS source,
               points,
               signal,
               reason,
               insertion_timestamp AS asof
        FROM ranked
        WHERE rn = 1;
        """,
        weight=0.7,
    ),
    SourceDef(
        name="multi_quote",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   quote_points AS points,
                   quote_signal AS signal,
                   quote_reason AS reason,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM multi_quote
            WHERE quote_points IS NOT NULL
        )
        SELECT ticker,
               NULL::text AS timespan,
               'multi_quote' AS source,
               points,
               signal,
               reason,
               insertion_timestamp AS asof
        FROM ranked
        WHERE rn = 1;
        """,
        weight=0.8,
    ),
    SourceDef(
        name="price_target",
        query="""
        WITH ranked AS (
            SELECT ticker,
                   price_target_points AS points,
                   price_target_signal AS signal,
                   price_target_reason AS reason,
                   insertion_timestamp,
                   ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY insertion_timestamp DESC NULLS LAST) AS rn
            FROM yf_pt
            WHERE price_target_points IS NOT NULL
        )
        SELECT ticker,
               NULL::text AS timespan,
               'price_target' AS source,
               points,
               signal,
               reason,
               insertion_timestamp AS asof
        FROM ranked
        WHERE rn = 1;
        """,
        weight=0.6,
    ),
]


db = PolygonOptions()


async def fetch_source(source: SourceDef) -> pd.DataFrame:
    rows = await db.fetch(source.query)
    if not rows:
        return pd.DataFrame(columns=["ticker", "timespan", "source", "points", "signal", "reason", "asof"])
    df = pd.DataFrame(rows)
    df["source"] = source.name  # enforce naming consistency
    df["weight"] = source.weight
    return df


async def build_detail() -> pd.DataFrame:
    frames = await asyncio.gather(*[fetch_source(src) for src in SOURCES])
    frames = [f for f in frames if not f.empty]
    if not frames:
        return pd.DataFrame(columns=["ticker", "timespan", "source", "points", "signal", "reason", "asof", "weight"])
    detail = pd.concat(frames, ignore_index=True)
    detail["points"] = pd.to_numeric(detail["points"], errors="coerce").fillna(0.0)
    detail["weight"] = pd.to_numeric(detail["weight"], errors="coerce").fillna(1.0)
    detail["weighted_points"] = detail["points"] * detail["weight"]
    detail["asof"] = pd.to_datetime(detail["asof"], errors="coerce")
    detail["timespan"] = detail["timespan"].fillna("")
    detail["reason"] = detail["reason"].fillna("")
    detail["signal"] = detail["signal"].fillna("neutral")
    detail["abs_weighted_points"] = detail["weighted_points"].abs()
    return detail


def build_summary(detail: pd.DataFrame) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame(columns=["ticker", "total_points", "combined_signal", "last_asof", "contributions", "source_breakdown"])

    summary = (
        detail.groupby("ticker")
        .agg(
            total_points=("weighted_points", "sum"),
            last_asof=("asof", "max"),
            contributions=("source", "count"),
        )
        .reset_index()
    )
    summary["combined_signal"] = summary["total_points"].apply(
        lambda val: "bullish" if val > 0 else ("bearish" if val < 0 else "neutral")
    )

    detail_sorted = detail.sort_values(["ticker", "abs_weighted_points"], ascending=[True, False])
    breakdown = (
        detail_sorted.assign(source_points=lambda df: df.apply(lambda row: f"{row['source']}:{row['weighted_points']:+.2f}", axis=1))
        .groupby("ticker")["source_points"]
        .apply(lambda values: ", ".join(values.tolist()))
        .reset_index(name="source_breakdown")
    )
    summary = summary.merge(breakdown, on="ticker", how="left")
    summary["run_ts"] = pd.Timestamp.utcnow()
    return summary


async def persist(detail: pd.DataFrame, summary: pd.DataFrame) -> None:
    if not detail.empty:
        await db.batch_upsert_dataframe(
            detail.drop(columns=["abs_weighted_points"]),
            table_name="confluence_signals",
            unique_columns=["ticker", "source", "timespan"],
        )
    if not summary.empty:
        await db.batch_upsert_dataframe(
            summary,
            table_name="confluence_master",
            unique_columns=["ticker"],
        )


async def main():
    await db.connect()
    try:
        detail = await build_detail()
        summary = build_summary(detail)
        await persist(detail, summary)
        if summary.empty:
            print("[!] No confluence data aggregated.")
        else:
            print(summary.sort_values("total_points", ascending=False).head(25))
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
