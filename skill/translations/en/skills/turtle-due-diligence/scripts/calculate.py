"""Portable scenario arithmetic. Python 3.10+, standard library, no I/O except JSON.
Inputs are already sourced, attributed and currency-normalized by the researcher.
This helper verifies numbers, not evidence, sustainability or investment eligibility.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys


def number(data, key, minimum=None, positive=False):
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key}: a known finite number is required; missing is not zero")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{key}: must be finite")
    if minimum is not None and value < minimum or positive and value <= 0:
        raise ValueError(f"{key}: outside permitted range")
    return value


def legacy_cash_path(d):
    """Original six-year fixed-delta path from explicitly prepared K/F0/delta."""
    k = number(d, "cash_base")
    f0 = number(d, "starting_fcf", minimum=0)
    delta = number(d, "delta_base")
    if abs(delta) > .1 * f0 + 1e-12:
        raise ValueError("delta_base exceeds the original 10% starting-FCF bound")
    cap = number(d, "market_cap", positive=True)
    price = number(d, "price", positive=True)
    projection = d.get("projection")
    if projection not in {"baseline", "stop_growth", "declining"}:
        raise ValueError("projection must be baseline, stop_growth or declining")
    rate = d.get("annual_change_pct")
    upper = projection == "declining" and (rate is None or rate == 0)
    if projection == "baseline":
        if rate is not None:
            raise ValueError("baseline must not silently ignore annual_change_pct")
    elif projection == "stop_growth":
        if rate is not None and number(d, "annual_change_pct") != 0:
            raise ValueError("stop_growth accepts null or zero annual_change_pct")
        delta = min(delta, 0)
    else:
        if rate is not None:
            rate = number(d, "annual_change_pct")
            if rate > 0:
                raise ValueError("declining cannot use a positive rate")
        delta = min(delta, f0 * (rate or 0) / 100)
    raw = [f0 + t * delta for t in range(1, 7)]
    path = [max(0, v) for v in raw]
    return summarize_cash(k, f0, delta, path, raw, cap, price, upper, "legacy_reference")


def cash_path(d):
    """Use six prepared attributable annual cash estimates without clipping or slope."""
    k = number(d, "cash_base")
    cap = number(d, "market_cap", positive=True)
    price = number(d, "price", positive=True)
    values = d.get("annual_fcf")
    if not isinstance(values, list) or len(values) != 6:
        raise ValueError("annual_fcf: exactly six annual cash estimates are required")
    path = [number({"annual_fcf": value}, "annual_fcf") for value in values]
    return summarize_cash(k, path[0], None, path, path, cap, price, False,
                          "normalized_six_year_forecast")


def summarize_cash(k, f0, delta, path, raw, cap, price, upper, basis):
    total = math.fsum(path)
    recovery = k + total
    surplus = recovery - cap
    payback = 0.0 if k >= cap else None
    prior = k
    if payback is None:
        for year, value in enumerate(path, 1):
            if prior + value >= cap and value > 0:
                payback = year - 1 + (cap - prior) / value
                break
            prior += value
    return {
        "calculation_basis": basis,
        "cash_base": k, "starting_fcf": f0, "annual_delta_used": delta,
        "projected_fcf_6y": path, "raw_unfloored_path": raw,
        "negative_fcf_floored": path != raw,
        "recovery_6y": recovery, "coverage_6y": recovery / cap,
        "flat_coverage_6y": (k + 6 * f0) / cap,
        "support_price_6y": price * max(0, recovery) / cap,
        "payback_years_within_six": payback,
        "arithmetic_threshold_met": recovery >= cap,
        "reference_upper_bound": upper,
        "cash_surplus": surplus,
        "annual_fcf_reduction_to_boundary": max(0, surplus) / 6,
        "decline_capacity_pct": 100 * min(1, max(0, surplus / total)) if total > 0 else None,
        "cash_base_covers_threshold": k >= cap,
    }


def returns(d):
    """Ordinary dividends then qualifying cancellation buybacks share pre-tax cash."""
    owner = number(d, "owner_cash", minimum=0)
    dividends = number(d, "ordinary_dividends", minimum=0)
    buybacks = number(d, "qualified_buybacks", minimum=0)
    tax = number(d, "dividend_tax_pct", minimum=0)
    if tax > 100:
        raise ValueError("dividend_tax_pct must be in [0, 100]")
    cap = number(d, "market_cap", positive=True)
    price = number(d, "price", positive=True)
    da = min(dividends, owner)
    ba = min(buybacks, max(0, owner - da))
    net = da * (1 - tax / 100) + ba
    gg = net / cap * 100
    ii = d.get("required_return_pct")
    result = {"dividends_allocated": da, "buybacks_allocated": ba,
              "shareholder_cash_net": net, "return_pct": gg,
              "arithmetic_threshold_met": None, "prices": None,
              "distribution_decline_capacity_pct": None}
    if ii is not None:
        ii = number(d, "required_return_pct", positive=True)
        result.update(arithmetic_threshold_met=gg >= ii,
                      distribution_decline_capacity_pct=100 * max(0, 1 - ii / gg) if gg > 0 else 0)
        if gg > 0:
            observe, heavy = price * gg / ii, price * gg / max(10, ii)
            result["prices"] = {"observe": observe, "heavy": heavy,
                                "standard": (observe + heavy) / 2}
    return result


def at_least(value, threshold):
    return value >= threshold or math.isclose(value, threshold, rel_tol=1e-12, abs_tol=1e-12)


def routing(d):
    """Optional candidate resource routing, never business quality or buy approval."""
    values = [d.get(k) for k in ("flat_coverage_6y", "conditional_return_pct", "required_return_pct")]
    if any(v is None for v in values):
        return {"route": "needs_input", "strict_cash_met": None, "strict_return_met": None}
    coverage = number(d, "flat_coverage_6y")
    ret = number(d, "conditional_return_pct")
    required = number(d, "required_return_pct", positive=True)
    return {"route": "research" if at_least(coverage, .65) and at_least(ret, .65 * required) else "defer",
            "strict_cash_met": coverage >= 1, "strict_return_met": ret >= required}


def calculate(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    operation = data.get("operation")
    dispatch = {"cash_path": cash_path, "legacy_cash_path": legacy_cash_path, "returns": returns, "routing": routing}
    if operation not in dispatch:
        raise ValueError("operation must be cash_path, legacy_cash_path, returns or routing")
    if not isinstance(data.get("inputs"), dict):
        raise ValueError("inputs must be an object")
    allowed = {
        "cash_path": {"cash_base", "annual_fcf", "market_cap", "price"},
        "legacy_cash_path": {"cash_base", "starting_fcf", "delta_base", "projection", "annual_change_pct", "market_cap", "price"},
        "returns": {"owner_cash", "ordinary_dividends", "qualified_buybacks", "dividend_tax_pct", "market_cap", "price", "required_return_pct"},
        "routing": {"flat_coverage_6y", "conditional_return_pct", "required_return_pct"},
    }
    unknown = set(data["inputs"]) - allowed[operation]
    if unknown:
        raise ValueError("Unsupported inputs cannot be silently ignored: " + ", ".join(sorted(unknown)))
    result = dispatch[operation](data["inputs"])
    # Reject derived overflows as well as nonfinite inputs.
    json.dumps(result, allow_nan=False)
    return {"method": "5.2.2", "operation": operation, "inputs": data["inputs"],
            "result": result, "evidence_verified": False,
            "strategy_eligibility": "not_assessed",
            "limits": "Arithmetic only. Preserve source dates, currency, attribution, sustainability and expiry separately. Headroom is not a loss forecast; the two margins cannot be added."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON path, or - for stdin")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        output = calculate(json.loads(raw))
        print(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, TypeError, OverflowError, OSError) as exc:
        print(json.dumps({"status": "invalid_input", "error": str(exc)}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
