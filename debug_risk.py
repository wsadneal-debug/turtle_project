#!/usr/bin/env python3
import websocket, json, time, requests

CDP_HOST, CDP_PORT = '127.0.0.1', 18800

# 连接
resp = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list')
tab_id = resp.json()[0]['id']
ws = websocket.create_connection(f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}', timeout=10)
ws.send(json.dumps({'id':1,'method':'Page.enable'}))
ws.send(json.dumps({'id':2,'method':'Runtime.enable'}))

# 导航
ws.send(json.dumps({'id':3,'method':'Page.navigate','params':{'url':'https://finance.eastmoney.com/a/cgsxw.html'}}))
print("导航中...")
time.sleep(6)
ws.settimeout(0.2)
while True:
    try: ws.recv()
    except: break

# 获取新闻
js = '''(function() {
    return Array.from(document.querySelectorAll('a'))
        .map(a => a.innerText.trim())
        .filter(t => t.length>15 && t.length<100)
        .slice(0, 30);
})()'''

ws.send(json.dumps({'id':10,'method':'Runtime.evaluate','params':{'expression':js,'returnByValue':True}}))
for i in range(30):
    try:
        msg = json.loads(ws.recv())
        if msg.get('id') == 10:
            titles = msg.get('result',{}).get('result',{}).get('value',[])
            print(f"\n找到 {len(titles)} 条标题:\n")
            for i, t in enumerate(titles, 1):
                print(f"{i:2}. {t}")
            break
    except: pass

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '证监会'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '财报延期'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘'],
    '高管变动': ['实控人被捕', '高管离职', '董事长辞职', '被调查', '辞职', '被捕'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌'],
}

print("\n" + "="*60)
print("风险匹配测试:\n")

for t in titles[:20]:
    for cat, kws in RISK_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                print(f"✅ [{cat}] {kw} → {t[:50]}...")
                break

ws.close()
