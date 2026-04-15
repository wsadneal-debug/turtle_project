#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 OpenClaw browser 工具爬取财经新闻
"""

import sys
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

def main():
    print("=" * 60)
    print("📰 港股风险新闻爬取")
    print("=" * 60)
    
    # 测试新闻标题
    test_news = [
        "碧桂园未能按期偿还债券利息，构成违约",
        "证监会对恒大地产立案调查，涉嫌信息披露违规",
        "融创中国审计师普华永道辞任，不再续聘",
        "腾讯控股发布正面业绩公告，净利润增长 20%",
        "小米集团被证监会问询",
        "实控人被捕，某上市公司股价暴跌",
        "某公司债务逾期，无法兑付",
        "停牌核查，某股票暂停上市",
    ]
    
    risk_news = []
    
    for title in test_news:
        risks = analyze_risk(title)
        if risks:
            code, name = extract_stock_info(title)
            risk_news.append({
                'title': title,
                'code': code,
                'name': name,
                'risks': risks,
                'max_level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium'
            })
    
    # 生成报告
    print("\n🔴 风险股票清单\n")
    
    high_risk = [n for n in risk_news if n['max_level'] == 'high']
    medium_risk = [n for n in risk_news if n['max_level'] == 'medium']
    
    if high_risk:
        print("=" * 60)
        print("🔴 高风险股票")
        print("=" * 60)
        for item in high_risk:
            risk_types = ', '.join(set([r['category'] for r in item['risks']]))
            print(f"\n{item['name']} {item['code']}")
            print(f"  新闻：{item['title']}")
            print(f"  风险：{risk_types}")
    
    if medium_risk:
        print("\n" + "=" * 60)
        print("🟡 中风险股票")
        print("=" * 60)
        for item in medium_risk:
            risk_types = ', '.join(set([r['category'] for r in item['risks']]))
            print(f"\n{item['name']} {item['code']}")
            print(f"  新闻：{item['title']}")
            print(f"  风险：{risk_types}")
    
    # 统计
    print("\n" + "=" * 60)
    print("📊 风险统计")
    print("=" * 60)
    risk_count = defaultdict(int)
    for item in risk_news:
        for r in item['risks']:
            risk_count[r['category']] += 1
    
    for category, count in sorted(risk_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
