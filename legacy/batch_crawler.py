#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量抓取东方财富公司资讯
逐页抓取并保存
"""

import json
from pathlib import Path

DATA_DIR = Path('data/pages')
DATA_DIR.mkdir(exist_ok=True)

# 全量新闻列表
all_news = []

def save_page(page_num, news_list):
    """保存单页数据"""
    filename = DATA_DIR / f'page_{page_num:02d}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    
    global all_news
    all_news.extend(news_list)
    
    print(f"✅ 第{page_num}页保存: {len(news_list)}条新闻")
    return len(all_news)

def save_all():
    """保存全部新闻"""
    filename = DATA_DIR.parent / 'all_news_raw.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 全量保存完成: {len(all_news)}条新闻 → {filename}")
    return len(all_news)

if __name__ == "__main__":
    # 统计当前已抓取数量
    existing_files = list(DATA_DIR.glob('page_*.json'))
    if existing_files:
        for f in existing_files:
            with open(f, 'r', encoding='utf-8') as file:
                news = json.load(file)
                all_news.extend(news)
        print(f"已抓取: {len(existing_files)}页, {len(all_news)}条新闻")