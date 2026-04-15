#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP 爬取器 - 修复版
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
}

OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news')

class CDPClient:
    def __init__(self):
        self.ws = None
        self.msg_id = 0
        self.msg_queue = []
    
    def connect(self):
        resp = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
        targets = resp.json()
        if not targets:
            return False
        self.tab_id = targets[0]['id']
        ws_url = f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{self.tab_id}'
        self.ws = websocket.create_connection(ws_url, timeout=10)
        # 启用 Page 和 Runtime 域
        self.send('Page.enable')
        self.send('Runtime.enable')
        return True
    
    def send(self, method, params=None):
        self.msg_id += 1
        cmd = {'id': self.msg_id, 'method': method}
        if params:
            cmd['params'] = params
        self.ws.send(json.dumps(cmd))
        return self.msg_id
    
    def recv_until(self, method=None, msg_id=None, timeout=10):
        """接收消息直到匹配条件"""
        start = time.time()
        while time.time() - start < timeout:
            try:
                msg = json.loads(self.ws.recv())
                self.msg_queue.append(msg)
                # 检查是否匹配
                if method and msg.get('method') == method:
                    return msg
                if msg_id and msg.get('id') == msg_id:
                    return msg
            except websocket.WebSocketTimeoutException:
                continue
            except Exception as e:
                print(f"接收错误：{e}")
                break
        return None
    
    def navigate(self, url):
        msg_id = self.send('Page.navigate', {'url': url})
        # 等待导航响应
        result = self.recv_until(msg_id=msg_id, timeout=10)
        print(f"📍 导航：{url}")
        return result
    
    def wait_load(self, timeout=8):
        """等待页面加载 - 使用固定等待时间"""
        print(f"等待 {timeout} 秒...", end=' ', flush=True)
        time.sleep(timeout)
        print("✅")
        # 清空消息队列
        self.ws.settimeout(0.3)
        while True:
            try:
                self.ws.recv()
            except:
                break
        return True
    
    def evaluate(self, js):
        """执行 JS 并返回结果"""
        msg_id = self.send('Runtime.evaluate', {'expression': js, 'returnByValue': True})
        result = self.recv_until(msg_id=msg_id, timeout=10)
        if result and 'result' in result and 'result' in result['result']:
            return result['result']['result'].get('value')
        return None
    
    def close(self):
        if self.ws:
            self.ws.close()

def analyze_risk(title):
    risks = []
    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                level = 'HIGH' if category in ['监管处罚', '债务违约', '停牌风险'] else 'MEDIUM'
                risks.append({'category': category, 'keyword': keyword, 'level': level})
    return risks

def extract_stock_info(title):
    code_match = re.search(r'([(\[]?\d{4,6}[)\]]?(?:\.HK|\.SZ|\.SH)?)', title)
    code = code_match.group(0).replace('(','').replace(')','').replace('[','').replace(']','').replace('.HK','') if code_match else ''
    name_match = re.search(r'^([^\(（]+)', title)
    name = name_match.group(0).strip() if name_match else ''
    return code, name

def crawl_eastmoney(client, pages=3):
    """爬取东方财富网"""
    all_news = []
    
    for page in range(1, pages + 1):
        url = f'https://finance.eastmoney.com/a/cgsxw_{page}.html' if page > 1 else 'https://finance.eastmoney.com/a/cgsxw.html'
        print(f"\n📰 第 {page} 页...")
        
        client.navigate(url)
        client.wait_load(timeout=15)
        time.sleep(1)  # 额外等待动态内容
        
        # 提取新闻 - 使用立即执行函数
        js = '''(function() {
            var links = Array.from(document.querySelectorAll('a'));
            return links.map(a => ({t: a.innerText.trim(), h: a.href}))
                .filter(x => x.t.length > 15 && x.t.length < 100 && x.h.includes('/a/'))
                .slice(0, 30);
        })()'''
        
        news = client.evaluate(js)
        print(f"  找到 {len(news) if news else 0} 条候选新闻")
        
        if news:
            for item in news:
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
                    print(f"  ✅ {title[:40]}...")
                # else:
                #     print(f"  ⚪ (无风险) {title[:40]}...")
        
        time.sleep(0.5)
    
    return all_news

def main():
    print("=" * 60)
    print("📰 港股风险新闻爬取 - 修复版")
    print("=" * 60)
    
    client = CDPClient()
    if not client.connect():
        print("❌ 无法连接浏览器")
        return
    
    try:
        all_news = crawl_eastmoney(client, pages=2)
        
        print(f"\n📊 共发现 {len(all_news)} 条风险新闻")
        
        if all_news:
            # 保存 JSON
            output_file = OUTPUT_DIR / f'crawl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total': len(all_news),
                    'news': all_news
                }, f, ensure_ascii=False, indent=2)
            print(f"💾 已保存：{output_file}")
            
            # 统计
            risk_stats = {}
            for news in all_news:
                for risk in news['risks']:
                    cat = risk['category']
                    risk_stats[cat] = risk_stats.get(cat, 0) + 1
            
            print("\n📈 风险类型统计:")
            for cat, count in sorted(risk_stats.items(), key=lambda x: -x[1]):
                print(f"  {cat}: {count}")
    
    finally:
        client.close()
    
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
