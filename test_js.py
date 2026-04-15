#!/usr/bin/env python3
import websocket, json, time, requests

CDP_HOST = '127.0.0.1'
CDP_PORT = 18800

# 连接
resp = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list')
tab_id = resp.json()[0]['id']
ws = websocket.create_connection(f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}', timeout=10)

# 启用域
ws.send(json.dumps({'id':1,'method':'Page.enable'}))
ws.send(json.dumps({'id':2,'method':'Runtime.enable'}))

# 导航
ws.send(json.dumps({'id':3,'method':'Page.navigate','params':{'url':'https://finance.eastmoney.com/a/cgsxw.html'}}))
print("导航中...")

# 等待加载
for i in range(30):
    try:
        msg = json.loads(ws.recv())
        if msg.get('method') == 'Page.loadEventFired':
            print("✅ 页面加载完成")
            break
    except: pass
else:
    print("⏱️ 等待超时")

time.sleep(2)

# 测试简单 JS
print("\n测试 1: 获取链接数量")
ws.send(json.dumps({'id':10,'method':'Runtime.evaluate','params':{'expression':'(function() { return document.querySelectorAll("a").length; })()','returnByValue':True}}))
for i in range(10):
    msg = json.loads(ws.recv())
    if msg.get('id') == 10:
        val = msg.get('result',{}).get('result',{}).get('value')
        print(f"  链接数：{val}")
        break

# 测试提取新闻
print("\n测试 2: 提取包含'公告'的链接")
js = '''(function() {
    var links = Array.from(document.querySelectorAll('a'));
    return links.map(a => ({t: a.innerText.trim(), h: a.href}))
        .filter(x => x.t.length > 15 && x.t.includes('公告'))
        .slice(0, 5);
})()'''
ws.send(json.dumps({'id':11,'method':'Runtime.evaluate','params':{'expression':js,'returnByValue':True}}))
for i in range(10):
    msg = json.loads(ws.recv())
    if msg.get('id') == 11:
        val = msg.get('result',{}).get('result',{}).get('value', [])
        print(f"  找到 {len(val)} 条:")
        for item in val:
            print(f"    - {item.get('t','')[:50]}")
        break

ws.close()
