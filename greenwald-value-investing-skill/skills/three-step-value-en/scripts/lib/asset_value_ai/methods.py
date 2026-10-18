"""Small explicit dispatch; legacy untagged valuations remain asset valuations."""


def method_name(value):
    aliases = {None: 'asset', 'asset': 'asset', 'asset_reproduction_v1': 'asset',
               'epv': 'epv', 'earnings_power_v1': 'epv',
               'growth': 'growth', 'growth_returns_v1': 'growth'}
    if value not in aliases:
        raise ValueError(f'未知估值方法：{value}')
    return aliases[value]


def select_method(inputs, valuation=None, requested=None):
    candidates = []
    if requested is not None:
        candidates.append(method_name(requested))
    if inputs.get('method') is not None:
        candidates.append(method_name(inputs['method']))
    if valuation is not None:
        candidates.append(method_name(valuation.get('method', 'epv' if 'earnings' in valuation else 'asset')))
    if len(set(candidates)) > 1:
        raise ValueError('输入、估值或命令指定的方法不一致；不同方法必须使用独立运行目录')
    return candidates[0] if candidates else 'asset'


def calculator(method):
    if method_name(method) == 'epv':
        from .epv import calculate
    elif method_name(method) == 'growth':
        from .growth import calculate
    else:
        from .valuation import calculate
    return calculate
