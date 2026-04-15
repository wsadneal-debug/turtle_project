#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控系统 - 每日自动运行
生成风险股票清单报告
"""

import websocket
import json
import time
import re
import requests
from datetime import datetime
from collections import defaultdict

CDP_HOST = '127.0.0.1'
CDP_PORT = 18800
OUTPUT_DIR = '/home/yxy/.openclaw/workspace/hk_risk_news'

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责', '证监会'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '更换审计师'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职', '被捕'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌'],
}

def get_targets():
    """获取所有标签页"""
    response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
    return response.json()

def connect_to_tab(tab_id):
    """连接到标签页"""
    ws_url = f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{tab_id}'
    ws = websocket.create_connection(ws_url)
    return ws

def navigate(ws, url):
    """导航到 URL"""
    cmd = {'id': 1, 'method': 'Page.navigate', 'params': {'url': url}}
    ws.send(json.dumps(cmd))
    return json.loads(ws.recv())

def get_page_html(ws):
    """获取页面 HTML"""
    cmd = {'id': 2, 'method': 'DOM.getDocument'}
    ws.send(json.dumps(cmd))
    response = json.loads(ws.recv())
    if 'result' in response:
        node_id = response['result']['root']['nodeId']
        cmd = {'id': 3, 'method': 'DOM.getOuterHTML', 'params': {'nodeId': node_id}}
        ws.send(json.dumps(cmd))
        response = json.loads(ws.recv())
        if 'result' in response:
            return response['result']['outerHTML']
    return None

def extract_news(html):
    """提取新闻"""
    news_list = []
    if not html:
        return news_list
    
    # 匹配新闻标题（阿思达克格式）
    patterns = [
        r'<a[^>]+href="([^"]*news[^"]*)"[^>]*>\s*<span[^>]*>([^<]+)</span>',
        r'<a[^>]+title="([^"]+)"[^>]*href="([^"]*news[^"]*)"',
        r'<div[^>]+class="[^"]*news[^"]*"[^>]*>(.*?)</div>',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if len(match) >= 2:
                title = re.sub(r'<[^>]+>', '', match[0]).strip()
                href = match[1] if len(match) > 1 else ''
                if title and len(title) > 5:
                    news_list.append({'title': title, 'url': href})
    
    # 去重
    seen = set()
    unique = []
    for n in news_list:
        if n['title'] not in seen:
            seen.add(n['title'])
            unique.append(n)
    
    return unique[:50]

def analyze_risk(title):
    """分析风险"""
    risks = []
    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                risks.append({
                    'category': category,
                    'keyword': keyword,
                    'level': 'high' if category in ['监管处罚', '债务违约', '停牌风险'] else 'medium'
                })
    return risks

def extract_stock_info(title):
    """提取股票信息"""
    # 匹配股票代码 (如 00700.HK, 00700)
    code_match = re.search(r'([(\[]?\d{4,6}[)\]]?(?:\.HK)?)', title)
    code = code_match.group(0) if code_match else ''
    
    # 匹配股票名称（通常在括号前）
    name_match = re.search(r'^([^\(（]+)', title)
    name = name_match.group(0).strip() if name_match else ''
    
    return code, name

def generate_report(risk_news, output_file):
    """生成报告"""
    report = []
    report.append("# 🔴 港股风险新闻监控报告\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**数据来源**: 阿思达克财经网\n")
    report.append(f"**风险新闻总数**: {len(risk_news)} 条\n")
    report.append("")
    
    # 按风险等级分类
    high_risk = [n for n in risk_news if any(r['level'] == 'high' for r in n['risks'])]
    medium_risk = [n for n in risk_news if all(r['level'] == 'medium' for r in n['risks'])]
    
    # 高风险
    if high_risk:
        report.append("## 🔴 高风险股票\n")
        report.append("| 股票 | 新闻标题 | 风险类型 |\n")
        report.append("|------|---------|---------|\n")
        for item in high_risk[:20]:
            code, name = extract_stock_info(item['title'])
            risk_types = ', '.join(set([r['category'] for r in item['risks']]))
            report.append(f"| {name} {code} | {item['title'][:40]} | {risk_types} |\n")
        report.append("")
    
    # 中风险
    if medium_risk:
        report.append("## 🟡 中风险股票\n")
        report.append("| 股票 | 新闻标题 | 风险类型 |\n")
        report.append("|------|---------|---------|\n")
        for item in medium_risk[:20]:
            code, name = extract_stock_info(item['title'])
            risk_types = ', '.join(set([r['category'] for r in item['risks']]))
            report.append(f"| {name} {code} | {item['title'][:40]} | {risk_types} |\n")
        report.append("")
    
    # 风险统计
    report.append("## 📊 风险类型统计\n")
    risk_count = defaultdict(int)
    for item in risk_news:
        for r in item['risks']:
            risk_count[r['category']] += 1
    
    report.append("| 风险类型 | 数量 |\n")
    report.append("|---------|------|\n")
    for category, count in sorted(risk_count.items(), key=lambda x: x[1], reverse=True):
        report.append(f"| {category} | {count} |\n")
    
    report.append("\n---\n")
    report.append("*本报告由自动化系统生成，仅供参考，不构成投资建议*\n")
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    return ''.join(report)

def main():
    print("=" * 60)
    print("📰 港股风险新闻监控系统")
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
    urls = [
        'https://www.aastocks.com/sc/stocks/news/lastest.aspx',
        'https://www.aastocks.com/sc/stocks/news/company.aspx',
    ]
    
    all_news = []
    
    for url in urls:
        print(f"\n爬取：{url}")
        navigate(ws, url)
        time.sleep(5)  # 等待加载
        
        html = get_page_html(ws)
        if html:
            news = extract_news(html)
            print(f"  ✅ 获取 {len(news)} 条新闻")
            all_news.extend(news)
    
    # 分析风险
    print(f"\n分析 {len(all_news)} 条新闻...")
    risk_news = []
    
    for news in all_news:
        risks = analyze_risk(news['title'])
        if risks:
            risk_news.append({
                'title': news['title'],
                'url': news['url'],
                'risks': risks,
                'max_level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium'
            })
    
    # 生成报告
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f'{OUTPUT_DIR}/risk_news_{date_str}.md'
    
    print(f"\n生成报告：{output_file}")
    report = generate_report(risk_news, output_file)
    
    # 显示摘要
    print("\n" + "=" * 60)
    print("📊 监控结果摘要")
    print("=" * 60)
    print(f"总新闻数：{len(all_news)}")
    print(f"风险新闻：{len(risk_news)}")
    print(f"高风险：{len([n for n in risk_news if n['max_level'] == 'high'])}")
    print(f"中风险：{len([n for n in risk_news if n['max_level'] == 'medium'])}")
    print(f"\n报告文件：{output_file}")
    print("=" * 60)
    
    ws.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n中断")
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
