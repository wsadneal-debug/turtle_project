"""Host-AI-assisted local packets and the existing three deterministic calculators.

This entrypoint deliberately imports neither research clients nor database adapters.
The host obtains official documents, reads them, and supplies facts/estimates. PDF
text conversion only exposes existing text; it does not extract financial facts.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import re
import shutil
import subprocess

from .deterministic import recalculate as calculate_and_save, write_json
from .epv_data import load_asset_context, make_history, normalized_code
from .growth_data import prepare_growth_input
from .methods import method_name, select_method


def _load(path) -> dict:
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'{path}须为JSON对象')
    return value


def _date(value) -> str:
    raw = str(value)
    if len(raw) == 8 and raw.isdigit():
        raw = f'{raw[:4]}-{raw[4:6]}-{raw[6:]}'
    return date.fromisoformat(raw).isoformat()


def _directory(run_dir, *, sources=(), fresh=False) -> Path:
    directory = Path(run_dir).expanduser().resolve()
    # Protect the current source checkout or the installed, portable skill.
    roots = [p for p in Path(__file__).resolve().parents
             if (p / 'pyproject.toml').is_file() or (p / 'SKILL.md').is_file()]
    roots.extend(Path(p).expanduser().resolve() for p in sources if p)
    if any(directory == root or root in directory.parents for root in roots):
        raise ValueError('运行目录须位于代码/技能目录及所选源研究目录之外')
    if fresh and directory.exists() and (not directory.is_dir() or any(directory.iterdir())):
        raise ValueError('准备须使用新的或空的运行目录，不覆盖已有材料/输入/研究')
    return directory


def _path(value, base: Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def _identity_problem(row: dict, text: str, issuer: dict) -> str | None:
    stated = row.get('code') or (row.get('issuer') or {}).get('code')
    if stated and normalized_code(stated) != normalized_code(issuer['code']):
        return '报告所列企业代码与本次企业不同'
    return None


def _cover_warning(row: dict, text: str) -> str | None:
    # Advisory only: report covers and fiscal-year labels vary. A mention of an
    # older annual report inside normal current text must never reject a file.
    title = str(row.get('title') or (text.splitlines() or [''])[0])
    cover = re.sub(r'\s+', '', title).lower()
    fiscal = r'(20\d{2}(?:/(?:20)?\d{2})?)'
    patterns = [
        ('interim', fiscal + r'年?(?:半年度报告|半年度報告|中期报告|中期報告|interimreport|semiannualreport)'),
        ('quarterly', fiscal + r'年?(?:第一|第三|第[一二三四])?(?:季度报告|季度報告|quarterlyreport)'),
        ('annual', fiscal + r'年?(?:年度报告|年度報告|年报|年報|annualreport)'),
        ('interim', r'(?:interimreport|semiannualreport)' + fiscal),
        ('annual', r'annualreport' + fiscal),
    ]
    for kind, pattern in patterns:
        match = re.search(pattern, cover)
        if match:
            label = match[1]
            year = label.split('/')[-1]
            year = label[:2] + year if len(year) == 2 else year
            if kind != row['report_type'] or year != row['period_end'][:4]:
                return '标题/首行年份或类型可能与元数据不同；财年标签须由宿主核对，不据启发式自动排除全文'
            break
    return None


def _material(row: dict, *, base: Path, directory: Path, index: int,
              issuer: dict, as_of: str) -> dict:
    result = deepcopy(row)
    result['period_end'] = _date(row['period_end'])
    if row.get('report_type') not in ('annual', 'interim', 'quarterly'):
        raise ValueError('报告report_type须为annual/interim/quarterly')
    if row.get('publication_date'):
        result['publication_date'] = _date(row['publication_date'])
    result.update(readable=False, status='missing_local_file')
    result.pop('text_path', None)
    result.pop('path', None)
    target = directory / 'materials'
    target.mkdir(parents=True, exist_ok=True)
    stem = f"{index:03d}_{result['period_end']}_{row['report_type']}"
    copied = None
    text_path = None
    for key in ('path', 'text_path'):
        if not row.get(key):
            continue
        source = _path(row[key], base)
        result['source_' + key] = str(source)
        if not source.is_file():
            result.setdefault('warnings', []).append(f'{key}本地文件不存在：{source}')
            continue
        suffix = '.txt' if key == 'text_path' else (source.suffix or '.document')
        destination = target / (stem + ('_text' if key == 'text_path' else '') + suffix)
        shutil.copyfile(source, destination)
        result[key] = str(destination)
        if key == 'path':
            copied = destination
        else:
            text_path = destination
    if text_path is None and copied is not None:
        if copied.suffix.lower() in ('.txt', '.md'):
            text_path = copied
        elif copied.suffix.lower() == '.pdf':
            if shutil.which('pdftotext'):
                converted = target / (stem + '_text.txt')
                try:
                    proc = subprocess.run(['pdftotext', '-layout', str(copied), str(converted)],
                                          capture_output=True, text=True, timeout=120)
                    if proc.returncode == 0:
                        text_path = converted
                    else:
                        result.update(status='conversion_failed', error=proc.stderr[:300])
                except (OSError, subprocess.TimeoutExpired) as exc:
                    result.update(status='conversion_failed', error=str(exc))
            else:
                result.update(status='needs_text', error='未安装可选pdftotext；由宿主提供可读全文text_path')
    text = ''
    if text_path:
        try:
            text = text_path.read_text(encoding='utf-8-sig')
        except (UnicodeError, OSError) as exc:
            result.update(status='needs_text', error=f'全文须为可读UTF-8文本：{exc}')
        result['text_path'] = str(text_path)
        result['text_characters'] = len(text)
        if text.strip():
            result.update(readable=True, status='readable')
        elif result['status'] not in ('needs_text', 'conversion_failed'):
            result.update(status='needs_ocr', error='未取得可读文本；扫描PDF需宿主OCR或可读官方版本')
    cover_warning = _cover_warning(result, text)
    if cover_warning:
        result.setdefault('warnings', []).append(cover_warning)
    issue = _identity_problem(result, text, issuer)
    if issue:
        result.update(readable=False, status='identity_mismatch', error=issue)
    elif result['period_end'] > as_of or (result.get('publication_date') or '') > as_of:
        result.update(readable=False, status='after_as_of', error='所列报告期间/披露日在研究截止日后，未计入已准备材料')
    elif row.get('full_text') is False or row.get('status') in ('needs_ocr', 'needs_text', 'partial'):
        result.update(readable=False, status=row.get('status') or 'partial',
                      error='宿主已标记原文未齐，不能仅凭文件存在升级为齐备')
    if not result['readable'] and row.get('url') and copied is None and text_path is None:
        result.setdefault('error', '官方URL仅保留来源；宿主须先取得本地全文，运行器不自动联网抓取')
    return result


def _materials(data: dict, *, base: Path, directory: Path) -> None:
    data['reports'] = [_material(row, base=base, directory=directory, index=i,
                                issuer=data['issuer'], as_of=data['as_of'])
                       for i, row in enumerate(data.get('reports', []), 1)]
    # Include known missing periods from both facts and supplied material entries.
    periods = {(s['period_end'], s['report_type'])
               for s in data.get('snapshots', []) + data['reports']
               if s.get('report_type') in ('annual', 'interim', 'quarterly')
               and s['period_end'] <= data['as_of']}
    annuals = sorted({p for p, kind in periods if kind == 'annual'}, reverse=True)[:2]
    if len(annuals) == 1:
        last = date.fromisoformat(annuals[0])
        try:
            previous = last.replace(year=last.year - 1)
        except ValueError:  # Leap-day fiscal year ends.
            previous = last.replace(year=last.year - 1, day=28)
        annuals.append(previous.isoformat())
    required = [(p, 'annual') for p in annuals]
    updates = sorted((p, kind) for p, kind in periods if kind != 'annual'
                     and (not annuals or p > annuals[0]))
    if updates:
        required.append(updates[-1])
    available = {(r['period_end'], r['report_type']) for r in data['reports'] if r['readable']}
    missing = [dict(period_end=p, report_type=k) for p, k in required if (p, k) not in available]
    data['required_reports'] = [dict(period_end=p, report_type=k) for p, k in required]
    data['missing_reports'] = missing
    data['materials_ready'] = len(annuals) == 2 and bool(updates) and not missing
    warnings = data.setdefault('warnings', [])
    if not data['materials_ready']:
        warnings.append('材料未齐：需最近两个独立财年的完整年报及附注、其后最新季报/中报；未知或缺件不视为已经取得。')
    warnings.extend(f"{r['period_end']} {r['report_type']}：{r.get('error') or r['status']}"
                    for r in data['reports'] if not r['readable'])
    warnings.extend(f"{r['period_end']} {r['report_type']}：{warning}"
                    for r in data['reports'] for warning in r.get('warnings', []))
    warnings.append('materials_ready仅表示所列期间可读原文的可用性；不证明宿主已读完、附注完整或已独立确认官方最新披露。')


def prepare(packet, *, method: str, run_dir, asset_run=None) -> dict:
    """Preserve an AI-supplied packet and copy named documents into a new run."""
    packet_path = Path(packet).expanduser().resolve()
    original = _load(packet_path)
    selected = method_name(method)
    if selected not in ('asset', 'epv'):
        raise ValueError('prepare仅接受asset/epv；成长使用growth命令显式选择EPV')
    select_method(original, requested=selected)
    data = deepcopy(original)
    if not isinstance(data.get('issuer'), dict) or not data['issuer'].get('code'):
        raise ValueError('packet须有issuer.code；name/market缺失可保留null')
    data['issuer']['code'] = normalized_code(data['issuer']['code'])
    data['as_of'] = _date(data['as_of'])
    data['method'] = selected
    data.setdefault('currency', None)
    data.setdefault('shares', None)
    for key in ('snapshots', 'reports', 'warnings'):
        data.setdefault(key, [])
        if not isinstance(data[key], list):
            raise ValueError(f'packet.{key}须为列表')
    for snapshot in data['snapshots']:
        snapshot['period_end'] = _date(snapshot['period_end'])
    # Resolve optional context before writing a new run. The same source model
    # code loads only explicitly chosen JSON, never a private financial database.
    if asset_run is not None:
        if selected != 'epv':
            raise ValueError('asset-run只用于EPV复用同企业资产依据')
        data['asset_context'] = load_asset_context(asset_run, data['issuer']['code'])
    if selected == 'epv' and 'history' not in data:
        data['history'] = make_history(data, 10)
        data['warnings'].extend(data['history']['warnings'])
    directory = _directory(run_dir, sources=[asset_run], fresh=True)
    directory.mkdir(parents=True, exist_ok=True)
    _materials(data, base=packet_path.parent, directory=directory)
    data['portable'] = {'mode': 'host_ai', 'financial_extraction': 'host_supplied',
                        'provider_calls': 0, 'database_reads': 0}
    shutil.copyfile(packet_path, directory / 'packet.json')
    write_json(directory / 'input.json', data)
    return data


def growth(*, epv_run, run_dir, asset_run=None, request=None, as_of=None) -> dict:
    root = Path(epv_run).expanduser().resolve()
    directory = _directory(run_dir, sources=[root, asset_run], fresh=True)
    original = _load(root / 'input.json')
    data = prepare_growth_input(original['issuer']['code'], epv_run=root, asset_run=asset_run,
                                request=_load(request) if request is not None else None, as_of=as_of)
    directory.mkdir(parents=True, exist_ok=True)
    _materials(data, base=root, directory=directory)
    data['portable'] = {'mode': 'host_ai', 'financial_extraction': 'frozen_epv_input',
                        'provider_calls': 0, 'database_reads': 0}
    write_json(directory / 'input.json', data)
    return data


def recalculate(*, run_dir, valuation=None, method=None) -> dict:
    directory = _directory(run_dir)
    data = _load(directory / 'input.json')
    # Explicit recalculate is the only operation allowed to replace saved outputs.
    source = _load(valuation if valuation is not None else directory / 'valuation.json')
    return calculate_and_save(data, source, directory, method=method)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='宿主AI准备事实与估计；本地零模型计算三步估值')
    commands = parser.add_subparsers(dest='command', required=True)
    packet = commands.add_parser('prepare', help='复制指定原文并保存asset/epv输入，不联网、不提取财务事实')
    packet.add_argument('--packet', required=True)
    packet.add_argument('--method', choices=('asset', 'epv'), required=True)
    packet.add_argument('--run-dir', required=True)
    packet.add_argument('--asset-run')
    frozen = commands.add_parser('growth', help='冻结选定EPV及报价/政策输入，不调用研究模型')
    frozen.add_argument('--epv-run', required=True)
    frozen.add_argument('--run-dir', required=True)
    frozen.add_argument('--asset-run')
    frozen.add_argument('--request')
    frozen.add_argument('--as-of')
    calc = commands.add_parser('recalculate', help='按已有参数重算并更新本方法valuation.json/report.md')
    calc.add_argument('--run-dir', required=True)
    calc.add_argument('--valuation')
    calc.add_argument('--method', choices=('asset', 'epv', 'growth'))
    args = vars(parser.parse_args(argv))
    command = args.pop('command')
    try:
        if command == 'prepare':
            value = prepare(**args)
        elif command == 'growth':
            value = growth(**args)
        else:
            value = recalculate(**args)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f'错误：{exc}\n')
    print(json.dumps({'command': command, 'method': value.get('method'),
                      'run_dir': str(Path(args['run_dir']).expanduser().resolve()),
                      'materials_ready': value.get('materials_ready'),
                      'calculation_status': (value.get('calculation') or {}).get('status'),
                      'provider_calls': 0, 'database_reads': 0}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
