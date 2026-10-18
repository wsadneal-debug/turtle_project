"""No-growth earnings-power arithmetic. Research supplies assumptions, not totals.

Amounts are base-currency units; earnings/maintenance/tax are annual flows.
No data retrieval, model calls, automatic risk rates or asset-value addition here.
"""
from __future__ import annotations

from copy import deepcopy
import math


ADDITIONS = {"excess_cash", "nonoperating_asset", "associate", "tax_benefit", "lease_advantage"}
DEDUCTIONS = {"financing_debt", "legacy_liability", "transition_cost", "nci", "preferred", "lease_debt"}
EXCLUDED = {"operating_asset", "operating_payable", "lease_right"}


def number(value, label, *, nonnegative=False):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{label}必须是数值而不是布尔值")
    result = float(value)
    if not math.isfinite(result) or (nonnegative and result < 0):
        raise ValueError(f"{label}必须是{'非负' if nonnegative else ''}有限数值")
    return result


def ratio(value, label, *, positive=False):
    result = number(value, label)
    if result is not None and (result < 0 or result > 1 or (positive and result == 0)):
        raise ValueError(f"{label}须用0至1的小数，{'且须大于0' if positive else '而非百分数整数'}")
    return result


def _sum(values):
    return None if any(v is None for v in values) else sum(values)


def _rows(rows, currency, *, signed=False):
    """One selected granularity; duplicate economic scope is reviewed by the model."""
    result, seen = [], set()
    for original in rows:
        row = deepcopy(original)
        identifier = row['id']
        if identifier in seen:
            raise ValueError(f"条目标识重复：{identifier}")
        seen.add(identifier)
        if row.get('currency', currency) != currency:
            raise ValueError(f"{identifier}币种不一致，须先显式换算")
        if row.get('unit', 'currency') not in ('currency', 'basic', currency):
            raise ValueError(f"{identifier}须使用基本货币单位")
        row['value'] = number(row.get('value'), identifier, nonnegative=not signed)
        row['included'] = row.get('include', True) and row.get('basis') != 'omitted'
        result.append(row)
    selected = {r['id'] for r in result if r['included']}
    by_id = {r['id']: r for r in result}
    for row in result:
        parent = row.get('parent_id')
        visited = {row['id']}
        while parent in by_id:
            if parent in visited:
                raise ValueError('父项关系循环')
            visited.add(parent)
            if row['included'] and parent in selected:
                raise ValueError(f"{row['id']}与父项同时选中，请选择一种计值粒度")
            parent = by_id[parent].get('parent_id')
    return result


def _adjustments(rows, currency, warnings):
    output = _rows(rows, currency, signed=True)
    total = 0.0
    for row in output:
        if not row['included']:
            continue
        if row['value'] is None:
            warnings.append(f"{row['id']}调整未计量，当前为其余项目的条件估计，不代表该项为零。")
        else:
            total += row['value']
    return total, output


def maintenance_value(spec, currency, warnings):
    mode = spec.get('mode', 'direct')
    if mode == 'direct':
        if any(r.get('include', True) for r in spec.get('items', [])):
            raise ValueError('维护投入直接金额与入选分项不能同时使用')
        return number(spec.get('value'), 'maintenance.value', nonnegative=True), []
    if mode != 'components':
        raise ValueError('maintenance.mode须为direct或components')
    if spec.get('value') is not None:
        raise ValueError('分项维护模式不能同时指定合计value')
    rows = _rows(spec.get('items', []), currency)
    values = []
    for row in rows:
        if not row['included']:
            continue
        if row['value'] is None and row.get('gross_cost') is not None:
            gross = number(row['gross_cost'], '全新成本', nonnegative=True)
            residual = number(row.get('residual', 0), '当前残值', nonnegative=True)
            life = number(row.get('life_years'), '更新周期', nonnegative=True)
            if life is None or life == 0 or residual > gross:
                raise ValueError(f"{row['id']}维护计算需要有效更新周期和残值")
            row['value'] = (gross - residual) / life
        if row['value'] is None:
            warnings.append(f"{row['id']}维护投入未计量，须估计；不把缺数作为零维护。")
        values.append(row['value'])
    return (_sum(values) if values else None), rows


def capital_rate(spec, currency):
    if spec.get('currency') != currency:
        raise ValueError('资本成本币种须明确且与盈利币种一致')
    mode = spec.get('mode', 'components')
    if mode == 'direct':
        if any(spec.get(key) is not None for key in ('equity_cost', 'debt_cost', 'debt_weight', 'tax_shield')):
            raise ValueError('直接WACC与组分口径互斥；参考组分请放reason，不同时作计算输入')
        return ratio(spec.get('wacc'), 'WACC', positive=True)
    if mode != 'components':
        raise ValueError('capital_cost.mode须为direct或components')
    if spec.get('wacc') is not None:
        raise ValueError('组分WACC由程序计算，不能再提供直接wacc')
    weight = ratio(spec.get('debt_weight'), '债务权重')
    if weight is None:
        return None
    equity = ratio(spec.get('equity_cost'), '股权成本', positive=True) if weight < 1 else 0.0
    debt = ratio(spec.get('debt_cost'), '税前债务成本') if weight > 0 else 0.0
    shield = ratio(spec.get('tax_shield'), '有效利息税盾') if weight > 0 else 0.0
    if any(v is None for v in (equity, debt, shield)):
        return None
    return ratio((1 - weight) * equity + weight * debt * (1 - shield), 'WACC', positive=True)


def _bridge_value(row):
    if row['value'] is not None:
        return row['value']
    method = row.get('calculation')
    if method == 'equity_epv':
        earnings = number(row.get('earnings'), '参股/少数股东税后可分配盈利')
        cost = ratio(row.get('equity_cost'), '参股股权成本', positive=True)
        ownership = ratio(row.get('ownership'), '持有或外部份额')
        return None if any(v is None for v in (earnings, cost, ownership)) else earnings / cost * ownership
    if method == 'present_value':
        rate = ratio(row.get('rate'), '现值折现率')
        if rate is None:
            return None
        flows = []
        for flow in row.get('cashflows', []):
            amount = number(flow.get('amount'), '现金流金额', nonnegative=True)
            years = number(flow.get('years'), '现金流年数', nonnegative=True)
            if amount is None or years is None:
                return None
            flows.append(amount / (1 + rate) ** years)
        return sum(flows) if flows else None
    if method == 'ownership':
        value = number(row.get('equity_value'), '被投资企业股权价值', nonnegative=True)
        share = ratio(row.get('ownership'), '持有份额')
        return None if value is None or share is None else value * share
    if method is not None:
        raise ValueError(f"不支持股权调整计算：{method}")
    return None


def _base(valuation):
    currency = valuation.get('currency')
    if not currency:
        raise ValueError('EPV须指定计价币种')
    warnings = []
    e = valuation.get('earnings', {})
    revenue = number(e.get('revenue'), '正常收入', nonnegative=True)
    margin = number(e.get('margin'), '正常营业利润率')
    if margin is not None and abs(margin) > 1:
        raise ValueError('营业利润率须为小数')
    base_ebit = None if revenue is None or margin is None else revenue * margin
    delta, delta_rows = _adjustments(e.get('ebit_adjustments', []), currency, warnings)
    lease = e.get('lease', {})
    lease_mode = lease.get('mode', 'none')
    if lease_mode not in ('none', 'operating', 'financing'):
        raise ValueError('租赁模式须为none/operating/financing')
    lease_delta = 0.0
    if lease_mode == 'operating':
        rou = number(lease.get('rou_depreciation_in_ebit'), '原营业利润内使用权折旧', nonnegative=True)
        expensed = number(lease.get('rent_expense_in_ebit'), '原营业利润内租金', nonnegative=True)
        rent = number(lease.get('normalized_rent'), '正常全部租金', nonnegative=True)
        lease_delta = None if any(v is None for v in (rou, expensed, rent)) else rou + expensed - rent
    ebit = _sum([base_ebit, delta, lease_delta])
    da = number(e.get('da_addback'), '需替换折旧摊销', nonnegative=True)
    maintenance, maintenance_rows = maintenance_value(valuation.get('maintenance', {}), currency, warnings)
    working = number(e.get('working_capital_addition'), '必要年度营运资本追加')
    if working is not None and working < 0:
        warnings.append('负营运资本追加表示持续释放现金；固定规模下须解释，单次释放应放股权桥而非永续。')
    tax = valuation.get('tax', {})
    tax_mode = tax.get('mode', 'rate')
    if tax_mode == 'rate':
        rate = ratio(tax.get('rate'), '正常经营税率')
        tax_base = None if ebit is None or rate is None else max(ebit, 0) * rate
    elif tax_mode == 'direct':
        tax_base = number(tax.get('value'), '直接经营税额')
    else:
        raise ValueError('tax.mode须为rate或direct')
    tax_delta, tax_rows = _adjustments(tax.get('adjustments', []), currency, warnings)
    tax_amount = _sum([tax_base, tax_delta])
    power = _sum([ebit, da, -maintenance if maintenance is not None else None,
                  -working if working is not None else None, -tax_amount if tax_amount is not None else None])
    wacc = capital_rate(valuation.get('capital_cost', {}), currency)
    core = None if power is None or wacc is None else power / wacc
    bridge = _rows(valuation.get('equity_adjustments', []), currency)
    bridge_total = 0.0
    for row in bridge:
        kind = row.get('kind')
        if kind not in ADDITIONS | DEDUCTIONS | EXCLUDED:
            raise ValueError(f"{row['id']}不支持的EPV股权调整类别：{kind}")
        if not row['included']:
            continue
        # A group's core rent does not cover a separately valued sublease or an
        # excluded business. Omitted flag retains the legacy core-rent treatment.
        covered_by_rent = row.get('covered_by_core_rent', True)
        if kind == 'lease_debt' and not isinstance(covered_by_rent, bool):
            raise ValueError('covered_by_core_rent须为布尔值，明确该债务是否由核心租金承担')
        if kind in EXCLUDED or (lease_mode == 'operating' and kind == 'lease_debt' and covered_by_rent):
            row['included'] = False
            warnings.append(f"{row['id']}：{kind}已在经营盈利/租金口径体现，不在股权桥重复计入。")
            continue
        if row.get('reflected_in_earnings'):
            if kind in {'financing_debt', 'lease_debt', 'preferred'}:
                warnings.append(f"{row['id']}属于资本提供者索取权；无杠杆经营EPV仍须扣除，不能因利息/股息已付而免扣本金。")
            else:
                row['included'] = False
                warnings.append(f"{row['id']}已声明在盈利中计价，本次不重复资本化或增减。")
                continue
        row['value'] = _bridge_value(row)
        row['effect'] = None if row['value'] is None else row['value'] * (1 if kind in ADDITIONS else -1)
        if row['value'] is None:
            warnings.append(f"{row['id']}股权调整未计量，仅提供其余项目的条件估计；不代表该权利/义务为零。")
        else:
            if row['value'] < 0:
                raise ValueError(f"{row['id']}价值为负，须改用对应义务/损失情景，不能自动增益普通股")
            bridge_total += row['effect']
    equity = None if core is None else core + bridge_total
    shares = number(valuation.get('shares'), '普通股数', nonnegative=True)
    if not shares:
        warnings.append('缺同口径发行在外普通股数，不计算每股；不得用加权股数或H流通股替代。')
    if core is None:
        warnings.append('正常盈利、维护、税或资本成本缺少决定性输入，未形成完整EPV；不套用默认折现率。')
    if power is not None and power <= 0:
        warnings.append('可分配经营盈利非正；永续结果仅作诊断，须重新判断经营可行性，不是负股价目标。')
    if tax_amount is not None and tax_amount < 0:
        warnings.append('模型采用负年度经营税负；需证明可持续性，有限税利益不得永续化。')
    labels_values = [('正常收入', revenue), ('正常营业利润率', margin), ('基础营业利润', base_ebit),
                     ('显式营业利润调整', delta), ('租赁经营口径调整', lease_delta), ('正常化营业利润', ebit),
                     ('折旧摊销加回', da), ('维护性资本支出', maintenance), ('必要净营运资本追加', working),
                     ('正常无杠杆经营税负', tax_amount), ('可持续可分配经营盈利', power)]
    return {'method': 'epv', 'method_id': 'earnings_power_v1', 'currency': currency,
            'shares': shares, 'revenue': revenue, 'margin': margin, 'normalized_ebit': ebit,
            'maintenance_capex': maintenance, 'cash_tax': tax_amount, 'earnings_power': power,
            'wacc': wacc, 'core_epv': core, 'equity_adjustment': bridge_total, 'equity_value': equity,
            'per_share': equity / shares if equity is not None and shares else None,
            'earnings_bridge': [{'name': k, 'value': v} for k, v in labels_values],
            'ebit_adjustments': delta_rows, 'tax_adjustments': tax_rows,
            'maintenance_items': maintenance_rows, 'equity_bridge': bridge, 'warnings': warnings,
            'status': 'incomplete' if core is None else 'nonpositive_power' if power <= 0 else 'conditional_estimate'}


def _scenario(valuation, scenario):
    allowed = {'name', 'reason', 'earnings', 'maintenance', 'tax', 'capital_cost', 'shares', 'equity_values'}
    if set(scenario) - allowed:
        raise ValueError(f"场景含未支持字段：{sorted(set(scenario) - allowed)}")
    candidate = deepcopy(valuation)
    fields = {
        'earnings': {'revenue', 'margin', 'ebit_adjustments', 'da_addback', 'working_capital_addition', 'lease'},
        'maintenance': {'mode', 'value', 'items'},
        'tax': {'mode', 'rate', 'value', 'adjustments'},
        'capital_cost': {'mode', 'currency', 'wacc', 'equity_cost', 'debt_cost', 'debt_weight', 'tax_shield', 'as_of'},
    }
    for key in fields:
        if key in scenario:
            # Changes of measurement mode replace the block, preventing stale fields.
            current = candidate.get(key, {})
            change = scenario[key]
            if not isinstance(change, dict) or set(change) - fields[key] - {'reason', 'sources'}:
                raise ValueError(f'{key}情景含未支持参数；请检查字段，不能将未执行变化称为已重算')
            candidate[key] = change if 'mode' in change and change['mode'] != current.get('mode') else {**current, **change}
    if 'shares' in scenario:
        candidate['shares'] = scenario['shares']
    values = scenario.get('equity_values', {})
    known = {r['id'] for r in candidate.get('equity_adjustments', [])}
    if set(values) - known:
        raise ValueError('场景试图替换不存在的股权项目')
    for row in candidate.get('equity_adjustments', []):
        if row['id'] in values:
            row['value'] = values[row['id']]
    return candidate


def calculate(valuation: dict) -> dict:
    """Evaluate baseline, explicit joint scenarios, and optional margin/WACC grid."""
    result = _base(valuation)
    result['scenarios'] = []
    for scenario in valuation.get('scenarios', []):
        computed = _base(_scenario(valuation, scenario))
        if valuation.get('tax', {}).get('mode') == 'direct' and 'earnings' in scenario and 'tax' not in scenario:
            computed['warnings'].append('此盈利情景保留直接年度税额；非自动随盈利变化的税负，请检查配对。')
        result['scenarios'].append({'name': scenario.get('name', '未命名情景'),
                                    'reason': scenario.get('reason', ''), 'calculation': computed})
    sensitivity = valuation.get('sensitivity', {})
    result['sensitivity'] = []
    for margin in sensitivity.get('margins', []):
        for wacc in sensitivity.get('waccs', []):
            scenario = {'earnings': {'margin': margin}, 'capital_cost': {
                'mode': 'direct', 'currency': result['currency'], 'wacc': wacc}}
            computed = _base(_scenario(valuation, scenario))
            result['sensitivity'].append({k: computed[k] for k in ('margin', 'wacc', 'earnings_power', 'equity_value', 'per_share')})
    if result['sensitivity'] and valuation.get('tax', {}).get('mode') == 'direct':
        result['warnings'].append('敏感性网格保留直接税额；重大税差请使用显式联合情景。')
    return result
