"""EPV report: two bridges, auditable assumptions and recomputed scenarios."""
from .reporting import _amount, _text, _paragraph, _market_comparison


def _rate(value):
    return '未计量' if value is None else f'{value:.2%}'


def _render_details(inputs, valuation, calculation):
    c = calculation
    issuer = inputs.get('issuer', {})
    research = valuation.get('research', {})
    lines = [f"# {_text(issuer.get('name') or issuer.get('code') or '企业')}盈利能力价值研究", '',
             f"**归母普通股EPV：{_amount(c['equity_value'])} {c['currency']}；每股 {_amount(c['per_share'])}。**", '',
             f"估值基准日：{_text(valuation.get('valuation_date'))}；研究截止日：{_text(inputs.get('as_of'))}。",
             f"股权桥财务存量日：{_text(valuation.get('financial_position_date') or '未单列')}；股权桥口径：{_text(valuation.get('equity_basis') or '未单列')}。",
             f"金额单位：{c['currency']}基本单位；盈利、税和维护为完整年度流量，股权桥存量以单列财务存量日为准。",
             '假设当前正常业务不增长。结果不是分红承诺、清算底价或自动买入结论；不与资产价值相加。', '',
             '| 核心结果 | 数值 |', '| --- | ---: |',
             f"| 正常收入 | {_amount(c['revenue'])} |", f"| 正常营业利润率（显式调整前） | {_rate(c['margin'])} |",
             f"| 可持续可分配经营盈利 | {_amount(c['earnings_power'])} |", f"| WACC | {_rate(c['wacc'])} |",
             f"| 核心经营EPV | {_amount(c['core_epv'])} |", f"| 归母普通股EPV | {_amount(c['equity_value'])} |",
             f"| 普通股数 | {_amount(c['shares'])} |", f"| 每股EPV | {_amount(c['per_share'])} |", '']
    if inputs.get('simulation') or valuation.get('simulation') or research.get('mode') == 'simulated':
        lines += ['**合成/模拟结果，仅验证计算和流程，不是企业真实估值。**', '']
    if research:
        lines += [f"研究模式：{_text(research.get('mode'))}；模型：{_text(research.get('model'))}；实际调用数：{_text(research.get('calls_used'))}。", '']
    lines += ['## 经营判断与基准理由', '', _paragraph(valuation.get('summary')), '', _paragraph(valuation.get('premise')), '',
              '## 第一张表：从营业利润到可分配经营盈利', '', '| 项目 | 金额/比例 |', '| --- | ---: |']
    for row in c['earnings_bridge']:
        value = _rate(row['value']) if row['name'] == '正常营业利润率' else _amount(row['value'])
        lines.append(f"| {_text(row['name'])} | {value} |")
    for key, label in [('ebit_adjustments', '税前调整'), ('maintenance_items', '年度维护分项'), ('tax_adjustments', '税差调整')]:
        if c[key]:
            lines += ['', f'### {label}', '', '| 项目 | 采用金额 | 计入 | 依据 |', '| --- | ---: | --- | --- |']
            for row in c[key]:
                detail = row.get('reason', '') + '；来源：' + _paragraph(row.get('sources', []))
                if row.get('gross_cost') is not None:
                    detail += f"；全新成本{row['gross_cost']}，残值{row.get('residual', 0)}，更新周期{row.get('life_years')}年"
                lines.append(f"| {_text(row.get('name', row['id']))} | {_amount(row.get('value'))} | {'是' if row['included'] else '否'} | {_text(detail)} |")
    lines += ['', '## 第二张表：从核心经营EPV到归母权益', '',
              f"核心经营EPV：{_amount(c['core_epv'])}。", '',
              '| 项目 | 类别 | 估计金额 | 对权益影响 | 计入 | 理由及来源 |', '| --- | --- | ---: | ---: | --- | --- |']
    for row in c['equity_bridge']:
        detail = row.get('reason', '') + '；来源：' + _paragraph(row.get('sources', []))
        lines.append(f"| {_text(row.get('name', row['id']))} | {_text(row['kind'])} | {_amount(row['value'])} | {_amount(row.get('effect'))} | {'是' if row['included'] else '否'} | {_text(detail)} |")
    lines += ['', f"经营EPV {_amount(c['core_epv'])} + 股权调整净额 {_amount(c['equity_adjustment'])} = 归母EPV {_amount(c['equity_value'])}。", '',
              '## 税、资本成本、维护和租赁依据', '']
    for key, label in [('tax', '正常经营税负'), ('capital_cost', '资本成本'), ('maintenance', '维护性投入'), ('earnings', '正常化与租赁口径')]:
        detail = valuation.get(key)
        if key == 'tax' and isinstance(detail, dict):
            detail = dict(detail)
            if 'rate' in detail:
                detail['正常经营税率'] = _rate(detail.pop('rate'))
        lines += [f'### {label}', '', _paragraph(detail), '']
    if c['scenarios']:
        lines += ['## 联合情景（已实际重算）', '', '| 情景 | 盈利 | WACC | 归母EPV | 每股 |', '| --- | ---: | ---: | ---: | ---: |']
        for row in c['scenarios']:
            r = row['calculation']
            lines.append(f"| {_text(row['name'])} | {_amount(r['earnings_power'])} | {_rate(r['wacc'])} | {_amount(r['equity_value'])} | {_amount(r['per_share'])} |")
        for row in c['scenarios']:
            lines += ['', f"**{row['name']}：** {row['reason']}"]
            lines += [f'- {w}' for w in row['calculation']['warnings']]
    if c['sensitivity']:
        lines += ['', '## 利润率×资本成本敏感性（已实际重算）', '',
                  '其他假设保持基准；这不是概率置信区间，配对税项及维护变化另见联合情景。', '',
                  '| 营业利润率 | WACC | 年度可分配盈利 | 归母EPV | 每股 |', '| ---: | ---: | ---: | ---: | ---: |']
        for r in c['sensitivity']:
            lines.append(f"| {_rate(r['margin'])} | {_rate(r['wacc'])} | {_amount(r['earnings_power'])} | {_amount(r['equity_value'])} | {_amount(r['per_share'])} |")
    comparison = valuation.get('asset_comparison')
    if comparison:
        lines += ['', '## 与资产价值并列比较', '', _paragraph(comparison)]
        from .report_reader import asset_comparison_lines
        lines += ['', *asset_comparison_lines(valuation, c)]
    history = inputs.get('history', {})
    lines += ['', '## 资料与历史比较', '',
              f"完整年报及最新报告准备：{'已准备' if inputs.get('materials_ready') else '未齐'}；历史数据请求{history.get('requested_years', '未列')}年，取得{history.get('annual_periods', '未列')}个财年。",
              '历史数据年数不代表已逐年阅读全文或完成周期正常化；实际采用范围与利润率理由见下方研究说明。',
              '', '| 报告期 | 类型 | 原文 |', '| --- | --- | --- |']
    for r in inputs.get('reports', []):
        lines.append(f"| {_text(r.get('period_end'))} | {_text(r.get('report_type'))} | {_text(r.get('text_path') or r.get('url') or r.get('path'))} |")
    for key, label in [('history_analysis', '正常利润率的历史依据'), ('annual_comparison', '两个年度比较'), ('materials_read', '实际阅读'),
                       ('adoptions', '采纳与分歧'), ('review', '复核'), ('assumptions', '重要假设'),
                       ('distribution', '现金分配与留存使用'),
                       ('competitive_advantage', '盈利持续性与竞争优势（供后续核查）'),
                       ('unmeasured', '未明事项'), ('sources', '补充来源')]:
        if valuation.get(key):
            lines += ['', f'### {label}', '', _paragraph(valuation[key])]
    warnings = list(dict.fromkeys(inputs.get('warnings', []) + c['warnings'] + research.get('warnings', [])))
    if warnings:
        lines += ['', '## 局限与提示', ''] + [f'- {w}' for w in warnings]
    if valuation.get('unmeasured'):
        lines += ['', '**重大未计量项仍须结合条件解释；未扣完义务的数值不是验证下限。**']
    if valuation.get('market_comparison'):
        lines += [''] + [line.replace('资产价值', '盈利能力价值').replace('资产参数', '盈利及资本成本参数').replace('资产已重估', '盈利已重新研究')
                        for line in _market_comparison(valuation, c)]
    return '\n'.join(lines).rstrip() + '\n'


def render_report(inputs, valuation, calculation):
    from .report_reader import compose_report
    return compose_report(inputs, valuation, calculation,
                          _render_details(inputs, valuation, calculation), method='epv')
