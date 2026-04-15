#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过 CDP 直接控制 Chrome 浏览器爬取财经新闻
"""

import requests
import json
import time
import re

CDP_HOST = '127.0.0.1'
CDP_PORT = 18800

def get_browser_websocket_url():
    """获取浏览器 WebSocket 调试 URL"""
    response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/version', timeout=5)
    data = response.json()
    return data.get('webSocketDebuggerUrl')

def get_targets():
    """获取所有页面标签"""
    response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
    return response.json()

def create_target(url):
    """创建新标签页"""
    response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/new?{url}', timeout=10)
    return response.json()

def navigate_to(tab_id, url):
    """导航到指定 URL"""
    ws_url = f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}'
    
    # 使用 CDP Runtime.evaluate 执行 JavaScript
    cmd = {
        'id': 1,
        'method': 'Runtime.evaluate',
        'params': {
            'expression': f'window.location.href = "{url}"'
        }
    }
    
    # 简单 HTTP 调用 CDP
    response = requests.post(
        f'http://{CDP_HOST}:{CDP_PORT}/json/execute/{tab_id}',
        data=json.dumps(cmd),
        timeout=10
    )
    return response.json()

def main():
    print("=" * 60)
    print("🌐 通过 CDP 控制 Chrome 浏览器")
    print("=" * 60)
    
    # 获取浏览器信息
    try:
        ws_url = get_browser_websocket_url()
        print(f"✅ 浏览器 WebSocket: {ws_url}")
    except Exception as e:
        print(f"❌ 获取浏览器信息失败：{e}")
        return
    
    # 获取当前标签页
    try:
        targets = get_targets()
        print(f"\n📑 当前标签页：{len(targets)} 个")
        for t in targets[:5]:
            print(f"   - {t.get('title', 'N/A')[:50]}")
            print(f"     URL: {t.get('url', 'N/A')[:60]}")
    except Exception as e:
        print(f"❌ 获取标签页失败：{e}")
    
    print("\n" + "=" * 60)
    print("浏览器已就绪，可以通过 CDP 控制")
    print("=" * 60)

if __name__ == "__main__":
    main()
