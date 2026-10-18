"""Lightweight method selection, not a moat score or an investment decision.

The existing leader owns this judgment. A specialist may supply evidence but
cannot unilaterally route the whole company. Old valuations without an explicit
route retain their original deterministic calculation behavior.
"""
from __future__ import annotations

from copy import deepcopy

TERMINAL_ACTIONS = ('skip', 'defer')


def route_decision(answer: dict, *, settle: bool = False) -> dict:
    """Interpret a leader's explicit choice; never infer a moat from value ratios."""
    raw = answer.get('growth_route')
    if raw is not None and not isinstance(raw, dict):
        raise ValueError('growth_route须为含action及reason的对象')
    route = deepcopy(raw or {})
    franchise = answer.get('franchise')
    franchise = franchise if isinstance(franchise, dict) else {}
    action = route.get('action', 'evaluate')
    if action not in ('evaluate', 'investigate', 'skip', 'defer'):
        raise ValueError('growth_route.action须为evaluate/investigate/skip/defer')
    reason = route.get('reason') or franchise.get('reason') or answer.get('summary') or ''
    # An explicit negative finding must not be ignored just because the same
    # answer accidentally retains the positive-valuation template.
    if action == 'evaluate' and franchise.get('status') == 'unsupported':
        action = 'skip'
    elif action in ('evaluate', 'skip') and franchise.get('status') == 'not_assessed':
        action = 'defer'
    if settle and action == 'investigate':
        action = 'defer'  # No recursive probing after the one focused task.
        reason = '本轮定向核查后仍未收敛：' + str(reason or '关键适用性问题待人工处理。')
    if action != 'evaluate' and (not isinstance(reason, str) or not reason.strip()):
        raise ValueError('结束或定向核查须给具体原因，不按空标签自动跳过')
    return {**route, 'action': action, 'reason': reason}


def terminal_route(answer: dict) -> dict | None:
    """Only explicit persisted terminal decisions suppress calculation/replay."""
    raw = answer.get('growth_route')
    if isinstance(raw, dict) and raw.get('action') in TERMINAL_ACTIONS:
        return route_decision(answer)
    return None


def terminal_calculation(answer: dict) -> dict:
    route = terminal_route(answer)
    if route is None:
        raise ValueError('没有明确的成长终止决定')
    return {
        'method': 'growth', 'method_id': 'growth_returns_v1',
        'status': 'not_applicable' if route['action'] == 'skip' else 'awaiting_evidence',
        'calculation_performed': False,
        'preliminary_calculation_performed': route.get('stopped_at') == 'review',
        'reason': route['reason'],
        'baseline_return': None, 'net_return': None,
        'meets_explicit_return_requirement': None,
        'interpretation': '未采用成长溢价，不是将成长经济价值算为零，也不是否决整家公司；原资产与EPV仍保留各自条件。',
    }


def attach_module_context(input_data: dict, valuation: dict) -> dict:
    """Freeze provenance into outputs; source judgments are not current facts."""
    final = deepcopy(valuation)
    if isinstance(input_data.get('module_context'), dict):
        final['module_context'] = deepcopy(input_data['module_context'])
    else:
        final.pop('module_context', None)  # Do not invent unprovided source totals.
    return final


def bind_terminal_context(input_data: dict, valuation: dict) -> dict:
    """A no-calculation conclusion needs no quote, growth rate, F or decay input."""
    final = attach_module_context(input_data, valuation)
    final['method'] = 'growth'
    final['growth_route'] = terminal_route(final)
    context = input_data.get('epv_context') or {}
    if isinstance(context, dict):
        if isinstance(context.get('basis'), dict):
            final['source_basis'] = deepcopy(context['basis'])
        final['upstream_context'] = {key: deepcopy(context.get(key)) for key in (
            'source_run', 'source_input_as_of', 'source_valuation_date',
            'financial_position_date', 'equity_basis', 'source_research')}
        final['source_limitations'] = {
            'warnings': deepcopy((context.get('calculation') or {}).get('warnings') or []),
            'unmeasured': deepcopy((context.get('valuation') or {}).get('unmeasured') or []),
        }
    # Explicit inputs remain provenance only, never prerequisites to skip.
    for key in ('price', 'price_grid', 'policy'):
        request = input_data.get('growth_request') or {}
        if key in request:
            final[key] = deepcopy(request[key])
    return final
