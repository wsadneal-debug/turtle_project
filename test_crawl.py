#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试爬取 - 检查实际页面内容
"""

import websocket
import json
import time
import requests

CDP_HOST = '127.0.0.1'
CDP_PORT = 18800

def connect_browser():
    """连接浏览器"""
    response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
    targets = response.json()
    if not targets:
        return None
    
    tab_id = targets[0]['id']
    ws_url = f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}'
    ws = websocket.create_connection(ws_url, timeout=10)
    return ws

def navigate(ws, url):
    """导航"""
    cmd = {'id': 1, 'method': 'Page.navigate', 'params': {'url': url}}
    ws.send(json.dumps(cmd))
    return json.loads(ws.recv())

def wait_load(ws, timeout=10):
    """等待加载"""
    import time
    start = time.time()
    while time.time() - start < timeout:
        try:
            msg = json.loads(ws.recv())
            if msg.get('method') == 'Page.loadEventFired':
                return True
        except:
            time.sleep(0.5)
    return False

def get_titles(ws):
    """获取所有链接文本"""
    cmd = {
        'id': 2,
        'method': 'Runtime.evaluate',
        'params': {
            'expression': '''
            () => {
                const links = document.querySelectorAll('a');
                const titles = [];
                links.forEach(a => {
                    const text = a.innerText.trim();
                    if (text.length > 10 && text.length < 100) {
                        titles.push({
                            text: text,
                            href: a.href
                        });
                    }
                });
                return titles.slice(0, 50);
            }
            '''
        }
    }
    ws.send(json.dumps(cmd))
    result = json.loads(ws.recv())
    if 'result' in result and 'result' in result['result']:
        return result['result']['result'].get('value', [])
    return []

def main():
    print("=" * 60)
    print("🔍 测试爬取 - 东方财富网")
    print("=" * 60)
    
    ws = connect_browser()
    if not ws:
        print("❌ 无法连接浏览器")
        return
    
    # 导航到东方财富
    url = 'https://finance.eastmoney.com/a/cgsxw.html'
    print(f"\n📍 导航到：{url}")
    navigate(ws, url)
    print("等待页面加载...")
    time.sleep(5)
    
    # 获取链接
    print("\n📰 获取页面链接...")
    titles = get_titles(ws)
    
    print(f"\n找到 {len(titles)} 个链接:")
    print("-" * 60)
    
    for i, item in enumerate(titles[:30], 1):
        text = item.get('text', '')[:60]
        href = item.get('href', '')[:60]
        print(f"{i:2}. {text}")
        # print(f"    {href}")
    
    ws.close()
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
