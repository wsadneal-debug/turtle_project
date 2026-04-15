#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控系统 - 测试版
通过爬取财经网站新闻，识别潜在风险股票
"""

import requests
import json
import re
from datetime import datetime
from collections import defaultdict

# 配置
OUTPUT_DIR = '/home/yxy/.openclaw/workspace/hk_risk_news'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '审计异常', '更换审计师'],
    '经营风险': ['合同违约', '资产冻结', '破产清算', '停业整顿', '重大亏损'],
    '诉讼仲裁': ['重大诉讼', '仲裁', '失信被执行人', '被执行', '冻结股权'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约'],
    '停牌风险': ['停牌', '暂停上市', '终止上市'],
}

def fetch_eastmoney_news():
    """从东方财富网获取港股新闻"""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    news_list = []
    
    # 东方财富港股新闻 API
    urls = [
        'https://api.eastmoney.com/Platform/GetPlatformData?callback=jQuery&cate=gd&sort=1&pageindex=1&pagesize=50',
    ]
    
    for url in urls:
        try:
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                print(f"✅ 成功获取：{url}")
                # 解析 JSONP
                content = response.text
                if 'jQuery(' in content:
                    content = content[content.find('(')+1:content.rfind(')')]
                data = json.loads(content)
                print(f"   数据：{len(data.get('Data', []))} 条")
        except Exception as e:
            print(f"❌ 获取失败：{e}")
    
    return news_list

def fetch_hkex_announcements():
    """从港交所披露易获取公告（需要处理反爬虫）"""
    # 港交所有反爬虫，暂时用模拟数据测试
    print("⚠️  港交所披露易需要处理反爬虫，暂用模拟数据")
    return []

def analyze_risk(text, stock_name=''):
    """分析文本中的风险信号"""
    risks = []
    
    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                risks.append({
                    'category': category,
                    'keyword': keyword,
                    'level': 'high' if category in ['监管处罚', '债务违约', '停牌风险'] else 'medium'
                })
    
    return risks

def test_risk_detection():
    """测试风险检测功能"""
    test_cases = [
        ("腾讯控股发布公告，公司财务总监因个人原因辞职", "腾讯控股"),
        ("碧桂园未能按期偿还美元债券利息，构成违约", "碧桂园"),
        ("证监会对恒大地产立案调查，涉嫌信息披露违规", "恒大地产"),
        ("融创中国审计师普华永道辞任，不再续聘", "融创中国"),
        ("小米集团发布正面业绩公告，净利润增长 20%", "小米集团"),
    ]
    
    print("\n=== 风险检测测试 ===\n")
    
    for text, stock in test_cases:
        risks = analyze_risk(text, stock)
        if risks:
            print(f"🔴 {stock}:")
            for r in risks:
                print(f"   - [{r['level']}] {r['category']}: {r['keyword']}")
        else:
            print(f"🟢 {stock}: 未发现风险")
        print()

def main():
    print("=" * 60)
    print("📰 港股风险新闻监控系统 - 测试版")
    print("=" * 60)
    
    # 测试风险检测
    test_risk_detection()
    
    print("\n" + "=" * 60)
    print("下一步：接入真实新闻源")
    print("=" * 60)

if __name__ == "__main__":
    main()
