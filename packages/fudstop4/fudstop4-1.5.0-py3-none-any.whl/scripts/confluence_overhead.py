#!/usr/bin/env python3
"""
Overhead confluence aggregator.

Pulls signals from legacy pipelines (analysts, earnings, volume/cost,
options monitor, info/volatility, gaps, ITM dollars) plus derived
financial health scores (balance sheet + cash flow + income statement)
and produces a ranked summary table.

Outputs:
  - confluence_overhead_detail: per-ticker, per-source weighted points
  - confluence_overhead: per-ticker total score and combined signal
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from UTILS.confluence import (
    score_analyst_ratings,
    score_earnings_setup,
    score_financial_health,
    score_gap_profile,
    score_itm_balance,
    score_options_flow,
    score_volatility_profile,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("confluence_overhead")


db = PolygonOptions()


def _is_number(val: Any) -> bool:
    return isinstance(val, (int, float)) and pd.notnull(val)


def _safe_ratio(numer: Optional[float], denom: Optional[float]) -> Optional[float]:
    if not _is_number(numer) or not _is_number(denom) or float(denom) == 0:
        return None
    return float(numer) / float(denom)


def _pct_diff(new: Optional[float], old: Optional[float]) -> Optional[float]:
    if not _is_number(new) or not _is_number(old) or float(old) == 0:
        return None
    return ((float(new) - float(old)) / float(old)) * 100.0


async def safe_fetch(query: str) -> List[Dict[str, Any]]:
    try:
        return await db.fetch(query)
    except Exception as e:
        logger.warning("Query failed: %s | %s", query.splitlines()[0], e)
        return []


def _detail_frame(df: pd.DataFrame,
                  source: Optional[str],
                  weight: Optional[float]) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    if source:
        df["source"] = source
    if "source" not in df.columns:
        df["source"] = "external"
    if weight is not None:
        df["weight"] = weight
    if "weight" not in df.columns:
        df["weight"] = 1.0
    if "points" not in df.columns:
        df["points"] = 0.0
    if "signal" not in df.columns:
        df["signal"] = "neutral"
    if "reason" not in df.columns:
        df["reason"] = ""
    df["asof"] = pd.to_datetime(df.get("asof", pd.Timestamp.utcnow()), errors="coerce")
    return df[["ticker", "source", "points", "signal", "reason", "asof", "weight"]]


async def build_volume() -> pd.DataFrame:
    rows = await safe_fetch(
        "SELECT ticker, volume_points AS points, volume_signal AS signal, volume_reason AS reason, insertion_timestamp AS asof "
        "FROM volume_analysis"
    )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df.rename(columns={
        "volume_points": "points",
        "volume_signal": "signal",
        "volume_reason": "reason",
    }, inplace=True)
    return _detail_frame(df, source="volume_analysis", weight=0.7)


async def build_cost() -> pd.DataFrame:
    rows = await safe_fetch(
        "SELECT ticker, cost_points AS points, cost_signal AS signal, cost_reason AS reason, insertion_timestamp AS asof "
        "FROM cost_distribution"
    )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df.rename(columns={
        "cost_points": "points",
        "cost_signal": "signal",
        "cost_reason": "reason",
    }, inplace=True)
    return _detail_frame(df, source="cost_distribution", weight=0.7)


async def build_analysts() -> pd.DataFrame:
    rows = await safe_fetch(
        "SELECT ticker, strong_buy, buy, hold, underperform, sell, "
        "analyst_points, analyst_signal, analyst_reason, analyst_asof AS asof "
        "FROM analysts"
    )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "analyst_points" not in df.columns:
        df["analyst_points"] = pd.NA
    if "analyst_signal" not in df.columns:
        df["analyst_signal"] = pd.NA
    if "analyst_reason" not in df.columns:
        df["analyst_reason"] = pd.NA

    scored = []
    for _, row in df.iterrows():
        if pd.notnull(row.get("analyst_points")):
            points = row.get("analyst_points")
            signal = row.get("analyst_signal", "neutral")
            reason = row.get("analyst_reason", "")
        else:
            res = score_analyst_ratings(
                row.get("strong_buy"), row.get("buy"),
                row.get("hold"), row.get("underperform"), row.get("sell")
            )
            points, signal, reason = res.points, res.signal, res.reason
        scored.append({
            "ticker": row.get("ticker"),
            "points": points,
            "signal": signal,
            "reason": reason,
            "asof": row.get("asof") or pd.Timestamp.utcnow(),
        })
    return _detail_frame(pd.DataFrame(scored), source="analysts", weight=0.8)


async def build_earnings() -> pd.DataFrame:
    rows = await safe_fetch(
        "SELECT ticker, eps_estimate, eps_last, revenue_estimate, revenue_last, "
        "earnings_points, earnings_signal, earnings_reason, start_date AS asof "
        "FROM earnings_soon"
    )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    records = []
    for _, row in df.iterrows():
        if pd.notnull(row.get("earnings_points")):
            points = row.get("earnings_points")
            signal = row.get("earnings_signal", "neutral")
            reason = row.get("earnings_reason", "")
        else:
            res = score_earnings_setup(
                row.get("eps_estimate"),
                row.get("eps_last"),
                row.get("revenue_estimate"),
                row.get("revenue_last"),
            )
            points, signal, reason = res.points, res.signal, res.reason
        records.append({
            "ticker": row.get("ticker"),
            "points": points,
            "signal": signal,
            "reason": reason,
            "asof": row.get("asof") or pd.Timestamp.utcnow(),
        })
    return _detail_frame(pd.DataFrame(records), source="earnings", weight=0.8)


async def build_options_monitor() -> pd.DataFrame:
    rows = await safe_fetch(
        "SELECT ticker, "
        "SUM(COALESCE(call_volume, 0)) AS call_volume, "
        "SUM(COALESCE(put_volume, 0)) AS put_volume, "
        "SUM(COALESCE(call_openinterest_eod, 0)) AS call_oi, "
        "SUM(COALESCE(put_openinterest_eod, 0)) AS put_oi "
        "FROM options_monitor "
        "GROUP BY ticker"
    )
    if not rows:
        return pd.DataFrame()
    records = []
    for row in rows:
        res = score_options_flow(
            row.get("call_volume"), row.get("put_volume"),
            row.get("call_oi"), row.get("put_oi"),
            label="options_monitor",
        )
        records.append({
            "ticker": row.get("ticker"),
            "points": res.points,
            "signal": res.signal,
            "reason": res.reason,
            "asof": pd.Timestamp.utcnow(),
        })
    return _detail_frame(pd.DataFrame(records), source="options_monitor", weight=0.9)


async def build_info() -> pd.DataFrame:
    rows = await safe_fetch(
        "SELECT ticker, info_points, info_signal, info_reason, asof "
        "FROM info_signals"
    )
    if not rows:
        rows = await safe_fetch(
            "SELECT ticker, volatile_rank, call_vol, put_vol "
            "FROM info"
        )
        records = []
        for row in rows:
            res = score_volatility_profile(row.get("volatile_rank"), row.get("call_vol"), row.get("put_vol"))
            records.append({
                "ticker": row.get("ticker"),
                "points": res.points,
                "signal": res.signal,
                "reason": res.reason,
                "asof": pd.Timestamp.utcnow(),
            })
        return _detail_frame(pd.DataFrame(records), source="info", weight=0.6)

    df = pd.DataFrame(rows)
    df.rename(columns={
        "info_points": "points",
        "info_signal": "signal",
        "info_reason": "reason",
    }, inplace=True)
    return _detail_frame(df, source="info", weight=0.6)


async def build_itm() -> pd.DataFrame:
    rows = await safe_fetch(
        "SELECT ticker, itm_points, itm_signal, itm_reason, asof "
        "FROM itm_dollars_summary"
    )
    if not rows:
        rows = await safe_fetch(
            "SELECT ticker, "
            "SUM(CASE WHEN call_put = 'call' THEN total_itm_dollars ELSE 0 END) AS call_itm, "
            "SUM(CASE WHEN call_put = 'put' THEN total_itm_dollars ELSE 0 END) AS put_itm "
            "FROM itm_dollars "
            "GROUP BY ticker"
        )
        records = []
        for row in rows:
            res = score_itm_balance(row.get("call_itm"), row.get("put_itm"))
            records.append({
                "ticker": row.get("ticker"),
                "points": res.points,
                "signal": res.signal,
                "reason": res.reason,
                "asof": pd.Timestamp.utcnow(),
            })
        return _detail_frame(pd.DataFrame(records), source="itm_balance", weight=0.7)

    df = pd.DataFrame(rows)
    df.rename(columns={
        "itm_points": "points",
        "itm_signal": "signal",
        "itm_reason": "reason",
    }, inplace=True)
    return _detail_frame(df, source="itm_balance", weight=0.7)


async def build_gaps() -> pd.DataFrame:
    rows = await safe_fetch(
        "SELECT ticker, timespan, type, gap_low_pct, gap_high_pct, from_ts, to_ts "
        "FROM gaps"
    )
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    if df.empty or "ticker" not in df.columns:
        return pd.DataFrame()
    for col in ["gap_low_pct", "gap_high_pct"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    def nearest_levels(gdf: pd.DataFrame) -> Dict[str, Any]:
        rec: Dict[str, Any] = {"ticker": gdf["ticker"].iloc[0]}
        # nearest_pct = boundary (low/high) closest to spot, preserves sign
        nearest_pct = gdf.apply(
            lambda r: min(
                [v for v in (r.get("gap_low_pct"), r.get("gap_high_pct")) if pd.notnull(v)],
                key=lambda x: abs(x),
                default=None,
            ),
            axis=1,
        )
        gdf = gdf.assign(nearest_pct=nearest_pct)
        support = gdf[gdf["nearest_pct"] < 0]
        resistance = gdf[gdf["nearest_pct"] > 0]

        support_pct = support["nearest_pct"].max() if not support.empty else None
        resistance_pct = resistance["nearest_pct"].min() if not resistance.empty else None

        rec["support_pct"] = support_pct
        rec["resistance_pct"] = resistance_pct

        points = 0
        reasons: list[str] = []
        if pd.notnull(support_pct):
            if abs(support_pct) <= 2:
                points += 2
                reasons.append(f"support gap {support_pct:+.2f}% from price")
            elif abs(support_pct) <= 5:
                points += 1
                reasons.append(f"support gap {support_pct:+.2f}%")
            else:
                reasons.append(f"support gap {support_pct:+.2f}% (far)")
        if pd.notnull(resistance_pct):
            if resistance_pct <= 2:
                points -= 2
                reasons.append(f"resistance gap {resistance_pct:+.2f}% from price")
            elif resistance_pct <= 5:
                points -= 1
                reasons.append(f"resistance gap {resistance_pct:+.2f}%")
            else:
                reasons.append(f"resistance gap {resistance_pct:+.2f}% (far)")

        rec["points"] = points
        rec["signal"] = "bullish" if points > 0 else "bearish" if points < 0 else "neutral"
        rec["reason"] = "; ".join(reasons) if reasons else "no nearby gaps"
        rec["asof"] = pd.Timestamp.utcnow()
        return rec

    records = [nearest_levels(g) for _, g in df.groupby("ticker")]
    return _detail_frame(pd.DataFrame(records), source="gaps", weight=0.6)


async def build_external_layers() -> pd.DataFrame:
    """
    Generic passthrough builder. Any script can upsert standardized rows into
    `confluence_layers` (ticker, source, points, signal, reason, asof, weight)
    and they will automatically flow into the overhead summary.
    """
    rows = await safe_fetch(
        "SELECT ticker, source, points, signal, reason, asof, weight "
        "FROM confluence_layers"
    )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["points"] = pd.to_numeric(df.get("points"), errors="coerce").fillna(0.0)
    df["weight"] = pd.to_numeric(df.get("weight"), errors="coerce").fillna(1.0)
    df["signal"] = df.get("signal", "neutral").fillna("neutral")
    df["reason"] = df.get("reason", "").fillna("")
    df["asof"] = pd.to_datetime(df.get("asof"), errors="coerce")
    return _detail_frame(df, source=None, weight=None)


async def build_financials() -> pd.DataFrame:
    bs_rows = await safe_fetch(
        "SELECT * FROM ("
        "  SELECT ticker, total_current_assets, total_current_liabilities, total_debt, total_equity, end_date, "
        "         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY fiscal_year DESC, fiscal_period DESC, end_date DESC NULLS LAST) AS rn "
        "  FROM balance_sheet"
        ") t WHERE rn = 1"
    )
    cf_rows = await safe_fetch(
        "SELECT * FROM ("
        "  SELECT ticker, cash_from_operating_activities, capital_expenditures, end_date, "
        "         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY fiscal_year DESC, fiscal_period DESC, end_date DESC NULLS LAST) AS rn "
        "  FROM cash_flow"
        ") t WHERE rn = 1"
    )
    inc_rows = await safe_fetch(
        "SELECT * FROM ("
        "  SELECT ticker, total_revenue, net_income, end_date, "
        "         LAG(total_revenue) OVER (PARTITION BY ticker ORDER BY fiscal_year DESC, fiscal_period DESC, end_date DESC NULLS LAST) AS prev_revenue, "
        "         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY fiscal_year DESC, fiscal_period DESC, end_date DESC NULLS LAST) AS rn "
        "  FROM income_statement"
        ") t WHERE rn = 1"
    )

    bs_map = {row["ticker"]: row for row in bs_rows if row.get("ticker")}
    cf_map = {row["ticker"]: row for row in cf_rows if row.get("ticker")}
    inc_map = {row["ticker"]: row for row in inc_rows if row.get("ticker")}

    tickers = set(bs_map) | set(cf_map) | set(inc_map)
    records: List[Dict[str, Any]] = []
    for ticker in tickers:
        bs = bs_map.get(ticker, {})
        cf = cf_map.get(ticker, {})
        inc = inc_map.get(ticker, {})

        current_ratio = _safe_ratio(bs.get("total_current_assets"), bs.get("total_current_liabilities"))
        debt_to_equity = _safe_ratio(bs.get("total_debt"), bs.get("total_equity"))

        ocf = cf.get("cash_from_operating_activities")
        capex = cf.get("capital_expenditures")
        fcf = None
        if _is_number(ocf):
            fcf = float(ocf) - abs(float(capex or 0))

        revenue = inc.get("total_revenue")
        prev_revenue = inc.get("prev_revenue")
        revenue_growth = _pct_diff(revenue, prev_revenue)
        net_income = inc.get("net_income")
        net_margin = None
        if _is_number(net_income) and _is_number(revenue) and float(revenue) != 0:
            net_margin = (float(net_income) / float(revenue)) * 100.0
        fcf_margin = None
        if _is_number(fcf) and _is_number(revenue) and float(revenue) != 0:
            fcf_margin = (float(fcf) / float(revenue)) * 100.0

        score = score_financial_health(current_ratio, debt_to_equity, fcf_margin, revenue_growth, net_margin)
        records.append({
            "ticker": ticker,
            "points": score.points,
            "signal": score.signal,
            "reason": score.reason,
            "asof": bs.get("end_date") or inc.get("end_date") or cf.get("end_date") or pd.Timestamp.utcnow(),
        })

    return _detail_frame(pd.DataFrame(records), source="financials", weight=1.2)


async def build_detail() -> pd.DataFrame:
    builders = [
        build_volume,
        build_cost,
        build_analysts,
        build_options_monitor,
        build_info,
        build_earnings,
        build_financials,
        build_itm,
        build_gaps,
        build_external_layers,
    ]
    frames = []
    for fn in builders:
        try:
            frames.append(await fn())
        except Exception as e:
            logger.warning("Builder %s failed: %s", fn.__name__, e)
    frames = [f for f in frames if f is not None and not f.empty]
    if not frames:
        return pd.DataFrame(columns=["ticker", "source", "points", "signal", "reason", "asof", "weight", "weighted_points"])
    detail = pd.concat(frames, ignore_index=True)
    detail["points"] = pd.to_numeric(detail["points"], errors="coerce").fillna(0.0)
    detail["weight"] = pd.to_numeric(detail["weight"], errors="coerce").fillna(1.0)
    detail["weighted_points"] = detail["points"] * detail["weight"]
    detail["signal"] = detail["signal"].fillna("neutral")
    detail["reason"] = detail["reason"].fillna("")
    detail["asof"] = pd.to_datetime(detail["asof"], errors="coerce")
    detail["timespan"] = ""  # reserved for future intraday conditions
    return detail


def build_summary(detail: pd.DataFrame) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame(columns=["ticker", "total_points", "combined_signal", "last_asof", "contributions", "run_ts"])
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
    summary["run_ts"] = pd.Timestamp.utcnow()
    return summary


async def persist(detail: pd.DataFrame, summary: pd.DataFrame) -> None:
    if not detail.empty:
        detail = detail.copy()
        detail["asof"] = detail["asof"].astype(str)
        await db.batch_upsert_dataframe(
            detail,
            table_name="confluence_overhead_detail",
            unique_columns=["ticker", "source"],
        )
    if not summary.empty:
        summary = summary.copy()
        summary["last_asof"] = summary["last_asof"].astype(str)
        summary["run_ts"] = summary["run_ts"].astype(str)
        await db.batch_upsert_dataframe(
            summary,
            table_name="confluence_overhead",
            unique_columns=["ticker"],
        )


async def main() -> None:
    await db.connect()
    try:
        detail = await build_detail()
        summary = build_summary(detail)
        await persist(detail, summary)
        if summary.empty:
            logger.info("No confluence data produced.")
        else:
            top = summary.sort_values("total_points", ascending=False).head(25)
            logger.info("Top confluence:\n%s", top[["ticker", "total_points", "combined_signal"]])
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
