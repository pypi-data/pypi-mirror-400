#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import itertools
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd

from fudstop4.apis.polygonio.polygon_options import PolygonOptions


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_CONFIG = REPO_ROOT / "rule_factory.yaml"
LIVE_RULES_PATH = REPO_ROOT / "live_rules.yaml"
RUNS_DIR = REPO_ROOT / "runs"

sys.path.insert(0, str(SCRIPT_DIR))
import rule_characterization as rc  # noqa: E402

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required for rule_factory.yaml parsing.") from exc

_EVAL_COLS = [
    "rule_id",
    "direction",
    "n_val",
    "tickers_val",
    "distinct_days_val",
    "hit_0",
    "hit_10bp",
    "hit_20bp",
    "p15_mfe",
    "p50_mae",
    "p85_mae",
    "p95_mae",
    "signals_per_day_val",
    "signals_per_day_per_ticker",
    "p15_mfe_p85_mae_ratio",
    "side",
    "base_name",
    "addon_labels",
    "addon_count",
    "eval_conditions",
    "exportable",
    "entry_mode",
    "entry_price",
    "trigger_minutes",
    "window_min",
    "window_max",
    "live_conditions",
    "wilson_lb",
    "rank_ratio",
]


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
    return cleaned or "rule"


def _hash_suffix(value: str, length: int = 8) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def _normalize_rule_name(base_name: str, addon_labels: List[str]) -> str:
    name = base_name
    for label in addon_labels:
        name = f"{name}_plus_{label}"
    if len(name) > 80:
        name = f"{name[:64]}_{_hash_suffix(name)}"
    return name


def _chunked(items: List[dict], size: int) -> Iterable[List[dict]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def _normalize_base(entry: Any) -> dict:
    if isinstance(entry, dict):
        name = entry.get("name") or _slugify(entry.get("where", "base"))
        return {
            "name": name,
            "where": entry.get("where") or entry.get("eval_where"),
            "live_where": entry.get("live_where"),
            "live_where_bearish": entry.get("live_where_bearish"),
            "live_where_bullish": entry.get("live_where_bullish"),
        }
    return {"name": _slugify(str(entry)), "where": str(entry)}


def _normalize_addon(entry: Any) -> dict:
    if isinstance(entry, dict):
        label = entry.get("label") or _slugify(entry.get("where", "addon"))
        return {
            "label": label,
            "eval_where": entry.get("eval_where") or entry.get("where"),
            "live_where": entry.get("live_where") or entry.get("where"),
            "live_where_bearish": entry.get("live_where_bearish"),
            "live_where_bullish": entry.get("live_where_bullish"),
            "sides": entry.get("sides"),
            "group": entry.get("group") or entry.get("family") or entry.get("category"),
            "exportable": entry.get("exportable", True),
        }
    expr = str(entry)
    return {
        "label": _slugify(expr),
        "eval_where": expr,
        "live_where": expr,
        "live_where_bearish": None,
        "live_where_bullish": None,
        "sides": None,
        "group": None,
        "exportable": True,
    }


def _addon_live_where(addon: dict, side: str) -> str | None:
    if side == "bearish" and addon.get("live_where_bearish"):
        return addon["live_where_bearish"]
    if side == "bullish" and addon.get("live_where_bullish"):
        return addon["live_where_bullish"]
    return addon.get("live_where")


def _base_live_where(base: dict, side: str) -> str | None:
    if side == "bearish" and base.get("live_where_bearish"):
        return base["live_where_bearish"]
    if side == "bullish" and base.get("live_where_bullish"):
        return base["live_where_bullish"]
    return base.get("live_where") or base.get("where")



def _safe_float(x: Any, default: float = 0.0) -> float:
    """Coerce asyncpg/pandas numeric types (e.g., Decimal) to float safely."""
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        try:
            return float(str(x))
        except Exception:
            return default


def _safe_int(x: Any, default: int = 0) -> int:
    """Coerce asyncpg/pandas numeric types to int safely."""
    try:
        if x is None:
            return default
        return int(x)
    except Exception:
        try:
            return int(float(str(x)))
        except Exception:
            return default

def _wilson_lb(p_hat: float, n: int, z: float) -> float | None:
    if n <= 0:
        return None
    denom = 1.0 + (z * z) / n
    center = p_hat + (z * z) / (2 * n)
    margin = z * math.sqrt(((p_hat * (1 - p_hat)) + (z * z) / (4 * n)) / n)
    return (center - margin) / denom


def _apply_guardrails(df: pd.DataFrame, guard: dict) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    out = df.copy()

    def _get_guard(*keys: str):
        for key in keys:
            if key in guard and guard.get(key) is not None:
                return guard.get(key)
        return None

    def _filter(col: str, op, threshold):
        if threshold is None:
            return
        if col not in out.columns:
            # Guardrail specified but column missing -> no candidates.
            out.drop(out.index, inplace=True)
            return
        out.loc[:, col] = pd.to_numeric(out[col], errors="coerce")
        out.dropna(subset=[col], inplace=True)
        out.query(f"{col} {op} @threshold", inplace=True)

    min_val = _get_guard("min_val", "min_n_val")
    min_tickers = _get_guard("min_tickers_val", "min_tickers")
    min_p15 = _get_guard("min_p15_mfe")
    max_p85 = _get_guard("max_p85_mae")
    min_wilson = _get_guard("min_wilson_lb")
    min_hit_0 = _get_guard("min_hit_0")
    min_hit_10 = _get_guard("min_hit_10bp")
    min_hit_20 = _get_guard("min_hit_20bp")

    _filter("n_val", ">=", float(min_val) if min_val is not None else None)
    _filter("tickers_val", ">=", float(min_tickers) if min_tickers is not None else None)
    _filter("p15_mfe", ">=", float(min_p15) if min_p15 is not None else None)
    _filter("p85_mae", "<=", float(max_p85) if max_p85 is not None else None)
    _filter("wilson_lb", ">=", float(min_wilson) if min_wilson is not None else None)
    _filter("hit_0", ">=", float(min_hit_0) if min_hit_0 is not None else None)
    _filter("hit_10bp", ">=", float(min_hit_10) if min_hit_10 is not None else None)
    _filter("hit_20bp", ">=", float(min_hit_20) if min_hit_20 is not None else None)

    return out


async def _evaluate_rules(
    *,
    db: PolygonOptions,
    rules: List[dict],
    meta_rows: List[dict],
    config: dict,
    entry_mode: str,
    trigger_minutes: int,
    entry_price: str,
    window_min: int,
    window_max: int,
    timespan: str,
) -> pd.DataFrame:
    if not rules:
        return pd.DataFrame()
    sql = rc.build_characterization_query(
        rules=rules,
        val_window=config.get("val_window", "60 days"),
        window_min=window_min,
        window_max=window_max,
        timespan=timespan,
        entry_mode=entry_mode,
        trigger_window_minutes=trigger_minutes,
        entry_price=entry_price,
    )
    rows = await db.fetch_new(sql)
    df = pd.DataFrame([dict(r) for r in rows])

    # Normalize numeric dtypes (asyncpg often returns Decimal for NUMERIC)
    if not df.empty:
        float_cols = [
            "hit_0",
            "hit_10bp",
            "hit_20bp",
            "p15_mfe",
            "p50_mfe",
            "p85_mfe",
            "p15_mae",
            "p50_mae",
            "p85_mae",
            "p95_mae",
            "signals_per_day_val",
            "s",
        ]
        for c in float_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        int_cols = ["n_val", "tickers_val", "distinct_days_val"]
        for c in int_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

    if df.empty:
        return df

    meta_df = pd.DataFrame(meta_rows)
    df = df.merge(meta_df, on="rule_id", how="left")

    guard = config.get("guardrails", {})
    metric = guard.get("wilson_metric", "hit_0")
    z_val = float(guard.get("wilson_z", 1.96))

    if metric not in df.columns:
        raise ValueError(f"Wilson metric '{metric}' not available in characterization output.")

    df["wilson_lb"] = [
        _wilson_lb(p_hat or 0.0, int(n_val or 0), z_val)
        for p_hat, n_val in zip(df[metric].fillna(0.0), df["n_val"].fillna(0))
    ]
    df["entry_mode"] = entry_mode
    df["entry_price"] = entry_price
    df["trigger_minutes"] = trigger_minutes
    df["window_min"] = window_min
    df["window_max"] = window_max
    df["rank_ratio"] = df["p15_mfe_p85_mae_ratio"]
    return df


def _rank(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values(
        by=[
            "rank_ratio",
            "p15_mfe",
            "p85_mae",
            "n_val",
            "signals_per_day_val",
        ],
        ascending=[False, False, True, False, False],
    )



def _select_top_addon_labels(addon_only: pd.DataFrame, addons: List[dict], guard: dict) -> List[str]:
    """Select addon labels used to form pairs/triples.

    Default behavior: classic beam (top `beam_width`).

    If you set `guardrails.beam_per_group > 0` and tag addons with `group`,
    selection becomes group-diversified: take up to N per group (in ranked order)
    then fill the remainder up to beam_width with next-best overall.
    """
    if addon_only is None or addon_only.empty:
        return []

    beam_width = int(guard.get("beam_width", 10))
    if beam_width <= 0:
        return []

    ranked = addon_only["addon_labels"].tolist()
    beam_per_group = int(guard.get("beam_per_group", 0))

    if beam_per_group <= 0:
        return ranked[:beam_width]

    label_to_group = {a.get("label"): (a.get("group") or "ungrouped") for a in (addons or [])}

    group_to_labels: Dict[str, List[str]] = {}
    for lbl in ranked:
        grp = label_to_group.get(lbl) or "ungrouped"
        group_to_labels.setdefault(grp, []).append(lbl)

    selected: List[str] = []
    for _grp, grp_labels in group_to_labels.items():
        selected.extend(grp_labels[:beam_per_group])

    if len(selected) < beam_width:
        for lbl in ranked:
            if lbl not in selected:
                selected.append(lbl)
            if len(selected) >= beam_width:
                break

    return selected[:beam_width]

def _build_rule_meta(
    *,
    base: dict,
    addon_labels: List[str],
    addon_exprs: List[str],
    side: str,
    entry_mode: str,
    entry_price: str,
    trigger_minutes: int,
    window_min: int,
    window_max: int,
    exportable: bool,
    live_conditions: List[str],
) -> dict:
    name = _normalize_rule_name(base["name"], addon_labels)
    return {
        "rule_id": name,
        "side": side,
        "base_name": base["name"],
        "addon_labels": ", ".join(addon_labels) if addon_labels else "",
        "addon_count": len(addon_labels),
        "eval_conditions": " AND ".join(addon_exprs),
        "exportable": exportable,
        "entry_mode": entry_mode,
        "entry_price": entry_price,
        "trigger_minutes": trigger_minutes,
        "window_min": window_min,
        "window_max": window_max,
        "live_conditions": live_conditions,
    }


def _build_candidate_rules(
    *,
    base: dict,
    side: str,
    addons: List[dict],
    entry_mode: str,
    trigger_minutes: int,
    entry_price: str,
    window_min: int,
    window_max: int,
    include_base_only: bool = True,
) -> tuple[List[dict], List[dict]]:
    rules: List[dict] = []
    meta_rows: List[dict] = []

    base_eval = base.get("where")
    if not base_eval:
        return rules, meta_rows
    base_live = _base_live_where(base, side)
    base_live_conditions = [base_live] if base_live else []

    if include_base_only:
        name = _normalize_rule_name(base["name"], [])
        rules.append(
            {
                "name": name,
                "side": side,
                "conditions": [f"direction = '{side}'", base_eval],
            }
        )
        meta_rows.append(
            _build_rule_meta(
                base=base,
                addon_labels=[],
                addon_exprs=[base_eval],
                side=side,
                entry_mode=entry_mode,
                entry_price=entry_price,
                trigger_minutes=trigger_minutes,
                window_min=window_min,
                window_max=window_max,
                exportable=True,
                live_conditions=base_live_conditions,
            )
        )

    for addon in addons:
        addon_eval = addon.get("eval_where")
        if not addon_eval:
            continue
        addon_label = addon["label"]
        name = _normalize_rule_name(base["name"], [addon_label])
        rules.append(
            {
                "name": name,
                "side": side,
                "conditions": [f"direction = '{side}'", base_eval, addon_eval],
            }
        )
        live_where = _addon_live_where(addon, side)
        exportable = addon.get("exportable", True) and live_where is not None
        meta_rows.append(
            _build_rule_meta(
                base=base,
                addon_labels=[addon_label],
                addon_exprs=[base_eval, addon_eval],
                side=side,
                entry_mode=entry_mode,
                entry_price=entry_price,
                trigger_minutes=trigger_minutes,
                window_min=window_min,
                window_max=window_max,
                exportable=exportable,
                live_conditions=base_live_conditions + ([live_where] if live_where else []),
            )
        )

    return rules, meta_rows


def _build_pair_rules(
    *,
    base: dict,
    side: str,
    addon_pairs: List[tuple[dict, dict]],
    entry_mode: str,
    trigger_minutes: int,
    entry_price: str,
    window_min: int,
    window_max: int,
) -> tuple[List[dict], List[dict]]:
    rules: List[dict] = []
    meta_rows: List[dict] = []
    base_eval = base.get("where")
    if not base_eval:
        return rules, meta_rows
    base_live = _base_live_where(base, side)
    base_live_conditions = [base_live] if base_live else []

    for addon_a, addon_b in addon_pairs:
        addon_eval = [addon_a.get("eval_where"), addon_b.get("eval_where")]
        if not addon_eval[0] or not addon_eval[1]:
            continue
        addon_labels = [addon_a["label"], addon_b["label"]]
        name = _normalize_rule_name(base["name"], addon_labels)
        rules.append(
            {
                "name": name,
                "side": side,
                "conditions": [f"direction = '{side}'", base_eval] + addon_eval,
            }
        )

        live_a = _addon_live_where(addon_a, side)
        live_b = _addon_live_where(addon_b, side)
        exportable = (
            addon_a.get("exportable", True)
            and addon_b.get("exportable", True)
            and live_a is not None
            and live_b is not None
        )
        live_conditions = base_live_conditions + [c for c in (live_a, live_b) if c]
        meta_rows.append(
            _build_rule_meta(
                base=base,
                addon_labels=addon_labels,
                addon_exprs=[base_eval] + addon_eval,
                side=side,
                entry_mode=entry_mode,
                entry_price=entry_price,
                trigger_minutes=trigger_minutes,
                window_min=window_min,
                window_max=window_max,
                exportable=exportable,
                live_conditions=live_conditions,
            )
        )

    return rules, meta_rows



def _build_triple_rules(
    *,
    base: dict,
    side: str,
    addon_triples: List[tuple[dict, dict, dict]],
    entry_mode: str,
    trigger_minutes: int,
    entry_price: str,
    window_min: int,
    window_max: int,
) -> tuple[List[dict], List[dict]]:
    """Build base + 3-addon rules (deeper layering)."""
    rules: List[dict] = []
    meta_rows: List[dict] = []

    base_eval = base.get("where")
    if not base_eval:
        return rules, meta_rows
    base_live = _base_live_where(base, side)
    base_live_conditions = [base_live] if base_live else []

    for addon_a, addon_b, addon_c in addon_triples:
        eval_a = addon_a.get("eval_where")
        eval_b = addon_b.get("eval_where")
        eval_c = addon_c.get("eval_where")
        if not eval_a or not eval_b or not eval_c:
            continue

        addon_labels = [addon_a["label"], addon_b["label"], addon_c["label"]]
        name = _normalize_rule_name(base["name"], addon_labels)

        rules.append(
            {
                "name": name,
                "side": side,
                "conditions": [f"direction = '{side}'", base_eval, eval_a, eval_b, eval_c],
            }
        )

        live_a = _addon_live_where(addon_a, side)
        live_b = _addon_live_where(addon_b, side)
        live_c = _addon_live_where(addon_c, side)

        exportable = (
            addon_a.get("exportable", True)
            and addon_b.get("exportable", True)
            and addon_c.get("exportable", True)
            and live_a is not None
            and live_b is not None
            and live_c is not None
        )

        live_conditions = base_live_conditions + [c for c in (live_a, live_b, live_c) if c]
        meta_rows.append(
            _build_rule_meta(
                base=base,
                addon_labels=addon_labels,
                addon_exprs=[base_eval, eval_a, eval_b, eval_c],
                side=side,
                entry_mode=entry_mode,
                entry_price=entry_price,
                trigger_minutes=trigger_minutes,
                window_min=window_min,
                window_max=window_max,
                exportable=exportable,
                live_conditions=live_conditions,
            )
        )

    return rules, meta_rows

def _filter_addons(addons: List[dict], side: str) -> List[dict]:
    filtered = []
    for addon in addons:
        sides = addon.get("sides")
        if sides and side not in sides:
            continue
        filtered.append(addon)
    return filtered


def _write_rules_yaml(path: Path, rules: List[dict]) -> None:
    lines = ["rules:"]
    for rule in rules:
        lines.append(f"  - name: {rule['name']}")
        if rule.get("side"):
            lines.append(f"    side: {rule['side']}")
        if rule.get("status"):
            lines.append(f"    status: {rule['status']}")
        for key in ("entry_mode", "entry_price", "trigger_minutes", "window_min", "window_max"):
            if key in rule:
                lines.append(f"    {key}: {rule[key]}")
        lines.append("    conditions:")
        for cond in rule.get("conditions", []):
            lines.append(f"      - {cond}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_live_rules(path: Path) -> List[dict]:
    if not path.exists():
        return []
    rules: List[dict] = []
    current: dict | None = None
    in_conditions = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "rules:":
            continue
        if stripped.startswith("- name:"):
            name = stripped.split(":", 1)[1].strip()
            current = {"name": name, "conditions": []}
            rules.append(current)
            in_conditions = False
            continue
        if current is None:
            continue
        if stripped.startswith("conditions:"):
            in_conditions = True
            continue
        if in_conditions and stripped.startswith("- "):
            current["conditions"].append(stripped[2:].strip())
            continue
        if ":" in stripped and not stripped.startswith("- "):
            key, val = stripped.split(":", 1)
            current[key.strip()] = val.strip()
            in_conditions = False
    return rules


def _select_export_candidates(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    export_cfg = cfg.get("export", {})
    if not export_cfg.get("enabled", True):
        return pd.DataFrame()

    df = df[df["exportable"] == True]  # noqa: E712

    entry_mode = export_cfg.get("entry_mode")
    if entry_mode:
        df = df[df["entry_mode"] == entry_mode]
    entry_price = export_cfg.get("entry_price")
    if entry_price:
        df = df[df["entry_price"] == entry_price]
    trigger_minutes = export_cfg.get("trigger_minutes")
    if trigger_minutes is not None:
        df = df[df["trigger_minutes"] == int(trigger_minutes)]
    window_min = export_cfg.get("window_min")
    if window_min is not None:
        df = df[df["window_min"] == int(window_min)]
    window_max = export_cfg.get("window_max")
    if window_max is not None:
        df = df[df["window_max"] == int(window_max)]

    df = _rank(df)

    # Optional: keep bullish rules from being crowded out by bearish (or vice versa)
    max_rules_per_side = int(export_cfg.get("max_rules_per_side", 0) or 0)
    if max_rules_per_side > 0 and "direction" in df.columns and not df.empty:
        parts = []
        for direction, g in df.groupby("direction", sort=False):
            parts.append(g.head(max_rules_per_side))
        if parts:
            df = pd.concat(parts, ignore_index=True)
            df = _rank(df)

    max_rules = int(export_cfg.get("max_rules", 0) or 0)
    if max_rules > 0:
        df = df.head(max_rules)
    return df


async def main() -> None:
    parser = argparse.ArgumentParser(description="Rule factory: controlled stacking sweeps.")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG),
        help="Path to rule_factory.yaml (default: repo root).",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip updating live_rules.yaml.",
    )
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    timespan = cfg.get("timespan", "m1")
    entry_modes = cfg.get("entry_modes", [])
    windows = cfg.get("windows", [])
    guard = cfg.get("guardrails", {})

    bearish_bases = [_normalize_base(b) for b in cfg.get("bearish_bases", [])]
    bullish_bases = [_normalize_base(b) for b in cfg.get("bullish_bases", [])]
    addons = [_normalize_addon(a) for a in cfg.get("addons", [])]

    if not entry_modes or not windows:
        raise ValueError("entry_modes and windows must be defined in rule_factory.yaml")

    db = PolygonOptions()
    await db.connect()

    all_results: List[pd.DataFrame] = []
    pre_guardrails: List[pd.DataFrame] = []
    try:
        for side, bases in (("bearish", bearish_bases), ("bullish", bullish_bases)):
            side_addons = _filter_addons(addons, side)
            for base in bases:
                base_where = base.get("where")
                if not base_where:
                    continue
                for entry in entry_modes:
                    entry_mode = entry.get("mode", "setup")
                    trigger_minutes = int(entry.get("trigger_minutes", 3))
                    entry_price = entry.get("entry_price", "close")
                    for window in windows:
                        window_min = int(window.get("min", 1))
                        window_max = int(window.get("max", 10))

                        rules, meta_rows = _build_candidate_rules(
                            base=base,
                            side=side,
                            addons=side_addons,
                            entry_mode=entry_mode,
                            trigger_minutes=trigger_minutes,
                            entry_price=entry_price,
                            window_min=window_min,
                            window_max=window_max,
                            include_base_only=True,
                        )

                        batch_limit = int(guard.get("max_rules_per_query", 120))
                        stage_frames: List[pd.DataFrame] = []
                        for batch_rules, batch_meta in zip(
                            _chunked(rules, batch_limit),
                            _chunked(meta_rows, batch_limit),
                        ):
                            df_stage = await _evaluate_rules(
                                db=db,
                                rules=batch_rules,
                                meta_rows=batch_meta,
                                config=cfg,
                                entry_mode=entry_mode,
                                trigger_minutes=trigger_minutes,
                                entry_price=entry_price,
                                window_min=window_min,
                                window_max=window_max,
                                timespan=timespan,
                            )
                            stage_frames.append(df_stage)
                        stage_df_raw = pd.concat(stage_frames, ignore_index=True) if stage_frames else pd.DataFrame()
                        if not stage_df_raw.empty:
                            pre_guardrails.append(_rank(stage_df_raw).head(int(guard.get("pre_guardrails_limit", 300))))
                        stage_df = _apply_guardrails(stage_df_raw, guard)
                        stage_df = _rank(stage_df)

                        if not stage_df.empty:
                            all_results.append(stage_df)

                        if stage_df is None or stage_df.empty:


                            continue


                        if "addon_count" not in stage_df.columns:
                            continue
                        addon_only = stage_df[stage_df["addon_count"] == 1]
                        addon_only = _rank(addon_only)
                        # Build addon pairs/triples among top add-ons
                        max_addons_per_rule = int(guard.get("max_addons_per_rule", 2))
                        top_labels = _select_top_addon_labels(addon_only, side_addons, guard)
                        addon_lookup = {a["label"]: a for a in side_addons}

                        # Pairs (k=2)
                        if max_addons_per_rule >= 2 and len(top_labels) >= 2:
                            max_pair_combos = int(guard.get("max_pair_combos", 0))  # 0 = unlimited
                            addon_pairs: List[tuple[dict, dict]] = []

                            for label_a, label_b in itertools.combinations(top_labels, 2):
                                if label_a not in addon_lookup or label_b not in addon_lookup:
                                    continue
                                addon_pairs.append((addon_lookup[label_a], addon_lookup[label_b]))
                                if max_pair_combos > 0 and len(addon_pairs) >= max_pair_combos:
                                    break

                            pair_rules, pair_meta = _build_pair_rules(
                                base=base,
                                addon_pairs=addon_pairs,
                                side=side,
                                entry_mode=entry_mode,
                                trigger_minutes=trigger_minutes,
                                entry_price=entry_price,
                                window_min=window_min,
                                window_max=window_max,
                            )
                            pair_frames = []
                            for rules_chunk, meta_chunk in zip(_chunked(pair_rules, batch_limit), _chunked(pair_meta, batch_limit)):
                                df_chunk = await _evaluate_rules(
                                    db=db,
                                    rules=rules_chunk,
                                    meta_rows=meta_chunk,
                                    config=cfg,
                                    entry_mode=entry_mode,
                                    trigger_minutes=trigger_minutes,
                                    entry_price=entry_price,
                                    window_min=window_min,
                                    window_max=window_max,
                                    timespan=timespan,
                                )
                                pair_frames.append(df_chunk)
                                meta_rows.extend(meta_chunk)
                            pair_df = pd.concat(pair_frames, ignore_index=True) if pair_frames else pd.DataFrame(columns=_EVAL_COLS)
                            pair_df = _apply_guardrails(pair_df, guard)
                            pair_df = _rank(pair_df)
                            if not pair_df.empty:
                                all_results.append(pair_df)

                        # Triples (k=3)
                        if max_addons_per_rule >= 3 and len(top_labels) >= 3:
                            max_triple_combos = int(guard.get("max_triple_combos", guard.get("max_triple_candidates", 0)))
                            if max_triple_combos <= 0:
                                max_triple_combos = 250  # override in YAML if you want more/less

                            addon_triples: List[tuple[dict, dict, dict]] = []
                            for label_a, label_b, label_c in itertools.combinations(top_labels, 3):
                                if label_a not in addon_lookup or label_b not in addon_lookup or label_c not in addon_lookup:
                                    continue
                                addon_triples.append((addon_lookup[label_a], addon_lookup[label_b], addon_lookup[label_c]))
                                if len(addon_triples) >= max_triple_combos:
                                    break

                            trip_rules, trip_meta = _build_triple_rules(
                                base=base,
                                addon_triples=addon_triples,
                                side=side,
                                entry_mode=entry_mode,
                                trigger_minutes=trigger_minutes,
                                entry_price=entry_price,
                                window_min=window_min,
                                window_max=window_max,
                            )
                            trip_frames = []
                            for rules_chunk, meta_chunk in zip(_chunked(trip_rules, batch_limit), _chunked(trip_meta, batch_limit)):
                                df_chunk = await _evaluate_rules(
                                    db=db,
                                    rules=rules_chunk,
                                    meta_rows=meta_chunk,
                                    config=cfg,
                                    entry_mode=entry_mode,
                                    trigger_minutes=trigger_minutes,
                                    entry_price=entry_price,
                                    window_min=window_min,
                                    window_max=window_max,
                                    timespan=timespan,
                                )
                                trip_frames.append(df_chunk)
                                meta_rows.extend(meta_chunk)
                            trip_df = pd.concat(trip_frames, ignore_index=True) if trip_frames else pd.DataFrame(columns=_EVAL_COLS)
                            trip_df = _apply_guardrails(trip_df, guard)
                            trip_df = _rank(trip_df)
                            if not trip_df.empty:
                                all_results.append(trip_df)
    finally:
        await db.close()

    if not all_results:
        run_stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out_dir = RUNS_DIR / run_stamp
        out_dir.mkdir(parents=True, exist_ok=True)
        if pre_guardrails:
            pre_df = pd.concat(pre_guardrails, ignore_index=True).drop_duplicates(
                subset=["rule_id", "entry_mode", "window_min", "window_max"],
            )
            pre_df = _rank(pre_df)
            pre_path = out_dir / "run_report_pre_guardrails.csv"
            pre_df.to_csv(pre_path, index=False)
            print(f"Wrote pre-guardrails report: {pre_path}")
        print("No candidates passed guardrails.")
        return

    results_df = pd.concat(all_results, ignore_index=True).drop_duplicates(subset=["rule_id", "entry_mode", "window_min", "window_max"])
    results_df = _rank(results_df)

    run_stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = RUNS_DIR / run_stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "run_report.csv"
    results_df.to_csv(out_path, index=False)
    print(f"Wrote run report: {out_path}")

    if args.no_export:
        return

    export_df = _select_export_candidates(results_df, cfg)
    if export_df.empty:
        print("No exportable rules passed export gates.")
        return

    live_rules = _load_live_rules(LIVE_RULES_PATH)
    existing_names = {r.get("name") for r in live_rules}
    export_cfg = cfg.get("export", {})
    status = export_cfg.get("status", "pending_confirmation")

    added = 0
    for _, row in export_df.iterrows():
        name = row["rule_id"]
        if name in existing_names:
            continue
        conditions = row["live_conditions"]
        if isinstance(conditions, str):
            conditions = [conditions]
        rule_entry = {
            "name": name,
            "side": row["side"],
            "status": status,
            "entry_mode": row["entry_mode"],
            "entry_price": row["entry_price"],
            "trigger_minutes": int(row["trigger_minutes"]),
            "window_min": int(row["window_min"]),
            "window_max": int(row["window_max"]),
            "conditions": conditions,
        }
        live_rules.append(rule_entry)
        existing_names.add(name)
        added += 1

    _write_rules_yaml(LIVE_RULES_PATH, live_rules)
    print(f"Updated live_rules.yaml with {added} rules.")


if __name__ == "__main__":
    asyncio.run(main())
