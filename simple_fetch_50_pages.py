#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单爬取东方财富公司资讯 50 页
不依赖 Chrome CDP，直接使用 requests
"""

import json
import re
import requests
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news/data/pages')
OUTPUT_DIR.mkdir(exist_ok=True)

# 东方财富公司资讯 URL 模式
BASE_URL = "https://finance.eastmoney.com/a/cgsxw_{}.html"

def fetch_page(page_num):
    """抓取单页"""
    if page_num == 1:
        url = "https://finance.eastmoney.com/a/cgsxw.html"
    else:
        url = BASE_URL.format(page_num)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ 第{page_num}页失败：{e}")
        return None

def extract_news_from_html(html, page_num):
    """从 HTML 提取新闻列表"""
    news_list = []
    
    # 匹配新闻条目
    pattern = r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>\s*<span[^>]*>([^<]+)</span>'
    matches = re.findall(pattern, html)
    
    for url, title, time_str in matches[:30]:  # 每页约 20-30 条
        if 'finance.eastmoney.com' in url or url.startswith('/a/'):
            full_url = f"https://finance.eastmoney.com{url}" if url.startswith('/a/') else url
            news_list.append({
                'title': title.strip(),
                'url': full_url,
                'time': time_str.strip(),
                'page': page_num
            })
    
    return news_list

def main():
    print("=" * 60)
    print("📰 东方财富公司资讯 50 页全量爬取")
    print("=" * 60)
    
    all_news = []
    
    for page in range(1, 51):
        print(f"\n正在抓取第 {page}/50 页...")
        
        html = fetch_page(page)
        if not html:
            print(f"  ⚠️ 第{page}页抓取失败，跳过")
            continue
        
        # 保存原始 HTML
        html_file = OUTPUT_DIR / f"page_{page:02d}_raw.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # 提取新闻
        news = extract_news_from_html(html, page)
        print(f"  ✅ 提取 {len(news)} 条新闻")
        
        # 保存 JSON
        json_file = OUTPUT_DIR / f"page_{page:02d}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(news, f, ensure_ascii=False, indent=2)
        
        all_news.extend(news)
        
        # 保存进度
        progress = {
            'last_page': page,
            'total_news': len(all_news),
            'timestamp': datetime.now().isoformat()
        }
        with open(OUTPUT_DIR / 'progress.json', 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    # 合并所有新闻
    all_file = OUTPUT_DIR / 'all_50_pages.json'
    with open(all_file, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！共抓取 {len(all_news)} 条新闻")
    print(f"📁 保存位置：{OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
