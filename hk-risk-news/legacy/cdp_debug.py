#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP 调试 - 查看实际返回
"""

import websocket
import json
import time
import requests

CDP_HOST = '127.0.0.1'
CDP_PORT = 18800

def main():
    print("连接浏览器...")
    response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
    targets = response.json()
    if not targets:
        print("❌ 无标签页")
        return
    
    tab_id = targets[0]['id']
    ws_url = f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}'
    ws = websocket.create_connection(ws_url, timeout=10)
    print(f"✅ 已连接：{tab_id}")
    
    # 导航
    url = 'https://finance.eastmoney.com/a/cgsxw.html'
    print(f"导航到：{url}")
    cmd = {'id': 1, 'method': 'Page.navigate', 'params': {'url': url}}
    ws.send(json.dumps(cmd))
    print(f"导航响应：{ws.recv()}")
    
    # 等待加载
    print("等待加载...")
    time.sleep(5)
    
    # 执行 JS - 注意要用括号立即执行
    js = '(function() { return document.querySelectorAll("a").length; })()'
    print(f"执行 JS: {js}")
    cmd = {'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}
    ws.send(json.dumps(cmd))
    
    # 接收响应
    print("接收响应...")
    for i in range(5):
        try:
            msg = json.loads(ws.recv())
            print(f"消息 {i}: {json.dumps(msg, ensure_ascii=False)[:500]}")
            if msg.get('id') == 2:
                print(f">>> 找到结果：{msg}")
                break
        except Exception as e:
            print(f"接收错误：{e}")
            break
    
    ws.close()

if __name__ == '__main__':
    main()
