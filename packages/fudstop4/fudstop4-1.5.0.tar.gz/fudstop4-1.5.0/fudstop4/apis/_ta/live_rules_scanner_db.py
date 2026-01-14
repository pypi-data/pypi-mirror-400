#!/usr/bin/env python3
"""
live_rules_scanner_db.py

Polls the candle_analysis table for *closed* candles and fires YAML-defined rules.

This is meant to be the "live forward test" layer:
- Your ingest job keeps candle_analysis up to date (with indicators).
- This scanner loads rules from live_rules.yaml (exported by rule_factory).
- It tracks setup -> watchlist -> trigger for each (ticker, rule).
- It inserts entry signals into `reversal_signals` (or your chosen table), with sent_to_discord=false.

Supported entry_mode:
- trigger-red   : after setup, first red candle (c < o) within trigger_minutes triggers entry
- trigger-green : after setup, first green candle (c > o) within trigger_minutes triggers entry
- break-low     : after setup, first candle whose low <= setup_low within trigger_minutes triggers entry
- break-high    : after setup, first candle whose high >= setup_high within trigger_minutes triggers entry
- immediate     : setup candle itself triggers entry (uses entry_price on the setup candle)

Notes
- This scanner intentionally processes candles with a lag (CANDLE_LAG_SECONDS) so we avoid firing on
  a currently-forming 1m candle that Webull may still revise/upsert.
- State persists to JSON so restarts don’t spam duplicates.

Env vars (optional)
- CANDLE_TABLE             default "candle_analysis"
- TIMESPAN                 default "m1"
- LIVE_RULES_PATH          default "live_rules.yaml"
- SIGNALS_TABLE            default "reversal_signals"
- INCLUDE_PENDING          default "false" (only status=production)
- CANDLE_LAG_SECONDS       default "75"
- LOOKBACK_MINUTES         default auto from rules, min 15
- POLL_SECONDS             default "10"
- COOLDOWN_MINUTES         default "10"
- STATE_PATH               default "live_rules_scanner_state.json"
"""

from __future__ import annotations

import argparse
import asyncio
import ast
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

import pandas as pd

from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers


# ───────────────────────── config ─────────────────────────
CANDLE_TABLE = os.getenv("CANDLE_TABLE", "candle_analysis")
TIMESPAN = os.getenv("TIMESPAN", "m1")

LIVE_RULES_PATH = Path(os.getenv("LIVE_RULES_PATH", "live_rules.yaml"))
SIGNALS_TABLE = os.getenv("SIGNALS_TABLE", "reversal_signals")

INCLUDE_PENDING = os.getenv("INCLUDE_PENDING", "false").lower() in ("1", "true", "yes")
CANDLE_LAG_SECONDS = int(os.getenv("CANDLE_LAG_SECONDS", "75"))
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "10"))

COOLDOWN_MINUTES = int(os.getenv("COOLDOWN_MINUTES", "10"))
STATE_PATH = Path(os.getenv("STATE_PATH", "live_rules_scanner_state.json"))

# Default for break/high/low triggers if not present
DEFAULT_TRIGGER_MINUTES = int(os.getenv("DEFAULT_TRIGGER_MINUTES", "3"))
DEFAULT_ENTRY_PRICE = os.getenv("DEFAULT_ENTRY_PRICE", "open")


# ───────────────────────── YAML parsing ─────────────────────────
def load_live_rules_yaml(path: Path) -> List[dict]:
    """Lightweight parser matching rule_factory.py export format."""
    if not path.exists():
        raise FileNotFoundError(f"rules file not found: {path.resolve()}")

    rules: List[dict] = []
    current: Optional[dict] = None
    in_conditions = False

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "rules:":
            continue
        if line.startswith("- name:"):
            if current:
                rules.append(current)
            current = {"name": line.split(":", 1)[1].strip(), "conditions": []}
            in_conditions = False
            continue
        if current is None:
            continue
        if line == "conditions:":
            in_conditions = True
            continue
        if in_conditions and line.startswith("- "):
            current["conditions"].append(line[2:].strip())
            continue
        if ":" in line and not line.startswith("- "):
            k, v = line.split(":", 1)
            current[k.strip()] = v.strip()
            continue

    if current:
        rules.append(current)
    return rules


# ───────────────────────── safe condition compilation ─────────────────────────
_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.And,
    ast.Or,
    ast.Not,
    ast.USub,
    ast.UAdd,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
)


def _normalize_expr(expr: str) -> str:
    s = expr.strip()

    # common SQL-ish sugar
    s = re.sub(r"\bAND\b", "and", s, flags=re.IGNORECASE)
    s = re.sub(r"\bOR\b", "or", s, flags=re.IGNORECASE)
    s = re.sub(r"\bNOT\b", "not", s, flags=re.IGNORECASE)

    s = re.sub(r"\btrue\b", "True", s, flags=re.IGNORECASE)
    s = re.sub(r"\bfalse\b", "False", s, flags=re.IGNORECASE)

    s = s.replace("<>", "!=")

    # Replace bare "=" with "==" (but keep <=, >=, !=, ==)
    s = re.sub(r"(?<![<>=!])=(?!=)", "==", s)

    return s


def _validate_ast(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")
        if isinstance(node, ast.Name):
            # Prevent sneaky dunder lookups like __class__
            if node.id.startswith("__"):
                raise ValueError("Disallowed name")
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (str, bytes)):
                # keep expressions numeric/bool only
                raise ValueError("String constants are not allowed in conditions")


@dataclass(frozen=True)
class CompiledCondition:
    raw: str
    expr: str
    code: Any
    names: Tuple[str, ...]


def compile_condition(raw: str) -> CompiledCondition:
    expr = _normalize_expr(raw)
    tree = ast.parse(expr, mode="eval")
    _validate_ast(tree)

    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.append(node.id)

    code = compile(tree, "<condition>", "eval")
    names_u = tuple(sorted(set(names)))
    return CompiledCondition(raw=raw, expr=expr, code=code, names=names_u)


def eval_condition(cond: CompiledCondition, row: Dict[str, Any]) -> bool:
    # Missing columns -> condition fails
    for n in cond.names:
        if n not in row:
            return False

    # Ensure python-native values
    locals_d = {k: row[k] for k in cond.names}
    try:
        return bool(eval(cond.code, {"__builtins__": {}}, locals_d))
    except Exception:
        return False


# ───────────────────────── rule model ─────────────────────────
@dataclass
class LiveRule:
    name: str
    side: str  # bullish|bearish|unknown
    status: str
    entry_mode: str
    entry_price: str
    trigger_minutes: int
    window_min: int
    window_max: int
    conditions: List[CompiledCondition]


def _coerce_int(x: Any, default: int) -> int:
    try:
        return int(float(str(x)))
    except Exception:
        return default


def _coerce_str(x: Any, default: str) -> str:
    s = str(x).strip() if x is not None else ""
    return s or default


def build_rules(doc_rules: List[dict]) -> List[LiveRule]:
    out: List[LiveRule] = []
    for r in doc_rules:
        name = _coerce_str(r.get("name"), "unnamed")
        status = _coerce_str(r.get("status"), "pending_confirmation")
        side = _coerce_str(r.get("side"), "unknown").lower()

        if (not INCLUDE_PENDING) and status.lower() != "production":
            continue

        entry_mode = _coerce_str(r.get("entry_mode"), "trigger-red").lower()
        entry_price = _coerce_str(r.get("entry_price"), DEFAULT_ENTRY_PRICE).lower()
        trigger_minutes = _coerce_int(r.get("trigger_minutes"), DEFAULT_TRIGGER_MINUTES)
        window_min = _coerce_int(r.get("window_min"), 1)
        window_max = _coerce_int(r.get("window_max"), 10)

        conds_raw = r.get("conditions") or []
        conds: List[CompiledCondition] = []
        for c in conds_raw:
            try:
                conds.append(compile_condition(str(c)))
            except Exception as exc:
                print(f"[rules] skipping bad condition in {name}: {c} ({exc})")

        if not conds:
            continue

        out.append(
            LiveRule(
                name=name,
                side=side,
                status=status,
                entry_mode=entry_mode,
                entry_price=entry_price,
                trigger_minutes=trigger_minutes,
                window_min=window_min,
                window_max=window_max,
                conditions=conds,
            )
        )
    return out


# ───────────────────────── state ─────────────────────────
def _ts_to_iso(ts: Optional[pd.Timestamp]) -> Optional[str]:
    if ts is None:
        return None
    if isinstance(ts, str):
        return ts
    try:
        return pd.Timestamp(ts).isoformat()
    except Exception:
        return None


def _iso_to_ts(s: Optional[str]) -> Optional[pd.Timestamp]:
    if not s:
        return None
    try:
        return pd.Timestamp(s, tz="UTC")
    except Exception:
        try:
            return pd.Timestamp(s)
        except Exception:
            return None


def load_state(path: Path) -> dict:
    if not path.exists():
        return {
            "last_ts_by_ticker": {},
            "setups": {},  # key: "TICKER|RULE" -> setup dict
            "cooldowns": {},  # key -> cooldown_until iso
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "last_ts_by_ticker": {},
            "setups": {},
            "cooldowns": {},
        }


def save_state(path: Path, state: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


# ───────────────────────── scanning logic ─────────────────────────
def _entry_price_from_row(row: Dict[str, Any], entry_price: str) -> Optional[float]:
    try:
        if entry_price == "open":
            return float(row.get("o"))
        if entry_price == "close":
            return float(row.get("c"))
        if entry_price == "vwap":
            v = row.get("vwap")
            return float(v) if v is not None else float(row.get("c"))
        if entry_price == "hl2":
            return (float(row.get("h")) + float(row.get("l"))) / 2.0
        # default
        return float(row.get("o"))
    except Exception:
        return None


def _row_is_red(row: Dict[str, Any]) -> bool:
    try:
        return float(row.get("c")) < float(row.get("o"))
    except Exception:
        return False


def _row_is_green(row: Dict[str, Any]) -> bool:
    try:
        return float(row.get("c")) > float(row.get("o"))
    except Exception:
        return False


def _key(ticker: str, rule_name: str) -> str:
    return f"{ticker}|{rule_name}"


def _in_cooldown(state: dict, ticker: str, rule_name: str, now: pd.Timestamp) -> bool:
    k = _key(ticker, rule_name)
    s = state.get("cooldowns", {}).get(k)
    ts = _iso_to_ts(s)
    return ts is not None and now <= ts


def _set_cooldown(state: dict, ticker: str, rule_name: str, until: pd.Timestamp) -> None:
    k = _key(ticker, rule_name)
    state.setdefault("cooldowns", {})[k] = _ts_to_iso(until)


def _get_setup(state: dict, ticker: str, rule_name: str) -> Optional[dict]:
    return state.get("setups", {}).get(_key(ticker, rule_name))


def _set_setup(state: dict, ticker: str, rule_name: str, setup: dict) -> None:
    state.setdefault("setups", {})[_key(ticker, rule_name)] = setup


def _clear_setup(state: dict, ticker: str, rule_name: str) -> None:
    state.get("setups", {}).pop(_key(ticker, rule_name), None)


def _all_conditions_pass(rule: LiveRule, row: Dict[str, Any]) -> bool:
    return all(eval_condition(c, row) for c in rule.conditions)


def _maybe_trigger(rule: LiveRule, setup: dict, row: Dict[str, Any]) -> Tuple[bool, Optional[float], str]:
    """
    Returns: (triggered, entry_price, trigger_reason)
    """
    mode = rule.entry_mode

    # Trigger only on candles after setup candle
    try:
        if pd.Timestamp(row["ts_utc"]) <= pd.Timestamp(setup["setup_ts"]):
            return False, None, ""
    except Exception:
        return False, None, ""

    if mode == "trigger-red":
        if _row_is_red(row):
            return True, _entry_price_from_row(row, rule.entry_price), "trigger-red"
        return False, None, ""

    if mode == "trigger-green":
        if _row_is_green(row):
            return True, _entry_price_from_row(row, rule.entry_price), "trigger-green"
        return False, None, ""

    if mode == "break-low":
        try:
            setup_low = float(setup.get("setup_low"))
            if float(row.get("l")) <= setup_low:
                # entry at setup_low (limit-style)
                return True, setup_low, "break-low"
        except Exception:
            pass
        return False, None, ""

    if mode == "break-high":
        try:
            setup_high = float(setup.get("setup_high"))
            if float(row.get("h")) >= setup_high:
                return True, setup_high, "break-high"
        except Exception:
            pass
        return False, None, ""

    if mode == "immediate":
        return True, _entry_price_from_row(row, rule.entry_price), "immediate"

    # Unknown mode -> no trigger
    return False, None, ""


async def _insert_signal(
    db: PolygonOptions,
    *,
    ticker: str,
    signal_time: pd.Timestamp,
    rule: LiveRule,
    entry_price: float,
    current_price: float,
    context: dict,
) -> None:
    # Minimal insert compatible with your Discord notifier loop
    sql = f"""
        INSERT INTO {SIGNALS_TABLE}
        (ticker, signal_time, rule_name, side, context, entry_price, current_price, sent_to_discord)
        VALUES ($1, $2, $3, $4, $5, $6, $7, FALSE)
    """
    await db.execute(
        sql,
        ticker,
        signal_time,
        rule.name,
        (rule.side or "unknown"),
        json.dumps(context),
        float(entry_price),
        float(current_price),
    )


def _compute_lookback_minutes(rules: List[LiveRule]) -> int:
    # Need enough history to see triggers and avoid missing writes.
    if not rules:
        return 15
    mx = max((r.trigger_minutes for r in rules), default=3)
    # Add buffer so restarts still catch setups/triggers
    return max(15, mx + 5)


async def scan_loop(
    *,
    tickers: List[str],
    rules: List[LiveRule],
) -> None:
    if not tickers:
        raise SystemExit("no tickers")
    if not rules:
        raise SystemExit("no rules (check INCLUDE_PENDING / live_rules.yaml)")

    lookback_minutes = int(os.getenv("LOOKBACK_MINUTES", str(_compute_lookback_minutes(rules))))

    # Build minimal select column list
    needed_cols: Set[str] = {"ticker", "ts_utc", "o", "c", "h", "l", "vwap"}
    for r in rules:
        for c in r.conditions:
            needed_cols.update(c.names)

    # Clean up any non-existent/odd cols (SQL injection protection is out of scope; this is trusted local config)
    # We'll only keep safe identifiers: letters, numbers, underscore
    safe_cols = []
    for col in sorted(needed_cols):
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", col):
            safe_cols.append(col)

    cols_sql = ", ".join(safe_cols)

    db = PolygonOptions()
    await db.connect()

    state = load_state(STATE_PATH)
    last_ts_by_ticker: Dict[str, Optional[pd.Timestamp]] = {
        t: _iso_to_ts(state.get("last_ts_by_ticker", {}).get(t)) for t in tickers
    }

    last_state_flush = 0.0

    print(f"[scanner] rules={len(rules)} tickers={len(tickers)} timespan={TIMESPAN} table={CANDLE_TABLE}")
    print(f"[scanner] lookback_minutes={lookback_minutes} candle_lag={CANDLE_LAG_SECONDS}s poll={POLL_SECONDS}s")
    print(f"[scanner] writing signals to {SIGNALS_TABLE} (status filter: {'production+pending' if INCLUDE_PENDING else 'production'})")

    try:
        while True:
            now = pd.Timestamp.utcnow().tz_localize("UTC")
            end_ts = now - pd.Timedelta(seconds=CANDLE_LAG_SECONDS)
            start_ts = end_ts - pd.Timedelta(minutes=lookback_minutes)

            sql = f"""
                SELECT {cols_sql}
                FROM {CANDLE_TABLE}
                WHERE timespan = $1
                  AND ticker = ANY($2)
                  AND ts_utc >= $3
                  AND ts_utc <= $4
                ORDER BY ts_utc ASC
            """

            rows = await db.fetch(sql, TIMESPAN, tickers, start_ts, end_ts) or []
            # asyncpg.Record -> dict
            items: List[Dict[str, Any]] = []
            for r in rows:
                try:
                    items.append(dict(r))
                except Exception:
                    continue

            # Process in time order
            fired = 0
            setups_created = 0

            for row in items:
                tkr = str(row.get("ticker"))
                ts = row.get("ts_utc")
                if not tkr or ts is None:
                    continue

                ts = pd.Timestamp(ts)
                prev = last_ts_by_ticker.get(tkr)
                if prev is not None and ts <= prev:
                    continue

                # Update last seen ts for this ticker
                last_ts_by_ticker[tkr] = ts

                # First: attempt triggers for existing setups
                for rule in rules:
                    k = _key(tkr, rule.name)
                    setup = state.get("setups", {}).get(k)
                    if not setup:
                        continue

                    # Expire setups
                    exp = _iso_to_ts(setup.get("expires_ts"))
                    if exp is not None and ts > exp:
                        _clear_setup(state, tkr, rule.name)
                        continue

                    trig, entry_px, reason = _maybe_trigger(rule, setup, row)
                    if trig and entry_px is not None:
                        # Fire!
                        ctx = {
                            "stage": "entry",
                            "reason": reason,
                            "setup_ts": setup.get("setup_ts"),
                            "setup_o": setup.get("setup_o"),
                            "setup_c": setup.get("setup_c"),
                            "setup_h": setup.get("setup_high"),
                            "setup_l": setup.get("setup_low"),
                            "trigger_ts": _ts_to_iso(ts),
                            "entry_price_mode": rule.entry_price,
                            "entry_mode": rule.entry_mode,
                            "window_min": rule.window_min,
                            "window_max": rule.window_max,
                            "conditions": [c.raw for c in rule.conditions],
                        }
                        cur_px = float(row.get("c")) if row.get("c") is not None else float(entry_px)
                        await _insert_signal(
                            db,
                            ticker=tkr,
                            signal_time=ts,
                            rule=rule,
                            entry_price=float(entry_px),
                            current_price=cur_px,
                            context=ctx,
                        )
                        fired += 1

                        # cooldown
                        _set_cooldown(
                            state,
                            tkr,
                            rule.name,
                            until=(ts + pd.Timedelta(minutes=COOLDOWN_MINUTES)),
                        )
                        _clear_setup(state, tkr, rule.name)

                # Second: create setups (if conditions pass)
                for rule in rules:
                    if _get_setup(state, tkr, rule.name):
                        continue  # only one active setup per (ticker, rule)
                    if _in_cooldown(state, tkr, rule.name, now=ts):
                        continue
                    if not _all_conditions_pass(rule, row):
                        continue

                    # Create setup
                    try:
                        setup_ts = _ts_to_iso(ts)
                        expires = ts + pd.Timedelta(minutes=max(1, rule.trigger_minutes))
                        setup = {
                            "setup_ts": setup_ts,
                            "expires_ts": _ts_to_iso(expires),
                            "setup_o": float(row.get("o")) if row.get("o") is not None else None,
                            "setup_c": float(row.get("c")) if row.get("c") is not None else None,
                            "setup_high": float(row.get("h")) if row.get("h") is not None else None,
                            "setup_low": float(row.get("l")) if row.get("l") is not None else None,
                        }
                        _set_setup(state, tkr, rule.name, setup)
                        setups_created += 1
                    except Exception:
                        continue

            # Persist state periodically
            state["last_ts_by_ticker"] = {t: _ts_to_iso(last_ts_by_ticker.get(t)) for t in tickers}
            now_s = time.time()
            if (now_s - last_state_flush) > 5.0 or fired:
                save_state(STATE_PATH, state)
                last_state_flush = now_s

            if fired or setups_created:
                print(f"[scanner] fired={fired} setups={setups_created} rows={len(items)} end={end_ts}")
            await asyncio.sleep(POLL_SECONDS)

    finally:
        save_state(STATE_PATH, state)
        await db.disconnect()


# ───────────────────────── CLI ─────────────────────────
def _parse_tickers(args: argparse.Namespace) -> List[str]:
    if args.tickers:
        return [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    if args.tickers_file:
        p = Path(args.tickers_file)
        out: List[str] = []
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            out.append(s.upper())
        return out
    return list(most_active_tickers)


def main() -> None:
    ap = argparse.ArgumentParser(description="Live YAML rules scanner (DB-driven)")
    ap.add_argument("--rules", default=str(LIVE_RULES_PATH), help="Path to live_rules.yaml")
    ap.add_argument("--tickers", help="Comma-separated tickers (defaults to most_active_tickers)")
    ap.add_argument("--tickers-file", help="File with one ticker per line (defaults to most_active_tickers)")
    args = ap.parse_args()

    rules_doc = load_live_rules_yaml(Path(args.rules))
    rules = build_rules(rules_doc)
    tickers = _parse_tickers(args)

    asyncio.run(scan_loop(tickers=tickers, rules=rules))


if __name__ == "__main__":
    main()
