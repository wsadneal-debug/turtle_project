#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 V2 - 结构化风险股票记录
改进版：将新闻映射到具体股票代码，输出可直接使用的风险股票名单
"""

import json
import re
import sqlite3
import subprocess
import sys
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# 导入股票映射器
from stock_mapper import map_company_to_stock, simple_extract_company_from_title

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责', '证监会', '交易所问询', '罚款', '处罚', '开庭', '案件', '认罪', '悔罪', '起诉', '判决', '一审', '二审', '上诉', '被抓', '被捕', '司法冻结', '股份冻结', '实际控制人', '股权冻结'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '更换审计师', '审计意见'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷', '逾期', '无力偿还'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘', '跳水', '暴跌', '亏损', '裁员', '停业', '一字板跌停', '股份被冻结', '冻结'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职', '被捕', '被抓', '离职'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌', '退市'],
    '市场风险': ['关税战', '威胁', '封锁', '中断', '危机', '制裁', '暴跌'],
}

OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news')
DB_PATH = OUTPUT_DIR / 'risk_stocks.db'

def analyze_risk(title):
    """分析新闻风险等级和类型"""
    risks = []
    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                risks.append({
                    'category': category,
                    'keyword': keyword,
                    'level': 'HIGH' if category in ['监管处罚', '债务违约', '停牌风险'] else 'MEDIUM'
                })
    return risks

def process_news_to_stock_record(news_item):
    """
    将新闻记录转换为结构化的风险股票记录
    返回格式：
    {
        'stock_code': '00700.HK',
        'stock_name': '腾讯控股',
        'risk_level': 'HIGH',
        'risk_type': '监管处罚',
        'news_title': '...',
        'news_url': '...',
        'confidence': 'high',
        'record_date': '2026-04-14'
    }
    """
    title = news_item.get('title', '')
    url = news_item.get('url', '')
    
    # 分析风险
    risks = analyze_risk(title)
    if not risks:
        return None
    
    # 映射股票
    # 1. 先提取公司名
    company_name = simple_extract_company_from_title(title)
    if company_name:
        stock_code, stock_name, confidence = map_company_to_stock(company_name)
    else:
        stock_code, stock_name, confidence = None, None, 'none'
    
    # 确定最高风险等级
    max_level = 'HIGH' if any(r['level'] == 'HIGH' for r in risks) else 'MEDIUM'
    
    # 判定动作
    action = 'exclude' if max_level == 'HIGH' else 'watch'
    
    # 判定市场
    market = 'A' if stock_code and stock_code.endswith('.SZ') or stock_code and stock_code.endswith('.SH') else 'HK' if stock_code else None
    
    # 计算有效期
    from datetime import datetime, timedelta
    valid_from = datetime.now()
    valid_days = 20 if max_level == 'HIGH' else 5
    valid_to = valid_from + timedelta(days=valid_days)
    
    # 收集所有风险类型
    risk_types = list(set([r['category'] for r in risks]))
    
    return {
        'stock_code': stock_code,
        'stock_name': stock_name or '未识别',
        'market': market,
        'risk_level': max_level,
        'risk_type': risk_types[0] if risk_types else '未知',
        'action': action,
        'matched_keywords': [r['keyword'] for r in risks],
        'news_title': title,
        'news_url': url,
        'news_source': 'eastmoney',
        'publish_time': news_item.get('publish_time', datetime.now().isoformat()),
        'confidence': confidence,
        'record_date': datetime.now().strftime('%Y-%m-%d'),
        'valid_from': valid_from.isoformat(),
        'valid_to': valid_to.isoformat(),
        'crawl_time': datetime.now().isoformat()
    }

def save_to_database(records):
    """保存风险股票记录到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for record in records:
        if record['stock_code']:  # 只保存有股票代码的记录
            cursor.execute('''
                INSERT INTO risk_records (
                    record_date, stock_code, stock_name, market,
                    risk_type, risk_level, action, news_title, news_url,
                    news_source, publish_time, valid_from, valid_to, hit_keywords, crawl_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['record_date'],
                record['stock_code'],
                record['stock_name'],
                record['market'],
                record['risk_type'],
                record['risk_level'],
                record['action'],
                record['news_title'],
                record['news_url'],
                record['news_source'],
                record['publish_time'],
                record['valid_from'],
                record['valid_to'],
                json.dumps(record['matched_keywords']),
                record['crawl_time']
            ))
    
    conn.commit()
    conn.close()

def generate_structured_report(records):
    """
    生成结构化风险股票报告
    格式：可直接给龟龟项目使用的风险股票名单
    """
    # 分类：高风险 + 中风险
    high_risk = [r for r in records if r['risk_level'] == 'HIGH' and r['stock_code']]
    medium_risk = [r for r in records if r['risk_level'] == 'MEDIUM' and r['stock_code']]
    unmatched = [r for r in records if not r['stock_code']]
    
    # Markdown 报告
    report = []
    report.append("# 🔴 港股风险股票监控日报 (结构化)\n\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    report.append(f"**风险股票总数**: {len(high_risk) + len(medium_risk)} 只\n\n")
    report.append(f"- 高风险: {len(high_risk)} 只\n")
    report.append(f"- 中风险: {len(medium_risk)} 只\n")
    report.append(f"- 未匹配股票: {len(unmatched)} 条\n\n")
    
    # 高风险股票名单（可直接使用）
    if high_risk:
        report.append("## 🔴 高风险股票名单\n\n")
        report.append("| 股票代码 | 股票名称 | 风险类型 | 匹配关键词 | 新闻摘要 |\n")
        report.append("|----------|----------|----------|------------|----------|\n")
        
        # 按股票代码分组
        for record in sorted(high_risk, key=lambda x: x['stock_code'] or ''):
            title_short = record['news_title'][:40] + '...' if len(record['news_title']) > 40 else record['news_title']
            keywords = ', '.join(record['matched_keywords'][:3])
            report.append(f"| {record['stock_code']} | {record['stock_name']} | {record['risk_type']} | {keywords} | {title_short} |\n")
        report.append("\n")
        
        # JSON 格式输出（可直接复制使用）
        report.append("### JSON 格式 (可直接导入龟龟项目)\n\n")
        report.append("```json\n")
        json_output = [{
            'stock_code': r['stock_code'],
            'stock_name': r['stock_name'],
            'risk_level': r['risk_level'],
            'risk_type': r['risk_type']
        } for r in high_risk]
        report.append(json.dumps(json_output, ensure_ascii=False, indent=2))
        report.append("\n```\n\n")
    
    # 中风险股票名单
    if medium_risk:
        report.append("## 🟡 中风险股票名单\n\n")
        report.append("| 股票代码 | 股票名称 | 风险类型 | 匹配关键词 | 新闻摘要 |\n")
        report.append("|----------|----------|----------|------------|----------|\n")
        
        for record in sorted(medium_risk, key=lambda x: x['stock_code'] or ''):
            title_short = record['news_title'][:40] + '...' if len(record['news_title']) > 40 else record['news_title']
            keywords = ', '.join(record['matched_keywords'][:3])
            report.append(f"| {record['stock_code']} | {record['stock_name']} | {record['risk_type']} | {keywords} | {title_short} |\n")
        report.append("\n")
    
    # 未匹配的新闻（需要人工审核）
    if unmatched:
        report.append("## ⚠️ 未匹配股票的新闻 (需人工审核)\n\n")
        report.append("| 新闻标题 | 风险类型 |\n")
        report.append("|----------|----------|\n")
        for record in unmatched[:10]:  # 只显示前10条
            title_short = record['news_title'][:60] + '...' if len(record['news_title']) > 60 else record['news_title']
            report.append(f"| {title_short} | {record['risk_type']} |\n")
        report.append("\n")
    
    report.append("---\n\n")
    report.append("*本报告由自动化系统生成，结构化风险股票名单可直接导入交易系统使用*\n")
    
    return ''.join(report)

def main():
    print("=" * 60)
    print("📰 港股风险新闻监控 V2 - 结构化风险股票记录")
    print("=" * 60)
    print()
    
    # 模拟新闻数据（实际应从 browser 爬取）
    sample_news = [
        {'title': '腾讯控股遭证监会立案调查，涉嫌违反证券法', 'url': 'https://finance.eastmoney.com/a/1.html'},
        {'title': '碧桂园未能按期偿还债券利息，构成实质性违约', 'url': 'https://finance.eastmoney.com/a/2.html'},
        {'title': '美团-W审计师辞任，引发市场担忧', 'url': 'https://finance.eastmoney.com/a/3.html'},
        {'title': '小米集团股价暴跌20%，创历史新低', 'url': 'https://finance.eastmoney.com/a/4.html'},
        {'title': '中国恒大被申请清盘，债务危机持续', 'url': 'https://finance.eastmoney.com/a/5.html'},
        {'title': '阿里巴巴高管离职，CEO辞职', 'url': 'https://finance.eastmoney.com/a/6.html'},
        {'title': '某科技公司停牌整顿，涉嫌财务造假', 'url': 'https://finance.eastmoney.com/a/7.html'},
        {'title': '汇丰控股被罚款5000万港元', 'url': 'https://finance.eastmoney.com/a/8.html'},
        {'title': '港交所问询函：要求某地产公司解释财报', 'url': 'https://finance.eastmoney.com/a/9.html'},
        {'title': '工商银行董事长辞职', 'url': 'https://finance.eastmoney.com/a/10.html'},
    ]
    
    print("正在处理新闻...")
    
    # 处理新闻 → 结构化记录
    structured_records = []
    for news in sample_news:
        record = process_news_to_stock_record(news)
        if record:
            structured_records.append(record)
            print(f"  ✓ {record['stock_code']} {record['stock_name']} | {record['risk_level']} | {record['risk_type']}")
    
    print(f"\n共识别 {len(structured_records)} 条风险新闻")
    
    # 保存到数据库
    print("\n保存到数据库...")
    save_to_database(structured_records)
    print("✓ 已保存到 risk_records 表")
    
    # 生成报告
    print("\n生成结构化报告...")
    report = generate_structured_report(structured_records)
    
    output_file = OUTPUT_DIR / f'risk_report_{datetime.now().strftime("%Y%m%d_%H%M")}.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ 报告已保存: {output_file}")
    
    # 同时保存 JSON 格式
    json_file = output_file.with_suffix('.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(structured_records, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON 已保存: {json_file}")
    
    print("\n" + "=" * 60)
    print("✅ 结构化风险股票记录生成完成")
    print("=" * 60)
    
    # 打印摘要
    high = [r for r in structured_records if r['risk_level'] == 'HIGH' and r['stock_code']]
    medium = [r for r in structured_records if r['risk_level'] == 'MEDIUM' and r['stock_code']]
    
    print("\n📊 风险股票名单摘要:")
    print(f"   高风险: {len(high)} 只")
    for r in high:
        print(f"      {r['stock_code']} {r['stock_name']} - {r['risk_type']}")
    print(f"   中风险: {len(medium)} 只")
    for r in medium[:5]:
        print(f"      {r['stock_code']} {r['stock_name']} - {r['risk_type']}")

if __name__ == "__main__":
    main()