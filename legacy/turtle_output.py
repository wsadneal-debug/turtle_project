#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成龟龟项目风险剔除名单
输出：output/turtle_risk_exclusion_latest.json
格式：可直接被龟龟项目准入池过滤使用
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path('/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db')
OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news/output')
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_turtle_exclusion_list():
    """生成当前有效的风险剔除名单"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询：action=exclude 且有效期内的股票
    now = datetime.now().isoformat()
    cursor.execute('''
        SELECT 
            stock_code,
            stock_name,
            market,
            risk_level,
            risk_type,
            action,
            valid_from,
            valid_to,
            news_title,
            news_url,
            news_source,
            publish_time,
            hit_keywords
        FROM risk_records
        WHERE stock_code IS NOT NULL
          AND action = 'exclude'
          AND valid_to >= ?
        ORDER BY valid_to DESC
    ''', (now,))
    
    records = cursor.fetchall()
    
    # 转换为龟龟项目格式
    exclusion_list = []
    for row in records:
        exclusion_list.append({
            'ts_code': row[0],
            'stock_name': row[1],
            'market': row[2],
            'risk_level': row[3],
            'risk_type': row[4],
            'action': row[5],
            'valid_from': row[6],
            'valid_to': row[7],
            'news_title': row[8],
            'news_url': row[9],
            'source': row[10],
            'publish_time': row[11],
            'hit_keywords': json.loads(row[12]) if row[12] else []
        })
    
    conn.close()
    
    # 保存最新版本（给龟龟项目直接读取）
    latest_file = OUTPUT_DIR / 'turtle_risk_exclusion_latest.json'
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(exclusion_list, f, ensure_ascii=False, indent=2)
    
    # 保存归档版本
    archive_file = OUTPUT_DIR / f'turtle_risk_exclusion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(exclusion_list, f, ensure_ascii=False, indent=2)
    
    # 生成watch名单（中风险观察）
    cursor = conn.cursor()
    cursor.execute('''
        SELECT stock_code, stock_name, market, risk_type, valid_to, news_title
        FROM risk_records
        WHERE stock_code IS NOT NULL
          AND action = 'watch'
          AND valid_to >= ?
    ''', (now,))
    
    watch_records = cursor.fetchall()
    watch_list = [{
        'ts_code': r[0],
        'stock_name': r[1],
        'market': r[2],
        'risk_type': r[3],
        'valid_to': r[4],
        'news_title': r[5]
    } for r in watch_records]
    
    conn.close()
    
    watch_file = OUTPUT_DIR / 'turtle_risk_watch_latest.json'
    with open(watch_file, 'w', encoding='utf-8') as f:
        json.dump(watch_list, f, ensure_ascii=False, indent=2)
    
    print(f"✅ exclude名单: {len(exclusion_list)} 只")
    print(f"✅ watch名单: {len(watch_list)} 只")
    print(f"✅ 输出文件: {latest_file}")
    
    return exclusion_list, watch_list

if __name__ == "__main__":
    generate_turtle_exclusion_list()