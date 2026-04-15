#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过 CDP 控制 Chrome 爬取阿思达克财经新闻
"""

import websocket
import json
import time
import re

CDP_HOST = '127.0.0.1'
CDP_PORT = 18800

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '更换审计师'],
    '经营风险': ['合同违约', '资产冻结', '破产清算', '停业整顿', '重大亏损', '亏损'],
    '诉讼仲裁': ['重大诉讼', '仲裁', '失信被执行人', '被执行', '冻结股权'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约'],
    '停牌风险': ['停牌', '暂停上市', '终止上市'],
}

def get_targets():
    """获取所有标签页"""
    import requests
    response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
    return response.json()

def connect_to_tab(tab_id):
    """连接到指定标签页的 WebSocket"""
    ws_url = f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}'
    ws = websocket.create_connection(ws_url)
    return ws

def navigate(ws, url):
    """导航到 URL"""
    cmd = {
        'id': 1,
        'method': 'Page.navigate',
        'params': {'url': url}
    }
    ws.send(json.dumps(cmd))
    result = json.loads(ws.recv())
    return result

def wait_for_load(ws):
    """等待页面加载完成"""
    while True:
        try:
            msg = json.loads(ws.recv())
            if msg.get('method') == 'Page.loadEventFired':
                return True
        except:
            break
    return False

def get_page_content(ws):
    """获取页面 HTML"""
    cmd = {'id': 2, 'method': 'DOM.getDocument'}
    ws.send(json.dumps(cmd))
    
    # 接收响应
    response = json.loads(ws.recv())
    if 'result' in response:
        root = response['result']['root']
        return get_node_html(ws, root['nodeId'])
    return None

def get_node_html(ws, node_id):
    """获取节点 HTML"""
    cmd = {
        'id': 3,
        'method': 'DOM.getOuterHTML',
        'params': {'nodeId': node_id}
    }
    ws.send(json.dumps(cmd))
    response = json.loads(ws.recv())
    if 'result' in response:
        return response['result']['outerHTML']
    return None

def extract_news_from_html(html):
    """从 HTML 提取新闻"""
    news_list = []
    
    if not html:
        return news_list
    
    # 匹配新闻链接和标题
    pattern = r'<a[^>]+href="([^"]*news[^"]*)"[^>]*>([^<]+)</a>'
    matches = re.findall(pattern, html, re.IGNORECASE)
    
    for href, title in matches[:30]:
        title = re.sub(r'<[^>]+>', '', title).strip()
        if title and len(title) > 5:
            news_list.append({
                'title': title,
                'url': f'https://www.aastocks.com{href}' if href.startswith('/') else href
            })
    
    return news_list

def analyze_risk(title):
    """分析风险"""
    risks = []
    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                risks.append({'category': category, 'keyword': keyword})
    return risks

def main():
    print("=" * 60)
    print("🌐 CDP 浏览器爬取阿思达克财经新闻")
    print("=" * 60)
    
    # 获取标签页
    targets = get_targets()
    if not targets:
        print("❌ 没有可用的标签页")
        return
    
    tab_id = targets[0]['id']
    print(f"使用标签页：{tab_id}")
    
    # 连接 WebSocket
    try:
        ws = connect_to_tab(tab_id)
        print("✅ 已连接到浏览器")
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        return
    
    # 导航到阿思达克
    url = 'https://www.aastocks.com/sc/stocks/news/lastest.aspx'
    print(f"导航到：{url}")
    
    result = navigate(ws, url)
    print(f"导航结果：{result}")
    
    # 等待加载
    print("等待页面加载...")
    time.sleep(5)
    
    # 获取页面内容
    print("获取页面内容...")
    html = get_page_content(ws)
    
    if html:
        print(f"✅ 页面内容长度：{len(html)} 字节")
        
        # 提取新闻
        news_list = extract_news_from_html(html)
        print(f"\n📰 找到 {len(news_list)} 条新闻")
        
        for i, news in enumerate(news_list[:10], 1):
            print(f"  {i}. {news['title'][:60]}")
        
        # 分析风险
        print("\n🔴 风险新闻:")
        risk_found = False
        for news in news_list:
            risks = analyze_risk(news['title'])
            if risks:
                risk_found = True
                print(f"\n  ⚠️  {news['title']}")
                for r in risks:
                    print(f"     风险：{r['category']} - {r['keyword']}")
        
        if not risk_found:
            print("  ✅ 未发现风险新闻")
    else:
        print("❌ 无法获取页面内容")
    
    ws.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        import websocket
        main()
    except ImportError:
        print("❌ 需要安装 websocket-client: pip install websocket-client")
