#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 生成今日报告
"""

import json
import re
from datetime import datetime
from collections import defaultdict

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责', '证监会'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '更换审计师'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职', '被捕'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌'],
}

# 测试新闻数据（实际应从浏览器爬取）
TEST_NEWS = [
    # 高风险
    {'title': '碧桂园未能按期偿还债券利息，构成违约', 'url': 'https://example.com/1'},
    {'title': '证监会对恒大地产立案调查，涉嫌信息披露违规', 'url': 'https://example.com/2'},
    {'title': '融创中国债务逾期，无法兑付到期债券', 'url': 'https://example.com/3'},
    {'title': '小米集团被证监会问询', 'url': 'https://example.com/4'},
    {'title': '某港股公司停牌核查，暂停上市', 'url': 'https://example.com/5'},
    
    # 中风险
    {'title': '融创中国审计师普华永道辞任，不再续聘', 'url': 'https://example.com/6'},
    {'title': '实控人被捕，某上市公司股价暴跌', 'url': 'https://example.com/7'},
    {'title': '高管离职，某科技公司董事长辞职', 'url': 'https://example.com/8'},
    {'title': '某公司财报延期，无法按时披露', 'url': 'https://example.com/9'},
    
    # 无风险
    {'title': '腾讯控股发布正面业绩公告，净利润增长 20%', 'url': 'https://example.com/10'},
    {'title': '港股通今日净流入 50 亿元', 'url': 'https://example.com/11'},
]

def analyze_risk(title):
    """分析风险"""
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
    code_match = re.search(r'([(\[]?\d{4,6}[)\]]?(?:\.HK)?)', title)
    code = code_match.group(0) if code_match else ''
    name_match = re.search(r'^([^\(（]+)', title)
    name = name_match.group(0).strip() if name_match else ''
    return code, name

def generate_report(news_list, output_file):
    """生成报告"""
    risk_news = []
    
    for news in news_list:
        risks = analyze_risk(news['title'])
        if risks:
            code, name = extract_stock_info(news['title'])
            risk_news.append({
                'title': news['title'],
                'url': news['url'],
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
    report.append("# 🔴 港股风险股票监控报告\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**数据来源**: 东方财富网\n")
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
    
    return risk_news, ''.join(report)

def main():
    print("=" * 60)
    print("📰 港股风险新闻监控报告")
    print("=" * 60)
    
    output_file = '/home/yxy/.openclaw/workspace/hk_risk_news/risk_report_' + datetime.now().strftime('%Y%m%d') + '.md'
    
    risk_news, report = generate_report(TEST_NEWS, output_file)
    
    print(f"\n✅ 报告已生成：{output_file}\n")
    print(f"风险新闻总数：{len(risk_news)}")
    print(f"高风险：{len([n for n in risk_news if n['max_level'] == 'high'])}")
    print(f"中风险：{len([n for n in risk_news if n['max_level'] == 'medium'])}")
    
    print("\n" + "=" * 60)
    print("报告预览:")
    print("=" * 60)
    print(report[:2000])

if __name__ == "__main__":
    main()
