from __future__ import annotations

import ast
import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import yaml
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed

from fudstop4.apis.polygonio.polygon_options import PolygonOptions

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc


CONFIG_PATH = Path(os.getenv("RULE_FACTORY_CONFIG", "scripts/rule_factory.yaml"))
HOOK_URL = os.getenv("RULE_FEEDS_WEBHOOK", "https://discord.com/api/webhooks/1458488191144165437/mH0dPPrFxhTMJ-95MAhblmMGuCZWLxBeAUjOuOZxxw2orehKrArtokrsvVtfdAMl6Ekl")

LIVE_TABLE = os.getenv("CANDLE_LIVE_TABLE", "candle_analysis_live")
HISTORY_TABLE = os.getenv("CANDLE_HISTORY_TABLE", "candle_analysis")
TIMESPAN = os.getenv("TIMESPAN", "m1")

LOOKBACK_MINUTES = int(os.getenv("FEED_LOOKBACK_MINUTES", "3"))
POLL_SECONDS = float(os.getenv("FEED_POLL_SECONDS", "10"))
CHART_BARS = int(os.getenv("FEED_CHART_BARS", "60"))

INCLUDE_ADDONS = os.getenv("FEED_INCLUDE_ADDONS", "true").lower() in ("1", "true", "yes")
MAX_ADDONS_PER_BASE = int(os.getenv("FEED_MAX_ADDONS_PER_BASE", "12"))

STATE_PATH = Path(os.getenv("FEED_STATE_PATH", "feeds_state.json"))
CACHE_TTL_MINUTES = int(os.getenv("FEED_CACHE_TTL_MINUTES", "360"))

SEND_CONCURRENCY = int(os.getenv("FEED_SEND_CONCURRENCY", "4"))
FEED_SIGNALS_TABLE = os.getenv("FEED_SIGNALS_TABLE", "feed_signals")
FEED_OUTCOME_MINUTES = int(os.getenv("FEED_OUTCOME_MINUTES", "5"))
FEED_OUTCOME_BATCH = int(os.getenv("FEED_OUTCOME_BATCH", "250"))


_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Tuple,
    ast.List,
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
    ast.In,
    ast.NotIn,
)


def _normalize_expr(expr: str) -> str:
    s = expr.strip()
    s = re.sub(r"\bAND\b", "and", s, flags=re.IGNORECASE)
    s = re.sub(r"\bOR\b", "or", s, flags=re.IGNORECASE)
    s = re.sub(r"\bNOT\b", "not", s, flags=re.IGNORECASE)
    s = re.sub(r"\bTRUE\b", "True", s, flags=re.IGNORECASE)
    s = re.sub(r"\bFALSE\b", "False", s, flags=re.IGNORECASE)
    s = re.sub(r"\bIS\s+TRUE\b", "== True", s, flags=re.IGNORECASE)
    s = re.sub(r"\bIS\s+FALSE\b", "== False", s, flags=re.IGNORECASE)
    s = re.sub(r"\bNOT\s+IN\b", "not in", s, flags=re.IGNORECASE)
    s = re.sub(r"\bIN\b", "in", s, flags=re.IGNORECASE)
    s = s.replace("<>", "!=")
    s = re.sub(r"(?<![<>=!])=(?!=)", "==", s)
    return s


def _validate_ast(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"Disallowed expression node: {type(node).__name__}")
        if isinstance(node, ast.Name):
            if node.id.startswith("__"):
                raise ValueError("Disallowed name")


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
    names = [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
    code = compile(tree, "<condition>", "eval")
    return CompiledCondition(raw=raw, expr=expr, code=code, names=tuple(sorted(set(names))))


def eval_condition(cond: CompiledCondition, row: Dict[str, Any], side: str) -> bool:
    locals_d: Dict[str, Any] = {}
    for name in cond.names:
        if name == "direction":
            locals_d[name] = side
            continue
        if name not in row:
            return False
        locals_d[name] = row[name]
    try:
        return bool(eval(cond.code, {"__builtins__": {}}, locals_d))
    except Exception:
        return False


def _coerce_float(value: Any) -> float:
    if value in (None, "", "--", "—"):
        return 0.0
    try:
        return float(str(value).replace("%", "").strip())
    except Exception:
        return 0.0


def _coerce_str(value: Any) -> str:
    return "" if value is None else str(value)


@dataclass(frozen=True)
class FeedRule:
    name: str
    side: str
    conditions: Tuple[CompiledCondition, ...]
    raw_conditions: Tuple[str, ...]


class FeedSignals:
    def __init__(self, data: Iterable[dict]):
        rows = list(data)
        self.rule_name = [_coerce_str(i.get("rule_name")) for i in rows]
        self.side = [_coerce_str(i.get("side")) for i in rows]
        self.ticker = [_coerce_str(i.get("ticker")) for i in rows]
        self.ts_utc = [i.get("ts_utc") for i in rows]
        self.entry_price = [_coerce_float(i.get("entry_price")) for i in rows]

        self.data_dict = {
            "rule_name": self.rule_name,
            "side": self.side,
            "ticker": self.ticker,
            "ts_utc": self.ts_utc,
            "entry_price": self.entry_price,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class FeedSignalOutcomes:
    def __init__(self, data: Iterable[dict]):
        rows = list(data)
        self.rule_name = [_coerce_str(i.get("rule_name")) for i in rows]
        self.side = [_coerce_str(i.get("side")) for i in rows]
        self.ticker = [_coerce_str(i.get("ticker")) for i in rows]
        self.ts_utc = [i.get("ts_utc") for i in rows]
        self.entry_price = [_coerce_float(i.get("entry_price")) for i in rows]
        self.price_5m = [_coerce_float(i.get("price_5m")) for i in rows]
        self.price_5m_ts = [i.get("price_5m_ts") for i in rows]
        self.ret_5m = [_coerce_float(i.get("ret_5m")) for i in rows]

        self.data_dict = {
            "rule_name": self.rule_name,
            "side": self.side,
            "ticker": self.ticker,
            "ts_utc": self.ts_utc,
            "entry_price": self.entry_price,
            "price_5m": self.price_5m,
            "price_5m_ts": self.price_5m_ts,
            "ret_5m": self.ret_5m,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


def _normalize_base(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": entry.get("name") or entry.get("label") or "base",
        "where": entry.get("live_where") or entry.get("where"),
        "live_where_bearish": entry.get("live_where_bearish"),
        "live_where_bullish": entry.get("live_where_bullish"),
    }


def _normalize_addon(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "label": entry.get("label") or entry.get("name") or "addon",
        "where": entry.get("live_where") or entry.get("eval_where") or entry.get("where"),
        "live_where_bearish": entry.get("live_where_bearish"),
        "live_where_bullish": entry.get("live_where_bullish"),
        "sides": entry.get("sides"),
    }


def _addon_applies(addon: Dict[str, Any], side: str) -> bool:
    sides = addon.get("sides")
    if not sides:
        return True
    return side in {s.lower() for s in sides}


def _base_live_where(base: Dict[str, Any], side: str) -> Optional[str]:
    if side == "bearish" and base.get("live_where_bearish"):
        return base["live_where_bearish"]
    if side == "bullish" and base.get("live_where_bullish"):
        return base["live_where_bullish"]
    return base.get("where")


def _addon_live_where(addon: Dict[str, Any], side: str) -> Optional[str]:
    if side == "bearish" and addon.get("live_where_bearish"):
        return addon["live_where_bearish"]
    if side == "bullish" and addon.get("live_where_bullish"):
        return addon["live_where_bullish"]
    return addon.get("where")


def load_rule_factory(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def build_feed_rules(cfg: Dict[str, Any]) -> List[FeedRule]:
    rules: List[FeedRule] = []
    addons_raw = [_normalize_addon(a) for a in cfg.get("addons", [])]

    for side, bases in (("bearish", cfg.get("bearish_bases", [])), ("bullish", cfg.get("bullish_bases", []))):
        side_bases = [_normalize_base(b) for b in bases]
        side_addons = [a for a in addons_raw if _addon_applies(a, side)]

        for base in side_bases:
            base_expr = _base_live_where(base, side)
            if not base_expr:
                continue

            base_conds = [base_expr]
            compiled_base = [compile_condition(c) for c in base_conds]
            rules.append(
                FeedRule(
                    name=base["name"],
                    side=side,
                    conditions=tuple(compiled_base),
                    raw_conditions=tuple(base_conds),
                )
            )

            if not INCLUDE_ADDONS:
                continue

            for addon in side_addons[:MAX_ADDONS_PER_BASE]:
                addon_expr = _addon_live_where(addon, side)
                if not addon_expr:
                    continue
                rule_name = f"{base['name']}_plus_{addon['label']}"
                raw = [base_expr, addon_expr]
                try:
                    compiled = [compile_condition(c) for c in raw]
                except Exception:
                    continue
                rules.append(
                    FeedRule(
                        name=rule_name,
                        side=side,
                        conditions=tuple(compiled),
                        raw_conditions=tuple(raw),
                    )
                )
    return rules


def _ts_to_iso(ts: pd.Timestamp) -> str:
    return pd.Timestamp(ts).isoformat()


def _load_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"sent": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"sent": {}}


def _save_state(path: Path, state: Dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _prune_state(state: Dict[str, Any], now: pd.Timestamp) -> None:
    if CACHE_TTL_MINUTES <= 0:
        return
    cutoff = now - timedelta(minutes=CACHE_TTL_MINUTES)
    sent = state.get("sent", {})
    stale = [k for k, v in sent.items() if pd.Timestamp(v) < cutoff]
    for k in stale:
        sent.pop(k, None)


def _signal_key(rule: FeedRule, ticker: str, ts_utc: pd.Timestamp) -> str:
    return f"{rule.name}|{ticker}|{_ts_to_iso(ts_utc)}"


async def _record_signals(db: PolygonOptions, signals: List[Dict[str, Any]]) -> None:
    if not signals:
        return
    model = FeedSignals(signals)
    await db.batch_upsert_dataframe(
        model.as_dataframe,
        table_name=FEED_SIGNALS_TABLE,
        unique_columns=["rule_name", "ticker", "ts_utc"],
    )


async def _fetch_pending_outcomes(db: PolygonOptions, cutoff: pd.Timestamp) -> List[Dict[str, Any]]:
    sql = f"""
        SELECT
          s.rule_name,
          s.side,
          s.ticker,
          s.ts_utc,
          s.entry_price,
          f.ts_utc AS price_5m_ts,
          f.c AS price_5m
        FROM {FEED_SIGNALS_TABLE} s
        CROSS JOIN LATERAL (
          SELECT ts_utc, c
          FROM {HISTORY_TABLE}
          WHERE timespan = $1
            AND ticker = s.ticker
            AND ts_utc >= s.ts_utc + interval '{FEED_OUTCOME_MINUTES} minutes'
          ORDER BY ts_utc ASC
          LIMIT 1
        ) f
        WHERE s.price_5m IS NULL
          AND s.ts_utc <= $2
        ORDER BY s.ts_utc ASC
        LIMIT $3
    """
    rows = await db.fetch_new(sql, TIMESPAN, cutoff.to_pydatetime(), FEED_OUTCOME_BATCH)
    return [dict(r) for r in rows or []]


def _build_outcome_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in rows:
        entry = _coerce_float(row.get("entry_price"))
        price_5m = _coerce_float(row.get("price_5m"))
        if entry <= 0 or price_5m <= 0:
            continue
        side = _coerce_str(row.get("side")).lower()
        if side == "bearish":
            ret = (entry / price_5m) - 1.0
        else:
            ret = (price_5m / entry) - 1.0
        out.append(
            {
                "rule_name": row.get("rule_name"),
                "side": row.get("side"),
                "ticker": row.get("ticker"),
                "ts_utc": row.get("ts_utc"),
                "entry_price": entry,
                "price_5m": price_5m,
                "price_5m_ts": row.get("price_5m_ts"),
                "ret_5m": ret,
            }
        )
    return out


async def _update_outcomes(db: PolygonOptions, now: pd.Timestamp) -> None:
    if not await db.table_exists(FEED_SIGNALS_TABLE):
        return
    cutoff = now - timedelta(minutes=FEED_OUTCOME_MINUTES)
    rows = await _fetch_pending_outcomes(db, cutoff)
    if not rows:
        return
    updates = _build_outcome_rows(rows)
    if not updates:
        return
    model = FeedSignalOutcomes(updates)
    await db.batch_upsert_dataframe(
        model.as_dataframe,
        table_name=FEED_SIGNALS_TABLE,
        unique_columns=["rule_name", "ticker", "ts_utc"],
    )


async def _fetch_live_rows(db: PolygonOptions, cutoff: pd.Timestamp) -> List[Dict[str, Any]]:
    sql = f"""
        SELECT *
        FROM {LIVE_TABLE}
        WHERE timespan = $1
          AND ts_utc::timestamptz >= $2
    """
    rows = await db.fetch_new(sql, TIMESPAN, cutoff.to_pydatetime())
    return [dict(r) for r in rows or []]


async def _fetch_chart_rows(
    db: PolygonOptions,
    ticker: str,
    end_ts: pd.Timestamp,
    bars: int,
    live_row: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    sql = f"""
        SELECT ts_utc, o, h, l, c
        FROM {HISTORY_TABLE}
        WHERE timespan = $1
          AND ticker = $2
          AND ts_utc::timestamptz <= $3
        ORDER BY ts_utc DESC
        LIMIT $4
    """
    limit = max(bars * 5, bars)
    rows = await db.fetch_new(sql, TIMESPAN, ticker, end_ts.to_pydatetime(), limit)
    df = pd.DataFrame([dict(r) for r in rows or []])
    if df.empty:
        return df
    df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True)
    df = df.sort_values("ts_utc").reset_index(drop=True)

    # Focus chart on the current RTH session (avoids overnight/pre-market gaps).
    end_ts_utc = pd.Timestamp(end_ts)
    if end_ts_utc.tzinfo is None:
        end_ts_utc = end_ts_utc.tz_localize("UTC")

    session_date = end_ts_utc.tz_convert("America/New_York").date()
    session_start_et = pd.Timestamp(f"{session_date} 09:30", tz="America/New_York")
    session_end_et = pd.Timestamp(f"{session_date} 16:00", tz="America/New_York")
    session_start_utc = session_start_et.tz_convert("UTC")
    session_end_utc = session_end_et.tz_convert("UTC")

    session_df = df.loc[
        (df["ts_utc"] >= session_start_utc) & (df["ts_utc"] <= session_end_utc)
    ].copy()
    df = session_df.tail(bars).reset_index(drop=True) if not session_df.empty else pd.DataFrame()

    # Overlay the latest live row (replace or append) if it falls in-session.
    if live_row:
        try:
            live_ts = pd.to_datetime(live_row.get("ts_utc"), utc=True)
            if session_start_utc <= live_ts <= session_end_utc:
                live_rec = {
                    "ts_utc": live_ts,
                    "o": float(live_row.get("o")),
                    "h": float(live_row.get("h")),
                    "l": float(live_row.get("l")),
                    "c": float(live_row.get("c")),
                }
                if not df.empty:
                    df = df[df["ts_utc"] != live_ts]
                df = pd.concat([df, pd.DataFrame([live_rec])], ignore_index=True)
                df = df.sort_values("ts_utc").reset_index(drop=True)
                df = df.tail(bars).reset_index(drop=True)
        except Exception:
            pass

    return df


def _render_chart(df: pd.DataFrame, ticker: str, side: str) -> bytes:
    if df is None or df.empty or len(df) < 2:
        return b""

    plot = df.copy()
    plot["num"] = mdates.date2num(plot["ts_utc"])
    ohlc = plot[["num", "o", "h", "l", "c"]].values

    width = (plot["num"].iloc[1] - plot["num"].iloc[0]) * 0.6

    fig, ax = plt.subplots(figsize=(8, 4.2))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")

    candlestick_ohlc(
        ax,
        ohlc,
        width=width,
        colorup="#22c55e",
        colordown="#ef4444",
        alpha=0.9,
    )

    close = plot["c"].astype(float)
    plot["ema_9"] = close.ewm(span=9, adjust=False).mean()
    plot["ema_21"] = close.ewm(span=21, adjust=False).mean()

    mid = close.rolling(window=20, min_periods=20).mean()
    std = close.rolling(window=20, min_periods=20).std(ddof=0)
    upper = mid + 2.0 * std
    lower = mid - 2.0 * std

    ax.plot(plot["num"], plot["ema_9"], color="#38bdf8", linewidth=0.9, label="EMA 9")
    ax.plot(plot["num"], plot["ema_21"], color="#f59e0b", linewidth=0.9, label="EMA 21")
    ax.plot(plot["num"], upper, color="#94a3b8", linewidth=0.8, alpha=0.7)
    ax.plot(plot["num"], lower, color="#94a3b8", linewidth=0.8, alpha=0.7)

    ax.set_title(f"{ticker} {side} signal", color="#e2e8f0", fontsize=11, loc="left")
    ax.tick_params(axis="x", colors="#cbd5e1", labelsize=8)
    ax.tick_params(axis="y", colors="#cbd5e1", labelsize=8)
    ax.grid(color="#334155", alpha=0.3, linestyle="--", linewidth=0.6)
    ax.legend(facecolor="#0f172a", edgecolor="#0f172a", fontsize=7, labelcolor="#e2e8f0")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _build_embed(rule: FeedRule, row: Dict[str, Any], ts_utc: pd.Timestamp) -> DiscordEmbed:
    side = rule.side.lower()
    color = "2ecc71" if side == "bullish" else "e74c3c"

    ts_et = ts_utc.tz_convert("America/New_York") if ts_utc.tzinfo else ts_utc
    title = f"{rule.name} signal"
    desc = f"{row.get('ticker')} @ {ts_et.strftime('%Y-%m-%d %H:%M ET')}"

    embed = DiscordEmbed(title=title, description=desc, color=color)
    embed.set_timestamp()

    def _fmt(val: Any) -> str:
        try:
            return f"{float(val):.2f}"
        except Exception:
            return str(val)

    fields = []
    for key, label in (
        ("rsi", "RSI"),
        ("td_buy_count", "TD Buy"),
        ("td_sell_count", "TD Sell"),
        ("bb_width", "BB Width"),
        ("stoch_k", "Stoch"),
        ("mfi", "MFI"),
        ("williams_r", "WillR"),
    ):
        if key in row and row[key] is not None:
            fields.append((label, _fmt(row[key])))

    for label, value in fields[:6]:
        embed.add_embed_field(name=label, value=value, inline=True)

    embed.add_embed_field(
        name="Conditions",
        value=" and ".join(rule.raw_conditions[:2])[:900],
        inline=False,
    )
    return embed


async def _send_signal(
    db: PolygonOptions,
    rule: FeedRule,
    row: Dict[str, Any],
    *,
    semaphore: asyncio.Semaphore,
) -> None:
    if not HOOK_URL:
        return

    ticker = str(row.get("ticker", ""))
    ts_utc = pd.Timestamp(row.get("ts_utc"))
    chart_df = await _fetch_chart_rows(db, ticker, ts_utc, CHART_BARS, live_row=row)
    chart_bytes = await asyncio.to_thread(_render_chart, chart_df, ticker, rule.side)

    embed = _build_embed(rule, row, ts_utc)

    async with semaphore:
        webhook = AsyncDiscordWebhook(url=HOOK_URL)
        if chart_bytes:
            filename = f"{ticker}_{rule.side}.png"
            webhook.add_file(file=chart_bytes, filename=filename)
            embed.set_image(url=f"attachment://{filename}")
        webhook.add_embed(embed)
        await webhook.execute()


async def run() -> None:
    if not HOOK_URL:
        raise SystemExit("RULE_FEEDS_WEBHOOK is not set")

    cfg = load_rule_factory(CONFIG_PATH)
    rules = build_feed_rules(cfg)
    if not rules:
        raise SystemExit("No feed rules built from rule_factory.yaml")

    db = PolygonOptions()
    await db.connect()

    state = _load_state(STATE_PATH)
    send_sem = asyncio.Semaphore(max(1, SEND_CONCURRENCY))

    try:
        while True:
            now = pd.Timestamp.now(tz="UTC")
            _prune_state(state, now)
            cutoff = now - timedelta(minutes=LOOKBACK_MINUTES)

            rows = await _fetch_live_rows(db, cutoff)
            if not rows:
                await asyncio.sleep(POLL_SECONDS)
                continue

            send_tasks = []
            signal_rows = []
            for row in rows:
                ts_utc = row.get("ts_utc")
                if not ts_utc:
                    continue
                ts_utc = pd.Timestamp(ts_utc)
                if ts_utc.tzinfo is None:
                    ts_utc = ts_utc.tz_localize("UTC")
                ticker = str(row.get("ticker", ""))
                if not ticker:
                    continue

                for rule in rules:
                    if not all(eval_condition(c, row, rule.side) for c in rule.conditions):
                        continue
                    key = _signal_key(rule, ticker, ts_utc)
                    if key in state.get("sent", {}):
                        continue
                    state.setdefault("sent", {})[key] = _ts_to_iso(now)
                    signal_rows.append(
                        {
                            "rule_name": rule.name,
                            "side": rule.side,
                            "ticker": ticker,
                            "ts_utc": ts_utc,
                            "entry_price": _coerce_float(row.get("c")),
                        }
                    )
                    send_tasks.append(_send_signal(db, rule, row, semaphore=send_sem))

            if signal_rows:
                await _record_signals(db, signal_rows)

            if send_tasks:
                await asyncio.gather(*send_tasks)
                _save_state(STATE_PATH, state)

            await _update_outcomes(db, now)

            await asyncio.sleep(POLL_SECONDS)
    finally:
        _save_state(STATE_PATH, state)
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(run())
