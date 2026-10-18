"""Read-only EPV history and optional first-module research context."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

# Exact statement-specific aliases; raw operating profit is NOT normalized EBIT.
FIELDS = {
    'reported_operating_profit': ('income', ('operate_profit', '营业利润', '经营溢利', '经营利润', '營業利潤', '經營溢利')),
    'profit_before_tax': ('income', ('total_profit', '除税前溢利', '税前利润', '除稅前溢利')),
    'income_tax': ('income', ('income_tax', '所得税', '所得税开支', '所得稅開支')),
    'finance_cost': ('income', ('fin_exp', 'finance_cost', '财务费用', '融资成本', '財務成本')),
    'interest_expense': ('income', ('int_exp', '利息支出')),
    'investment_income': ('income', ('invest_income', '投资收益', '应占联营公司溢利', '應佔聯營公司業績')),
    'selling_expense': ('income', ('sell_exp', '销售费用', '销售及分销费用')),
    'administrative_expense': ('income', ('admin_exp', '行政开支', '行政费用', '行政開支')),
    'research_expense': ('income', ('rd_exp', '研发费用')),
    'ppe_depreciation': ('cashflow', ('depr_fa_coga_dpba', '固定资产折旧', '物业、厂房及设备折旧')),
    'intangible_amortization': ('cashflow', ('amort_intang_assets', '无形资产摊销')),
    'capital_expenditure': ('cashflow', ('c_pay_acq_const_fiolta', '购买物业、厂房及设备', '购建固定资产、无形资产和其他长期资产支付的现金')),
}


def normalized_code(code):
    code = str(code).strip().upper()
    return code.split('.')[0].zfill(5) + '.HK' if code.endswith('.HK') else code


def make_history(data: dict, requested_years: int) -> dict:
    periods = []
    for snapshot in data.get('snapshots', []):
        metrics = deepcopy(snapshot.get('canonical', {}))
        for key, (statement, aliases) in FIELDS.items():
            # A supplied key is the host's selection, including an explicit
            # unknown (null or value=null). Aliases only fill absent semantics.
            if key in metrics:
                continue
            candidates = [f for alias in aliases for f in snapshot.get('statements', {}).get(statement, [])
                          if f['field'] == alias and f.get('value') is not None]
            if candidates:
                metrics[key] = deepcopy(candidates[0])
        periods.append({'period_end': snapshot['period_end'], 'report_type': snapshot['report_type'],
                        'currency': snapshot.get('currency'), 'scope': snapshot.get('scope'),
                        'metrics': metrics, 'report_facts': snapshot.get('report_facts', [])})
    periods.sort(key=lambda p: p['period_end'], reverse=True)
    annual = [p for p in periods if p['report_type'] == 'annual']
    warnings = list(data.get('warnings', []))
    if len(annual) < requested_years:
        warnings.append(f'请求{requested_years}年，实际取得{len(annual)}个完整财年；较短窗口可估计，不宣称覆盖两个周期。')
    ttm = {}
    if periods and annual and periods[0]['report_type'] != 'annual':
        current = periods[0]
        prior_date = str(int(current['period_end'][:4]) - 1) + current['period_end'][4:]
        previous = next((p for p in periods if p['period_end'] == prior_date and p['report_type'] == current['report_type']), None)
        year = next((p for p in annual if p['period_end'] < current['period_end']), None)
        if previous and year and previous['period_end'] < year['period_end']:
            same = all(p.get('currency') and p['currency'] == current['currency'] and p['scope'] == current['scope']
                       for p in (previous, year))
            if same:
                for key in ('revenue', 'reported_operating_profit', 'net_income', 'parent_net_income',
                            'operating_cashflow', 'capital_expenditure', 'income_tax'):
                    facts = [p['metrics'].get(key) for p in (year, current, previous)]
                    if all(f and isinstance(f.get('value'), (int, float)) and not isinstance(f['value'], bool)
                           and f.get('unit') == 'currency' and f.get('currency') == current['currency'] for f in facts):
                        ttm[key] = {'value': facts[0]['value'] + facts[1]['value'] - facts[2]['value'],
                                    'currency': current['currency'], 'unit': 'currency',
                                    'formula': '最近完整年度 + 本期累计 - 上年同累计',
                                    'periods': [p['period_end'] for p in (year, current, previous)],
                                    'sources': [f.get('source') for f in facts],
                                    'note': '仅算术参照，未调整分拆、会计口径及直营加盟变化，不是正常化盈利。'}
        if not ttm:
            warnings.append('缺同币种同口径上年同期或完整年度事实，未生成TTM；没有把季度/半年乘四/乘二。')
    if periods:
        missing = [key for key in ('revenue', 'reported_operating_profit', 'operating_cashflow', 'capital_expenditure')
                   if not periods[0]['metrics'].get(key) or periods[0]['metrics'][key].get('value') is None]
        if missing:
            warnings.append(f"{periods[0]['period_end']}关键事实字段缺失：{', '.join(missing)}；保留缺项，研究时查财报，不用期末现金/净利润替代。")
    return {'requested_years': requested_years, 'annual_periods': len(annual), 'periods': periods,
            'ttm_reference': ttm, 'warnings': warnings,
            'note': '报表营业利润不自动视作EBIT；需独立排除融资、投资和非正常因素。历史会计范围须研究后判断。'}


def load_asset_context(asset_run, code):
    root = Path(asset_run).expanduser().resolve()
    source_input = json.loads((root / 'input.json').read_text(encoding='utf-8'))
    source = json.loads((root / 'valuation.json').read_text(encoding='utf-8'))
    if normalized_code(source_input.get('issuer', {}).get('code', '')) != normalized_code(code):
        raise ValueError('资产研究引用不是同一企业')
    if source.get('method', source_input.get('method', 'asset')) not in ('asset', 'asset_reproduction_v1'):
        raise ValueError('asset-run须为资产研究，而不是另一个EPV结果')
    premise = source.get('premise')
    dates = premise if isinstance(premise, dict) else {}
    # Do not feed final asset totals, target share prices or market comparison into normalization.
    items = [{k: deepcopy(v) for k, v in item.items()
              if k in ('id', 'name', 'kind', 'operating', 'value', 'book_value', 'basis', 'reason', 'sources', 'include', 'formula')}
             for item in source.get('items', [])]
    return {'source_run': str(root), 'issuer': source_input.get('issuer'),
            'valuation_date': source.get('valuation_date') or source.get('effective_date') or dates.get('valuation_date'),
            'currency': source.get('currency'), 'scope': source.get('scope'),
            'source_status': source.get('scope_status') or source.get('status') or '完整性未自动确认，需阅读限制',
            'premise': premise, 'items': items, 'assumptions': source.get('assumptions'),
            'unmeasured': source.get('unmeasured'),
            'financial_position_date': source.get('financial_position_date'),
            'reproduction_context': deepcopy(source.get('reproduction_context')),
            'use': '仅复用成本/寿命/权属证据，金额需重判；不自动加总资产价值、不升级局部测算。'}


def load_review_asset_reference(input_data):
    """Only the final EPV review receives an independently computed asset total.

    Read an explicitly selected source, never search for another channel's run.
    Missing optional comparison does not block the EPV estimate.
    """
    context = input_data.get('asset_context') or {}
    source_run = context.get('source_run') if isinstance(context, dict) else None
    if not source_run:
        return None
    try:
        code = input_data['issuer']['code']
        checked = load_asset_context(source_run, code)
        source_path = Path(source_run).expanduser().resolve() / 'valuation.json'
        source = json.loads(source_path.read_text(encoding='utf-8'))
        from .valuation import _base_calculate
        result = _base_calculate(source)
        status = checked['source_status']
        if status not in ('full', 'partial'):
            status = 'unknown'
        if any(row.get('material') for row in result.get('missing_items', [])):
            status = 'partial'
        premise = source.get('premise') if isinstance(source.get('premise'), dict) else {}
        return {'equity_value': result['equity_value'], 'currency': result['currency'],
                'valuation_date': checked['valuation_date'],
                'financial_position_date': source.get('financial_position_date'),
                'scope': checked['scope'], 'lease_basis': source.get('lease_basis', premise.get('lease_basis')),
                'status': status, 'source_status': checked['source_status'], 'comparable': False,
                'sources': [str(source_path)], 'unmeasured': checked.get('unmeasured'),
                'warnings': result['warnings'],
                'use': '独立EPV综合完成后才提供；只解释差异，不据此倒调盈利，不把未知完整性升级为full。'}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'status': 'unavailable', 'comparable': False, 'equity_value': None,
                'reason': f'可选资产比较未取得：{exc}；不阻断EPV。'}


