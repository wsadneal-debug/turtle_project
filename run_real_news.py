#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行实际新闻数据的风险分析
"""

import json
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from daily_crawler_v2 import process_news_to_stock_record, save_to_database, generate_structured_report

DB_PATH = Path(__file__).parent / 'risk_stocks.db'
OUTPUT_DIR = Path(__file__).parent

def main():
    # 加载实际新闻数据
    news_file = Path(__file__).parent / 'data/news_20260414.json'
    with open(news_file, 'r', encoding='utf-8') as f:
        news_list = json.load(f)
    
    print("=" * 60)
    print(f"📰 港股风险新闻监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print(f"\n获取到 {len(news_list)} 条实际新闻")
    
    # 处理新闻
    structured_records = []
    for news in news_list:
        record = process_news_to_stock_record(news)
        if record:
            structured_records.append(record)
            if record['stock_code']:
                print(f"  ✓ {record['stock_code']} {record['stock_name']} | {record['risk_level']} | {record['risk_type']}")
    
    print(f"\n共识别 {len(structured_records)} 条风险新闻")
    
    # 保存数据库
    if structured_records:
        save_to_database(structured_records)
        print("✓ 已保存到 risk_records 表")
    
    # 生成报告
    report = generate_structured_report(structured_records)
    
    report_file = OUTPUT_DIR / f'output/risk_report_{datetime.now().strftime("%Y%m%d_%H%M")}.md'
    report_file.parent.mkdir(exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # JSON输出
    json_file = report_file.with_suffix('.json')
    json_output = [{
        'stock_code': r['stock_code'],
        'stock_name': r['stock_name'],
        'risk_level': r['risk_level'],
        'risk_type': r['risk_type'],
        'matched_keywords': r.get('matched_keywords', []),
        'news_title': r['news_title'],
        'news_url': r.get('news_url', '')
    } for r in structured_records if r['stock_code']]
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    
    # 统计
    high_risk = [r for r in structured_records if r['risk_level'] == 'HIGH' and r['stock_code']]
    medium_risk = [r for r in structured_records if r['risk_level'] == 'MEDIUM' and r['stock_code']]
    
    print("\n" + "=" * 60)
    print("📊 风险股票名单摘要:")
    print(f"   高风险: {len(high_risk)} 只")
    for r in high_risk:
        print(f"      {r['stock_code']} {r['stock_name']} - {r['risk_type']}")
    print(f"   中风险: {len(medium_risk)} 只")
    for r in medium_risk:
        print(f"      {r['stock_code']} {r['stock_name']} - {r['risk_type']}")
    print("=" * 60)
    
    return {
        'total_news': len(news_list),
        'risk_news': len(structured_records),
        'high_risk': len(high_risk),
        'medium_risk': len(medium_risk),
        'report_file': str(report_file),
        'json_file': str(json_file)
    }

if __name__ == "__main__":
    result = main()
    print(f"\n✅ 正式业务运行完成")
    print(f"输出文件: {result['report_file']}")
    print(f"JSON文件: {result['json_file']}")