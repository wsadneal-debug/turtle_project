"""Deterministic arithmetic for a manually selected asset valuation ledger.

All monetary inputs are in basic units of ``currency``. Research determines
economic assumptions; this module only resolves selected rows and arithmetic.
"""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Any


KINDS = {"asset", "liability", "nci", "preferred"}


def _number(value: Any, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{label} 必须是数值")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} 必须是有限数值")
    return result


def _formula(formula: dict) -> float:
    """A few ordinary calculations, rather than an expression evaluator."""
    method = formula["method"]
    if method == "quantity_cost":
        return float(formula["quantity"]) * float(formula["unit_cost"])
    if method == "factor":
        return float(formula["base"]) * float(formula["factor"])
    if method == "net":
        return float(formula["gross"]) - float(formula.get("deduction", 0))
    if method == "ownership":
        return float(formula["net_value"]) * float(formula["share"])
    if method == "present_value":
        return sum(float(flow["amount"]) / (1 + float(formula["rate"])) ** float(flow["years"])
                   for flow in formula["cashflows"])
    raise ValueError(f"不支持的计算方法：{method}")


def _totals(items: list[dict], shares: float | None, scenario: str = "base") -> dict:
    amounts = dict.fromkeys(KINDS, 0.0)
    operating_assets = operating_liabilities = 0.0
    measured_count = 0
    for item in items:
        if not item["included"] or item["value"] is None:
            continue
        measured_count += 1
        value = item["value"]
        if scenario != "base":
            # low/high describe each amount, not the sign of its contribution.
            boundary = scenario if item["kind"] == "asset" else {"low": "high", "high": "low"}[scenario]
            value = item.get(boundary) if item.get(boundary) is not None else value
        amounts[item["kind"]] += value
        if item.get("operating"):
            if item["kind"] == "asset":
                operating_assets += value
            elif item["kind"] == "liability":
                operating_liabilities += value
    equity = (amounts["asset"] - amounts["liability"] - amounts["nci"] - amounts["preferred"]
              if measured_count else None)
    return {
        "operating_assets": operating_assets,
        "operating_liabilities": operating_liabilities,
        "operating_net_assets": operating_assets - operating_liabilities,
        "total_assets": amounts["asset"],
        "total_liabilities": amounts["liability"],
        "minority_interests": amounts["nci"],
        "preferred_interests": amounts["preferred"],
        "equity_value": equity,
        "per_share": equity / shares if equity is not None and shares is not None and shares > 0 else None,
    }


def _base_calculate(valuation: dict) -> dict:
    """Calculate the three asset-value views, optional bounds and book bridge.

    ``value`` always wins over an optional formula. For ``basis='book'`` a
    missing value uses book_value. Omitted and unmeasured rows remain visible
    without failing the whole run. When both an ancestor and descendant are
    selected, a measured ancestor is retained and descendants only displayed.
    To adopt children instead, set the parent include=false and separately
    estimate any balance not covered by the children.
    """
    currency = valuation.get("currency")
    warnings = []
    items = []
    ids = set()
    for original in valuation.get("items", []):
        item = dict(original)
        identifier = item["id"]
        if identifier in ids:
            raise ValueError(f"项目 id 重复：{identifier}")
        ids.add(identifier)
        if item["kind"] not in KINDS:
            raise ValueError(f"未知项目类别：{item['kind']}")
        if item.get("currency") and currency and item["currency"] != currency:
            raise ValueError(f"{identifier} 币种不同，需先换算至 {currency}")
        if item.get("unit") not in (None, "currency", "basic", currency):
            raise ValueError(f"{identifier} 金额必须先换算为基本货币单位，收到 {item['unit']}")
        for field in ("book_value", "value", "low", "high"):
            item[field] = _number(item.get(field), f"{identifier}.{field}")
        item["included"] = bool(item.get("include", True))
        item["effective_basis"] = item.get("basis", "estimate")
        if item.get("basis") == "omitted":
            item["value"] = None
        elif item["value"] is None:
            if item.get("formula"):
                item["value"] = _number(_formula(item["formula"]), f"{identifier}.formula")
            elif item.get("basis") == "book":
                item["value"] = item["book_value"]
        if item["low"] is not None and item["high"] is not None and item["low"] > item["high"]:
            raise ValueError(f"{identifier} low 不能高于 high")
        items.append(item)

    by_id = {item["id"]: item for item in items}
    selected = [item for item in items if item["included"] and item.get("basis") != "omitted"]
    excluded = {}
    for item in selected:
        parent_id = item.get("parent_id")
        visited = {item["id"]}
        while parent_id in by_id:
            if parent_id in visited:
                raise ValueError("parent_id 存在循环，无法选择计值粒度")
            visited.add(parent_id)
            parent = by_id[parent_id]
            if parent["included"] and parent["value"] is not None:
                excluded[item["id"]] = parent_id
            parent_id = parent.get("parent_id")
    for identifier, parent_id in excluded.items():
        by_id[identifier]["included"] = False
        warnings.append(f"{by_id[identifier].get('name', identifier)} 与父项 {by_id[parent_id].get('name', parent_id)} 同时入选，保留父项金额，子项仅展示不累加；如采用子项，须排除父项并另列未拆明余额。")

    missing_items = []
    for item in items:
        if item["included"] and item["value"] is None:
            missing_items.append({"id": item["id"], "name": item.get("name", item["id"]),
                                  "kind": item["kind"], "basis": item.get("basis"),
                                  "reason": item.get("reason", ""), "material": item.get("material", False)})
            verb = "明确略去" if item.get("basis") == "omitted" else "尚未计量"
            warnings.append(f"{item.get('name', item['id'])} {verb}，未进入总值。{item.get('reason', '')}")

    shares = _number(valuation.get("shares"), "shares")
    if shares is None or shares <= 0:
        warnings.append("缺少有效的同口径发行在外普通股数，每股结果未计算。")
    result = _totals(items, shares)
    if result["equity_value"] is None:
        warnings.append("无已选且已计量项目，尚未形成企业资产价值；分项零合计不代表企业价值为零。")
    result.update(currency=currency, shares=shares, items=items, warnings=warnings, missing_items=missing_items)
    if any(item["included"] and item["value"] is not None and (item["low"] is not None or item["high"] is not None) for item in items):
        result["scenarios"] = {name: _totals(items, shares, name) for name in ("low", "high")}

    # A book bridge is available only for the same selected, measured scope.
    measured = [item for item in items if item["included"] and item["value"] is not None]
    if measured and all(item["book_value"] is not None for item in measured):
        book_equity = 0.0
        deltas = dict.fromkeys(KINDS, 0.0)
        for item in measured:
            sign = 1 if item["kind"] == "asset" else -1
            book_equity += sign * item["book_value"]
            deltas[item["kind"]] += item["value"] - item["book_value"]
        bridge = book_equity + deltas["asset"] - deltas["liability"] - deltas["nci"] - deltas["preferred"]
        result["book_bridge"] = {"book_equity": book_equity, "asset_adjustment": deltas["asset"],
                                  "liability_adjustment": deltas["liability"], "nci_adjustment": deltas["nci"],
                                  "preferred_adjustment": deltas["preferred"], "equity_value": bridge,
                                  "difference": bridge - result["equity_value"], "scope": "已选且已计量项目"}
    else:
        result["book_bridge"] = None
    return result


def _joint_scenario(valuation: dict, scenario: Any, baseline_items: list[dict]) -> dict:
    """Apply explicit paired amounts to a copy; prose/ranges are not executions."""
    record = {"name": scenario.get("name", "未命名情景") if isinstance(scenario, dict) else "未命名情景",
              "parameters": deepcopy(scenario), "status": "discussion_only", "calculation": None}
    if not isinstance(scenario, dict):
        record["reason"] = "仅有讨论内容，未计算总值。"
        return record
    record["reason"] = scenario.get("reason") or scenario.get("treatment") or ""
    if not ({"item_values", "shares"} & set(scenario)):
        record["note"] = "仅列范围或讨论，没有明确替换金额/股数，未计算总值。"
        return record
    try:
        supported = {"name", "reason", "treatment", "sources", "item_values", "shares", "currency"}
        if set(scenario) - supported:
            raise ValueError("含未支持变更，不能只执行部分并声称全部已算：" + ",".join(sorted(set(scenario) - supported)))
        if scenario.get("currency", valuation.get("currency")) != valuation.get("currency"):
            raise ValueError("情景须与基准同币种，先明确换算后的金额")
        values = scenario.get("item_values", {})
        if not isinstance(values, dict):
            raise ValueError("item_values须为既有项目ID到同币种金额的对象")
        if not values and "shares" not in scenario:
            record["note"] = "未给出实际替换，未计算总值。"
            return record
        candidate = deepcopy(valuation)
        candidate.pop("scenarios", None)
        rows = {row["id"]: row for row in candidate.get("items", [])}
        unknown = set(values) - set(rows)
        if unknown:
            raise ValueError("没有这些项目：" + ",".join(sorted(unknown)))
        for identity, value in values.items():
            amount = _number(value, identity)
            if amount is None:
                raise ValueError(f"{identity}未提供金额；缺数不是零")
            row = rows[identity]
            if not row.get("include", True) or row.get("basis") == "omitted":
                raise ValueError(f"{identity}是未计入项目；本接口不改变计值粒度或复活略去项")
            # The baseline has already resolved fact_ref when called by research.
            # A scenario amount is an explicit estimate, not a new source fact.
            row.update(value=amount, basis="estimate")
            for key in ("fact_ref", "formula", "low", "high"):
                row.pop(key, None)
        if "shares" in scenario:
            shares = _number(scenario["shares"], "情景股数")
            if shares is None or shares <= 0:
                raise ValueError("情景普通股数须为正数")
            candidate["shares"] = shares
        computed = _base_calculate(candidate)
        applied = {row["id"] for row in computed["items"] if row["included"]}
        if set(values) - applied:
            raise ValueError("替换项目被父项排除，未实际进入总值；请先确定同一计值粒度")
        baseline_selected = {row["id"] for row in baseline_items if row["included"]}
        if applied != baseline_selected:
            raise ValueError("替换金额改变了父子计值粒度；请先准备同一计值范围的独立基准台账")
        # Per-item independent bounds are not this joint scenario's result.
        computed.pop("scenarios", None)
        record.update(status="calculated", calculation=computed)
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        record.update(status="not_calculated", note=str(exc))
    return record


def calculate(valuation: dict) -> dict:
    """Original baseline plus optional, independently recomputed joint scenarios.

    An invalid optional scenario is reported locally and never erases a valid
    baseline. No change is silently ignored or turned into an assumed zero.
    """
    result = _base_calculate(valuation)
    scenarios = valuation.get("scenarios")
    if scenarios:
        entries = scenarios if isinstance(scenarios, list) else [scenarios]
        result["joint_scenarios"] = [_joint_scenario(valuation, entry, result["items"]) for entry in entries]
    return result
