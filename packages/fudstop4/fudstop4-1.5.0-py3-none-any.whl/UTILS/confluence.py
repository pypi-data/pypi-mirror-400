from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional


def _is_number(value: Optional[float]) -> bool:
    return value is not None and isinstance(value, (int, float)) and math.isfinite(value)


def _pct_diff(value: Optional[float], base: Optional[float]) -> Optional[float]:
    if not _is_number(value) or not _is_number(base) or base == 0:
        return None
    return ((value - base) / base) * 100.0


def _signal_from_points(points: int) -> str:
    if points > 0:
        return "bullish"
    if points < 0:
        return "bearish"
    return "neutral"


@dataclass
class FactorResult:
    signal: str
    points: int
    reason: str
    meta: Optional[Dict[str, float]] = None

    def to_columns(self, prefix: str) -> Dict[str, object]:
        out: Dict[str, object] = {
            f"{prefix}_signal": self.signal,
            f"{prefix}_points": self.points,
            f"{prefix}_reason": self.reason,
            f"{prefix}_confluence_score": self.points,
        }
        if self.meta:
            for key, value in self.meta.items():
                out[f"{prefix}_{key}"] = value
        return out


def score_price_target(current: Optional[float],
                       mean: Optional[float],
                       median: Optional[float],
                       high: Optional[float],
                       low: Optional[float]) -> FactorResult:
    points = 0
    reasons = []
    meta: Dict[str, float] = {}

    upside_candidates = [
        pct for pct in (_pct_diff(mean, current), _pct_diff(median, current))
        if pct is not None
    ]
    upside_pct = max(upside_candidates) if upside_candidates else None

    if upside_pct is not None:
        meta["target_upside_pct"] = float(upside_pct)
        if upside_pct >= 25:
            points += 3
            reasons.append(f"avg target {upside_pct:.1f}% above price")
        elif upside_pct >= 15:
            points += 2
            reasons.append(f"avg target {upside_pct:.1f}% above price")
        elif upside_pct >= 8:
            points += 1
            reasons.append(f"avg target modest {upside_pct:.1f}% above price")
        elif upside_pct <= -20:
            points -= 3
            reasons.append(f"targets sit {abs(upside_pct):.1f}% below price")
        elif upside_pct <= -10:
            points -= 2
            reasons.append(f"targets sit {abs(upside_pct):.1f}% below price")
        elif upside_pct <= -5:
            points -= 1
            reasons.append("targets slightly below price")

    if _is_number(low) and _is_number(current):
        downside_pct = _pct_diff(low, current)
        if downside_pct is not None:
            meta["target_low_pct_vs_price"] = float(downside_pct)
            if downside_pct >= -2:
                points += 1
                reasons.append("even low target sits near or above price")
    if _is_number(high) and _is_number(current):
        high_pct = _pct_diff(high, current)
        if high_pct is not None and high_pct <= 0:
            points -= 1
            reasons.append("street high already below price")

    if not reasons:
        reasons.append("targets roughly in line with price")

    signal = _signal_from_points(points)
    return FactorResult(signal=signal, points=points, reason="; ".join(reasons), meta=meta or None)


def score_cost_distribution(profit_ratio: Optional[float]) -> FactorResult:
    if not _is_number(profit_ratio):
        return FactorResult("neutral", 0, "no profit ratio data")

    ratio = float(profit_ratio)
    points = 0
    reasons = [f"{ratio:.1f}% of holders in profit"]

    if ratio <= 20:
        points += 3
        reasons.append("vast majority under water (contrarian fuel)")
    elif ratio <= 35:
        points += 2
        reasons.append("only a third green -> prone to relief pops")
    elif ratio <= 45:
        points += 1
        reasons.append("slightly oversold positioning")
    elif ratio >= 90:
        points -= 3
        reasons.append("crowded winners ripe for locking gains")
    elif ratio >= 80:
        points -= 2
        reasons.append("most holders deep in profit")
    elif ratio >= 65:
        points -= 1
        reasons.append("moderate profit taking risk")

    return FactorResult(signal=_signal_from_points(points),
                        points=points,
                        reason="; ".join(reasons),
                        meta={"profit_ratio": ratio})


def score_options_flow(call_volume: float,
                       put_volume: float,
                       call_oi: float,
                       put_oi: float,
                       label: str = "options_flow") -> FactorResult:
    call_volume = float(call_volume or 0)
    put_volume = float(put_volume or 0)
    call_oi = float(call_oi or 0)
    put_oi = float(put_oi or 0)

    vol_ratio = (call_volume + 1e-9) / (put_volume + 1e-9)
    oi_ratio = (call_oi + 1e-9) / (put_oi + 1e-9)

    points = 0
    reasons = []

    if vol_ratio >= 1.7:
        points += 3
        reasons.append("call volume running >1.7x puts")
    elif vol_ratio >= 1.3:
        points += 2
        reasons.append("call volume outpacing puts")
    elif vol_ratio >= 1.15:
        points += 1
        reasons.append("mild call skew in volume")
    elif vol_ratio <= 1 / 1.7:
        points -= 3
        reasons.append("put volume running >1.7x calls")
    elif vol_ratio <= 1 / 1.3:
        points -= 2
        reasons.append("put volume outpacing calls")
    elif vol_ratio <= 1 / 1.15:
        points -= 1
        reasons.append("mild put skew in volume")

    if oi_ratio >= 1.4:
        points += 2
        reasons.append("call OI loaded relative to puts")
    elif oi_ratio >= 1.2:
        points += 1
        reasons.append("call OI leaning bullish")
    elif oi_ratio <= 0.7:
        points -= 2
        reasons.append("put OI stacked vs calls")
    elif oi_ratio <= 0.85:
        points -= 1
        reasons.append("slight put OI tilt")

    meta = {
        f"{label}_call_volume": call_volume,
        f"{label}_put_volume": put_volume,
        f"{label}_call_put_volume_ratio": vol_ratio,
        f"{label}_call_put_oi_ratio": oi_ratio,
        f"{label}_call_oi": call_oi,
        f"{label}_put_oi": put_oi,
    }

    if not reasons:
        reasons.append("balanced call/put flow")

    return FactorResult(signal=_signal_from_points(points),
                        points=points,
                        reason="; ".join(reasons),
                        meta=meta)


def score_gex(total_gex: Optional[float],
              spot_price: Optional[float],
              flip_strike: Optional[float] = None) -> FactorResult:
    if not _is_number(total_gex):
        return FactorResult("neutral", 0, "no GEX data")

    total_gex = float(total_gex)
    spot_price = float(spot_price or 0)
    magnitude_billions = abs(total_gex) / 1_000_000_000

    points = 0
    reasons = [f"total GEX {total_gex/1e9:.2f}B"]

    if total_gex > 0:
        if magnitude_billions >= 5:
            points += 3
        elif magnitude_billions >= 2:
            points += 2
        elif magnitude_billions >= 0.5:
            points += 1
        reasons.append("positive gamma cushions dips")
    else:
        if magnitude_billions >= 5:
            points -= 3
        elif magnitude_billions >= 2:
            points -= 2
        elif magnitude_billions >= 0.5:
            points -= 1
        reasons.append("negative gamma amplifies moves")

    meta: Dict[str, float] = {
        "total_gex": total_gex,
        "spot_price": spot_price,
        "gex_magnitude_billions": magnitude_billions,
    }

    if _is_number(flip_strike) and spot_price > 0:
        flip_diff = ((spot_price - float(flip_strike)) / spot_price) * 100.0
        meta["gamma_flip_pct_vs_spot"] = flip_diff
        if total_gex < 0 and flip_diff <= -1:
            points -= 1
            reasons.append("spot below largest negative gamma strike")
        elif total_gex > 0 and flip_diff >= 1:
            points += 1
            reasons.append("spot well above flip strike")

    return FactorResult(signal=_signal_from_points(points),
                        points=points,
                        reason="; ".join(reasons),
                        meta=meta)


def score_iv_skew(skew_type: str,
                  skew_diff: Optional[float],
                  close_price: Optional[float],
                  iv: Optional[float]) -> FactorResult:
    if skew_diff is None or close_price in (None, 0):
        return FactorResult("neutral", 0, "no skew data")

    pct = (float(skew_diff) / float(close_price)) * 100.0
    abs_pct = abs(pct)
    iv = float(iv or 0)
    points = 0
    reasons = []

    if skew_type == "call_skew" and pct > 0:
        if abs_pct >= 5:
            points += 3
        elif abs_pct >= 3:
            points += 2
        elif abs_pct >= 1.5:
            points += 1
        reasons.append(f"call skew strike {abs_pct:.1f}% above spot")
    elif skew_type == "put_skew":
        if abs_pct >= 5:
            points -= 3
        elif abs_pct >= 3:
            points -= 2
        elif abs_pct >= 1.5:
            points -= 1
        reasons.append(f"put skew strike {abs_pct:.1f}% below spot")

    if iv >= 0.7:
        bump = 1 if points > 0 else -1 if points < 0 else 0
        if bump:
            points += bump
            reasons.append("elevated IV makes skew more meaningful")

    if not reasons:
        reasons.append("skew balanced around spot")

    meta = {
        "skew_pct_vs_spot": pct,
        "skew_type_numeric": 1 if skew_type == "call_skew" else -1 if skew_type == "put_skew" else 0,
        "skew_iv": iv,
    }

    return FactorResult(signal=_signal_from_points(points),
                        points=points,
                        reason="; ".join(reasons),
                        meta=meta)


def score_multi_quote(close_price: Optional[float],
                      open_price: Optional[float],
                      volume: Optional[float],
                      avg_vol_10d: Optional[float],
                      avg_vol_3m: Optional[float],
                      day_change_pct: Optional[float] = None) -> FactorResult:
    if not _is_number(close_price) or not _is_number(open_price) or open_price == 0:
        return FactorResult("neutral", 0, "insufficient quote data")

    close_price = float(close_price)
    open_price = float(open_price)
    intraday_ret = ((close_price - open_price) / open_price) * 100.0
    volume_ratio_10d = (float(volume or 0) + 1e-9) / (float(avg_vol_10d or 0) + 1e-9)
    volume_ratio_3m = (float(volume or 0) + 1e-9) / (float(avg_vol_3m or 0) + 1e-9)

    points = 0
    reasons = []

    if intraday_ret >= 2 and volume_ratio_10d >= 1.5:
        points += 3
        reasons.append("price up >2% on 1.5x 10d volume")
    elif intraday_ret >= 1 and volume_ratio_10d >= 1.2:
        points += 2
        reasons.append("price up >1% on rising volume")
    elif intraday_ret >= 0.5 and volume_ratio_10d >= 1.1:
        points += 1
        reasons.append("modest positive momentum")
    elif intraday_ret <= -2 and volume_ratio_10d >= 1.5:
        points -= 3
        reasons.append("selloff >2% on heavy volume")
    elif intraday_ret <= -1 and volume_ratio_10d >= 1.2:
        points -= 2
        reasons.append("price down >1% on rising volume")
    elif intraday_ret <= -0.5 and volume_ratio_10d >= 1.1:
        points -= 1
        reasons.append("soft momentum lower")

    if day_change_pct is not None and _is_number(day_change_pct):
        if day_change_pct >= 3:
            points += 1
            reasons.append("headline change >3%")
        elif day_change_pct <= -3:
            points -= 1
            reasons.append("headline drop >3%")

    if not reasons:
        reasons.append("flat intraday trend")

    meta = {
        "intraday_return_pct": intraday_ret,
        "volume_vs_10d": volume_ratio_10d,
        "volume_vs_3m": volume_ratio_3m,
    }

    return FactorResult(signal=_signal_from_points(points),
                        points=points,
                        reason="; ".join(reasons),
                        meta=meta)


def score_volume_breakdown(buy_pct: Optional[float],
                           sell_pct: Optional[float],
                           neutral_pct: Optional[float]) -> FactorResult:
    if not all(_is_number(pct) for pct in (buy_pct, sell_pct, neutral_pct)):
        return FactorResult("neutral", 0, "no volume split data")

    buy_pct = float(buy_pct)
    sell_pct = float(sell_pct)
    neutral_pct = float(neutral_pct)

    points = 0
    reasons = []

    if buy_pct >= 60:
        points += 3
        reasons.append("buy volume >=60% (strong accumulation)")
    elif buy_pct >= 55:
        points += 2
        reasons.append("buy volume >55%")
    elif buy_pct >= 52:
        points += 1
        reasons.append("slight accumulation tilt")

    if sell_pct >= 60:
        points -= 3
        reasons.append("sell volume >=60% (distribution)")
    elif sell_pct >= 55:
        points -= 2
        reasons.append("sell volume >55%")
    elif sell_pct >= 52:
        points -= 1
        reasons.append("mild distribution tilt")

    if neutral_pct >= 60 and points == 0:
        reasons.append("majority neutral flow")

    meta = {
        "buy_pct": buy_pct,
        "sell_pct": sell_pct,
        "neutral_pct": neutral_pct,
    }

    if not reasons:
        reasons.append("balanced tape")

    return FactorResult(signal=_signal_from_points(points),
                        points=points,
                        reason="; ".join(reasons),
                        meta=meta)


# -----------------------------
# Fundamental / meta scorers
# -----------------------------

def _safe_ratio(numer: Optional[float], denom: Optional[float]) -> Optional[float]:
    if not _is_number(numer) or not _is_number(denom) or float(denom) == 0:
        return None
    return float(numer) / float(denom)


def score_analyst_ratings(strong_buy: Optional[float],
                          buy: Optional[float],
                          hold: Optional[float],
                          underperform: Optional[float],
                          sell: Optional[float]) -> FactorResult:
    counts = {
        "strong_buy": float(strong_buy or 0),
        "buy": float(buy or 0),
        "hold": float(hold or 0),
        "underperform": float(underperform or 0),
        "sell": float(sell or 0),
    }
    coverage = sum(counts.values())
    if coverage == 0:
        return FactorResult("neutral", 0, "no analyst coverage")

    bullish = counts["strong_buy"] * 2 + counts["buy"]
    bearish = counts["sell"] * 1.5 + counts["underperform"]
    net = bullish - bearish
    skew = net / max(coverage, 1e-6)

    points = 0
    reasons = [f"{int(coverage)} analysts total, bias {skew:+.2f}"]

    if skew >= 1.0:
        points += 3
        reasons.append("heavy strong buy skew")
    elif skew >= 0.5:
        points += 2
        reasons.append("buy-leaning consensus")
    elif skew >= 0.2:
        points += 1
        reasons.append("mild bullish tilt")
    elif skew <= -1.0:
        points -= 3
        reasons.append("heavy sell/underperform skew")
    elif skew <= -0.5:
        points -= 2
        reasons.append("bearish consensus")
    elif skew <= -0.2:
        points -= 1
        reasons.append("mild bearish tilt")
    else:
        reasons.append("roughly balanced coverage")

    return FactorResult(
        signal=_signal_from_points(points),
        points=points,
        reason="; ".join(reasons),
        meta={"analyst_skew": skew, "analyst_coverage": coverage},
    )


def score_earnings_setup(eps_estimate: Optional[float],
                         eps_last: Optional[float],
                         revenue_estimate: Optional[float],
                         revenue_last: Optional[float]) -> FactorResult:
    points = 0
    reasons = []

    eps_delta = _pct_diff(eps_estimate, eps_last)
    rev_delta = _pct_diff(revenue_estimate, revenue_last)

    if eps_delta is not None:
        if eps_delta >= 25:
            points += 2
            reasons.append(f"EPS est +{eps_delta:.1f}% vs last")
        elif eps_delta >= 10:
            points += 1
            reasons.append(f"EPS est trending higher ({eps_delta:.1f}%)")
        elif eps_delta <= -15:
            points -= 2
            reasons.append(f"EPS est -{abs(eps_delta):.1f}% vs last")
        elif eps_delta <= -5:
            points -= 1
            reasons.append(f"EPS est soft ({eps_delta:.1f}%)")

    if rev_delta is not None:
        if rev_delta >= 15:
            points += 2
            reasons.append(f"Revenue est +{rev_delta:.1f}% vs last")
        elif rev_delta >= 5:
            points += 1
            reasons.append(f"Revenue est rising ({rev_delta:.1f}%)")
        elif rev_delta <= -10:
            points -= 2
            reasons.append(f"Revenue est -{abs(rev_delta):.1f}% vs last")
        elif rev_delta <= -3:
            points -= 1
            reasons.append(f"Revenue est soft ({rev_delta:.1f}%)")

    if not reasons:
        reasons.append("estimates roughly flat to prior")

    meta = {}
    if eps_delta is not None:
        meta["eps_estimate_vs_last_pct"] = eps_delta
    if rev_delta is not None:
        meta["revenue_estimate_vs_last_pct"] = rev_delta

    return FactorResult(
        signal=_signal_from_points(points),
        points=points,
        reason="; ".join(reasons),
        meta=meta or None,
    )


def score_financial_health(current_ratio: Optional[float],
                           debt_to_equity: Optional[float],
                           fcf_margin: Optional[float],
                           revenue_growth_pct: Optional[float],
                           net_margin_pct: Optional[float]) -> FactorResult:
    points = 0
    reasons = []
    meta: Dict[str, float] = {}

    if _is_number(current_ratio):
        cr = float(current_ratio)
        meta["current_ratio"] = cr
        if cr >= 2.0:
            points += 2
            reasons.append("current ratio >=2 (solid liquidity)")
        elif cr >= 1.5:
            points += 1
            reasons.append("current ratio healthy")
        elif cr < 1.0:
            points -= 2
            reasons.append("current ratio <1 (liquidity risk)")

    if _is_number(debt_to_equity):
        dte = float(debt_to_equity)
        meta["debt_to_equity"] = dte
        if dte <= 0.5:
            points += 2
            reasons.append("low leverage")
        elif dte <= 1.0:
            points += 1
            reasons.append("manageable leverage")
        elif dte >= 3.0:
            points -= 3
            reasons.append("high leverage burden")
        elif dte >= 2.0:
            points -= 2
            reasons.append("elevated leverage")

    if _is_number(fcf_margin):
        fcf = float(fcf_margin)
        meta["fcf_margin_pct"] = fcf
        if fcf >= 10:
            points += 2
            reasons.append("double-digit FCF margin")
        elif fcf >= 5:
            points += 1
            reasons.append("positive FCF margin")
        elif fcf <= -5:
            points -= 2
            reasons.append("burning cash")

    if _is_number(revenue_growth_pct):
        rg = float(revenue_growth_pct)
        meta["revenue_growth_pct"] = rg
        if rg >= 15:
            points += 2
            reasons.append("revenue growing >15%")
        elif rg >= 5:
            points += 1
            reasons.append("revenue trending up")
        elif rg <= -5:
            points -= 2
            reasons.append("revenue contracting")

    if _is_number(net_margin_pct):
        nm = float(net_margin_pct)
        meta["net_margin_pct"] = nm
        if nm >= 15:
            points += 2
            reasons.append("healthy net margin")
        elif nm >= 8:
            points += 1
            reasons.append("positive net margin")
        elif nm <= 0:
            points -= 1
            reasons.append("negative profitability")
        if nm <= -5:
            points -= 1
            reasons.append("deep net losses")

    if not reasons:
        reasons.append("insufficient financials")

    return FactorResult(
        signal=_signal_from_points(points),
        points=points,
        reason="; ".join(reasons),
        meta=meta or None,
    )


def score_itm_balance(call_itm_dollars: Optional[float],
                      put_itm_dollars: Optional[float]) -> FactorResult:
    call_val = float(call_itm_dollars or 0)
    put_val = float(put_itm_dollars or 0)

    ratio = _safe_ratio(call_val, put_val)
    points = 0
    reasons = []

    if ratio is not None:
        if ratio >= 1.8:
            points += 2
            reasons.append("ITM $ skewed to calls")
        elif ratio >= 1.3:
            points += 1
            reasons.append("more ITM call value than puts")
        elif ratio <= 1 / 1.8:
            points -= 2
            reasons.append("ITM $ skewed to puts")
        elif ratio <= 1 / 1.3:
            points -= 1
            reasons.append("more ITM put value than calls")
    else:
        reasons.append("no ITM skew data")

    meta = {"call_itm_dollars": call_val, "put_itm_dollars": put_val}
    if ratio is not None:
        meta["itm_call_put_ratio"] = ratio

    return FactorResult(
        signal=_signal_from_points(points),
        points=points,
        reason="; ".join(reasons),
        meta=meta,
    )


def score_gap_profile(gap_type: str,
                      gap_low_pct: Optional[float],
                      gap_high_pct: Optional[float]) -> FactorResult:
    points = 0
    reasons = []
    gap_type = (gap_type or "").lower()

    low = float(gap_low_pct) if _is_number(gap_low_pct) else None
    high = float(gap_high_pct) if _is_number(gap_high_pct) else None

    if gap_type == "up" and high is not None:
        if high < 0:
            points += 2
            reasons.append("unfilled up-gap below spot (support)")
        elif high <= 2:
            points += 1
            reasons.append("nearby up-gap support")
    elif gap_type == "down" and low is not None:
        if low > 0:
            points -= 2
            reasons.append("unfilled down-gap above spot (supply)")
        elif low >= -2:
            points -= 1
            reasons.append("nearby down-gap risk")

    if not reasons:
        reasons.append("gap neutral to price")

    meta = {}
    if low is not None:
        meta["gap_low_pct"] = low
    if high is not None:
        meta["gap_high_pct"] = high

    return FactorResult(
        signal=_signal_from_points(points),
        points=points,
        reason="; ".join(reasons),
        meta=meta or None,
    )


def score_volatility_profile(volatile_rank: Optional[str],
                             call_vol: Optional[float],
                             put_vol: Optional[float]) -> FactorResult:
    rank = (volatile_rank or "").lower()
    call_vol = float(call_vol or 0)
    put_vol = float(put_vol or 0)
    vol_ratio = _safe_ratio(call_vol, put_vol)

    points = 0
    reasons = []

    if rank in {"absolutely still", "quiet"}:
        points += 1
        reasons.append("low realized volatility backdrop")
    elif rank in {"volatile", "extremely volatile"}:
        points -= 1
        reasons.append("elevated volatility regime")

    if vol_ratio is not None:
        if vol_ratio >= 1.5:
            points += 2
            reasons.append("call volume >1.5x puts")
        elif vol_ratio >= 1.2:
            points += 1
            reasons.append("call volume leaning bullish")
        elif vol_ratio <= 1 / 1.5:
            points -= 2
            reasons.append("put volume >1.5x calls")
        elif vol_ratio <= 1 / 1.2:
            points -= 1
            reasons.append("put volume leaning bearish")

    if not reasons:
        reasons.append("balanced volatility profile")

    meta = {"call_volume": call_vol, "put_volume": put_vol}
    if vol_ratio is not None:
        meta["call_put_volume_ratio"] = vol_ratio
    if rank:
        meta["volatile_rank"] = rank

    return FactorResult(
        signal=_signal_from_points(points),
        points=points,
        reason="; ".join(reasons),
        meta=meta,
    )
