#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 每日执行脚本
定时任务入口点
"""

import json
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from daily_crawler_v2 import process_news_to_stock_record, save_to_database, generate_structured_report

DB_PATH = Path(__file__).parent / 'risk_stocks.db'
OUTPUT_DIR = Path(__file__).parent

def get_latest_news_from_db():
    """从数据库获取最新爬取的新闻（由browser爬虫存入）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询今天的新闻记录（如果有raw_news表）
    cursor.execute("""
        SELECT title, url FROM raw_news 
        WHERE crawl_date = ?
        ORDER BY crawl_time DESC
    """, (datetime.now().strftime('%Y-%m-%d'),))
    
    news = [{'title': row[0], 'url': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return news

def run_with_sample_data():
    """使用示例数据运行（当没有实际爬取数据时）"""
    sample_news = [
        {'title': '腾讯控股遭证监会立案调查，涉嫌违反证券法', 'url': 'https://finance.eastmoney.com/a/1.html'},
        {'title': '碧桂园未能按期偿还债券利息，构成实质性违约', 'url': 'https://finance.eastmoney.com/a/2.html'},
        {'title': '贵州茅台股价创新高，市值突破2万亿', 'url': 'https://finance.eastmoney.com/a/3.html'},
        {'title': '宁德时代被监管问询，要求解释财报异常', 'url': 'https://finance.eastmoney.com/a/4.html'},
        {'title': '比亚迪董事长辞职，引发市场担忧', 'url': 'https://finance.eastmoney.com/a/5.html'},
        {'title': '工商银行年报披露，净利润增长5%', 'url': 'https://finance.eastmoney.com/a/6.html'},
        {'title': '中国平安审计师辞任，审计意见存疑', 'url': 'https://finance.eastmoney.com/a/7.html'},
        {'title': '小米集团股价暴跌20%，创历史新低', 'url': 'https://finance.eastmoney.com/a/8.html'},
        {'title': '美团-W更换审计师，引发市场关注', 'url': 'https://finance.eastmoney.com/a/9.html'},
        {'title': '招商银行高管离职，CEO辞职', 'url': 'https://finance.eastmoney.com/a/10.html'},
    ]
    return sample_news

def main():
    print("=" * 60)
    print(f"📰 港股风险新闻监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 1. 获取新闻数据
    # 这里应该从实际爬虫获取，暂时用示例数据
    news_list = run_with_sample_data()
    
    print(f"\n获取到 {len(news_list)} 条新闻")
    
    # 2. 处理新闻 → 结构化风险记录
    structured_records = []
    for news in news_list:
        record = process_news_to_stock_record(news)
        if record:
            structured_records.append(record)
            if record['stock_code']:
                print(f"  ✓ {record['stock_code']} {record['stock_name']} | {record['risk_level']} | {record['risk_type']}")
    
    print(f"\n共识别 {len(structured_records)} 条风险新闻")
    
    # 3. 保存到数据库
    if structured_records:
        save_to_database(structured_records)
        print("✓ 已保存到 risk_records 表")
    
    # 4. 生成报告
    report = generate_structured_report(structured_records)
    
    # 保存报告
    report_file = OUTPUT_DIR / f'output/risk_report_{datetime.now().strftime("%Y%m%d")}.md'
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ 报告已保存: {report_file}")
    
    # 保存JSON（给龟龟项目使用）
    json_file = report_file.with_suffix('.json')
    json_output = [{
        'stock_code': r['stock_code'],
        'stock_name': r['stock_name'],
        'risk_level': r['risk_level'],
        'risk_type': r['risk_type'],
        'matched_keywords': r.get('matched_keywords', []),
        'news_title': r['news_title']
    } for r in structured_records if r['stock_code']]
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON已保存: {json_file}")
    
    # 5. 统计摘要
    high_risk = [r for r in structured_records if r['risk_level'] == 'HIGH' and r['stock_code']]
    medium_risk = [r for r in structured_records if r['risk_level'] == 'MEDIUM' and r['stock_code']]
    
    print("\n" + "=" * 60)
    print("📊 风险股票名单摘要:")
    print(f"   高风险: {len(high_risk)} 只")
    for r in high_risk:
        print(f"      {r['stock_code']} {r['stock_name']} - {r['risk_type']}")
    print(f"   中风险: {len(medium_risk)} 只")
    for r in medium_risk[:5]:
        print(f"      {r['stock_code']} {r['stock_name']} - {r['risk_type']}")
    print("=" * 60)
    
    return {
        'high_risk_count': len(high_risk),
        'medium_risk_count': len(medium_risk),
        'report_file': str(report_file),
        'json_file': str(json_file)
    }

if __name__ == "__main__":
    result = main()
    print(f"\n✅ 执行完成")
    print(f"输出文件: {result['report_file']}")