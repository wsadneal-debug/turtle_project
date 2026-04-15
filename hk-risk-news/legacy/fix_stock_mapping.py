#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复股票映射 - 对已爬取的验证数据添加股票代码
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db')
INPUT_FILE = Path('/home/yxy/.openclaw/workspace/hk_risk_news/verified_20260414_150134.json')
OUTPUT_FILE = Path('/home/yxy/.openclaw/workspace/hk_risk_news/verified_20260414_150134_fixed.json')

def map_company_to_stock(company_name):
    """从数据库映射公司名到股票代码"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 尝试直接匹配
    cursor.execute('''
        SELECT stock_code, stock_name, market FROM stock_pool 
        WHERE stock_name LIKE ? OR stock_name LIKE ?
        LIMIT 1
    ''', (f'%{company_name}%', f'{company_name}%'))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0], result[1], 'high'
    
    # 尝试从标题提取股票代码
    code_match = re.search(r'(\d{6})(?:\.SZ|\.SH|\.HK)?', company_name)
    if code_match:
        code = code_match.group(1)
        cursor2 = sqlite3.connect(DB_PATH).cursor()
        cursor2.execute('SELECT stock_code, stock_name, market FROM stock_pool WHERE stock_code LIKE ?', (f'%{code}%',))
        result2 = cursor2.fetchone()
        if result2:
            return result2[0], result2[1], 'medium'
    
    return None, None, 'none'

def extract_company_from_title(title):
    """从标题提取公司名"""
    # 模式 1: 冒号前
    if ':' in title or ':' in title:
        match = re.search(r'^([^::]+)[::]', title)
        if match:
            return match.group(1).strip()
    
    # 模式 2: 股票代码后的内容
    code_match = re.search(r'\d{6}', title)
    if code_match:
        pos = code_match.end()
        rest = title[pos:].lstrip(' ,.:-')
        if rest:
            return rest.split()[0] if rest.split() else None
    
    return None

def main():
    print("=" * 60)
    print("🔧 修复股票映射")
    print("=" * 60)
    
    # 读取原始数据
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"原始数据：{data['total']} 条新闻")
    
    # 修复每条新闻
    fixed_news = []
    for news in data['news']:
        title = news['title']
        
        # 提取公司名
        company = extract_company_from_title(title)
        if not company:
            company = title[:20]  #  fallback
        
        # 映射股票
        stock_code, stock_name, confidence = map_company_to_stock(company)
        
        # 如果映射失败，尝试从标题直接提取
        if not stock_code:
            code_match = re.search(r'(\d{6})', title)
            if code_match:
                code = code_match.group(1)
                # 查数据库
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT stock_code, stock_name, market FROM stock_pool WHERE stock_code LIKE ?', (f'%{code}%',))
                result = cursor.fetchone()
                conn.close()
                if result:
                    stock_code, stock_name, confidence = result[0], result[1], 'medium'
        
        # 创建修复后的记录
        fixed_news.append({
            'title': title,
            'url': news['url'],
            'source': news['source'],
            'stock_code': stock_code or '',
            'stock_name': stock_name or news.get('stock_name', ''),
            'risks': news['risks'],
            'risk_level': news['risk_level'],
            'quality_score': news['quality_score'],
            'verified': news['verified'],
            'crawl_time': news['crawl_time'],
            'mapping_confidence': confidence
        })
        
        status = "✅" if stock_code else "❌"
        print(f"{status} {title[:50]}... → {stock_name or '未映射'} ({stock_code or 'N/A'})")
    
    # 保存修复后的数据
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
    
    print("\n" + "=" * 60)
    print(f"✅ 修复完成！")
    print(f"   总数：{len(fixed_news)} 条")
    print(f"   已映射：{output['mapped_count']} 条")
    print(f"   未映射：{len(fixed_news) - output['mapped_count']} 条")
    print(f"📁 输出：{OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
