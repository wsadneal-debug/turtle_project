#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据源爬取测试
"""

import websocket, json, time, requests
from datetime import datetime

CDP_HOST, CDP_PORT = '127.0.0.1', 18800

SOURCES = [
    # 名称，URL，是否已测试
    ("第一财经", "https://www.yicai.com/news/", False),
    ("腾讯财经", "https://news.qq.com/ch/finance", False),
    ("证券时报", "https://stcn.com/news/", False),
]

def connect():
    resp = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
    tab_id = resp.json()[0]['id']
    ws = websocket.create_connection(f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}', timeout=10)
    ws.send(json.dumps({'id':1,'method':'Page.enable'}))
    ws.send(json.dumps({'id':2,'method':'Runtime.enable'}))
    return ws

def test_source(ws, name, url):
    """测试单个数据源"""
    print(f"\n📰 测试：{name}")
    print(f"   URL: {url}")
    
    # 导航
    ws.send(json.dumps({'id':3,'method':'Page.navigate','params':{'url':url}}))
    time.sleep(5)
    
    # 清空消息
    ws.settimeout(0.2)
    while True:
        try: ws.recv()
        except: break
    
    # 提取链接
    js = '''(function() {
        return Array.from(document.querySelectorAll('a'))
            .map(a => ({t: a.innerText.trim(), h: a.href}))
            .filter(x => x.t.length > 10 && x.t.length < 80)
            .slice(0, 10);
    })()'''
    
    ws.send(json.dumps({'id':10,'method':'Runtime.evaluate','params':{'expression':js,'returnByValue':True}}))
    
    for i in range(30):
        try:
            msg = json.loads(ws.recv())
            if msg.get('id') == 10:
                news = msg.get('result',{}).get('result',{}).get('value',[])
                if news:
                    print(f"   ✅ 成功获取 {len(news)} 条新闻")
                    for item in news[:3]:
                        t = item.get('t','')[:50]
                        print(f"     - {t}...")
                    return True
                else:
                    print(f"   ⚠️ 无数据")
                    return False
        except: pass
    
    print(f"   ❌ 超时")
    return False

def main():
    print("="*60)
    print("🌐 多数据源爬取测试")
    print("="*60)
    
    ws = connect()
    print("✅ 已连接浏览器\n")
    
    results = []
    try:
        for name, url, tested in SOURCES:
            if tested:
                print(f"\n⏭️  跳过 {name} (已测试)")
                continue
            
            result = test_source(ws, name, url)
            results.append((name, url, result))
            time.sleep(2)
    
    finally:
        ws.close()
    
    # 汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for name, url, ok in results:
        status = "✅ 可用" if ok else "❌ 不可用"
        print(f"{status} | {name}")
        print(f"       {url}")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误：{e}")
