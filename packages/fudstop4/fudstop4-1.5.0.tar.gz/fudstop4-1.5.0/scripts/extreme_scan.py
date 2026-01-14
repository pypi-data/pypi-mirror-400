#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from itertools import combinations
from pathlib import Path
from typing import Iterable, List, Tuple

import pandas as pd

from fudstop4.apis.polygonio.polygon_options import PolygonOptions


@dataclass(frozen=True)
class Addon:
    label: str
    where: str


@dataclass(frozen=True)
class Rule:
    name: str
    side: str
    where: str


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for k, v in raw.items():
        try:
            out[k] = datetime.fromisoformat(v)
        except Exception:
            continue
    return out


def _save_state(path: Path, state: dict) -> None:
    tmp = {k: v.isoformat() for k, v in state.items()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tmp, indent=2, sort_keys=True), encoding="utf-8")


def _build_rules(
    *,
    side: str,
    bases: List[Tuple[str, str]],
    addons: List[Addon],
    max_k: int,
    max_rules: int,
) -> List[Rule]:
    rules: List[Rule] = []
    for base_label, base_where in bases:
        rules.append(Rule(name=base_label, side=side, where=base_where))
        for k in range(1, max_k + 1):
            for combo in combinations(addons, k):
                addon_label = "__".join(a.label for a in combo)
                rule_name = f"{base_label}__{addon_label}"
                clause = base_where + " AND " + " AND ".join(a.where for a in combo)
                rules.append(Rule(name=rule_name, side=side, where=clause))
                if len(rules) >= max_rules:
                    return rules
    return rules


def _wrap_select(rule: Rule, per_rule_limit: int, ts_col: str) -> str:
    cols = [
        f"'{rule.name}'::text AS rule_name",
        f"'{rule.side}'::text AS side",
        "ticker",
        f"{ts_col} AS ts_utc",
        "rsi",
        "td_buy_count",
        "td_sell_count",
        "bb_width",
        "stoch_k",
        "mfi",
        "williams_r",
        "rvol",
        "vwap_dist_pct",
        "candle_green",
        "candle_red",
    ]
    return (
        "SELECT * FROM (\n"
        f"  SELECT {', '.join(cols)}\n"
        "  FROM recent\n"
        f"  WHERE {rule.where}\n"
        f"  ORDER BY {ts_col} DESC\n"
        f"  LIMIT {per_rule_limit}\n"
        ") s"
    )


def _build_union_query(
    *,
    timespan: str,
    lookback_minutes: int,
    lag_minutes: int,
    rules: Iterable[Rule],
    per_rule_limit: int,
    ts_col: str,
) -> str:
    cte = (
        "WITH recent AS (\n"
        "  SELECT *\n"
        "  FROM candle_analysis\n"
        f"  WHERE timespan = '{timespan}'\n"
        f"    AND {ts_col} >= (now() - interval '{lookback_minutes} minutes')\n"
        f"    AND {ts_col} <= (now() - interval '{lag_minutes} minutes')\n"
        ")\n"
    )
    selects = [_wrap_select(rule, per_rule_limit, ts_col) for rule in rules]
    if not selects:
        return cte + "SELECT NULL WHERE FALSE;"
    return cte + "\nUNION ALL\n".join(selects) + "\nORDER BY ts_utc DESC;"


async def _resolve_ts_column(db: PolygonOptions, table_name: str) -> str:
    query = (
        "SELECT column_name\n"
        "FROM information_schema.columns\n"
        "WHERE table_name = $1\n"
        "  AND column_name IN ('ts_utc', 'ts')\n"
        "ORDER BY CASE WHEN column_name = 'ts_utc' THEN 0 ELSE 1 END\n"
        "LIMIT 1"
    )
    rows = await db.fetch_new(query, table_name)
    if rows:
        return rows[0]["column_name"]
    return "ts_utc"


async def _run_scan(args) -> pd.DataFrame:
    db = PolygonOptions()
    await db.connect()
    try:
        bull_bases = [
            ("bull_rsi20_td15", "rsi <= 20 AND td_buy_count >= 15"),
            ("bull_rsi20_td20", "rsi <= 20 AND td_buy_count >= 20"),
        ]
        bear_bases = [
            ("bear_rsi75_td15", "rsi >= 75 AND td_sell_count >= 15"),
            ("bear_rsi80_td20", "rsi >= 80 AND td_sell_count >= 20"),
        ]

        bull_addons = [
            Addon("bb_width_0_03", "bb_width >= 0.03"),
            Addon("bb_width_0_04", "bb_width >= 0.04"),
            Addon("bb_close_outside", "c < lower_band"),
            Addon("bb_wick_outside", "l < lower_band"),
            Addon("bb_full_outside", "candle_completely_below_lower IS TRUE"),
            Addon("stoch_le_20", "stoch_k <= 20"),
            Addon("mfi_le_20", "mfi <= 20"),
            Addon("willr_le_-80", "williams_r <= -80"),
            Addon("rvol_ge_1_5", "rvol >= 1.5"),
            Addon("rvol_ge_2_0", "rvol >= 2.0"),
            Addon("vwap_ext_le_-0_20", "vwap_dist_pct <= -0.20"),
            Addon("vwap_ext_le_-0_35", "vwap_dist_pct <= -0.35"),
            Addon("ema_stack_bull", "ema_stack_bull IS TRUE"),
            Addon("macd_cross_up", "macd_cross_up IS TRUE"),
            Addon("tsi_cross_up", "tsi_cross_up IS TRUE"),
            Addon("candle_green", "candle_green IS TRUE"),
            Addon("volume_confirm", "volume_confirm IS TRUE"),
            Addon("momentum_confirm_bull", "momentum_confirm_bull IS TRUE"),
            Addon("pattern_bull", "(is_hammer IS TRUE OR bullish_engulfing IS TRUE OR is_doji IS TRUE)"),
        ]

        bear_addons = [
            Addon("bb_width_0_03", "bb_width >= 0.03"),
            Addon("bb_width_0_04", "bb_width >= 0.04"),
            Addon("bb_close_outside", "c > upper_band"),
            Addon("bb_wick_outside", "h > upper_band"),
            Addon("bb_full_outside", "candle_completely_above_upper IS TRUE"),
            Addon("stoch_ge_80", "stoch_k >= 80"),
            Addon("mfi_ge_80", "mfi >= 80"),
            Addon("willr_ge_-20", "williams_r >= -20"),
            Addon("rvol_ge_1_5", "rvol >= 1.5"),
            Addon("rvol_ge_2_0", "rvol >= 2.0"),
            Addon("vwap_ext_ge_0_20", "vwap_dist_pct >= 0.20"),
            Addon("vwap_ext_ge_0_35", "vwap_dist_pct >= 0.35"),
            Addon("ema_stack_bear", "ema_stack_bear IS TRUE"),
            Addon("macd_cross_dn", "macd_cross_dn IS TRUE"),
            Addon("tsi_cross_dn", "tsi_cross_dn IS TRUE"),
            Addon("candle_red", "candle_red IS TRUE"),
            Addon("volume_confirm", "volume_confirm IS TRUE"),
            Addon("momentum_confirm_bear", "momentum_confirm_bear IS TRUE"),
            Addon("pattern_bear", "(is_shooting_star IS TRUE OR bearish_engulfing IS TRUE OR is_doji IS TRUE)"),
        ]

        bull_rules = _build_rules(
            side="bullish",
            bases=bull_bases,
            addons=bull_addons,
            max_k=args.max_k,
            max_rules=args.max_rules_per_side,
        )
        bear_rules = _build_rules(
            side="bearish",
            bases=bear_bases,
            addons=bear_addons,
            max_k=args.max_k,
            max_rules=args.max_rules_per_side,
        )
        rules = bull_rules + bear_rules

        ts_col = await _resolve_ts_column(db, "candle_analysis")
        sql = _build_union_query(
            timespan=args.timespan,
            lookback_minutes=args.lookback_minutes,
            lag_minutes=args.lag_minutes,
            rules=rules,
            per_rule_limit=args.per_rule_limit,
            ts_col=ts_col,
        )

        if args.dump_sql:
            print(sql)
            return pd.DataFrame()

        rows = await db.fetch_new(sql)
        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows, columns=rows[0].keys())
        return df
    finally:
        await db.disconnect()


def _apply_dedupe(df: pd.DataFrame, state_path: Path, cooldown_minutes: int) -> pd.DataFrame:
    if df.empty:
        return df
    if cooldown_minutes <= 0:
        return df

    state = _load_state(state_path)
    cooldown = timedelta(minutes=cooldown_minutes)
    kept_rows = []

    for row in df.to_dict(orient="records"):
        key = f"{row.get('rule_name')}|{row.get('ticker')}"
        ts = row.get("ts_utc")
        if not isinstance(ts, datetime):
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        last = state.get(key)
        if last and last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        if last and ts <= (last + cooldown):
            continue
        kept_rows.append(row)
        state[key] = ts

    _save_state(state_path, state)
    return pd.DataFrame(kept_rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Scan candle_analysis for extreme setups (recent minutes).")
    ap.add_argument("--timespan", default=os.getenv("TIMESPAN", "m1"))
    ap.add_argument("--lookback-minutes", type=int, default=int(os.getenv("LOOKBACK_MINUTES", "60")))
    ap.add_argument("--lag-minutes", type=int, default=int(os.getenv("LAG_MINUTES", "1")))
    ap.add_argument("--max-k", type=int, default=int(os.getenv("MAX_K", "2")))
    ap.add_argument("--max-rules-per-side", type=int, default=int(os.getenv("MAX_RULES_PER_SIDE", "80")))
    ap.add_argument("--per-rule-limit", type=int, default=int(os.getenv("PER_RULE_LIMIT", "50")))
    ap.add_argument("--cooldown-minutes", type=int, default=int(os.getenv("COOLDOWN_MINUTES", "15")))
    ap.add_argument("--state-path", default=os.getenv("STATE_PATH", "logs/extreme_scan_state.json"))
    ap.add_argument("--dump-sql", action="store_true")
    args = ap.parse_args()

    df = asyncio.run(_run_scan(args))
    if df.empty:
        print("No matches found.")
        return

    state_path = Path(args.state_path)
    df = _apply_dedupe(df, state_path, args.cooldown_minutes)
    if df.empty:
        print("Matches found, but all within cooldown.")
        return

    df = df.sort_values(["ts_utc", "rule_name"], ascending=[False, True])

    summary = (
        df.groupby(["rule_name", "side"])
        .agg(n_hits=("ticker", "count"), tickers=("ticker", "nunique"), last_ts=("ts_utc", "max"))
        .reset_index()
        .sort_values(["n_hits", "last_ts"], ascending=[False, False])
    )

    print("\n=== Summary ===")
    print(summary.to_string(index=False))

    print("\n=== Latest Signals ===")
    print(df.head(200).to_string(index=False))


if __name__ == "__main__":
    main()
