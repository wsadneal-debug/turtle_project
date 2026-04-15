#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取阿思达克财经新闻，识别风险股票（不使用 BeautifulSoup）
"""

import requests
import re
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '更换审计师'],
    '经营风险': ['合同违约', '资产冻结', '破产清算', '停业整顿', '重大亏损', '亏损'],
    '诉讼仲裁': ['重大诉讼', '仲裁', '失信被执行人', '被执行', '冻结股权'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约'],
    '停牌风险': ['停牌', '暂停上市', '终止上市'],
}

def fetch_aastocks_news():
    """爬取阿思达克财经最新新闻"""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    urls = [
        'https://www.aastocks.com/sc/stocks/news/lastest.aspx',
        'https://www.aastocks.com/sc/stocks/news/company.aspx',
    ]
    
    news_list = []
    
    for url in urls:
        try:
            print(f"爬取：{url}")
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                html = response.text
                
                # 用正则提取新闻标题和链接
                # 匹配 <a href="...">标题</a>
                pattern = r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
                matches = re.findall(pattern, html)
                
                for href, title in matches[:30]:
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    
                    if title and len(title) > 5 and 'news' in href.lower():
                        news_list.append({
                            'title': title,
                            'url': f'https://www.aastocks.com{href}' if href.startswith('/') else href,
                            'source': '阿思达克'
                        })
                
                print(f"  ✅ 获取 {len(news_list)} 条新闻")
                
        except Exception as e:
            print(f"  ❌ 失败：{e}")
    
    return news_list

def analyze_news_risk(news_list):
    """分析新闻中的风险信号"""
    risk_stocks = []
    
    for news in news_list:
        title = news['title']
        risks = []
        
        for category, keywords in RISK_KEYWORDS.items():
            for keyword in keywords:
                if keyword in title:
                    risks.append({
                        'category': category,
                        'keyword': keyword,
                        'level': 'high' if category in ['监管处罚', '债务违约', '停牌风险'] else 'medium'
                    })
        
        if risks:
            # 提取股票代码
            stock_match = re.search(r'([(\[][0-9]{4,5}[)])', title)
            stock_code = stock_match.group(0) if stock_match else ''
            
            risk_stocks.append({
                'title': title,
                'url': news['url'],
                'stock_code': stock_code,
                'risks': risks,
                'max_level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium'
            })
    
    return risk_stocks

def main():
    print("=" * 60)
    print("📰 港股风险新闻监控 - 阿思达克财经")
    print("=" * 60)
    
    # 爬取新闻
    news_list = fetch_aastocks_news()
    
    print(f"\n共获取 {len(news_list)} 条新闻\n")
    
    # 显示前 10 条新闻标题
    print("📰 最新新闻标题:")
    for i, news in enumerate(news_list[:10], 1):
        print(f"  {i}. {news['title'][:60]}")
    
    # 分析风险
    risk_stocks = analyze_news_risk(news_list)
    
    print("\n" + "=" * 60)
    print("🔴 风险股票")
    print("=" * 60)
    
    if risk_stocks:
        for item in risk_stocks:
            level = "🔴" if item['max_level'] == 'high' else "🟡"
            print(f"\n{level} {item['stock_code']}")
            print(f"   标题：{item['title']}")
            print(f"   风险：{', '.join([r['keyword'] for r in item['risks']])}")
    else:
        print("✅ 未发现风险新闻")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
