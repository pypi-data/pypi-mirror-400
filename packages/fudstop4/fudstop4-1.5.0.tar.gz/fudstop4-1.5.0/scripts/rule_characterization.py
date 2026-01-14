#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import asyncio
from pathlib import Path
from typing import Dict, List

import pandas as pd

from fudstop4.apis.polygonio.polygon_options import PolygonOptions

DEFAULT_SEED_TABLE = os.getenv("SEED_TABLE", "public.ca_seed_td_rsi_rev_5_10")



REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = REPO_ROOT / "live_rules.yaml"


def _strip_quotes(value: str) -> str:
    val = value.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        return val[1:-1]
    return val


def load_rules_yaml(path: Path) -> List[dict]:
    rules: List[dict] = []
    current: dict | None = None
    in_conditions = False

    for raw_line in path.read_text().splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "rules:":
            continue
        if stripped.startswith("- name:"):
            name = stripped.split(":", 1)[1].strip()
            current = {"name": _strip_quotes(name), "conditions": []}
            rules.append(current)
            in_conditions = False
            continue
        if current is None:
            continue
        if stripped.startswith("conditions:"):
            in_conditions = True
            continue
        if in_conditions and stripped.startswith("- "):
            current["conditions"].append(_strip_quotes(stripped[2:].strip()))
            continue
        if ":" in stripped and not stripped.startswith("- "):
            key, val = stripped.split(":", 1)
            current[key.strip()] = _strip_quotes(val.strip())
            in_conditions = False

    return rules


def resolve_conditions(
    rule_name: str,
    rules_by_name: Dict[str, dict],
    stack: List[str] | None = None,
) -> List[str]:
    stack = list(stack or [])
    if rule_name in stack:
        raise ValueError(f"Circular rule reference: {' -> '.join(stack + [rule_name])}")
    stack.append(rule_name)

    rule = rules_by_name.get(rule_name)
    if not rule:
        return []

    resolved: List[str] = []
    for cond in rule.get("conditions", []):
        if cond in rules_by_name:
            resolved.extend(resolve_conditions(cond, rules_by_name, stack))
        else:
            resolved.append(cond)
    return resolved


def compile_rules(status: str | None, include_all: bool) -> List[dict]:
    rules = load_rules_yaml(RULES_PATH)
    rules_by_name = {r["name"]: r for r in rules if r.get("name")}
    compiled: List[dict] = []

    for rule in rules:
        if not include_all and status and rule.get("status") != status:
            continue
        name = rule.get("name")
        if not name:
            continue
        side = rule.get("side", "")
        conditions = resolve_conditions(name, rules_by_name)
        if not conditions:
            continue
        compiled.append(
            {
                "name": name,
                "side": side,
                "conditions": conditions,
            }
        )
    return compiled


def build_entries_cte(
    *,
    rules: List[dict],
    val_window: str,
    entry_mode: str,
    trigger_window_minutes: int,
    entry_price: str,
    timespan: str,
    seed_table: str = DEFAULT_SEED_TABLE,
) -> str:
    union_parts = []
    for rule in rules:
        cond_sql = " AND ".join(rule["conditions"])
        union_parts.append(
            f"""SELECT
  '{rule['name']}'::text AS rule_id,
  '{rule['side']}'::text AS rule_direction,
  b.*
FROM base b
WHERE {cond_sql}"""
        )

    union_sql = "\nUNION ALL\n".join(union_parts)
    entry_col = "t.o" if entry_price == "open" else "t.c"
    setup_entry_col = "s.o" if entry_price == "open" else "s.c"

    if entry_mode == "trigger-red":
        entry_sql = f"""
entries AS (
  SELECT
    s.rule_id,
    s.rule_direction,
    s.ticker,
    s.ts_utc AS setup_ts,
    s.c AS setup_price,
    s.is_val,
    t.ts_utc AS entry_ts,
    {entry_col} AS entry_price
  FROM signals s
  JOIN LATERAL (
    SELECT
      f.ts_utc,
      f.o,
      f.c
    FROM candle_analysis f
    WHERE f.timespan = '{timespan}'
      AND f.ticker = s.ticker
      AND f.ts_utc > s.ts_utc
      AND f.ts_utc <= s.ts_utc + interval '{trigger_window_minutes} minutes'
      AND (
        (s.rule_direction = 'bearish' AND f.c < f.o)
        OR (s.rule_direction = 'bullish' AND f.c > f.o)
      )
    ORDER BY f.ts_utc ASC
    LIMIT 1
  ) t ON true
)
"""
    elif entry_mode == "break-low":
        entry_sql = f"""
entries AS (
  SELECT
    s.rule_id,
    s.rule_direction,
    s.ticker,
    s.ts_utc AS setup_ts,
    s.c AS setup_price,
    s.is_val,
    t.ts_utc AS entry_ts,
    {entry_col} AS entry_price
  FROM signals s
  JOIN LATERAL (
    SELECT
      x.ts_utc,
      x.o,
      x.c,
      x.h,
      x.l
    FROM (
      SELECT
        f.ts_utc,
        f.o,
        f.c,
        f.h,
        f.l,
        lag(f.l) OVER (ORDER BY f.ts_utc) AS prev_l,
        lag(f.h) OVER (ORDER BY f.ts_utc) AS prev_h
      FROM candle_analysis f
      WHERE f.timespan = '{timespan}'
        AND f.ticker = s.ticker
        AND f.ts_utc > s.ts_utc
        AND f.ts_utc <= s.ts_utc + interval '{trigger_window_minutes} minutes'
      ORDER BY f.ts_utc ASC
    ) x
    WHERE (
      (s.rule_direction = 'bearish' AND x.prev_l IS NOT NULL AND x.l < x.prev_l)
      OR (s.rule_direction = 'bullish' AND x.prev_h IS NOT NULL AND x.h > x.prev_h)
    )
    ORDER BY x.ts_utc ASC
    LIMIT 1
  ) t ON true
)
"""
    elif entry_mode == "close-inside-band":
        entry_sql = f"""
entries AS (
  SELECT
    s.rule_id,
    s.rule_direction,
    s.ticker,
    s.ts_utc AS setup_ts,
    s.c AS setup_price,
    s.is_val,
    t.ts_utc AS entry_ts,
    {entry_col} AS entry_price
  FROM signals s
  JOIN LATERAL (
    SELECT
      f.ts_utc,
      f.o,
      f.c,
      f.upper_band,
      f.lower_band
    FROM candle_analysis f
    WHERE f.timespan = '{timespan}'
      AND f.ticker = s.ticker
      AND f.ts_utc > s.ts_utc
      AND f.ts_utc <= s.ts_utc + interval '{trigger_window_minutes} minutes'
      AND (
        (s.rule_direction = 'bearish' AND f.c < f.upper_band)
        OR (s.rule_direction = 'bullish' AND f.c > f.lower_band)
      )
    ORDER BY f.ts_utc ASC
    LIMIT 1
  ) t ON true
)
"""
    else:
        entry_sql = f"""
entries AS (
  SELECT
    s.rule_id,
    s.rule_direction,
    s.ticker,
    s.ts_utc AS setup_ts,
    s.c AS setup_price,
    s.is_val,
    s.ts_utc AS entry_ts,
    {setup_entry_col} AS entry_price
  FROM signals s
)
"""

    return f"""
WITH base AS (
  SELECT
    ca.*,
    s.as_of_ts,
    (ca.ts_utc >= s.as_of_ts - interval '{val_window}') AS is_val
  FROM {seed_table} s
  JOIN public.candle_analysis ca
    ON ca.ticker = s.ticker
   AND ca.ts_utc = s.ts_utc
  WHERE ca.timespan = '{timespan}'
),
signals AS (
{union_sql}
),
{entry_sql.rstrip()}
,
"""


def build_characterization_query(
    *,
    rules: List[dict],
    val_window: str,
    window_min: int,
    window_max: int,
    timespan: str,
    entry_mode: str,
    trigger_window_minutes: int,
    entry_price: str,
    seed_table: str = DEFAULT_SEED_TABLE,
) -> str:
    entries_cte = build_entries_cte(
        rules=rules,
        val_window=val_window,
        entry_mode=entry_mode,
        trigger_window_minutes=trigger_window_minutes,
        entry_price=entry_price,
        timespan=timespan,
        seed_table=seed_table,
    )
    offset = window_min - 1
    limit = window_max - window_min + 1

    return f"""
{entries_cte}
fwd AS (
  SELECT
    e.*,
    fw.max_h,
    fw.min_l,
    fw.n_fwd
  FROM entries e
  CROSS JOIN LATERAL (
    SELECT
      max(w.h) AS max_h,
      min(w.l) AS min_l,
      count(*) AS n_fwd
    FROM (
      SELECT f.h, f.l
      FROM candle_analysis f
      WHERE f.timespan = '{timespan}'
        AND f.ticker = e.ticker
        AND f.ts_utc > e.entry_ts
      ORDER BY f.ts_utc
      OFFSET {offset}
      LIMIT {limit}
    ) w
  ) fw
),
scored AS (
  SELECT
    f.*,
    CASE
      WHEN f.rule_direction = 'bearish' THEN (f.entry_price / NULLIF(f.min_l, 0) - 1)
      ELSE (f.max_h / NULLIF(f.entry_price, 0) - 1)
    END AS mfe,
    CASE
      WHEN f.rule_direction = 'bearish' THEN (f.max_h / NULLIF(f.entry_price, 0) - 1)
      ELSE (f.entry_price / NULLIF(f.min_l, 0) - 1)
    END AS mae
  FROM fwd f
  WHERE f.n_fwd = {limit}
),
stats AS (
  SELECT
    rule_id,
    rule_direction AS direction,
    count(*) FILTER (WHERE is_val) AS n_val,
    count(DISTINCT ticker) FILTER (WHERE is_val) AS tickers_val,
    count(DISTINCT date_trunc('day', entry_ts)) FILTER (WHERE is_val) AS distinct_days_val,
    avg((mfe >= 0.0)::int) FILTER (WHERE is_val) AS hit_0,
    avg((mfe >= 0.001)::int) FILTER (WHERE is_val) AS hit_10bp,
    avg((mfe >= 0.002)::int) FILTER (WHERE is_val) AS hit_20bp,
    percentile_cont(0.15) WITHIN GROUP (ORDER BY mfe)
      FILTER (WHERE is_val) AS p15_mfe,
    percentile_cont(0.50) WITHIN GROUP (ORDER BY mae)
      FILTER (WHERE is_val) AS p50_mae,
    percentile_cont(0.85) WITHIN GROUP (ORDER BY mae)
      FILTER (WHERE is_val) AS p85_mae,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY mae)
      FILTER (WHERE is_val) AS p95_mae
  FROM scored
  GROUP BY rule_id, rule_direction
)
SELECT
  *,
  CASE
    WHEN distinct_days_val > 0 THEN n_val::double precision / distinct_days_val
    ELSE NULL
  END AS signals_per_day_val,
  CASE
    WHEN distinct_days_val > 0 AND tickers_val > 0
      THEN n_val::double precision / (distinct_days_val * tickers_val)
    ELSE NULL
  END AS signals_per_day_per_ticker,
  CASE
    WHEN p85_mae > 0 THEN p15_mfe / p85_mae
    ELSE NULL
  END AS p15_mfe_p85_mae_ratio
FROM stats
ORDER BY rule_id;
"""


def build_first_hit_distribution_query(
    *,
    rules: List[dict],
    val_window: str,
    window_min: int,
    window_max: int,
    timespan: str,
    entry_mode: str,
    trigger_window_minutes: int,
    entry_price: str,
) -> str:
    entries_cte = build_entries_cte(
        rules=rules,
        val_window=val_window,
        entry_mode=entry_mode,
        trigger_window_minutes=trigger_window_minutes,
        entry_price=entry_price,
        timespan=timespan,
    )

    return f"""
{entries_cte}
first_hits AS (
  SELECT
    e.rule_id,
    e.rule_direction AS direction,
    e.ticker,
    e.entry_ts,
    e.entry_price,
    fh.first_hit_offset,
    fh.max_idx
  FROM entries e
  CROSS JOIN LATERAL (
    SELECT
      max(idx) AS max_idx,
      min(idx) FILTER (
        WHERE idx BETWEEN {window_min} AND {window_max}
          AND (
            (e.rule_direction = 'bullish' AND w.h >= e.entry_price)
            OR (e.rule_direction = 'bearish' AND w.l <= e.entry_price)
          )
      ) AS first_hit_offset
    FROM (
      SELECT
        row_number() OVER (ORDER BY f.ts_utc) AS idx,
        f.h,
        f.l
      FROM candle_analysis f
      WHERE f.timespan = '{timespan}'
        AND f.ticker = e.ticker
        AND f.ts_utc > e.entry_ts
      ORDER BY f.ts_utc
      LIMIT {window_max}
    ) w
  ) fh
  WHERE e.is_val
    AND fh.max_idx = {window_max}
    AND fh.first_hit_offset IS NOT NULL
),
counts AS (
  SELECT
    rule_id,
    direction,
    first_hit_offset,
    count(*) AS n
  FROM first_hits
  GROUP BY rule_id, direction, first_hit_offset
),
totals AS (
  SELECT
    rule_id,
    direction,
    sum(n) AS total_hits
  FROM counts
  GROUP BY rule_id, direction
)
SELECT
  c.rule_id,
  c.direction,
  c.first_hit_offset,
  c.n,
  (c.n::double precision / NULLIF(t.total_hits, 0)) AS pct
FROM counts c
JOIN totals t
  ON t.rule_id = c.rule_id
 AND t.direction = c.direction
ORDER BY c.rule_id, c.direction, c.first_hit_offset;
"""


async def main() -> None:
    parser = argparse.ArgumentParser(description="Characterize live rules with MAE stats.")
    parser.add_argument(
        "--status",
        default="production",
        help="Only include rules with this status (default: production).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include all rules regardless of status.",
    )
    parser.add_argument(
        "--val-window",
        default="60 days",
        help="Validation window as an interval string (default: 60 days).",
    )
    parser.add_argument(
        "--window-min",
        type=int,
        default=5,
        help="Minimum candle offset for first-hit distribution (default: 5).",
    )
    parser.add_argument(
        "--window-max",
        type=int,
        default=10,
        help="Maximum candle offset for first-hit distribution (default: 10).",
    )
    parser.add_argument(
        "--timespan",
        default="m1",
        help="Timespan used for first-hit distribution (default: m1).",
    )
    parser.add_argument(
        "--entry-mode",
        default="setup",
        choices=["setup", "trigger-red", "break-low", "close-inside-band"],
        help="Entry mode: setup, trigger-red, break-low, close-inside-band (default: setup).",
    )
    parser.add_argument(
        "--trigger-window-minutes",
        type=int,
        default=3,
        help="Trigger window in minutes for trigger-red mode (default: 3).",
    )
    parser.add_argument(
        "--entry-price",
        default="close",
        choices=["open", "close"],
        help="Entry price source (default: close).",
    )
    args = parser.parse_args()

    rules = compile_rules(args.status, args.all)
    if not rules:
        print("No rules found for characterization.")
        return

    sql = build_characterization_query(
        rules=rules,
        val_window=args.val_window,
        window_min=args.window_min,
        window_max=args.window_max,
        timespan=args.timespan,
        entry_mode=args.entry_mode,
        trigger_window_minutes=args.trigger_window_minutes,
        entry_price=args.entry_price,
    )
    db = PolygonOptions()
    await db.connect()
    try:
        rows = await db.fetch_new(sql)
        df = pd.DataFrame([dict(r) for r in rows])
        first_hit_sql = build_first_hit_distribution_query(
            rules=rules,
            val_window=args.val_window,
            window_min=args.window_min,
            window_max=args.window_max,
            timespan=args.timespan,
            entry_mode=args.entry_mode,
            trigger_window_minutes=args.trigger_window_minutes,
            entry_price=args.entry_price,
        )
        first_rows = await db.fetch_new(first_hit_sql)
        first_df = pd.DataFrame([dict(r) for r in first_rows])
    finally:
        await db.close()

    if df.empty:
        print("No characterization rows returned.")
        return

    print("CHARACTERIZATION")
    print(df.to_string(index=False))
    print("")
    print("FIRST_HIT_DISTRIBUTION")
    if first_df.empty:
        print("No first-hit rows returned.")
    else:
        print(first_df.to_string(index=False))


if __name__ == "__main__":
    asyncio.run(main())
