#!/usr/bin/env python3
import websocket, json, time, requests

CDP_HOST = '127.0.0.1'
CDP_PORT = 18800

# 连接
resp = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list')
tab_id = resp.json()[0]['id']
ws = websocket.create_connection(f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}', timeout=10)
print(f"✅ 已连接 {tab_id}")

# 导航
url = 'https://finance.eastmoney.com/a/cgsxw.html'
ws.send(json.dumps({'id':1,'method':'Page.navigate','params':{'url':url}}))
print(f"📍 导航到：{url}")

# 简单等待
print("等待 8 秒...")
time.sleep(8)

# 清空消息队列
ws.settimeout(0.5)
while True:
    try:
        ws.recv()
    except:
        break

# 测试简单 JS
print("\n测试 1: 获取链接数量")
msg_id = 10
ws.send(json.dumps({'id':msg_id,'method':'Runtime.evaluate','params':{'expression':'(function() { return document.querySelectorAll("a").length; })()','returnByValue':True}}))

found = False
for i in range(20):
    try:
        msg = json.loads(ws.recv())
        if msg.get('id') == msg_id:
            val = msg.get('result',{}).get('result',{}).get('value')
            print(f"  链接数：{val}")
            found = True
            break
    except: pass

if not found:
    print("  ❌ 未收到响应")

# 测试提取新闻
print("\n测试 2: 提取包含'公告'的链接")
js = '''(function() {
    var links = Array.from(document.querySelectorAll('a'));
    return links.map(a => ({t: a.innerText.trim(), h: a.href}))
        .filter(x => x.t.length > 15 && x.t.includes('公告'))
        .slice(0, 5);
})()'''

msg_id = 11
ws.send(json.dumps({'id':msg_id,'method':'Runtime.evaluate','params':{'expression':js,'returnByValue':True}}))

found = False
for i in range(20):
    try:
        msg = json.loads(ws.recv())
        if msg.get('id') == msg_id:
            val = msg.get('result',{}).get('result',{}).get('value', [])
            print(f"  找到 {len(val)} 条:")
            for item in val:
                t = item.get('t','') if isinstance(item, dict) else str(item)
                print(f"    - {t[:50]}")
            found = True
            break
    except: pass

if not found:
    print("  ❌ 未收到响应")

ws.close()
print("\n完成")
