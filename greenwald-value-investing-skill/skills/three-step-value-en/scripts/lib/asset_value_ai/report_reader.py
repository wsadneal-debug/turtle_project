"""Small reading layer over the *same* final ledger; no model, scoring or rounding in calculations."""
from __future__ import annotations

import math
from .reporting import _text, _paragraph, _inline


class DisplayUnits:
    def __init__(self, calculation: dict):
        values = [calculation.get(k) for k in ('equity_value', 'total_assets', 'core_epv')]
        largest = max((abs(v) for v in values if isinstance(v, (int, float)) and math.isfinite(v)), default=0)
        self.scale, prefix = (100_000_000, '亿') if largest >= 100_000_000 else (10_000, '万') if largest >= 10_000 else (1, '')
        code = calculation.get('currency') or '未提供币种'
        self.currency = {'CNY': '人民币', 'HKD': '港元', 'USD': '美元', 'CNH': '离岸人民币'}.get(code, code)
        self.label = prefix + ('元人民币' if code == 'CNY' else self.currency)

    def amount(self, value):
        if value is None:
            return '未计量'
        scaled = value / self.scale
        # Do not make a nonzero small adjustment disappear as 0.00.
        return f'{scaled:.3g}' if 0 < abs(scaled) < .01 else f'{scaled:,.2f}'


def rate(value):
    return '未计量' if value is None else f'{value:.1%}'


def adoptions_table(valuation, calculation, units):
    """Optional existing adoptions become a small table, not a second fact ledger.

    A recognized item_id/parameter gets its numeric value from calculation,
    not from model prose. Unrecognized/legacy rows retain their explanation.
    """
    entries = valuation.get('adoptions')
    if not entries:
        return []
    if not isinstance(entries, list) or any(not isinstance(row, dict) for row in entries):
        return ['## 本轮采用口径', '', _paragraph(entries)]
    by_id = {row['id']: row for row in calculation.get('items', []) + calculation.get('equity_bridge', [])}
    parameters = {'revenue', 'margin', 'maintenance_capex', 'wacc', 'normalized_ebit', 'earnings_power', 'cash_tax'}
    lines = ['## 本轮采用口径', '', '金额或参数有计算引用时直接取最终结果；其余为研究说明，不是另算一份估值。', '',
             '| 项目 | 原出处／期间 | 本轮采用 | 用途 | 沿用或调整理由 |', '| --- | --- | --- | --- | --- |']
    for row in entries:
        item_id = row.get('item_id')
        item = by_id.get(item_id) if isinstance(item_id, str) else None
        parameter = row.get('parameter')
        parameter = parameter if isinstance(parameter, str) else None
        if item is not None:
            adopted = units.amount(item.get('value')) + ' ' + units.label
            if item.get('included') is False or item.get('value') is None:
                adopted += '（未计入总值）'
        elif parameter in parameters and parameter in calculation:
            value = calculation[parameter]
            adopted = rate(value) if parameter in {'margin', 'wacc'} else units.amount(value) + ' ' + units.label
        else:
            adopted = _inline(row.get('adopted', row.get('decision', '未单列')))
            if row.get('item_id') or parameter:
                adopted += '（未匹配计算引用，仅保留研究说明）'
        origin = row.get('source', row.get('sources', '未单列'))
        period = row.get('period', row.get('period_end'))
        origin = _inline(origin) + ('；' + str(period) if period else '')
        cells = [row.get('issue', row.get('name', row.get('id', '未命名项目'))), origin, adopted,
                 row.get('purpose', '未单列'), row.get('reason', '详见原专项及完整采纳记录')]
        lines.append('| ' + ' | '.join(_text(cell) for cell in cells) + ' |')
    return lines


def asset_comparison_lines(valuation, calculation):
    comparison = valuation.get('asset_comparison')
    if not comparison:
        return []
    if not isinstance(comparison, dict):
        return ['## 资产价值与盈利价值的差异', '', _paragraph(comparison), '仅有讨论说明，未计算数值差额。']
    units = DisplayUnits(calculation)
    value = comparison.get('equity_value')
    numeric = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    lines = ['## 资产价值与盈利价值的差异', '',
             '比较的是两种估值所描述的经济含义，不把差额自动认定为护城河或成长价值。', '']
    if numeric:
        same_currency = comparison.get('currency') == calculation.get('currency')
        shown = units.amount(value) + ' ' + units.label if same_currency else f"{value:,.2f} {comparison.get('currency', '币种未列')}"
        lines.append(f"资产法参照：{shown}；范围状态：{_text(comparison.get('status', '未确认'))}。")
    aligned = (comparison.get('comparable') is True and comparison.get('status') == 'full'
               and comparison.get('currency') == calculation.get('currency')
               and valuation.get('scope') == 'parent_common'
               and comparison.get('scope') == 'parent_common'
               and valuation.get('valuation_date') and comparison.get('valuation_date') == valuation['valuation_date']
               and comparison.get('lease_basis') == valuation.get('earnings', {}).get('lease', {}).get('mode', 'none'))
    dates = (valuation.get('financial_position_date'), comparison.get('financial_position_date'))
    if any(dates):
        aligned = aligned and bool(dates[0] and dates[0] == dates[1])
    if aligned and numeric and value > 0 and calculation.get('equity_value') is not None:
        lines.append(f"EPV相对同口径资产价值差额：{calculation['equity_value'] / value - 1:+.1%}。无固定通过门槛，不代表已证明护城河。")
    else:
        lines.append('日期、范围、租赁或完整性未确认一致：仅并列，不计算精确折溢价；局部测算不升级为完整估值。')
    if comparison.get('reason'):
        lines += ['', _paragraph(comparison['reason'])]
    else:
        lines += ['', '本轮未单列差异解释，不由程序代写竞争优势结论。']
    if comparison.get('sources'):
        lines += ['', '比较出处：' + _inline(comparison['sources'])]
    return lines


def tax_arithmetic_lines(valuation, calculation, units):
    """Expose the actual tax path; never infer tax law from model prose."""
    spec = valuation.get('tax') or {}
    total = calculation.get('cash_tax')
    if total is None:
        return ['实际正常现金税尚无完整数值；不能据文字说明认定税差已处理。']
    adjustments = [r.get('value') for r in calculation.get('tax_adjustments', []) if r.get('included')]
    delta = math.fsum(x for x in adjustments if x is not None)
    base = total - delta
    formula = (f"max(正常EBIT, 0) × {rate(spec.get('rate'))}"
               if spec.get('mode', 'rate') == 'rate' else '直接年度税额')
    note = '；另有未计量税差' if any(x is None for x in adjustments) else ''
    return [f"实际计税：{formula} = {units.amount(base)}，加已量化税差 {units.amount(delta)}，现金税合计 {units.amount(total)} {units.label}{note}。",
            '折旧摊销加回不自动增加税基；税率已吸收的差异不能再加税，未吸收的差异须进入税差参数。']


def compose_report(inputs, valuation, calculation, details: str, *, method: str) -> str:
    """Reading pages first; complete original explanations stay in an appendix."""
    c, v = calculation, valuation
    units = DisplayUnits(c)
    issuer = inputs.get('issuer', {}).get('name') or inputs.get('issuer', {}).get('code') or '企业'
    name = '盈利能力价值' if method == 'epv' else '资产价值'
    per_share = '未计量' if c.get('per_share') is None else f"{c['per_share']:.2f} {units.currency}/股"
    headline = ('尚未形成完整金额' if c.get('equity_value') is None
                else f"约 {units.amount(c['equity_value'])} {units.label}")
    lines = [f'# {_text(issuer)}{name}研究', '',
             f"**基准归母普通股价值：{headline}；每股 {per_share}。**", '']
    premise = v.get('premise')
    dates = premise if isinstance(premise, dict) else {}
    as_of = v.get('valuation_date') or v.get('effective_date') or dates.get('valuation_date') or dates.get('effective_date') or '未单列'
    lines += [f"估值基准日：{as_of}；研究截止日：{inputs.get('as_of') or '未单列'}。"]
    if method == 'epv':
        lines += [f"股权桥财务存量日：{v.get('financial_position_date') or '未单列'}；{v.get('equity_basis') or '期后调整及含息口径未单列'}。",
                  '当前正常规模、不增长的条件估计；不是分红承诺或保证底价。']
    else:
        lines += ['估值前提：', _paragraph(premise), '基准包含研究估计；再生产价值不等于保证清算所得。']
    if inputs.get('simulation') or v.get('simulation') or v.get('research', {}).get('mode') == 'simulated':
        lines += ['**合成／模拟结果，不是企业真实估值。**']
    if inputs.get('materials_ready') is False:
        lines += ['**材料尚未准备齐全：本轮数值只能按现有材料与显式假设理解，不能称已完成完整财报研究。**']
    lines += ['', f'正文金额采用{units.label}，显示为约数；基本单位明细、全部来源与研究边界见[复核底稿](#audit-detail)。未舍入计算数保存在valuation.json。', '',
              '## 结论与主要依据', '', _paragraph(v.get('summary'))]
    if method == 'epv':
        lines += ['', '## 三个主要估值参数', '', '| 参数 | 本轮采用 |', '| --- | ---: |',
                  f"| 正常营业利润率（显式调整前） | {rate(c.get('margin'))} |",
                  f"| 年度维护投入（{units.label}） | {units.amount(c.get('maintenance_capex'))} |",
                  f"| 资本成本 | {rate(c.get('wacc'))} |", '',
                  '参数不是已获保证的未来；历史位置、采用理由及其他重要假设均保留在底稿。', '',
                  f'## 从经营盈利到经营价值（{units.label}）', '', '| 项目 | 金额或比例 |', '| --- | ---: |']
        for row in c.get('earnings_bridge', []):
            amount = rate(row['value']) if row['name'] == '正常营业利润率' else units.amount(row['value'])
            lines.append(f"| {_text(row['name'])} | {amount} |")
        lines += [f"| 资本成本 | {rate(c.get('wacc'))} |", f"| 核心经营EPV | {units.amount(c.get('core_epv'))} |", '']
        lines += tax_arithmetic_lines(v, c, units)
        lines += ['', f'## 从经营价值到普通股权益（{units.label}）', '', '| 项目 | 对权益影响 |', '| --- | ---: |',
                  f"| 核心经营EPV | {units.amount(c.get('core_epv'))} |"]
        # Show the bridge's final contributions, never model-supplied totals.
        names = {'excess_cash': '超额现金', 'nonoperating_asset': '非经营资产', 'associate': '参股权益', 'tax_benefit': '有限税利益',
                 'lease_advantage': '有利租约', 'financing_debt': '融资债务', 'legacy_liability': '遗留义务',
                 'transition_cost': '过渡支出', 'nci': '少数权益', 'preferred': '优先权益', 'lease_debt': '单列租赁义务'}
        grouped = {}
        for row in c.get('equity_bridge', []):
            if row.get('included'):
                kind = row['kind']
                grouped.setdefault(kind, []).append(row.get('effect'))
        for kind, values in grouped.items():
            total = sum(x for x in values if x is not None)
            note = '（另有未计量项）' if any(x is None for x in values) else ''
            lines.append(f"| {names.get(kind, kind)}{note} | {units.amount(total) if any(x is not None for x in values) else '未计量'} |")
        lines += [f"| 归母普通股EPV | {units.amount(c.get('equity_value'))} |"]
    else:
        lines += ['', f'## 资产与权益计算（{units.label}）', '', '| 口径 | 金额 |', '| --- | ---: |']
        for key, label in [('operating_assets', '经营资产再生产成本总额'), ('operating_net_assets', '经营净资产再生产价值'),
                           ('total_assets', '全部资产'), ('total_liabilities', '减：全部负债'),
                           ('minority_interests', '减：少数权益'), ('preferred_interests', '减：其他优先权益'), ('equity_value', '归母普通股资产价值')]:
            lines.append(f'| {label} | {units.amount(c.get(key))} |')
        lines += ['', '经营净资产为分类参照；归母总值仍按全部资产减全部义务计算，不再次加净现金。']
        assumptions = v.get('assumptions')
        if isinstance(assumptions, list) and assumptions:
            lines += ['', '## 主要假设提示', '', '按研究原顺序展示前三项；全部假设与原参数在底稿保留，不据数量判断质量。']
            for row in assumptions[:3]:
                if isinstance(row, dict):
                    label = row.get('name', row.get('issue', row.get('id', '假设')))
                    explanation = row.get('reason', row.get('description', row.get('conclusion')))
                    lines += ['**' + str(label) + '**：' + (_inline(explanation) if explanation is not None else '具体参数见底稿；未单列原因。')]
                else:
                    lines += [_paragraph(row)]
    lines += ['', *adoptions_table(v, c, units)]
    if method == 'epv':
        lines += ['', *asset_comparison_lines(v, c)]
    scenarios = c.get('scenarios', []) if method == 'epv' else c.get('joint_scenarios', [])
    if isinstance(scenarios, list) and scenarios:
        lines += ['', f'## 主要情景（{units.label}）', '', '| 情景 | 执行情况 | 归母价值 | 每股价值 |', '| --- | --- | ---: | ---: |']
        for row in scenarios:
            result = row.get('calculation')
            state = row.get('status', 'calculated')
            status = '已重算的条件估计' if state == 'calculated' else '未计算总值'
            amount = units.amount(result.get('equity_value')) if result else '—'
            share = f"{result['per_share']:.2f}" if result and result.get('per_share') is not None else '—'
            lines.append(f"| {_text(row.get('name'))} | {status} | {amount} | {share} |")
        lines += ['', '仅说明各组假设下的结果，不是置信区间、亏损概率或保证上下限。全部情景理由及未计算原因见底稿。']
    if v.get('unmeasured'):
        lines += ['', '## 会限制结论的事项', '', _paragraph(v['unmeasured']), '未计量义务不能当零；基准并非已验证下限。']
    # Keep calculation caveats visible; do not suppress them by a numeric threshold.
    if c.get('warnings'):
        lines += ['', '## 计算边界', '', *['- ' + str(w) for w in dict.fromkeys(c['warnings'])]]
    lines += ['', '---', '<a id="audit-detail"></a>', '## 复核底稿：基本单位明细、来源及全部研究说明', '',
              '<details>', '<summary>展开完整底稿（不支持折叠的阅读器可继续向下阅读）</summary>', '', details, '', '</details>']
    return '\n'.join(lines).rstrip() + '\n'
