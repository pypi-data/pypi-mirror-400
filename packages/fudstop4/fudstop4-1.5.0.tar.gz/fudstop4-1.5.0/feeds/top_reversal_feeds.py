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

import numpy as np
import pandas as pd

try:
    from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
except Exception:
    from discord_webhook import AsyncDiscordWebhook, DiscordEmbed

from fudstop4.apis.polygonio.polygon_options import PolygonOptions

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc


LIVE_TABLE = os.getenv("CANDLE_LIVE_TABLE", "candle_analysis_live")
HISTORY_TABLE = os.getenv("CANDLE_HISTORY_TABLE", "candle_analysis")
TIMESPAN = os.getenv("TIMESPAN", "m1")

LOOKBACK_MINUTES = int(os.getenv("TOP_FEEDS_LOOKBACK_MINUTES", "3"))
POLL_SECONDS = float(os.getenv("TOP_FEEDS_POLL_SECONDS", "5"))
CHART_BARS = int(os.getenv("TOP_FEEDS_CHART_BARS", "60"))

MIN_N = int(os.getenv("TOP_FEEDS_MIN_N", "50"))
MIN_HIT20 = float(os.getenv("TOP_FEEDS_MIN_HIT20", "0.85"))
TOP_N_PER_SIDE = int(os.getenv("TOP_FEEDS_TOP_N", "2"))

STATE_PATH = Path(os.getenv("TOP_FEEDS_STATE_PATH", "feeds_top_reversal_state.json"))
CACHE_TTL_MINUTES = int(os.getenv("TOP_FEEDS_CACHE_TTL_MINUTES", "360"))

SEND_CONCURRENCY = int(os.getenv("TOP_FEEDS_SEND_CONCURRENCY", "4"))
FEED_SIGNALS_TABLE = os.getenv("FEED_SIGNALS_TABLE", "reversal_feed_signals")
FEED_OUTCOME_MINUTES = int(os.getenv("FEED_OUTCOME_MINUTES", "5"))
FEED_OUTCOME_BATCH = int(os.getenv("FEED_OUTCOME_BATCH", "250"))

BULL_WEBHOOKS_RAW = os.getenv(
    "TOP_FEEDS_BULL_WEBHOOKS",
    "https://discord.com/api/webhooks/1458720348391604427/Ow69LwrgKhC_EyRs1RwQumWvtaCoypd-r91BpoAkHxjn7pxAcH7OewbwlZOGZ0Epsil2,"
    "https://discord.com/api/webhooks/1458720441891033226/XZof2sKqN7vjHnfX8BgPwBOULsEkKv71shqAc0LoS8uiSLForAhabS3iTHgjx8OtjWQG",
)
BULL_WEBHOOKS = [u.strip() for u in BULL_WEBHOOKS_RAW.split(",") if u.strip()]

BEAR_WEBHOOKS_RAW = os.getenv(
    "TOP_FEEDS_BEAR_WEBHOOKS",
    "https://discord.com/api/webhooks/1458720501341097994/gHRG0iNdojS2kRpviFJZTpM3c-FMalujWyaaQL4YSz6fozH_P4cgeJ7CcMd9e9zl0vD4,"
    "https://discord.com/api/webhooks/1458720578608566415/d9lsMlLDcutdFilzAwdGxk8VZ0FzY0wiRvzDQmn6q-KcwojntWFWPjLRZfXFhWszZXrH",
)
BEAR_WEBHOOKS = [u.strip() for u in BEAR_WEBHOOKS_RAW.split(",") if u.strip()]


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
        if isinstance(node, ast.Name) and node.id.startswith("__"):
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


def eval_condition(cond: CompiledCondition, row: Dict[str, Any]) -> bool:
    locals_d: Dict[str, Any] = {}
    for name in cond.names:
        if name not in row:
            return False
        locals_d[name] = row[name]
    try:
        return bool(eval(cond.code, {"__builtins__": {}}, locals_d))
    except Exception:
        return False


def _coerce_float(value: Any) -> float:
    if value in (None, "", "--"):
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
    hit_20bp: float
    avg_best_move: float
    p15_best_move: float
    window_min: int
    window_max: int
    n_val: int
    tickers_val: int


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
    return f"{rule.name}|{ticker}|{ts_utc.isoformat()}"


def _split_conditions(label: str) -> List[str]:
    return [part.strip() for part in label.split(" AND ") if part.strip()]


def _normalize_threshold_conditions(conds: List[str]) -> List[str]:
    thresholds: Dict[Tuple[str, str], float] = {}
    others: List[str] = []
    for cond in conds:
        m = re.match(r"^([A-Za-z0-9_]+)\s*(>=|<=)\s*([0-9.]+)$", cond)
        if not m:
            others.append(cond)
            continue
        name, op, raw = m.group(1), m.group(2), m.group(3)
        try:
            val = float(raw)
        except Exception:
            others.append(cond)
            continue
        key = (name, op)
        if key not in thresholds:
            thresholds[key] = val
        else:
            if op == ">=":
                thresholds[key] = max(thresholds[key], val)
            else:
                thresholds[key] = min(thresholds[key], val)

    normalized = others[:]
    for (name, op), val in thresholds.items():
        val_str = f"{val:g}"
        normalized.append(f"{name}{op}{val_str}")
    return sorted(set(normalized))


def _load_top_rules(path: Path, side: str, base_conditions: List[str]) -> List[FeedRule]:
    if not path.exists():
        return []
    df = pd.read_csv(path)
    df = df[(df["hit_20bp"] >= MIN_HIT20) & (df["n_val"] >= MIN_N)].copy()
    if df.empty:
        return []
    df = df.sort_values(["hit_20bp", "avg_best_move", "n_val"], ascending=[False, False, False])
    rules: List[FeedRule] = []
    seen: List[Tuple[str, ...]] = []
    for _, row in df.iterrows():
        if len(rules) >= TOP_N_PER_SIDE:
            break
        label = str(row["label"])
        label_conds = _normalize_threshold_conditions(_split_conditions(label))
        cond_key = tuple(label_conds)
        if cond_key in seen:
            continue
        seen.append(cond_key)
        conditions = base_conditions + label_conds
        compiled = [compile_condition(c) for c in conditions]
        rules.append(
            FeedRule(
                name=f"{side}_top_{'_'.join(cond_key).replace('>=', 'ge').replace('<=', 'le').replace('.', '_')}",
                side=side,
                conditions=tuple(compiled),
                raw_conditions=tuple(conditions),
                hit_20bp=float(row["hit_20bp"]),
                avg_best_move=float(row["avg_best_move"]),
                p15_best_move=float(row["p15_best_move"]),
                window_min=int(row["window_min"]),
                window_max=int(row["window_max"]),
                n_val=int(row["n_val"]),
                tickers_val=int(row["tickers_val"]),
            )
        )
    return rules


def _get_rules() -> List[FeedRule]:
    base_bull = ["rsi <= 30", "td_buy_count >= 10", "candle_completely_below_lower == True"]
    base_bear = ["rsi >= 70", "td_sell_count >= 10", "candle_completely_above_upper == True"]

    bulls = _load_top_rules(Path("runs/bullish_combo_findings.csv"), "bullish", base_bull)
    bears = _load_top_rules(Path("runs/bearish_combo_findings.csv"), "bearish", base_bear)
    return bulls + bears


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

    prob = rule.hit_20bp * 100.0
    avg_move = rule.avg_best_move * 100.0
    p15_move = rule.p15_best_move * 100.0
    hold = f"{rule.window_min}-{rule.window_max} min"

    embed.add_embed_field(name="Probability (20bp)", value=f"{prob:.1f}%", inline=True)
    embed.add_embed_field(name="Expected Hold", value=hold, inline=True)
    embed.add_embed_field(name="Expected Move", value=f"avg {avg_move:.2f}% | p15 {p15_move:.2f}%", inline=False)
    embed.add_embed_field(name="Sample", value=f"n={rule.n_val}, tickers={rule.tickers_val}", inline=True)

    cond_preview = " and ".join(rule.raw_conditions)[:900]
    embed.add_embed_field(name="Conditions", value=cond_preview, inline=False)
    return embed


async def _send_signal(
    db: PolygonOptions,
    rule: FeedRule,
    row: Dict[str, Any],
    *,
    semaphore: asyncio.Semaphore,
) -> None:
    urls = BULL_WEBHOOKS if rule.side == "bullish" else BEAR_WEBHOOKS
    if not urls:
        return

    ticker = str(row.get("ticker", ""))
    ts_utc = pd.Timestamp(row.get("ts_utc"))
    chart_df = await _fetch_chart_rows(db, ticker, ts_utc, CHART_BARS, live_row=row)
    chart_bytes = await asyncio.to_thread(_render_chart, chart_df, ticker, rule.side)

    embed = _build_embed(rule, row, ts_utc)

    async with semaphore:
        for url in urls:
            webhook = AsyncDiscordWebhook(url=url)
            if chart_bytes:
                filename = f"{ticker}_{rule.side}.png"
                webhook.add_file(file=chart_bytes, filename=filename)
                embed.set_image(url=f"attachment://{filename}")
            webhook.add_embed(embed)
            await webhook.execute()


async def run() -> None:
    rules = _get_rules()
    if not rules:
        raise SystemExit("No top rules found from findings CSVs.")

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
                    if not all(eval_condition(c, row) for c in rule.conditions):
                        continue
                    key = _signal_key(rule, ticker, ts_utc)
                    if key in state.get("sent", {}):
                        continue
                    state.setdefault("sent", {})[key] = ts_utc.isoformat()
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
