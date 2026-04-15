#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复股票映射 V2 - 改进匹配逻辑
"""

import json
import sqlite3
import re
from pathlib import Path

DB_PATH = Path('/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db')
INPUT_FILE = Path('/home/yxy/.openclaw/workspace/hk_risk_news/verified_20260414_150134.json')
OUTPUT_FILE = Path('/home/yxy/.openclaw/workspace/hk_risk_news/verified_20260414_150134_fixed.json')

# 手动映射表（针对今天的数据）
MANUAL_MAP = {
    '张家界': ('000430.SZ', 'ST 张家界'),
    '国晟科技': ('603778.SH', '国晟科技'),
    '日上集团': ('002593.SZ', '日上集团'),
    '双象股份': ('002395.SZ', '双象股份'),
    '亚信安全': ('688225.SH', '亚信安全'),
}

def map_title_to_stock(title):
    """从标题映射股票"""
    # 1. 先查手动映射
    for name, (code, full_name) in MANUAL_MAP.items():
        if name in title:
            return code, full_name, 'high'
    
    # 2. 从数据库模糊匹配
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 提取标题中的关键词（去掉通用词）
    words = re.findall(r'[\u4e00-\u9fa5]{2,}', title)
    for word in words[:5]:  # 尝试前 5 个词
        if word in ['重整', '落地', '季度', '业绩', '终止', '收购', '引导', '上市', '鼓励', '经营', '活动', '现金', '流量', '营业', '收入', '归母', '净利润', '同比', '下降', '扣非', '净利', '亏损', '亿元', '大幅', '扩大']:
            continue
        cursor.execute('''
            SELECT stock_code, stock_name, market FROM stock_pool 
            WHERE stock_name LIKE ?
            LIMIT 1
        ''', (f'%{word}%',))
        result = cursor.fetchone()
        if result:
            conn.close()
            return result[0], result[1], 'medium'
    
    conn.close()
    return None, None, 'none'

def main():
    print("=" * 60)
    print("🔧 修复股票映射 V2")
    print("=" * 60)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"原始数据：{data['total']} 条新闻\n")
    
    fixed_news = []
    for news in data['news']:
        title = news['title']
        stock_code, stock_name, confidence = map_title_to_stock(title)
        
        fixed_news.append({
            'title': title,
            'url': news['url'],
            'source': news['source'],
            'stock_code': stock_code or '',
            'stock_name': stock_name or '',
            'risks': news['risks'],
            'risk_level': news['risk_level'],
            'quality_score': news['quality_score'],
            'verified': news['verified'],
            'crawl_time': news['crawl_time'],
            'mapping_confidence': confidence
        })
        
        status = "✅" if stock_code else "❌"
        print(f"{status} {title[:60]}...")
        if stock_code:
            print(f"   → {stock_name} ({stock_code}) [{confidence}]")
    
    output = {
        'time': data['time'],
        'total': len(fixed_news),
        'avg_quality_score': data['avg_quality_score'],
        'sources': data['sources'],
        'mapped_count': sum(1 for n in fixed_news if n['stock_code']),
        'news': fixed_news
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"✅ 修复完成！")
    print(f"   总数：{len(fixed_news)} 条")
    print(f"   已映射：{output['mapped_count']} 条")
    print(f"   未映射：{len(fixed_news) - output['mapped_count']} 条")
    print(f"📁 输出：{OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
