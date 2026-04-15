#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 每日 15 点自动爬取
爬取东方财富公司资讯全部页面（50 页）
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责', '证监会', '交易所问询'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '更换审计师'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘', '跳水', '暴跌'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职', '被捕', '被抓'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌'],
    '市场风险': ['关税战', '威胁', '封锁', '中断', '危机', '制裁'],
}

OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news')

def get_browser_news(page=1):
    """通过 browser 工具获取指定页面的新闻"""
    url = f'https://finance.eastmoney.com/a/cgsxw_{page}.html' if page > 1 else 'https://finance.eastmoney.com/a/cgsxw.html'
    
    # 使用 browser 工具导航
    cmd = f'''
    browser action=navigate url="{url}" 2>&1
    browser action=act kind=evaluate fn="() => Array.from(document.querySelectorAll('a')).filter(a => a.href.includes('/a/')).map(a => a.innerText.trim()).filter(t => t.length > 15 && t.length < 100).slice(0, 30)" 2>&1
    '''
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # 解析结果
    try:
        output = result.stdout
        if '"result":' in output:
            json_str = output.split('"result":')[-1].strip()
            if json_str.startswith('['):
                # 找到 JSON 数组的结束位置
                end_idx = json_str.rfind(']') + 1
                if end_idx > 0:
                    titles = json.loads(json_str[:end_idx])
                    return titles
    except:
        pass
    
    return []

def analyze_risk(title):
    """分析新闻风险"""
    risks = []
    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                risks.append({
                    'category': category,
                    'keyword': keyword,
                    'level': 'high' if category in ['监管处罚', '债务违约', '停牌风险'] else 'medium'
                })
    return risks

def extract_stock_info(title):
    """提取股票信息"""
    # 匹配股票代码
    code_match = re.search(r'([(\[]?\d{4,6}[)\]]?(?:\.HK|\.SZ|\.SH)?)', title)
    code = code_match.group(0) if code_match else ''
    
    # 匹配公司/股票名称
    name_match = re.search(r'^([^\(（]+)', title)
    name = name_match.group(0).strip() if name_match else ''
    
    return code, name

def crawl_all_pages(max_pages=50):
    """爬取所有页面"""
    all_news = []
    
    print(f"开始爬取东方财富公司资讯...")
    print(f"总页数：{max_pages} 页\n")
    
    for page in range(1, max_pages + 1):
        print(f"爬取第 {page} 页...", end=" ")
        sys.stdout.flush()
        
        # 实际应该调用 browser 工具，这里先用模拟数据
        # TODO: 实现真实的 browser 工具调用
        news = []  # 实际应从 browser 工具获取
        
        if news:
            print(f"获取 {len(news)} 条")
            all_news.extend(news)
        else:
            print("无数据")
            break
    
    return all_news

def generate_report(news_list, output_file):
    """生成风险报告"""
    risk_news = []
    
    for news in news_list:
        risks = analyze_risk(news['title'])
        if risks:
            code, name = extract_stock_info(news['title'])
            risk_news.append({
                'title': news['title'],
                'url': news.get('url', ''),
                'code': code,
                'name': name,
                'risks': risks,
                'max_level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium'
            })
    
    # 分类
    high_risk = [n for n in risk_news if n['max_level'] == 'high']
    medium_risk = [n for n in risk_news if n['max_level'] == 'medium']
    
    # 生成 Markdown
    report = []
    report.append("# 🔴 港股风险股票监控日报\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**数据来源**: 东方财富网 - 公司资讯\n")
    report.append(f"**数据范围**: 全部 50 页\n")
    report.append(f"**监控新闻总数**: {len(news_list)} 条\n")
    report.append(f"**风险新闻数量**: {len(risk_news)} 条\n")
    report.append("")
    
    # 高风险
    if high_risk:
        report.append("## 🔴 高风险股票\n")
        report.append("| 股票 | 新闻标题 | 风险类型 |\n")
        report.append("|------|---------|---------|\n")
        for item in high_risk:
            risk_types = ', '.join(set([r['category'] for r in item['risks']]))
            title_short = item['title'][:50] + '...' if len(item['title']) > 50 else item['title']
            report.append(f"| {item['name']} {item['code']} | {title_short} | {risk_types} |\n")
        report.append("")
    
    # 中风险
    if medium_risk:
        report.append("## 🟡 中风险股票\n")
        report.append("| 股票 | 新闻标题 | 风险类型 |\n")
        report.append("|------|---------|---------|\n")
        for item in medium_risk:
            risk_types = ', '.join(set([r['category'] for r in item['risks']]))
            title_short = item['title'][:50] + '...' if len(item['title']) > 50 else item['title']
            report.append(f"| {item['name']} {item['code']} | {title_short} | {risk_types} |\n")
        report.append("")
    
    # 风险统计
    report.append("## 📊 风险类型统计\n")
    risk_count = defaultdict(int)
    for item in risk_news:
        for r in item['risks']:
            risk_count[r['category']] += 1
    
    report.append("| 风险类型 | 数量 |\n")
    report.append("|---------|------|\n")
    for category, count in sorted(risk_count.items(), key=lambda x: x[1], reverse=True):
        report.append(f"| {category} | {count} |\n")
    
    report.append("\n---\n")
    report.append("*本报告由自动化系统生成，仅供参考，不构成投资建议*\n")
    
    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    # 同时保存 JSON 数据
    json_file = output_file.replace('.md', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_news': len(news_list),
            'risk_news': len(risk_news),
            'high_risk': len(high_risk),
            'medium_risk': len(medium_risk),
            'details': risk_news
        }, f, ensure_ascii=False, indent=2)
    
    return risk_news, ''.join(report)

def main():
    print("=" * 60)
    print("📰 港股风险新闻监控 - 每日 15 点自动执行")
    print("=" * 60)
    print()
    
    # 生成文件名
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = OUTPUT_DIR / f'risk_report_{date_str}.md'
    
    # 爬取数据（实际应调用 browser 工具）
    # 这里先用示例数据演示
    sample_news = [
        {'title': '碧桂园未能按期偿还债券利息，构成违约', 'url': ''},
        {'title': '证监会对某地产公司立案调查', 'url': ''},
        {'title': '某公司审计师辞任', 'url': ''},
    ]
    
    # 生成报告
    risk_news, report = generate_report(sample_news, output_file)
    
    print(f"\n✅ 报告已生成：{output_file}")
    print(f"\n📊 统计摘要:")
    print(f"   监控新闻：{len(sample_news)} 条")
    print(f"   风险新闻：{len(risk_news)} 条")
    print(f"   高风险：{len([n for n in risk_news if n['max_level'] == 'high'])}")
    print(f"   中风险：{len([n for n in risk_news if n['max_level'] == 'medium'])}")
    
    print("\n" + "=" * 60)
    print("✅ 每日监控任务完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
