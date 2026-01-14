#!/usr/bin/env python3
"""
Live rule scanner for candle_analysis_live.

Loads production rules from live_rules.yaml, polls new rows since last_ts_utc,
applies a per-(ticker, rule_id) cooldown, and writes signals/outcomes.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

from fudstop4.apis.polygonio.polygon_options import PolygonOptions


REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = REPO_ROOT / "live_rules.yaml"
STATE_PATH = REPO_ROOT / "logs" / "live_rules_scanner_state.json"

TIMESPAN = os.getenv("LIVE_RULE_TIMESPAN", "m1")
COOLDOWN_MINUTES = int(os.getenv("LIVE_RULE_COOLDOWN_MINUTES", "15"))
POLL_SECONDS = int(os.getenv("LIVE_RULE_POLL_SECONDS", "60"))
DEFAULT_LOOKBACK_MINUTES = int(os.getenv("LIVE_RULE_LOOKBACK_MINUTES", "2"))
TRIGGER_MODE = os.getenv("LIVE_RULE_TRIGGER_MODE", "red_candle")
TRIGGER_WINDOW_MINUTES = int(os.getenv("LIVE_RULE_TRIGGER_WINDOW_MINUTES", "3"))
TRIGGER_ENTRY_PRICE = os.getenv("LIVE_RULE_TRIGGER_ENTRY_PRICE", "close").lower()

OUTCOME_MIN_CANDLES = int(os.getenv("OUTCOME_MIN_CANDLES", "5"))
OUTCOME_MAX_CANDLES = int(os.getenv("OUTCOME_MAX_CANDLES", "10"))
OUTCOME_DELAY_MINUTES = int(
    os.getenv("OUTCOME_DELAY_MINUTES", str(OUTCOME_MAX_CANDLES + 2))
)
OUTCOME_BATCH_LIMIT = int(os.getenv("OUTCOME_BATCH_LIMIT", "250"))


def _coerce_float(value) -> float:
    if value in (None, "--", ""):
        return 0.0
    return float(str(value).replace("%", "").strip())


def _coerce_int(value) -> int:
    if value in (None, "--", ""):
        return 0
    return int(value)


def _coerce_str(value) -> str:
    return "" if value is None else str(value)


class LiveSignals:
    def __init__(self, data: Iterable[dict]):
        rows = list(data)
        self.rule_id = [_coerce_str(i.get("rule_id")) for i in rows]
        self.direction = [_coerce_str(i.get("direction")) for i in rows]
        self.ticker = [_coerce_str(i.get("ticker")) for i in rows]
        self.ts_utc = [i.get("ts_utc") for i in rows]
        self.entry_price = [_coerce_float(i.get("entry_price")) for i in rows]
        self.setup_ts = [i.get("setup_ts") for i in rows]
        self.setup_price = [_coerce_float(i.get("setup_price")) for i in rows]
        self.trigger_label = [_coerce_str(i.get("trigger_label")) for i in rows]

        self.data_dict = {
            "rule_id": self.rule_id,
            "direction": self.direction,
            "ticker": self.ticker,
            "ts_utc": self.ts_utc,
            "entry_price": self.entry_price,
            "setup_ts": self.setup_ts,
            "setup_price": self.setup_price,
            "trigger_label": self.trigger_label,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class LiveSignalOutcomes:
    def __init__(self, data: Iterable[dict]):
        rows = list(data)
        self.rule_id = [_coerce_str(i.get("rule_id")) for i in rows]
        self.direction = [_coerce_str(i.get("direction")) for i in rows]
        self.ticker = [_coerce_str(i.get("ticker")) for i in rows]
        self.ts_utc = [i.get("ts_utc") for i in rows]
        self.entry_price = [_coerce_float(i.get("entry_price")) for i in rows]
        self.max_h = [_coerce_float(i.get("max_h")) for i in rows]
        self.min_l = [_coerce_float(i.get("min_l")) for i in rows]
        self.n_fwd = [_coerce_int(i.get("n_fwd")) for i in rows]
        self.best_signed_ret = [_coerce_float(i.get("best_signed_ret")) for i in rows]
        self.adverse_ret = [_coerce_float(i.get("adverse_ret")) for i in rows]
        self.hit_0 = [bool(i.get("hit_0")) for i in rows]
        self.hit_10bp = [bool(i.get("hit_10bp")) for i in rows]
        self.hit_20bp = [bool(i.get("hit_20bp")) for i in rows]
        self.first_hit_offset = [_coerce_int(i.get("first_hit_offset")) for i in rows]
        self.window_min = [_coerce_int(i.get("window_min")) for i in rows]
        self.window_max = [_coerce_int(i.get("window_max")) for i in rows]

        self.data_dict = {
            "rule_id": self.rule_id,
            "direction": self.direction,
            "ticker": self.ticker,
            "ts_utc": self.ts_utc,
            "entry_price": self.entry_price,
            "max_h": self.max_h,
            "min_l": self.min_l,
            "n_fwd": self.n_fwd,
            "best_signed_ret": self.best_signed_ret,
            "adverse_ret": self.adverse_ret,
            "hit_0": self.hit_0,
            "hit_10bp": self.hit_10bp,
            "hit_20bp": self.hit_20bp,
            "first_hit_offset": self.first_hit_offset,
            "window_min": self.window_min,
            "window_max": self.window_max,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


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


def compile_production_rules() -> List[dict]:
    rules = load_rules_yaml(RULES_PATH)
    rules_by_name = {r["name"]: r for r in rules if r.get("name")}
    production = []

    for rule in rules:
        if rule.get("status") != "production":
            continue
        name = rule.get("name")
        if not name:
            continue
        side = rule.get("side", "")
        conditions = resolve_conditions(name, rules_by_name)
        if not conditions:
            continue
        production.append(
            {
                "name": name,
                "side": side,
                "conditions": conditions,
            }
        )
    return production


def build_rules_query(rules: List[dict]) -> str:
    union_parts = []
    for rule in rules:
        cond_sql = " AND ".join(rule["conditions"])
        union_parts.append(
            f"""SELECT
  ticker,
  ts_utc,
  c AS setup_price,
  '{rule['side']}'::text AS direction,
  '{rule['name']}'::text AS rule_id
FROM new_rows
WHERE {cond_sql}"""
        )

    union_sql = "\nUNION ALL\n".join(union_parts)
    return f"""
WITH new_rows AS (
  SELECT *
  FROM candle_analysis_live
  WHERE timespan = '{TIMESPAN}'
    AND ts_utc > $1
  ORDER BY ts_utc ASC
)
{union_sql}
ORDER BY ts_utc ASC;
"""


def build_new_rows_query() -> str:
    return f"""
SELECT
  ticker,
  ts_utc,
  o,
  c,
  h,
  l,
  upper_band,
  lower_band
FROM candle_analysis_live
WHERE timespan = '{TIMESPAN}'
  AND ts_utc > $1
ORDER BY ts_utc ASC;
"""


def load_state(path: Path) -> datetime:
    if not path.exists():
        return datetime.now(timezone.utc) - timedelta(minutes=DEFAULT_LOOKBACK_MINUTES)
    try:
        payload = json.loads(path.read_text())
        ts = payload.get("last_ts_utc")
        if not ts:
            return datetime.now(timezone.utc) - timedelta(minutes=DEFAULT_LOOKBACK_MINUTES)
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc) - timedelta(minutes=DEFAULT_LOOKBACK_MINUTES)


def save_state(path: Path, last_ts: datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"last_ts_utc": last_ts.isoformat()}
    path.write_text(json.dumps(payload, indent=2))


def should_fire(
    last_fired: Dict[Tuple[str, str], datetime],
    *,
    ticker: str,
    rule_name: str,
    ts_utc: datetime,
) -> bool:
    key = (ticker, rule_name)
    if key not in last_fired:
        last_fired[key] = ts_utc
        return True
    last_ts = last_fired[key]
    if ts_utc - last_ts >= timedelta(minutes=COOLDOWN_MINUTES):
        last_fired[key] = ts_utc
        return True
    return False


def _entry_price_from_row(row: dict) -> float:
    if TRIGGER_ENTRY_PRICE == "open":
        return _coerce_float(row.get("o"))
    return _coerce_float(row.get("c"))


def trigger_matches(row: dict, *, direction: str, prev_row: dict | None) -> Tuple[bool, str]:
    if TRIGGER_MODE == "red_candle":
        o = _coerce_float(row.get("o"))
        c = _coerce_float(row.get("c"))
        if direction == "bearish" and c < o:
            return True, "red_candle"
        if direction == "bullish" and c > o:
            return True, "green_candle"
        return False, ""

    if TRIGGER_MODE == "break_low" and prev_row:
        low = _coerce_float(row.get("l"))
        high = _coerce_float(row.get("h"))
        prev_low = _coerce_float(prev_row.get("l"))
        prev_high = _coerce_float(prev_row.get("h"))
        if direction == "bearish" and low < prev_low:
            return True, "break_low"
        if direction == "bullish" and high > prev_high:
            return True, "break_high"
        return False, ""

    if TRIGGER_MODE == "close_inside_band":
        close = _coerce_float(row.get("c"))
        upper = _coerce_float(row.get("upper_band"))
        lower = _coerce_float(row.get("lower_band"))
        if direction == "bearish" and close < upper:
            return True, "close_inside_upper"
        if direction == "bullish" and close > lower:
            return True, "close_inside_lower"
        return False, ""

    return False, ""


async def fetch_latest_ts(db: PolygonOptions, last_ts: datetime) -> datetime | None:
    sql = f"""
    SELECT max(ts_utc) AS max_ts
    FROM candle_analysis_live
    WHERE timespan = '{TIMESPAN}'
      AND ts_utc > $1;
    """
    return await db.fetchval(sql, last_ts)


def build_outcome_query() -> str:
    offset = OUTCOME_MIN_CANDLES - 1
    limit = OUTCOME_MAX_CANDLES - OUTCOME_MIN_CANDLES + 1
    return f"""
WITH pending AS (
  SELECT
    s.rule_id,
    s.ticker,
    s.ts_utc,
    s.direction,
    s.entry_price
  FROM live_signals s
  LEFT JOIN live_signal_outcomes o
    ON o.rule_id = s.rule_id
   AND o.ticker = s.ticker
   AND o.ts_utc = s.ts_utc
  WHERE o.rule_id IS NULL
    AND s.ts_utc <= now() - interval '{OUTCOME_DELAY_MINUTES} minutes'
  ORDER BY s.ts_utc ASC
  LIMIT {OUTCOME_BATCH_LIMIT}
)
SELECT
  p.rule_id,
  p.ticker,
  p.ts_utc,
  p.direction,
  p.entry_price,
  f.max_h,
  f.min_l,
  f.n_fwd,
  fh.first_hit_offset
FROM pending p
CROSS JOIN LATERAL (
  SELECT
    max(w.h) AS max_h,
    min(w.l) AS min_l,
    count(*) AS n_fwd
  FROM (
    SELECT f.h, f.l
    FROM candle_analysis f
    WHERE f.timespan = '{TIMESPAN}'
      AND f.ticker = p.ticker
      AND f.ts_utc > p.ts_utc
    ORDER BY f.ts_utc
    OFFSET {offset}
    LIMIT {limit}
  ) w
) f
CROSS JOIN LATERAL (
  SELECT min(idx) AS first_hit_offset
  FROM (
    SELECT
      row_number() OVER (ORDER BY f.ts_utc) AS idx,
      f.h,
      f.l
    FROM candle_analysis f
    WHERE f.timespan = '{TIMESPAN}'
      AND f.ticker = p.ticker
      AND f.ts_utc > p.ts_utc
    ORDER BY f.ts_utc
    LIMIT {OUTCOME_MAX_CANDLES}
  ) w
  WHERE idx BETWEEN {OUTCOME_MIN_CANDLES} AND {OUTCOME_MAX_CANDLES}
    AND (
      (p.direction = 'bullish' AND w.h >= p.entry_price)
      OR (p.direction = 'bearish' AND w.l <= p.entry_price)
    )
) fh;
"""


def build_outcome_rows(rows: Iterable[dict]) -> List[dict]:
    window_count = OUTCOME_MAX_CANDLES - OUTCOME_MIN_CANDLES + 1
    outcomes: List[dict] = []

    for row in rows:
        entry = row.get("entry_price")
        max_h = row.get("max_h")
        min_l = row.get("min_l")
        n_fwd = row.get("n_fwd")
        if not entry or not max_h or not min_l or n_fwd != window_count:
            continue

        direction = row.get("direction")
        entry_f = float(entry)
        max_h_f = float(max_h)
        min_l_f = float(min_l)

        if direction == "bearish":
            best_signed_ret = (entry_f / min_l_f) - 1.0 if min_l_f else 0.0
            adverse_ret = (max_h_f / entry_f) - 1.0 if entry_f else 0.0
        else:
            best_signed_ret = (max_h_f / entry_f) - 1.0 if entry_f else 0.0
            adverse_ret = (entry_f / min_l_f) - 1.0 if min_l_f else 0.0

        outcomes.append(
            {
                "rule_id": row.get("rule_id"),
                "direction": direction,
                "ticker": row.get("ticker"),
                "ts_utc": row.get("ts_utc"),
                "entry_price": entry_f,
                "max_h": max_h_f,
                "min_l": min_l_f,
                "n_fwd": int(n_fwd),
                "best_signed_ret": best_signed_ret,
                "adverse_ret": adverse_ret,
                "hit_0": best_signed_ret >= 0.0,
                "hit_10bp": best_signed_ret >= 0.001,
                "hit_20bp": best_signed_ret >= 0.002,
                "first_hit_offset": row.get("first_hit_offset") or 0,
                "window_min": OUTCOME_MIN_CANDLES,
                "window_max": OUTCOME_MAX_CANDLES,
            }
        )

    return outcomes


async def scan_forever() -> None:
    logger = logging.getLogger("live_rules_scanner")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    production_rules = compile_production_rules()
    if not production_rules:
        logger.warning("No production rules found in %s", RULES_PATH)
        return

    rules_query = build_rules_query(production_rules)
    rows_query = build_new_rows_query()
    rules_mtime = RULES_PATH.stat().st_mtime if RULES_PATH.exists() else 0.0
    last_ts = load_state(STATE_PATH)

    last_fired: Dict[Tuple[str, str], datetime] = {}
    watchlist: Dict[Tuple[str, str], dict] = {}
    prev_rows: Dict[str, dict] = {}
    db = PolygonOptions()
    await db.connect()

    try:
        while True:
            if RULES_PATH.exists():
                mtime = RULES_PATH.stat().st_mtime
                if mtime != rules_mtime:
                    production_rules = compile_production_rules()
                    if production_rules:
                        rules_query = build_rules_query(production_rules)
                        rules_mtime = mtime
                        logger.info("Reloaded production rules (%d)", len(production_rules))
            setup_rows = await db.fetch_new(rules_query, last_ts)
            new_rows = await db.fetch_new(rows_query, last_ts)
            setups_by_key: Dict[Tuple[str, datetime], List[dict]] = {}
            for record in setup_rows:
                row = dict(record)
                ticker = row.get("ticker")
                ts_utc = row.get("ts_utc")
                if not ticker or not ts_utc:
                    continue
                if ts_utc.tzinfo is None:
                    ts_utc = ts_utc.replace(tzinfo=timezone.utc)
                setups_by_key.setdefault((ticker, ts_utc), []).append(row)

            signals: List[dict] = []
            max_seen = last_ts
            now_ts = datetime.now(timezone.utc)

            for record in new_rows:
                row = dict(record)
                ticker = row.get("ticker")
                ts_utc = row.get("ts_utc")
                if ticker is None or ts_utc is None:
                    continue
                if ts_utc.tzinfo is None:
                    ts_utc = ts_utc.replace(tzinfo=timezone.utc)
                if ts_utc > max_seen:
                    max_seen = ts_utc

                for setup in setups_by_key.get((ticker, ts_utc), []):
                    rule_id = setup.get("rule_id")
                    if not rule_id:
                        continue
                    watchlist[(ticker, rule_id)] = {
                        "setup_ts": ts_utc,
                        "setup_price": _coerce_float(setup.get("setup_price")),
                        "direction": setup.get("direction"),
                        "expires_at": ts_utc + timedelta(minutes=TRIGGER_WINDOW_MINUTES),
                    }

                expired = [
                    key for key, item in watchlist.items()
                    if item.get("expires_at") and ts_utc > item["expires_at"]
                ]
                for key in expired:
                    watchlist.pop(key, None)

                for (wl_ticker, wl_rule), item in list(watchlist.items()):
                    if wl_ticker != ticker:
                        continue
                    setup_ts = item.get("setup_ts")
                    if not setup_ts or ts_utc <= setup_ts:
                        continue
                    if ts_utc > item.get("expires_at", now_ts):
                        continue
                    direction = item.get("direction") or ""
                    prev_row = prev_rows.get(ticker)
                    matched, label = trigger_matches(
                        row, direction=direction, prev_row=prev_row
                    )
                    if not matched:
                        continue
                    if not should_fire(
                        last_fired,
                        ticker=ticker,
                        rule_name=wl_rule,
                        ts_utc=ts_utc,
                    ):
                        continue
                    entry_price = _entry_price_from_row(row)
                    signals.append(
                        {
                            "rule_id": wl_rule,
                            "direction": direction,
                            "ticker": ticker,
                            "ts_utc": ts_utc,
                            "entry_price": entry_price,
                            "setup_ts": setup_ts,
                            "setup_price": item.get("setup_price"),
                            "trigger_label": label,
                        }
                    )
                    watchlist.pop((wl_ticker, wl_rule), None)

                prev_rows[ticker] = row

            if signals:
                model = LiveSignals(signals)
                await db.batch_upsert_dataframe(
                    model.as_dataframe,
                    table_name="live_signals",
                    unique_columns=["rule_id", "ticker", "ts_utc"],
                )
                logger.info("signals_written=%d", len(signals))

            outcomes_rows = await db.fetch_new(build_outcome_query())
            outcomes = build_outcome_rows(dict(r) for r in outcomes_rows)
            if outcomes:
                model = LiveSignalOutcomes(outcomes)
                await db.batch_upsert_dataframe(
                    model.as_dataframe,
                    table_name="live_signal_outcomes",
                    unique_columns=["rule_id", "ticker", "ts_utc"],
                )
                logger.info("outcomes_written=%d", len(outcomes))

            latest_ts = await fetch_latest_ts(db, last_ts)
            if latest_ts and latest_ts > max_seen:
                max_seen = latest_ts

            if max_seen > last_ts:
                last_ts = max_seen
                save_state(STATE_PATH, last_ts)

            await asyncio.sleep(POLL_SECONDS)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(scan_forever())
