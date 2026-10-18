"""Read a chosen EPV run once; freeze reusable basis without writing its files."""
from __future__ import annotations

from copy import deepcopy
from datetime import date
import json
from pathlib import Path

from .epv import calculate as calculate_epv
from .epv_data import normalized_code
from .methods import select_method


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path.name}须为JSON对象')
    return value


def prepare_growth_input(code: str, *, epv_run, as_of: str | None = None,
                         request: dict | None = None, asset_run=None) -> dict:
    """Zero-model reuse of explicit input/valuation, not a new financial refresh."""
    root = Path(epv_run).expanduser().resolve()
    original = _load(root / 'input.json')
    valuation = _load(root / 'valuation.json')
    if normalized_code(original.get('issuer', {}).get('code', '')) != normalized_code(code):
        raise ValueError('epv-run不是本次指定企业')
    if select_method(original, valuation) != 'epv':
        raise ValueError('epv-run须是盈利能力价值研究，不是资产法或成长研究')
    if as_of is not None:
        date.fromisoformat(as_of)
    request = deepcopy(request) if request is not None else {}
    if not isinstance(request, dict):
        raise ValueError('growth-request-json须为对象')
    if set(request) - {'price', 'price_grid', 'policy', 'question', 'notes'}:
        raise ValueError('成长人工输入支持price/price_grid/policy/question/notes，不静默接收未知参数')
    for key in ('price', 'policy'):
        if key in request and not isinstance(request[key], dict):
            raise ValueError(f'{key}须为对象')
    if 'price_grid' in request and not isinstance(request['price_grid'], list):
        raise ValueError('price_grid须为明确报价对象列表')
    source = deepcopy(valuation)
    source.pop('calculation', None)
    calculation = calculate_epv(source)
    basis = {
        'currency': calculation['currency'], 'unit': 'currency', 'scope': 'enterprise',
        'revenue': calculation['revenue'], 'earnings_power': calculation['earnings_power'],
        'equity_adjustment': calculation['equity_adjustment'], 'capital_cost': calculation['wacc'],
        'capital_cost_basis': 'wacc', 'shares': calculation['shares'],
        'valuation_date': source.get('valuation_date'),
        'financial_position_date': source.get('financial_position_date'),
        'reason': '从所选EPV纯计算复算取得；年度维护已扣，额外增长投入另计。原范围及兑现假设继续适用。',
    }
    # Full prior reasoning is retained in the chosen source; the current packet
    # excludes unrelated market targets and nested prior calculations.
    source.pop('market_comparison', None)
    source.pop('scenarios', None)
    source.pop('sensitivity', None)
    result = {key: deepcopy(original[key]) for key in (
        'issuer', 'currency', 'shares', 'reports', 'history', 'snapshots',
        'materials_ready', 'simulation', 'warnings') if key in original}
    result['method'] = 'growth'
    result['currency'] = basis['currency']
    result['as_of'] = as_of or original.get('as_of')
    result['growth_request'] = request
    result['epv_context'] = {
        'source_run': str(root), 'source_input_as_of': original.get('as_of'),
        'source_valuation_date': source.get('valuation_date'),
        'financial_position_date': source.get('financial_position_date'),
        'equity_basis': source.get('equity_basis'),
        'source_research': deepcopy(source.get('research', {})),
        'basis': basis, 'valuation': source,
        'calculation': {key: deepcopy(calculation.get(key)) for key in (
            'currency', 'revenue', 'earnings_power', 'wacc', 'core_epv', 'equity_adjustment',
            'equity_value', 'shares', 'per_share', 'earnings_bridge', 'equity_bridge', 'status', 'warnings')},
        'use': '冻结的上游研究，不因本轮日期变化变成最新事实；原EPV结果不修改，成长不与其相加。',
    }
    # Freeze references chosen by this EPV; never discover another model's run.
    asset_context = deepcopy(original.get('asset_context') or {})
    asset_reference = deepcopy(source.get('asset_comparison') or {})
    if not isinstance(asset_context, dict) or not isinstance(asset_reference, dict):
        raise ValueError('源资产参照须为对象，不能猜测其他研究目录')
    if asset_run is not None:
        from .epv_data import load_asset_context, load_review_asset_reference
        asset_context = load_asset_context(asset_run, code)
        asset_reference = load_review_asset_reference({
            'issuer': original['issuer'], 'asset_context': asset_context}) or {}
        asset_origin = 'explicit_asset_run'
    else:
        saved_reference = root / 'asset_comparison_input.json'
        if not asset_reference and saved_reference.exists():
            asset_reference = _load(saved_reference)
        asset_origin = 'frozen_epv_reference'
    if asset_context:
        issuer = asset_context.get('issuer') or {}
        if issuer.get('code') and normalized_code(issuer['code']) != normalized_code(code):
            raise ValueError('EPV中冻结的资产引用不是同一企业')
        result['asset_context'] = asset_context
    asset_link = {
        'source_run': asset_context.get('source_run'), 'origin': asset_origin,
        'status': asset_reference.get('status') or (
            asset_context.get('source_status', 'unknown') if asset_context else 'not_provided'),
        **{key: deepcopy(asset_reference.get(key)) for key in (
            'equity_value', 'currency', 'valuation_date', 'financial_position_date',
            'scope', 'lease_basis', 'unmeasured', 'warnings', 'sources')},
    }
    for key in ('currency', 'valuation_date', 'financial_position_date', 'scope', 'unmeasured'):
        if asset_link.get(key) is None:
            asset_link[key] = deepcopy(asset_context.get(key))
    asset_link['reproduction_context'] = deepcopy(asset_context.get('reproduction_context'))
    result['module_context'] = {
        'asset': asset_link,
        'epv': {'source_run': str(root), 'status': calculation.get('status'),
                'valuation_date': source.get('valuation_date'),
                'financial_position_date': source.get('financial_position_date'),
                'scope': source.get('scope'), 'currency': calculation['currency'],
                'equity_value': calculation.get('equity_value'), 'core_epv': calculation.get('core_epv'),
                'unmeasured': deepcopy(source.get('unmeasured') or [])},
        'prior_competitive_advantage': deepcopy(source.get('competitive_advantage')),
        'prior_asset_epv_explanation': deepcopy((source.get('asset_comparison') or {}).get('reason')),
        'comparison_note': ('本次另选资产参照；旧EPV差异解释针对原资产来源，不冒称已比较新来源。'
                            if asset_run is not None else '采用源EPV已保存的资产参照，不重新读取后来修改的资产结果。'),
        'use': '资产解释复制成本，EPV解释正常盈利；不相加、不自动证明护城河。缺资产数值不阻断定性判断；来源日期和局限保持。',
    }
    warnings = list(result.get('warnings') or [])
    warnings.extend(calculation.get('warnings') or [])
    if result.get('as_of') != original.get('as_of'):
        warnings.append('本轮截止日与源EPV不同；资料和金融存量仍是源研究范围，没有自动滚动更新。')
    if source.get('unmeasured'):
        warnings.append('源EPV仍有未明事项；须判断其重要性，不以成长模型抹去原局限。')
    if source.get('research', {}).get('mode') == 'simulated':
        result['simulation'] = True
    result['warnings'] = list(dict.fromkeys(warnings))
    return result


def bind_growth_context(input_data: dict, valuation: dict) -> dict:
    """Source facts and explicitly fixed prices are host inputs, not model votes.

    Adjusted basis is allowed with a reason, leaving the source unchanged. Free
    research descriptions remain free; no evidence score or completeness gate.
    """
    from .growth_routing import terminal_route, bind_terminal_context, attach_module_context
    if terminal_route(valuation) is not None:
        return bind_terminal_context(input_data, valuation)
    final = attach_module_context(input_data, valuation)
    final['method'] = 'growth'
    context = input_data.get('epv_context') or {}
    source_basis = context.get('basis') if isinstance(context, dict) else None
    mode = final.get('basis_mode', 'reuse_epv' if source_basis else 'explicit')
    if mode not in ('reuse_epv', 'adjusted', 'explicit'):
        raise ValueError('basis_mode须为reuse_epv、adjusted或explicit')
    if source_basis and mode == 'explicit':
        raise ValueError('已有源EPV时修正采用adjusted并说明理由，不能用explicit绕开源口径记录')
    notes = []
    original_basis = final.get('basis')
    if mode == 'reuse_epv':
        if not isinstance(source_basis, dict):
            raise ValueError('reuse_epv需要已冻结的epv_context；独立输入可用explicit basis')
        if original_basis and original_basis != source_basis:
            final.setdefault('model_basis', deepcopy(original_basis))
            notes.append('本轮沿用冻结EPV基础；模型另写的基础未直接替代源值。修正须采用adjusted并给理由。')
        final['basis'] = deepcopy(source_basis)
        if final.get('currency') not in (None, source_basis.get('currency')):
            final.setdefault('model_currency', final['currency'])
            notes.append('沿用源EPV时币种标签同时采用源基础，模型原标签另存，不对金额静默换汇。')
        final['currency'] = source_basis.get('currency')
    else:
        basis = final.get('basis')
        if not isinstance(basis, dict):
            raise ValueError('显式/调整基础须给basis对象')
        if mode == 'adjusted' and not (final.get('basis_change_reason') or basis.get('reason')):
            raise ValueError('调整基础须简述用途、范围或事实变化原因，不为贴现价暗改正常盈利')
    final['basis_mode'] = mode
    if source_basis:
        final['source_basis'] = deepcopy(source_basis)
        final['upstream_context'] = {key: deepcopy(context.get(key)) for key in (
            'source_run', 'source_input_as_of', 'source_valuation_date', 'financial_position_date',
            'equity_basis', 'source_research')}
        final['source_limitations'] = {
            'warnings': deepcopy((context.get('calculation') or {}).get('warnings') or []),
            'unmeasured': deepcopy((context.get('valuation') or {}).get('unmeasured') or []),
        }
    if final.get('currency') is None:
        final['currency'] = final['basis'].get('currency')
    request = input_data.get('growth_request') or {}
    for key in ('price', 'price_grid', 'policy'):
        if key in request:
            if key in final and final[key] != request[key]:
                final.setdefault('model_request_overrides', {})[key] = deepcopy(final[key])
                notes.append(f'{key}沿用人工冻结输入，模型建议另存，不暗改基准。')
            final[key] = deepcopy(request[key])
    final['input_binding_notes'] = notes
    return final
