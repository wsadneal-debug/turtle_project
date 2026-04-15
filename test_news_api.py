#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试访问财经网站获取港股新闻
"""

import requests
import json
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://www.eastmoney.com/',
}

session = requests.Session()
session.headers.update(HEADERS)

print("=" * 60)
print("📰 测试财经网站 API")
print("=" * 60)

# 测试 1：东方财富港股新闻 API
print("\n1️⃣ 东方财富港股新闻 API...")
try:
    url = 'https://api.eastmoney.com/Platform/GetPlatformData'
    params = {
        'cate': 'gd',  # 港股
        'sort': '1',  # 最新
        'pageindex': '1',
        'pagesize': '20',
    }
    response = session.get(url, params=params, timeout=15)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        content = response.text
        # 处理 JSONP
        if 'jQuery' in content:
            start = content.find('(') + 1
            end = content.rfind(')')
            content = content[start:end]
        data = json.loads(content)
        print(f"   ✅ 获取成功，{len(data.get('Data', []))} 条新闻")
        if data.get('Data'):
            print(f"   第一条：{data['Data'][0].get('Title', 'N/A')[:50]}")
    else:
        print(f"   ❌ 失败：{response.text[:200]}")
except Exception as e:
    print(f"   ❌ 错误：{e}")

# 测试 2：东方财富数据中心 - 港股公告
print("\n2️⃣ 东方财富港股公告 API...")
try:
    url = 'https://datacenter.eastmoney.com/securities/api/data/get'
    params = {
        'type': 'RPT_FCMR_FOCUS',
        'sty': 'ALL',
        'p': '1',
        'ps': '20',
    }
    response = session.get(url, params=params, timeout=15)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 获取成功，{len(data.get('result', {}).get('data', []))} 条")
    else:
        print(f"   ❌ 失败")
except Exception as e:
    print(f"   ❌ 错误：{e}")

# 测试 3：新浪财经港股
print("\n3️⃣ 新浪财经港股 API...")
try:
    url = 'https://finance.sina.com.hk/api/hk_stock_news.php'
    params = {
        'symbol': '00700',  # 腾讯控股
        'page': '1',
        'num': '10',
    }
    response = session.get(url, params=params, timeout=15)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ 获取成功")
        print(f"   内容：{response.text[:200]}...")
    else:
        print(f"   ❌ 失败：{response.status_code}")
except Exception as e:
    print(f"   ❌ 错误：{e}")

# 测试 4：阿思达克财经
print("\n4️⃣ 阿思达克财经新闻...")
try:
    url = 'https://www.aastocks.com/sc/stocks/news/lastest.aspx'
    response = session.get(url, timeout=15)
    print(f"   状态码：{response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ 页面可访问，{len(response.content)} 字节")
        if '公告' in response.text or '业绩' in response.text:
            print(f"   内容正常")
    else:
        print(f"   ❌ 失败：{response.status_code}")
except Exception as e:
    print(f"   ❌ 错误：{e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
