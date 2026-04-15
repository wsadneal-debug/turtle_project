#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单 CDP 爬取器 - 直接使用 WebSocket
"""

import websocket
import json
import time
import re
import requests
from datetime import datetime
from pathlib import Path

CDP_HOST = '127.0.0.1'
CDP_PORT = 18800

RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责', '证监会'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职', '被捕'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌'],
    '市场风险': ['关税战', '威胁', '封锁', '中断', '危机', '制裁'],
}

OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news')

def get_risk_level(category):
    if category in ['监管处罚', '债务违约', '停牌风险']:
        return 'HIGH'
    return 'MEDIUM'

def analyze_risk(title):
    risks = []
    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                risks.append({'category': category, 'keyword': keyword, 'level': get_risk_level(category)})
    return risks

def extract_stock_info(title):
    code_match = re.search(r'([(\[]?0\d{4,5}[)\]]?(?:\.HK)?)', title)
    code = code_match.group(0).replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('.HK', '') if code_match else ''
    name_match = re.search(r'^([^\(（]+)', title)
    name = name_match.group(0).strip() if name_match else ''
    return code, name

class CDPClient:
    def __init__(self):
        self.ws = None
        self.msg_id = 0
    
    def connect(self):
        response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
        targets = response.json()
        if not targets:
            return False
        self.tab_id = targets[0]['id']
        ws_url = f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{self.tab_id}'
        self.ws = websocket.create_connection(ws_url, timeout=10)
        print(f"✅ 已连接浏览器")
        return True
    
    def send(self, method, params=None):
        self.msg_id += 1
        cmd = {'id': self.msg_id, 'method': method}
        if params:
            cmd['params'] = params
        self.ws.send(json.dumps(cmd))
    
    def recv(self):
        return json.loads(self.ws.recv())
    
    def navigate(self, url):
        self.send('Page.navigate', {'url': url})
        result = self.recv()
        print(f"📍 导航：{url}")
        return result
    
    def wait_load(self, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            try:
                msg = self.recv()
                if msg.get('method') == 'Page.loadEventFired':
                    return True
            except:
                time.sleep(0.5)
        return False
    
    def evaluate(self, js):
        self.send('Runtime.evaluate', {'expression': js, 'returnByValue': True})
        # 接收响应
        while True:
            result = self.recv()
            if result.get('id') and result['id'] > self.msg_id - 1:
                if 'result' in result and 'result' in result['result']:
                    return result['result']['result'].get('value')
                break
        return None
    
    def close(self):
        if self.ws:
            self.ws.close()

def crawl_page(client, page=1):
    """爬取单页"""
    url = f'https://finance.eastmoney.com/a/cgsxw_{page}.html' if page > 1 else 'https://finance.eastmoney.com/a/cgsxw.html'
    client.navigate(url)
    time.sleep(3)
    client.wait_load(timeout=10)
    
    js = '''(function() {
        const links = Array.from(document.querySelectorAll('a'));
        return links
            .map(a => ({t: a.innerText.trim(), h: a.href}))
            .filter(x => x.t.length > 15 && x.t.length < 100 && 
                       (x.t.includes('公告') || x.t.includes('调查') || x.t.includes('诉讼') ||
                        x.t.includes('处罚') || x.t.includes('违约') || x.t.includes('审计') ||
                        x.t.includes('辞职') || x.t.includes('冻结') || x.t.includes('重组')));
    })()'''
    
    news = client.evaluate(js)
    return news if news else []

def main():
    print("=" * 60)
    print("📰 港股风险新闻爬取 - CDP 测试")
    print("=" * 60)
    
    client = CDPClient()
    if not client.connect():
        print("❌ 无法连接浏览器")
        return
    
    all_news = []
    
    for page in range(1, 4):
        print(f"\n爬取第 {page} 页...")
        news_list = crawl_page(client, page)
        
        for item in news_list:
            title = item.get('t', '')
            url = item.get('h', '')
            
            risks = analyze_risk(title)
            if risks:
                code, name = extract_stock_info(title)
                all_news.append({
                    'title': title,
                    'url': url,
                    'source': '东方财富网',
                    'stock_code': code,
                    'stock_name': name,
                    'risks': risks,
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"  ✅ {title[:50]}...")
        
        time.sleep(1)
    
    print(f"\n共发现 {len(all_news)} 条风险新闻")
    
    if all_news:
        output_file = OUTPUT_DIR / f'cdp_news_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total': len(all_news),
                'news': all_news
            }, f, ensure_ascii=False, indent=2)
        print(f"已保存：{output_file}")
    
    client.close()
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
