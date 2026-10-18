"""Greenwald-style growth RETURNS at an explicit price, not a growth target price.

Research supplies sustainable earnings, protected growth and capital allocation.
This module only evaluates the funds identity, return components and comparisons.
All money is in one base currency; rates are decimals. No market fetch, scoring,
recursive model calls, Gordon-price inversion or automatic investment action.
"""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any


def number(value: Any, label: str, *, minimum: float | None = None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f'{label}须为数值，不是布尔值')
    result = float(value)
    if not math.isfinite(result) or (minimum is not None and result < minimum):
        raise ValueError(f'{label}须为有限数值' + (f'且不小于{minimum}' if minimum is not None else ''))
    return result


def rate(value: Any, label: str, *, negative: bool = False) -> float | None:
    result = number(value, label)
    if result is not None and not (-1 < result <= 1 if negative else 0 <= result <= 1):
        raise ValueError(f'{label}须为小数比例，不是百分数整数')
    return result


def _block(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f'{label}须为对象')
    return value


def _money_scope(spec: dict, currency: str, label: str) -> None:
    if spec.get('currency', currency) != currency:
        raise ValueError(f'{label}币种不一致，请先显式换算')
    if spec.get('unit', 'currency') not in ('currency', 'basic', currency):
        raise ValueError(f'{label}使用基本货币单位，不能混入万元或每股金额')


def factor_value(spec: dict, scope: str) -> tuple[float | None, str]:
    """Value generated per unit allocated, including the unit invested itself."""
    mode = spec.get('mode', 'direct')
    if mode == 'direct':
        return number(spec.get('factor'), '价值创造因子', minimum=0), '研究直接估计'
    if mode == 'return_ratio':
        if spec.get('scope') != scope:
            raise ValueError('增量回报与资本成本须声明同一enterprise/equity口径')
        earned = number(spec.get('incremental_return'), '增量投资回报（小数，可高于100%）', minimum=0)
        cost = rate(spec.get('capital_cost'), '增量投资资本成本')
        if earned is None or cost is None:
            return None, '增量回报或匹配资本成本未估计'
        if cost <= 0:
            raise ValueError('增量投资资本成本须大于零')
        return earned / cost, '增量投资回报/匹配资本成本'
    if mode == 'allocations':
        rows = spec.get('items')
        if not isinstance(rows, list) or not rows:
            return None, '未提供积极投资投向'
        total_share = total = 0.0
        missing = False
        for row in rows:
            row = _block(row, '资金投向')
            share = rate(row.get('share'), '资金投向比例')
            factor = number(row.get('factor'), '投向价值因子', minimum=0)
            if share is None:
                return None, '资金投向比例未齐'
            total_share += share
            if share and factor is None:
                missing = True
            elif share:
                total += share * factor
        if not math.isclose(total_share, 1, abs_tol=1e-9):
            raise ValueError('积极投资投向比例须合计为1，不自动归一或忽略剩余资金')
        return (None, '部分投向因子未估计') if missing else (total, '按积极投资资金比例加权')
    if mode == 'repeat':
        first = number(spec.get('initial_factor'), '初始投资因子', minimum=0)
        payout = rate(spec.get('payout_ratio'), '新增业务后续分配比例')
        if first is None or payout is None:
            return None, '重复投资参数未齐'
        denominator = 1 - (1 - payout) * first
        if denominator <= 0:
            return None, '相同高回报无限重复假设无有限结果，不用无限值或兜底倍数'
        return payout * first / denominator, '明确的相同回报重复再投资极端，非默认'
    raise ValueError(f'不支持active.mode={mode}')


def decay_value(spec: dict) -> tuple[float | None, str]:
    mode = spec.get('mode', 'qualitative')
    if mode == 'embedded':
        if any(spec.get(key) is not None for key in ('rate', 'half_life', 'residual_fraction')):
            raise ValueError('已包含在净增长率的衰减不能再提供额外扣减参数')
        return 0.0, '连续侵蚀已在净有机增长中体现，不再扣一次'
    if mode == 'qualitative':
        if any(spec.get(key) is not None for key in ('rate', 'half_life', 'residual_fraction')):
            raise ValueError('定性衰减不同时输入数值扣减；请选择明确模式')
        return None, '仅定性讨论，未伪造净回报；可明确给额外回报余量补偿'
    if mode not in ('deduct', 'half_life'):
        raise ValueError(f'不支持decay.mode={mode}')
    residual = rate(spec.get('residual_fraction'), '衰减事件后的剩余价值比例')
    if residual is None:
        return None, '数值衰减残值未明，未估计优势丧失后的剩余价值比例'
    if mode == 'deduct':
        hazard = rate(spec.get('rate'), '年度衰减率')
        if hazard is None:
            return None, '数值衰减未估计年度衰减率'
        method = '显式年度衰减；近似损失率=衰减率×(1−残值比例)'
    elif mode == 'half_life':
        years = number(spec.get('half_life'), '特许权半衰期', minimum=0)
        if years is None:
            return None, '数值衰减未估计半衰期'
        if years <= 0:
            raise ValueError('半衰期须大于零')
        convention = spec.get('convention', 'rule72')
        if convention == 'rule72':
            hazard = .72 / years
            method = '书中72法则近似：年度率=0.72/年数，不是实测概率'
        elif convention == 'constant_hazard':
            hazard = -math.expm1(math.log(.5) / years)
            method = '恒定危险率假设：1−0.5^(1/年数)，不替换书中近似数'
        else:
            raise ValueError('半衰期约定须为rule72或constant_hazard')
        if hazard > 1:
            raise ValueError('72法则在本半衰期不适用，不能使用超过100%的年率')
    return hazard * (1 - residual), method


def _converted(value: Any, spec: dict, currency: str, label: str) -> float | None:
    amount = number(value, label, minimum=0)
    source_currency = spec.get('currency')
    if amount is None or not source_currency:
        return None
    if spec.get('unit', 'currency') not in ('currency', 'basic', source_currency):
        raise ValueError(f'{label}必须使用基本货币单位')
    if source_currency == currency:
        return amount
    fx = number(spec.get('fx_to_valuation'), '报价币种到估值币种汇率', minimum=0)
    if fx is None:
        return None
    if fx == 0:
        raise ValueError('汇率须为正数')
    return amount * fx


def purchase_cost(price: dict, basis: dict) -> tuple[float | None, str]:
    """Return the whole ordinary equity purchase cost; not yet core enterprise M."""
    currency, shares = basis['currency'], number(basis.get('shares'), '普通股数', minimum=0)
    mode = price.get('mode')
    if mode is None:
        return None, '未取得报价；资金分配和经营判断仍可进行'
    if mode == 'market_cap':
        result = _converted(price.get('value'), price, currency, '普通股总市值')
        label = '显式普通股总市值；研究须核对完整股类、日期和来源'
    elif mode == 'per_share':
        unit_price = _converted(price.get('value'), price, currency, '每股参考价格')
        result = None if unit_price is None or not shares else unit_price * shares
        label = '参考每股价×全部同权普通股：假设购买成本，非A/H分市场实际总市值'
    elif mode == 'share_classes':
        rows = price.get('quotes')
        if not isinstance(rows, list) or not rows:
            return None, '未提供分股类报价'
        total_shares = 0.0
        total = 0.0
        missing = False
        seen = set()
        for row in rows:
            row = _block(row, '股类报价')
            label = row.get('label')
            if not label or label in seen:
                raise ValueError('分股类报价须有不重复的label')
            seen.add(label)
            count = number(row.get('shares'), '股类实际在外股数', minimum=0)
            p = _converted(row.get('value'), row, currency, '股类每股价格')
            if count is None or p is None:
                missing = True
            else:
                if count <= 0 or p <= 0:
                    raise ValueError('股类股数和价格须大于零')
                total_shares += count
                total += count * p
        if missing or not shares or not math.isclose(total_shares, shares, rel_tol=1e-9, abs_tol=1e-6):
            return None, '股类报价、换汇或全部普通股覆盖未齐，不能以局部市值作全集团分母'
        result, label = total, '各类实际在外普通股×各自报价，逐类换算后合计'
    else:
        raise ValueError(f'不支持price.mode={mode}')
    if result is not None and result <= 0:
        raise ValueError('显式购买成本须大于零；缺报价用null，不用0')
    return result, label


def _base(valuation: dict) -> dict:
    b = _block(valuation.get('basis', {}), 'basis')
    currency = b.get('currency') or valuation.get('currency')
    if not currency:
        raise ValueError('成长回报须指定计价币种')
    if valuation.get('currency', currency) != currency:
        raise ValueError('估值和basis币种不一致')
    _money_scope(b, currency, 'basis')
    scope = b.get('scope', 'enterprise')
    expected_cost = {'enterprise': 'wacc', 'equity': 'equity_cost'}.get(scope)
    if expected_cost is None or b.get('capital_cost_basis') != expected_cost:
        raise ValueError('enterprise盈利须匹配wacc，equity盈利须匹配equity_cost，不能跨口径')
    E = number(b.get('earnings_power'), '增长投资前正常年度可分配盈利')
    S = number(b.get('revenue'), '同范围正常收入', minimum=0)
    B = number(b.get('equity_adjustment'), '核心价值至归母股权的净调整')
    cost = rate(b.get('capital_cost'), '匹配资本成本')
    if cost is not None and cost <= 0:
        raise ValueError('资本成本须大于零，不设隐含默认值')
    warnings = []
    price = _block(valuation.get('price', {}), 'price')
    purchase, price_note = purchase_cost(price, {**b, 'currency': currency})
    M = purchase - B if purchase is not None and B is not None else None
    usable_price = M is not None and M > 0
    if M is not None and M <= 0:
        warnings.append('核心购买成本非正；改做净资产及兑现分析，不除以零或给无限回报。')
    if purchase is None or B is None:
        warnings.append('报价或核心至股权净调整未齐；不以缺数为零，仍保留已知经营和资金分配分析。')
    distribution = _block(valuation.get('distribution', {}), 'distribution')
    _money_scope(distribution, currency, '分配')
    mode = distribution.get('mode', 'ratio')
    if mode == 'ratio':
        payout = number(distribution.get('value'), '可持续分配比例', minimum=0)
        D = None if payout is None or E is None or E < 0 else E * payout
        if payout is not None and payout > 1:
            warnings.append('分配超过盈利；不能把靠存量或融资维持的分配当作永续能力。')
    elif mode == 'direct':
        D = number(distribution.get('value'), '正常年度分配', minimum=0)
        payout = None if E is None or E <= 0 or D is None else D / E
    else:
        raise ValueError('distribution.mode须为ratio或direct')
    organic = _block(valuation.get('organic', {}), 'organic')
    sales_growth = rate(organic.get('revenue_growth'), '有机收入增长率', negative=True)
    growth = rate(organic.get('earnings_growth'), '有机盈利增长率', negative=True)
    investment = _block(organic.get('investment', {}), '有机增长投入')
    _money_scope(investment, currency, '有机增长投入')
    investment_mode = investment.get('mode', 'direct')
    if investment_mode == 'direct':
        I = number(investment.get('value'), '支持有机增长的增量投资')
    elif investment_mode == 'intensity':
        wc = number(investment.get('working_capital'), '增量净营运资本系数')
        fixed = number(investment.get('fixed_capital'), '增量固定资本系数', minimum=0)
        expensed = number(investment.get('expensed_growth'), '另需追加的费用化增长投入', minimum=0)
        if sales_growth is not None and sales_growth < 0:
            I = None
            warnings.append('负收入增长不机械推导资本回收；另给有依据的直接投入/释放估计。')
        else:
            I = None if any(x is None for x in (S, sales_growth, wc, fixed, expensed)) else S * sales_growth * (wc + fixed) + expensed
    else:
        raise ValueError('有机投资mode须为direct或intensity')
    if I is not None and I < 0:
        warnings.append('有机增长净释放资金：须说明持续的负营运资本机制，不能永续化一次性资产回收。')
    A = None if any(x is None for x in (E, D, I)) else math.fsum((E, -D, -I))
    if A is not None and abs(A) <= 4 * math.ulp(max(abs(E), abs(D), abs(I))):
        A = 0.0  # Floating representation only; never hide a real funding gap.
    funding_gap = -A if A is not None and A < 0 else 0.0 if A is not None else None
    if A is not None and A < 0:
        warnings.append('盈利不足以同时支持分配和有机增长；保留资金缺口，不自动借款、砍分红或将负余量截零。')
    active = _block(valuation.get('active', {}), 'active')
    if A == 0:
        factor, factor_note = None, '积极投资余量为零，无需估计因子'
        created = net_created = 0.0
    elif A is not None and A > 0:
        factor, factor_note = factor_value(active, scope)
        created = None if factor is None else A * factor
        net_created = None if factor is None else A * (factor - 1)
    else:
        factor, factor_note, created, net_created = None, '资金分配未闭合，不估积极投资贡献', None, None
    cash_return = D / M if D is not None and usable_price else None
    active_return = created / M if created is not None and usable_price else None
    raw_return = None if any(x is None for x in (cash_return, growth, active_return)) else cash_return + growth + active_return
    if E is not None and E <= 0:
        raw_return = None
        warnings.append('当前正常可分配盈利非正，不能靠稳定成长回报公式替代经营可行性研究。')
    decay = _block(valuation.get('decay', {}), 'decay')
    deduction, decay_note = decay_value(decay)
    net_return = None if raw_return is None or deduction is None else raw_return - deduction
    policy = _block(valuation.get('policy', {}), 'policy')
    margin = rate(policy.get('additional_margin'), '明确要求的额外回报余量')
    buffer = rate(policy.get('qualitative_decay_buffer'), '定性衰减的回报余量补偿')
    if buffer is not None and decay.get('mode', 'qualitative') != 'qualitative':
        raise ValueError('已量化或已嵌入的衰减不再另加定性衰减补偿')
    compare_return = net_return
    compensation = 0.0
    if deduction is None:
        if buffer is not None:
            compare_return, compensation = raw_return, buffer
        elif decay.get('mode', 'qualitative') == 'qualitative':
            warnings.append('衰减仅定性且未给补偿余量，不将衰减前回报冒称风险调整后的净回报。')
        else:
            warnings.append(f'{decay_note}；衰减扣减、净回报及相关判定保留未知，衰减前回报仍作参照。')
    surplus = None if compare_return is None or cost is None else compare_return - cost - compensation
    benchmark_gap = None if raw_return is None or cost is None else raw_return - cost
    threshold = None if cost is None or margin is None or (deduction is None and buffer is None) else cost + margin + compensation
    assessed = None if threshold is None or compare_return is None else compare_return >= threshold
    franchise = _block(valuation.get('franchise', {}), 'franchise')
    fit = franchise.get('status', 'not_assessed')
    if fit not in ('supported', 'conditional', 'unsupported', 'not_assessed'):
        raise ValueError('franchise.status须明确为supported/conditional/unsupported/not_assessed')
    if fit in ('unsupported', 'not_assessed'):
        warnings.append('特许权及增长适用性未获支持；数值仅作假设诊断，不能据此支付成长溢价。')
    if growth is not None and growth < 0:
        warnings.append('有机盈利萎缩：仅作回报分解参照，不套正增长的保守基准结论。')
    downward = None
    if net_return is not None and cost is not None and growth is not None and growth > 0 and 0 < net_return < cost:
        ratio = net_return / cost
        corrected_organic = growth * ratio
        corrected_gross = cash_return + corrected_organic + active_return
        downward = {'value_price_proxy': ratio, 'organic_return': corrected_organic,
                    'gross_return': corrected_gross, 'net_return': corrected_gross - deduction,
                    'note': '按第8章案例仅向下修正一次；V/M是提示性代理，不是真实IRR或精确内在价值，不用于倒算目标价。'}
    if E is not None and E <= 0:
        status = 'nonpositive_earnings'
    elif any(x is None for x in (E, D, I, growth)):
        status = 'incomplete_inputs'
    elif funding_gap and funding_gap > 0:
        status = 'unfunded_growth'
    elif not usable_price:
        status = 'missing_or_nonpositive_core_price'
    elif raw_return is None:
        status = 'incomplete_factor'
    elif fit in ('unsupported', 'not_assessed'):
        status = 'diagnostic_only'
    else:
        status = 'conditional_estimate'
    if fit not in ('supported', 'conditional') or status != 'conditional_estimate' or (growth is not None and growth < 0):
        assessed = None
    return {
        'method': 'growth', 'method_id': 'growth_returns_v1', 'currency': currency,
        'scope': scope, 'shares': b.get('shares'), 'revenue': S, 'earnings_power': E,
        'capital_cost': cost, 'capital_cost_basis': expected_cost, 'equity_adjustment': B,
        'equity_purchase_cost': purchase, 'core_purchase_cost': M, 'price_note': price_note,
        'distribution': D, 'payout_ratio': payout, 'organic_investment': I,
        'active_investment': A, 'funding_gap': funding_gap, 'factor': factor, 'factor_note': factor_note,
        'active_annual_value': created, 'active_net_value_created': net_created,
        'cash_return': cash_return, 'organic_return': growth, 'active_return': active_return,
        'baseline_return': raw_return, 'decay_deduction': deduction, 'decay_note': decay_note,
        'net_return': net_return, 'gross_gap_to_capital_cost': benchmark_gap,
        'return_surplus': surplus, 'qualitative_decay_buffer': buffer,
        'additional_margin': margin, 'comparison_threshold': threshold,
        'meets_explicit_return_requirement': assessed, 'one_step_downward': downward,
        'franchise_status': fit, 'status': status, 'warnings': warnings,
        'identity': '正常年度可分配盈利 = 分配 + 有机增长增量投资 + 积极投资余量',
        'interpretation': '基准假设价值约等于价格的回报比较，不是保证年化收益、精确目标价或投资指令；成长价值不与资产/EPV相加。',
    }


def calculate(valuation: dict) -> dict:
    """Pure baseline or an explicit no-calculation method conclusion."""
    from .growth_routing import terminal_route, terminal_calculation
    if terminal_route(valuation) is not None:
        return terminal_calculation(valuation)
    result = _base(valuation)
    result['scenarios'], result['price_grid'] = [], []
    for spec in valuation.get('scenarios') or []:
        record = {'name': spec.get('name', '未命名情景') if isinstance(spec, dict) else '未命名情景',
                  'parameters': deepcopy(spec), 'status': 'not_calculated', 'calculation': None}
        try:
            spec = _block(spec, 'scenario')
            fields = {'name', 'reason', 'basis', 'distribution', 'organic', 'active', 'decay', 'policy', 'price', 'franchise'}
            if set(spec) - fields:
                raise ValueError('情景含未支持字段，不静默忽略')
            if not (set(spec) & (fields - {'name', 'reason'})):
                record.update(status='discussion_only', reason='仅有讨论，没有明确参数变化；未计算总值')
                result['scenarios'].append(record)
                continue
            allowed = {
                'basis': {'currency', 'unit', 'scope', 'revenue', 'earnings_power', 'equity_adjustment', 'capital_cost', 'capital_cost_basis', 'shares', 'valuation_date', 'financial_position_date'},
                'distribution': {'mode', 'value', 'currency', 'unit'},
                'organic': {'revenue_growth', 'earnings_growth', 'investment'},
                'active': {'mode', 'factor', 'incremental_return', 'capital_cost', 'scope', 'items', 'initial_factor', 'payout_ratio'},
                'decay': {'mode', 'rate', 'half_life', 'convention', 'residual_fraction'},
                'policy': {'additional_margin', 'qualitative_decay_buffer'},
                'price': {'mode', 'value', 'currency', 'unit', 'date', 'fx_to_valuation', 'fx_date', 'quotes', 'name'},
                'franchise': {'status', 'protected_market'},
            }
            for key, permitted in allowed.items():
                if key in spec:
                    changes = _block(spec[key], key)
                    if set(changes) - permitted - {'reason', 'sources', 'note'}:
                        raise ValueError(f'{key}情景含未支持参数，不能忽略变更后返回基准')
                    if key == 'organic' and 'investment' in changes:
                        invest = _block(changes['investment'], 'investment')
                        if set(invest) - {'mode', 'value', 'working_capital', 'fixed_capital', 'expensed_growth', 'currency', 'unit', 'reason', 'sources'}:
                            raise ValueError('有机投入情景含未支持参数')
            candidate = deepcopy(valuation)
            candidate.pop('scenarios', None)
            candidate.pop('price_grid', None)
            for key in fields - {'name', 'reason'}:
                if key in spec:
                    change = _block(spec[key], key)
                    # Nested investment and allocations must be fully specified.
                    old = candidate.get(key) or {}
                    replace = key in ('price', 'decay', 'active') or ('mode' in change and change.get('mode') != old.get('mode'))
                    candidate[key] = deepcopy(change) if replace else {**old, **deepcopy(change)}
            record.update(status='calculated', calculation=_base(candidate))
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            record['reason'] = str(exc)
        result['scenarios'].append(record)
    for quote in valuation.get('price_grid') or []:
        record = {'price': deepcopy(quote), 'status': 'not_calculated', 'calculation': None}
        try:
            candidate = deepcopy(valuation)
            candidate['price'] = _block(quote, '候选报价')
            record.update(status='calculated', calculation=_base(candidate))
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            record['reason'] = str(exc)
        result['price_grid'].append(record)
    return result
