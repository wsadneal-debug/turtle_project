"""A compact price/return report from the final calculation; no inferred target."""
from __future__ import annotations

from .reporting import _paragraph, _text, _amount
from .report_reader import DisplayUnits


def _rate(value):
    return '未计算' if value is None else f'{value:.2%}'


def _points(value):
    return '未计算' if value is None else f'{value * 100:+.2f}个百分点'


def _requirement(value):
    return '未作数值判定' if value is None else '达到所给条件要求（非买入指令）' if value else '未达到所给条件要求'


def _calculation_state(c):
    return {'conditional_estimate': '条件算术已完成', 'incomplete_factor': '未采用唯一投资因子',
            'incomplete_inputs': '关键输入未齐', 'unfunded_growth': '分配与增长存在资金缺口',
            'missing_or_nonpositive_core_price': '缺报价或核心买价非正',
            'nonpositive_earnings': '正常盈利非正，仅作诊断',
            'diagnostic_only': '适用性未获支持，仅作诊断'}.get(c.get('status'), '沿本行条件解释')


def _net_return(c):
    if c.get('net_return') is not None:
        return _rate(c['net_return'])
    if c.get('decay_deduction') is None:
        return '衰减未量化，未给净回报'
    return '基准尚无唯一数值'


def _comparison(c):
    if c.get('additional_margin') is None:
        return '未设置额外门槛；不影响已有条件分析'
    return _requirement(c.get('meets_explicit_return_requirement'))


def _headline(c):
    label = '核心购买成本M上的' if c.get('scope') == 'enterprise' else '所选权益扣净调整后M上的'
    if c.get('baseline_return') is not None:
        net = f"衰减后净回报：{_net_return(c)}" if c.get('net_return') is not None else _net_return(c)
        return f"**{label}条件基准回报：{_rate(c['baseline_return'])}；{net}；匹配资本成本：{_rate(c['capital_cost'])}。**"
    # Do not replace a missing baseline by a scenario midpoint or combine price
    # grids / different capital scopes into an invented uncertainty interval.
    values = [r['calculation']['baseline_return'] for r in c.get('scenarios', [])
              if r.get('status') == 'calculated' and r.get('calculation')
              and r['calculation'].get('status') == 'conditional_estimate'
              and r['calculation'].get('scope') == c.get('scope')
              and r['calculation'].get('currency') == c.get('currency')
              and r['calculation'].get('baseline_return') is not None]
    if values:
        span = _rate(values[0]) if len(values) == 1 else f'{min(values):.2%}—{max(values):.2%}'
        return (f"**{_calculation_state(c)}；已执行{len(values)}项同口径联合假设，{label}基准回报参照为{span}。**"
                ' 各情景条件见下表，不取中点、不视为置信区间或风险已全部扣除。')
    return f"**{_calculation_state(c)}；保留已知资金账与判断，不补造完整回报。**"


def _source_limit_lines(inputs, valuation):
    context = valuation.get('module_context') or inputs.get('module_context') or {}
    groups = [(label, (context.get(key) or {}).get('unmeasured'))
              for key, label in (('asset', '源资产'), ('epv', '源EPV'))]
    groups.append(('源EPV', (valuation.get('source_limitations') or {}).get('unmeasured')))
    seen, rows = [], []
    for label, content in groups:
        items = content if isinstance(content, list) else [content] if content else []
        for item in items:
            if item not in seen:
                seen.append(item)
                rows.append(f'**{label}：** {_paragraph(item)}')
    if not rows:
        return []
    return ['', '## 上游原有条件与局限（合并展示）', '',
            '以下保留来源当时的说明；本轮处理见采用依据及上游影响。仅合并完全相同项，不按关键词删风险或宣告已解决。',
            *rows]


def _scenario_lines(c, unit):
    lines = []
    for key, heading in (('price_grid', '不同明确价格下的回报'), ('scenarios', '联合假设对照')):
        rows = c.get(key) or []
        if not rows:
            continue
        lines += ['', f'## {heading}', '',
                  '| 对照 | 股权买价Q | 净调整B | 核心买价M | 基准回报 | 净回报 | 计算状态 |',
                  '| --- | ---: | ---: | ---: | ---: | --- | --- |']
        for index, row in enumerate(rows, 1):
            result = row.get('calculation')
            quote = row.get('price') if isinstance(row.get('price'), dict) else {}
            title = row.get('name') or quote.get('name') or f'价格{index}'
            if result:
                state = _calculation_state(result)
                if result.get('return_surplus') is not None:
                    state += '；余量' + _points(result['return_surplus'])
                if result.get('additional_margin') is not None:
                    state += '；' + _requirement(result.get('meets_explicit_return_requirement'))
                if result.get('scope') != c.get('scope'):
                    state += '；资本口径不同，不混成区间'
                lines.append(f"| {_text(title)} | {unit.amount(result['equity_purchase_cost'])} | {unit.amount(result['equity_adjustment'])} | {unit.amount(result['core_purchase_cost'])} | {_rate(result['baseline_return'])} | {_net_return(result)} | {state} |")
            else:
                lines.append(f"| {_text(title)} | — | — | — | — | — | 未计算：{_text(row.get('reason'))} |")
        lines += ['每行均按各自明确参数重算；计算状态不是投资通过。M=Q−B，固定B的情景没有检验金融资源可兑现性。']
    return lines


def _module_lines(inputs, valuation):
    context = valuation.get('module_context') or inputs.get('module_context') or {}
    if not context:
        return []
    lines = ['', '## 前两模块的衔接（原日期、原假设）', '',
             '| 模块 | 原归母价值 | 估值日／财务存量日 | 范围说明 |',
             '| --- | ---: | --- | --- |']
    for key, label in (('asset', '资产再生产价值'), ('epv', '无增长EPV')):
        row = context.get(key) or {}
        value, currency = row.get('equity_value'), row.get('currency')
        unit = DisplayUnits({'equity_value': value, 'currency': currency or '未明币种'})
        amount = f'{unit.amount(value)} {unit.label}' if value is not None else '未提供数值，不视为零'
        state = {'full': '原报告完整范围', 'partial': '原报告仅部分范围',
                 'not_provided': '未提供，不强制补跑', 'unavailable': '本轮未取得',
                 'unknown': '原范围待核'}.get(row.get('status'), '沿原报告条件与局限')
        dates = f"{_text(row.get('valuation_date'))}／{_text(row.get('financial_position_date'))}"
        lines.append(f'| {label} | {amount} | {dates} | {state} |')
    lines += ['两种价值不相加，也不自动证明护城河。日期、币种、范围或租赁未对齐时，不计算精确差额；缺少资产总值不妨碍定性判断。']
    return lines


def _advantage_lines(valuation):
    franchise = valuation.get('franchise') or {}
    if not isinstance(franchise, dict):
        return []
    labels = {'market': '实际竞争市场', 'protection': '竞争者难以复制之处',
              'durability': '持续性与变化', 'growth_scope': '优势保护的增长范围',
              'incremental_returns': '新增投入回报依据', 'counterevidence': '最强反证'}
    rows = [f"**{label}：** {_paragraph(franchise[key])}" for key, label in labels.items() if franchise.get(key)]
    return ['', '## 持续竞争优势判断', '', *rows] if rows else []


def _terminal_report(inputs, valuation, calculation):
    name = inputs.get('issuer', {}).get('name') or inputs.get('issuer', {}).get('code') or '企业'
    definite = calculation['status'] == 'not_applicable'
    title = '本轮不采用成长回报定价' if definite else '关键适用性问题尚未解决，本轮暂不采用成长溢价'
    lines = [f'# {_text(name)}成长模块适用性结论', '', f'**{title}。**', '',
             calculation['reason']]
    summary = valuation.get('summary')
    if summary and summary != calculation['reason']:
        lines += ['', _paragraph(summary)]
    computation_note = ('综合阶段曾计算初稿，但主复核已撤回采用；原计算保留在复核输入中，未生成新的成长回报结果。'
                        if calculation.get('preliminary_calculation_performed') else
                        '本轮没有计算成长回报；不要求填写报价、增长率、投资因子或衰减率。')
    lines += ['', computation_note
              + ('这不是对整家公司的投资否决。' if definite else '这不等于已经证明企业没有竞争优势。')]
    if inputs.get('simulation') or valuation.get('research', {}).get('mode') == 'simulated':
        lines += ['', '**本轮为合成／离线模拟，不是实际企业投资结论。**']
    lines += _advantage_lines(valuation)
    for key, label in (('capital_allocation_risk', '仍需关注的资本配置风险'),
                       ('upstream_implications', '对原资产与EPV判断的影响'),
                       ('unmeasured', '决定性未明事项'), ('follow_up', '后续处理')):
        if valuation.get(key):
            lines += ['', f'## {label}', '', _paragraph(valuation[key])]
    lines += _module_lines(inputs, valuation)
    limits = valuation.get('source_limitations') or {}
    lines += _source_limit_lines(inputs, valuation)
    warnings = list(inputs.get('warnings') or []) + list(limits.get('warnings') or [])
    if inputs.get('materials_ready') is False:
        warnings.append('材料未齐，不声称已完成全部财报核查。')
    if warnings:
        lines += ['', '## 资料边界', '', *[str(x) for x in dict.fromkeys(warnings)]]
    lines += ['', '不为成长支付溢价，不代表忽略毁值扩张。若本轮证据损害旧盈利前提，保留原稿并明确需要修订，不能把旧EPV称为保证底价。']
    for key, label in (('materials_read', '实际阅读'), ('sources', '依据来源')):
        if valuation.get(key):
            lines += ['', f'## {label}', '', _paragraph(valuation[key])]
    return '\n'.join(lines).rstrip() + '\n'


def render_report(inputs: dict, valuation: dict, calculation: dict) -> str:
    c, v = calculation, valuation
    if c.get('calculation_performed') is False:
        return _terminal_report(inputs, v, c)
    unit = DisplayUnits({'equity_value': c.get('equity_purchase_cost'), 'currency': c['currency']})
    name = inputs.get('issuer', {}).get('name') or inputs.get('issuer', {}).get('code') or '企业'
    scope = '核心经营／全部资本提供者' if c['scope'] == 'enterprise' else '所选普通股权益'
    fit = {'supported': '有依据支持', 'conditional': '有条件支持',
           'unsupported': '不支持使用成长溢价', 'not_assessed': '尚未形成适用性判断'}[c['franchise_status']]
    purchase, distribution = c.get('equity_purchase_cost'), c.get('distribution')
    distribution_over_price = distribution / purchase if purchase is not None and purchase > 0 and distribution is not None else None
    lines = [f'# {_text(name)}成长回报定价研究', '', _headline(c), '',
             f"**全部股权买价Q：{unit.amount(purchase)} {unit.label}；扣净调整后的核心买价M：{unit.amount(c['core_purchase_cost'])} {unit.label}。**",
             f"同一年度分配D／全部股权买价Q：{_rate(distribution_over_price)}（仅作量级参照，D可含其他资本提供者分配，并非个人股息率或IRR）。",
             '上述基准按M计算，不是按整笔股票买价计算的年化收益；金融资源能否独立兑现及何时兑现，仍按本轮经济假设判断。', '',
             '本模块以给定价格上的回报作判断，不产生独立成长总价、精确最高买价或卖价，不与资产价值和EPV相加。', '',
             f"研究截止日：{_text(inputs.get('as_of'))}；盈利基础日：{_text(v.get('basis', {}).get('valuation_date'))}；财务存量日：{_text(v.get('basis', {}).get('financial_position_date'))}。",
             f'采用口径：{scope}；金额以{unit.label}展示，比例以百分比展示。', '',
             f'**方法适用性：{fit}。**', _paragraph((v.get('franchise') or {}).get('reason')), '',
             '## 结论与决定性理由', '', _paragraph(v.get('summary'))]
    if inputs.get('simulation') or v.get('simulation') or v.get('research', {}).get('mode') == 'simulated':
        lines += ['', '**本轮为合成／离线模拟，不是实际企业投资结论。**']
    if inputs.get('materials_ready') is False:
        lines += ['', '材料未齐：保留条件研究，不声称已完成全部财报核查。']
    if c.get('baseline_return') is None:
        lines += _scenario_lines(c, unit)
    lines += _advantage_lines(v)
    lines += _module_lines(inputs, v)
    if v.get('capital_allocation_risk'):
        lines += ['', '## 仍需关注的资本配置风险', '', _paragraph(v['capital_allocation_risk'])]
    if v.get('upstream_implications'):
        lines += ['', '## 对原资产与EPV判断的影响', '', _paragraph(v['upstream_implications'])]
    lines += ['', '## 从股权价格到核心购买成本', '',
              '| 项目 | 金额 |', '| --- | ---: |',
              f"| 普通股权益购买成本 | {unit.amount(c['equity_purchase_cost'])} |",
              f"| 减：核心价值至归母权益的净调整B | {unit.amount(c['equity_adjustment'])} |",
              f"| 核心购买成本M | {unit.amount(c['core_purchase_cost'])} |", '', c['price_note'],
              'B中资源为正、融资与外部权益为负：反向扣B还原核心购买成本；不是再加一次净现金。', '',
              '## 年度资金分配：同一份盈利只能用一次', '',
              '| 项目 | 金额 |', '| --- | ---: |',
              f"| 维护后、增长投入前的正常年度可分配盈利E | {unit.amount(c['earnings_power'])} |",
              f"| 减：可持续分配D | {unit.amount(c['distribution'])} |",
              f"| 减：有机增长增量投入 | {unit.amount(c['organic_investment'])} |",
              f"| 余下积极投资资金A | {unit.amount(c['active_investment'])} |",
              f"| 资金缺口 | {unit.amount(c['funding_gap'])} |", '',
              '企业口径的分配并不等于个人到账股息；回购、债务、利息与新投入的归属和含义需按本轮假设理解。', '',
              '## 三项回报、衰减与余量', '', '| 来源 | 条件贡献 |', '| --- | ---: |',
              f"| 分配贡献D/M | {_rate(c['cash_return'])} |",
              f"| 有机盈利增长（基准假设V≈M） | {_rate(c['organic_return'])} |",
              f"| 积极投资贡献A×F/M | {_rate(c['active_return'])} |",
              f"| 基准合计 | {_rate(c['baseline_return'])} |",
              f"| 单独衰减扣减 | {_rate(c['decay_deduction']) if c['decay_deduction'] is not None else '未量化，未设数值扣减'} |",
              f"| 净回报 | {_net_return(c)} |",
              f"| 资本成本 | {_rate(c['capital_cost'])} |",
              f"| 衰减前基准与资本成本之差 | {_points(c['gross_gap_to_capital_cost'])} |",
              f"| 扣衰减或明确补偿后的回报余量 | {_points(c['return_surplus'])} |",
              f"| 另行给定的额外余量要求 | {_rate(c['additional_margin']) if c['additional_margin'] is not None else '未设置额外门槛'} |", '',
              c['decay_note'], _paragraph((v.get('decay') or {}).get('reason')),
              f"数值比较：{_comparison(c)}。",
              '余量的单位是百分点，不是亏损概率或相对价值折扣；额外要求未给定时不捏造默认门槛。']
    if c['qualitative_decay_buffer'] is not None:
        lines += [f"定性衰减另需补偿：{_rate(c['qualitative_decay_buffer'])}。这是要求回报余量，不是估计出的真实年衰减率。"]
    lines += ['', '## 积极投资形成的价值', '',
              f"采用因子：{'无须或尚未估计' if c['factor'] is None else format(c['factor'], '.3g')}；{c['factor_note']}。",
              f"本年积极投入形成的全部价值：{unit.amount(c['active_annual_value'])} {unit.label}。",
              f"扣回投入本金后的净创造价值：{unit.amount(c['active_net_value_created'])} {unit.label}。",
              '前者用于回报贡献，后者只解释创造或毁损，不能再加到EPV或再次加入回报。']
    if c['one_step_downward']:
        adjustment = c['one_step_downward']
        lines += ['', '## 买贵时的一次向下提示', '',
                  f"V/M提示性代理约{adjustment['value_price_proxy']:.2f}；有机贡献调整为{_rate(adjustment['organic_return'])}；调整后净回报约{_rate(adjustment['net_return'])}。",
                  adjustment['note']]
    if c.get('baseline_return') is not None:
        lines += _scenario_lines(c, unit)
    if v.get('unmeasured'):
        lines += ['', '## 重要未明事项', '', _paragraph(v['unmeasured'])]
    limits = v.get('source_limitations') or {}
    lines += _source_limit_lines(inputs, v)
    if c.get('equity_purchase_cost') is not None:
        lines += ['', '本轮已有可计算的报价与换算输入（见报价依据），不等于程序独立验证市场真实性；源稿的未获取报价说明只描述当时状态，不影响其他仍存局限。']
    warnings = (list(inputs.get('warnings') or []) + list(c['warnings'])
                + list(limits.get('warnings') or []) + list(v.get('input_binding_notes') or []))
    if warnings:
        lines += ['', '## 边界与执行说明', '', *['- ' + str(w) for w in dict.fromkeys(warnings)]]
    lines += ['', '---', '<a id="growth-audit"></a>', '## 复核底稿', '',
              '<details>', '<summary>展开采用依据、出处、原始口径及研究说明</summary>', '']
    for key, label in (('basis', '本轮盈利与资本基础'), ('source_basis', '源EPV基础'),
                       ('basis_change_reason', '基础修改原因'), ('upstream_context', '来源与日期'),
                       ('price', '本次报价'), ('policy', '本次额外要求'),
                       ('distribution', '分配依据'), ('organic', '有机增长及投入'), ('active', '积极投资依据'),
                       ('decay', '衰减依据'), ('adoptions', '采用与分歧'), ('review', '主复核'),
                       ('assumptions', '重要假设'), ('materials_read', '实际阅读'), ('sources', '来源'),
                       ('model_basis', '未直接采用的模型基础'), ('model_request_overrides', '未替代人工输入的模型建议')):
        if v.get(key):
            lines += [f'### {label}', '', _paragraph(v[key]), '']
    lines += ['### 数值复核（基本货币单位，未舍入结果见valuation.json）', '',
              '| 项目 | 数值 |', '| --- | ---: |']
    for key in ('equity_purchase_cost', 'equity_adjustment', 'core_purchase_cost', 'earnings_power',
                'distribution', 'organic_investment', 'active_investment', 'funding_gap', 'active_annual_value', 'active_net_value_created'):
        lines.append(f'| {key} | {_amount(c.get(key))} |')
    for key in ('price_grid', 'scenarios'):
        if c.get(key):
            lines += ['', '### 全部' + ('报价' if key == 'price_grid' else '情景') + '参数与原因']
            for row in c[key]:
                lines += [_paragraph(row.get('parameters', row.get('price')))]
                if row.get('calculation') and row['calculation'].get('warnings'):
                    lines += [_paragraph(row['calculation']['warnings'])]
    lines += ['', '</details>', '', c['interpretation']]
    return '\n'.join(lines).rstrip() + '\n'
