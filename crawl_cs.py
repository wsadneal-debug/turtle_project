#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国证券报爬取器
"""

import websocket, json, time, requests, re
from datetime import datetime
from pathlib import Path

CDP_HOST, CDP_PORT = '127.0.0.1', 18800
OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news')

RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '证监会', '通报批评', '公开谴责'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '财报延期', '保留意见'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘', '亏损', '下滑'],
    '高管变动': ['实控人被捕', '高管离职', '董事长辞职', '被调查', '辞职', '被捕', '失联'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌', '退市'],
    '诉讼纠纷': ['诉讼', '纠纷', '仲裁', '被告', '被执行', '失信', '冻结股权'],
    '重组风险': ['重组不确定性', '终止收购', '重组失败', '重大资产重组'],
}

def connect():
    resp = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
    tab_id = resp.json()[0]['id']
    ws = websocket.create_connection(f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}', timeout=10)
    ws.send(json.dumps({'id':1,'method':'Page.enable'}))
    ws.send(json.dumps({'id':2,'method':'Runtime.enable'}))
    return ws

def navigate(ws, url):
    ws.send(json.dumps({'id':3,'method':'Page.navigate','params':{'url':url}}))
    print(f"📍 {url}")

def wait(ws, seconds=5):
    time.sleep(seconds)
    ws.settimeout(0.2)
    while True:
        try: ws.recv()
        except: break

def evaluate(ws, js, msg_id=10):
    ws.send(json.dumps({'id':msg_id,'method':'Runtime.evaluate','params':{'expression':js,'returnByValue':True}}))
    for i in range(30):
        try:
            msg = json.loads(ws.recv())
            if msg.get('id') == msg_id:
                return msg.get('result',{}).get('result',{}).get('value')
        except: pass
    return None

def analyze(title):
    for cat, kws in RISK_KEYWORDS.items():
        for kw in kws:
            if kw in title:
                return [{'category':cat,'keyword':kw,'level':'HIGH' if cat in ['监管处罚','债务违约','停牌风险'] else 'MEDIUM'}]
    return []

def crawl_cscom(ws):
    """爬取中国证券报"""
    print("\n📰 中国证券报")
    navigate(ws, 'https://www.cs.com.cn/')
    wait(ws, 6)
    
    # 提取快讯中的风险新闻
    js = '''(function() {
        return Array.from(document.querySelectorAll('a'))
            .map(a => ({t: a.innerText.trim(), h: a.href}))
            .filter(x => x.t.length > 10 && x.t.length < 80 && 
                       (x.t.includes('公告') || x.t.includes('调查') || x.t.includes('诉讼') ||
                        x.t.includes('处罚') || x.t.includes('违约') || x.t.includes('审计') ||
                        x.t.includes('辞职') || x.t.includes('重组') || x.t.includes('亏损')));
    })()'''
    
    news = evaluate(ws, js, msg_id=20)
    if not news:
        print("  ⚠️ 无数据")
        return []
    
    print(f"  找到 {len(news)} 条候选")
    
    results = []
    for item in news[:20]:
        t = item.get('t','')
        risks = analyze(t)
        if risks:
            results.append({
                'title': t, 'url': item.get('h',''), 'source': '中国证券报',
                'risks': risks, 'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"  ✅ {t[:45]}...")
    
    return results

def main():
    print("="*60 + "\n📰 中国证券报爬取测试\n" + "="*60)
    
    ws = connect()
    print("✅ 已连接浏览器\n")
    
    try:
        all_news = crawl_cscom(ws)
        print(f"\n📊 共 {len(all_news)} 条风险新闻")
        
        if all_news:
            fpath = OUTPUT_DIR / f'cs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(fpath,'w',encoding='utf-8') as f:
                json.dump({'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'total':len(all_news),'news':all_news}, f, ensure_ascii=False, indent=2)
            print(f"💾 保存：{fpath}")
    finally:
        ws.close()
    
    print("\n"+"="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
