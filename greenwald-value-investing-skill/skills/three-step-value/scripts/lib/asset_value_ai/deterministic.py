"""Shared zero-model bindings, calculation and reports; no source database access."""
from __future__ import annotations

import json
import math
from copy import deepcopy
from pathlib import Path

from .methods import calculator, select_method


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def resolve_fact_refs(input_data: dict, valuation: dict) -> dict:
    """Resolve explicitly chosen 1:1 amounts; unavailable references keep estimates."""
    result = deepcopy(valuation)
    warnings = []
    for item in result.get("items", []):
        if item.get("basis") == "omitted":
            continue
        reference = item.get("fact_ref")
        if not reference:
            continue
        period = str(reference.get("period_end", "")).replace("-", "") if isinstance(reference, dict) else ""
        key = reference.get("canonical_key") if isinstance(reference, dict) else None
        facts = [snapshot.get("canonical", {}).get(key) for snapshot in input_data.get("snapshots", [])
                 if str(snapshot.get("period_end", "")).replace("-", "") == period]
        fact = facts[0] if len(facts) == 1 and isinstance(facts[0], dict) else None
        value = fact.get("value") if fact else None
        problem = None
        if not isinstance(reference, dict) or set(reference) != {"period_end", "canonical_key"} or item.get("formula"):
            problem = "仅支持完整原额1:1引用；比例、拆分或公式项目应使用估计并移除fact_ref"
        elif fact is None or not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            problem = "未找到唯一、明确数值的同期间canonical事实"
        elif fact.get("unit") != "currency":
            problem = "引用单位不是基本货币单位，不能将百分比、股数或其他单位直接计值"
        elif not fact.get("currency") or fact["currency"] != result.get("currency"):
            problem = "引用事实币种与估值币种不一致或未知，需先在估计层换汇"
        if problem:
            message = f"{item.get('id', key)} fact_ref未直接采用：{problem}；保留原估计。"
            if item.get("basis") not in ("book", "omitted"):
                item["basis"] = "estimate"
        else:
            item.setdefault("model_value", item.get("value"))
            item.setdefault("model_book_value", item.get("book_value"))
            item["value"] = value
            item["book_value"] = value
            item["basis"] = "fact"
            bounds = {name: item.pop(name) for name in ("low", "high") if name in item}
            if any(bound is not None for bound in bounds.values()):
                item.setdefault("model_bounds", bounds)
            source = f"{reference['period_end']}/{key}：" + json.dumps(fact.get("source", {}), ensure_ascii=False, sort_keys=True)
            sources = item.get("sources") or []
            sources = [sources] if isinstance(sources, str) else list(sources)
            if source not in sources:
                sources.append(source)
            item["sources"] = sources
            message = (f"{item.get('id', key)} fact_ref按保存的原始事实值 {value} 直接采用；"
                       f"模型原建议 {item['model_value']} 已保留，差额 {value - item['model_value']}。"
                       if isinstance(item["model_value"], (int, float)) and item["model_value"] != value else "")
            if item.get("model_bounds"):
                message += f"{item.get('id', key)} 为确定原额1:1采用，模型区间已保留为model_bounds，不参与敏感性。"
        if message:
            warnings.append(message)
            reason = item.get("reason") or ""
            if message not in reason:
                item["reason"] = reason + ("；" if reason else "") + message
    result["fact_ref_warnings"] = warnings
    return result


def recalculate(input_data: dict, valuation: dict, run_dir, *, method=None) -> dict:
    """Save one method's deterministic report; never overwrite another method."""
    selected = select_method(input_data, valuation, requested=method)
    if selected == 'growth':
        from .growth_reporting import render_report
        from .growth_data import bind_growth_context
        final = bind_growth_context(input_data, valuation)
    elif selected == 'epv':
        from .epv_reporting import render_report
        final = deepcopy(valuation)
        final['method'] = 'epv'
    else:
        from .reporting import render_report
        final = resolve_fact_refs(input_data, valuation)
    directory = Path(run_dir).expanduser().resolve()
    target = directory / 'valuation.json'
    if target.exists():
        existing = json.loads(target.read_text(encoding='utf-8'))
        select_method(input_data, existing, requested=selected)
    directory.mkdir(parents=True, exist_ok=True)
    final.pop('calculation', None)
    calculation = calculator(selected)(final)
    final['calculation'] = calculation
    report = render_report(input_data, final, calculation)
    write_json(target, final)
    (directory / 'report.md').write_text(report, encoding='utf-8')
    return final


