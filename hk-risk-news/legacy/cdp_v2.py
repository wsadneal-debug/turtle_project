#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP 爬取器 v2 - 简化版
"""

import websocket, json, time, requests, re
from datetime import datetime
from pathlib import Path

CDP_HOST, CDP_PORT = '127.0.0.1', 18800
OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news')

RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '证监会', '通报批评', '公开谴责'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '财报延期', '保留意见'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷', '不能按期偿还'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘', '亏损', '下滑', '暴跌'],
    '高管变动': ['实控人被捕', '高管离职', '董事长辞职', '被调查', '辞职', '被捕', '失联', '被控制'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌', '退市'],
    '诉讼纠纷': ['诉讼', '纠纷', '仲裁', '被告', '被执行', '失信', '冻结股权', '再审'],
    '重组风险': ['重组不确定性', '终止收购', '重组失败', '收购失败', '重大资产重组'],
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

def wait(ws, seconds=6):
    time.sleep(seconds)
    # 清空队列
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

def extract(title):
    m = re.search(r'([(\[]?\d{4,6}[)\]]?(?:\.HK|\.SZ|\.SH)?)', title)
    code = m.group(0).replace('(','').replace(')','').replace('[','').replace(']','').replace('.HK','') if m else ''
    n = re.search(r'^([^\(（]+)', title)
    name = n.group(0).strip() if n else ''
    return code, name

def crawl_page(ws, url, page_num, seen_urls):
    print(f"\n📄 第{page_num}页")
    navigate(ws, url)
    wait(ws, 6)
    
    js = '''(function() {
        return Array.from(document.querySelectorAll('a'))
            .map(a => ({t:a.innerText.trim(), h:a.href}))
            .filter(x => x.t.length>15 && x.t.length<100 && x.h.includes('/a/'))
            .slice(0, 25);
    })()'''
    
    news = evaluate(ws, js, msg_id=page_num)
    if not news:
        print("  ⚠️ 无数据")
        return []
    
    print(f"  找到 {len(news)} 条")
    
    results = []
    for item in news:
        url = item.get('h','')
        # 去重
        if url in seen_urls:
            continue
        seen_urls.add(url)
        
        t = item.get('t','')
        risks = analyze(t)
        if risks:
            code, name = extract(t)
            results.append({
                'title': t, 'url': url, 'source': '东方财富网',
                'stock_code': code, 'stock_name': name, 'risks': risks,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"  ✅ {t[:45]}...")
    
    return results

def main():
    print("="*60 + "\n📰 港股风险新闻爬取 v2\n" + "="*60)
    
    ws = connect()
    print("✅ 已连接浏览器\n")
    
    all_news = []
    seen_urls = set()
    pages = ['https://finance.eastmoney.com/a/cgsxw.html',
             'https://finance.eastmoney.com/a/cgsxw_2.html',
             'https://finance.eastmoney.com/a/cgsxw_3.html']
    
    for i, url in enumerate(pages, 1):
        news = crawl_page(ws, url, i, seen_urls)
        all_news.extend(news)
        time.sleep(1)
    
    print(f"\n📊 共 {len(all_news)} 条风险新闻")
    
    if all_news:
        # 统计
        stats = {}
        for n in all_news:
            for r in n['risks']:
                stats[r['category']] = stats.get(r['category'],0)+1
        
        print("\n风险类型:")
        for cat,cnt in sorted(stats.items(), key=lambda x:-x[1]):
            print(f"  {cat}: {cnt}")
        
        # 保存
        fpath = OUTPUT_DIR / f'crawl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(fpath,'w',encoding='utf-8') as f:
            json.dump({'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'total':len(all_news),'news':all_news}, f, ensure_ascii=False, indent=2)
        print(f"\n💾 保存：{fpath}")
    
    ws.close()
    print("\n"+"="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ {e}")
        import traceback
        traceback.print_exc()
