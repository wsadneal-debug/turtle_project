#!/usr/bin/env python3
"""批量处理抓取数据"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import re

# 风险关键词库
RISK_KEYWORDS = {
    'HIGH': [
        '立案调查', '行政处罚', '开庭', '刑事案件', '认罪', '被捕', '被抓',
        '司法冻结', '股份冻结', '资产冻结', '轮候冻结',
        '债券违约', '无法兑付', '破产清算', '重整',
        '审计师辞任', '财报延期', '退市', '停牌风险',
        '实控人', '董事长', '高管被抓'
    ],
    'MEDIUM': [
        '高管辞职', '董事长辞职', '审计更换',
        '经营恶化', '亏损', '并购重组不确定',
        '减持', '质押', '诉讼'
    ]
}

def analyze_news(title, stock_mapper):
    """分析单条新闻风险"""
    risk_level = None
    risk_keywords = []
    
    # 检查高风险关键词
    for kw in RISK_KEYWORDS['HIGH']:
        if kw in title:
            risk_level = 'HIGH'
            risk_keywords.append(kw)
    
    # 检查中风险关键词
    if not risk_level:
        for kw in RISK_KEYWORDS['MEDIUM']:
            if kw in title:
                risk_level = 'MEDIUM'
                risk_keywords.append(kw)
    
    # 尝试识别股票
    stock_code, stock_name = stock_mapper.match(title)
    
    return {
        'title': title,
        'risk_level': risk_level,
        'risk_keywords': risk_keywords,
        'stock_code': stock_code,
        'stock_name': stock_name
    }

def merge_all_pages():
    """合并所有页面数据"""
    all_news = []
    pages_dir = Path('data/pages')
    
    for page_file in sorted(pages_dir.glob('page_*.json')):
        with open(page_file, 'r', encoding='utf-8') as f:
            news = json.load(f)
            all_news.extend(news)
    
    print(f"合并完成: {len(all_news)}条新闻")
    return all_news

if __name__ == '__main__':
    news = merge_all_pages()
    print(f"待分析: {len(news)}条")