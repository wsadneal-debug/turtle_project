#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据源公司风险新闻爬取器
聚焦：公司公告、风险事件、经营问题
过滤：宏观经济、政策解读、市场分析等泛财经新闻
"""

import websocket, json, time, requests, re
from datetime import datetime
from pathlib import Path

CDP_HOST, CDP_PORT = '127.0.0.1', 18800
OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news')

# 公司风险关键词（高优先级）
COMPANY_RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '证监会', '通报批评', '公开谴责', '收到警示函'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '财报延期', '保留意见', '非标意见'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷', '不能按期偿还', '失信被执行'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘', '业绩下滑', '净利润下降', '亏损', '下滑', '下降'],
    '高管变动': ['实控人被捕', '高管离职', '董事长辞职', '被调查', '辞职', '被捕', '失联', '被控制', '变更董事长'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌', '退市', '风险警示', 'ST'],
    '诉讼纠纷': ['诉讼', '纠纷', '仲裁', '被告', '被执行', '冻结股权', '专利诉讼', '起诉'],
    '重组风险': ['重组不确定性', '终止收购', '重组失败', '重大资产重组', '收购失败', '终止收购'],
    '业绩风险': ['业绩预亏', '业绩预告', '净利润下滑', '营收下降', '盈利下降', '大幅下滑'],
}

# 需要过滤的泛财经关键词
FILTER_KEYWORDS = [
    'GDP', 'CPI', 'PPI', '央行', '美联储', '加息', '降息',
    '宏观经济', '经济数据', '政策', '国务院', '发改委',
    'A 股', '沪指', '上证指数', '创业板', '板块', '概念',
    '开盘', '收盘', '涨停', '跌停', '涨幅', '跌幅',
    '市场', '行情', '指数', '大盘', '牛市', '熊市',
    '分析师', '机构', '券商', '基金', '私募', '公募',
    'IPO'  # 保留 IPO 相关，但需要进一步过滤
]

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

def is_company_news(title):
    """判断是否为公司相关新闻"""
    # 包含具体公司名称或股票代码的更可能是公司新闻
    if re.search(r'\d{4,6}', title):  # 包含数字（可能是股票代码）
        return True
    if any(kw in title for kw in ['公司', '股份', '集团', '有限', '科技', '实业', '药业', '银行', '证券']):
        return True
    return False

def is_filtered(title):
    """判断是否应该过滤的泛财经新闻"""
    # 明确是宏观、政策、市场分析的过滤
    macro_keywords = ['进出口', 'GDP', 'CPI', 'PPI', '海关总署', '商务部', '央行', '美联储', 
                      '宏观经济', '经济数据', '政策', '国务院', '发改委', 'A 股', '沪指', 
                      '上证指数', '创业板', '板块', '概念', '开盘', '收盘', '涨停', '跌停',
                      '涨幅', '跌幅', '市场', '行情', '指数', '大盘', '分析师', '机构',
                      '券商', '基金', '私募', '公募', '热点精选', '专题']
    
    for kw in macro_keywords:
        if kw in title:
            return True
    
    return False

def analyze_risk(title):
    """分析风险类型"""
    for cat, kws in COMPANY_RISK_KEYWORDS.items():
        for kw in kws:
            if kw in title:
                level = 'HIGH' if cat in ['监管处罚', '债务违约', '停牌风险'] else 'MEDIUM'
                return [{'category': cat, 'keyword': kw, 'level': level}]
    return []

def extract_stock_info(title):
    """提取股票信息"""
    # 匹配股票代码
    code_match = re.search(r'([(\[]?\d{4,6}[)\]]?(?:\.HK|\.SZ|\.SH)?)', title)
    code = code_match.group(0).replace('(','').replace(')','').replace('[','').replace(']','').replace('.HK','') if code_match else ''
    
    # 匹配公司名称（通常是标题开头）
    name_match = re.search(r'^([^\(（,，:：]+)', title)
    name = name_match.group(0).strip() if name_match else ''
    
    return code, name

def crawl_yicai(ws):
    """爬取第一财经 - 使用搜索页面"""
    print("\n📰 第一财经")
    navigate(ws, 'https://www.yicai.com/search?keys=%E4%B8%8A%E5%B8%82%E5%85%AC%E5%8F%B8')
    wait(ws, 6)
    
    # 提取搜索结果中的公司新闻
    js = '''(function() {
        return Array.from(document.querySelectorAll('a'))
            .map(a => ({t: a.innerText.trim(), h: a.href}))
            .filter(x => x.t.length > 15 && x.t.length < 100 &&
                       (x.t.includes('公告') || x.t.includes('调查') || x.t.includes('诉讼') ||
                        x.t.includes('处罚') || x.t.includes('违约') || x.t.includes('审计') ||
                        x.t.includes('辞职') || x.t.includes('重组') || x.t.includes('亏损') ||
                        x.t.includes('下滑') || x.t.includes('退市') || x.t.includes('警示')));
    })()'''
    
    news = evaluate(ws, js, msg_id=20)
    if not news:
        print("  ⚠️ 无数据")
        return []
    
    print(f"  找到 {len(news)} 条候选")
    
    results = []
    seen = set()
    for item in news[:30]:
        t = item.get('t','')
        url = item.get('h','')
        
        if url in seen:
            continue
        seen.add(url)
        
        if is_filtered(t):
            continue
        
        risks = analyze_risk(t)
        if risks:
            code, name = extract_stock_info(t)
            results.append({
                'title': t, 'url': url, 'source': '第一财经',
                'stock_code': code, 'stock_name': name,
                'risks': risks, 'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"  ✅ {t[:50]}...")
    
    return results

def crawl_qq(ws):
    """爬取腾讯财经 - 使用搜索"""
    print("\n📰 腾讯财经")
    navigate(ws, 'https://search.qq.com/search?query=%E4%B8%8A%E5%B8%82%E5%85%AC%E5%8F%B8%E5%85%AC%E5%91%8A')
    wait(ws, 6)
    
    js = '''(function() {
        return Array.from(document.querySelectorAll('a'))
            .map(a => ({t: a.innerText.trim(), h: a.href}))
            .filter(x => x.t.length > 15 && x.t.length < 100 &&
                       (x.t.includes('公告') || x.t.includes('调查') || x.t.includes('诉讼') ||
                        x.t.includes('处罚') || x.t.includes('违约') || x.t.includes('审计') ||
                        x.t.includes('辞职') || x.t.includes('重组') || x.t.includes('亏损') ||
                        x.t.includes('下滑') || x.t.includes('退市') || x.t.includes('警示') ||
                        x.t.includes('被执行') || x.t.includes('冻结')));
    })()'''
    
    news = evaluate(ws, js, msg_id=21)
    if not news:
        print("  ⚠️ 无数据")
        return []
    
    print(f"  找到 {len(news)} 条候选")
    
    results = []
    seen = set()
    for item in news[:30]:
        t = item.get('t','')
        url = item.get('h','')
        
        if url in seen:
            continue
        seen.add(url)
        
        if is_filtered(t):
            continue
        
        risks = analyze_risk(t)
        if risks:
            code, name = extract_stock_info(t)
            results.append({
                'title': t, 'url': url, 'source': '腾讯财经',
                'stock_code': code, 'stock_name': name,
                'risks': risks, 'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"  ✅ {t[:50]}...")
    
    return results

def crawl_stcn(ws):
    """爬取证券时报"""
    print("\n📰 证券时报")
    navigate(ws, 'https://stcn.com/')
    wait(ws, 6)
    
    js = '''(function() {
        return Array.from(document.querySelectorAll('a'))
            .map(a => ({t: a.innerText.trim(), h: a.href}))
            .filter(x => x.t.length > 15 && x.t.length < 80 &&
                       (x.t.includes('公司') || x.t.includes('股份') || x.t.includes('集团') ||
                        x.t.includes('公告') || x.t.includes('调查') || x.t.includes('诉讼') ||
                        x.t.includes('处罚') || x.t.includes('违约') || x.t.includes('审计') ||
                        x.t.includes('辞职') || x.t.includes('重组') || x.t.includes('亏损') ||
                        x.t.includes('下滑') || x.t.includes('下降') || x.t.includes('退市')));
    })()'''
    
    news = evaluate(ws, js, msg_id=22)
    if not news:
        print("  ⚠️ 无数据")
        return []
    
    print(f"  找到 {len(news)} 条候选")
    
    results = []
    seen = set()
    for item in news[:30]:
        t = item.get('t','')
        url = item.get('h','')
        
        if url in seen:
            continue
        seen.add(url)
        
        if is_filtered(t):
            continue
        
        risks = analyze_risk(t)
        if risks:
            code, name = extract_stock_info(t)
            results.append({
                'title': t, 'url': url, 'source': '证券时报',
                'stock_code': code, 'stock_name': name,
                'risks': risks, 'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"  ✅ {t[:50]}...")
    
    return results

def main():
    print("="*60 + "\n📰 多数据源公司风险新闻爬取\n" + "="*60)
    
    ws = connect()
    print("✅ 已连接浏览器\n")
    
    all_news = []
    seen_urls = set()
    
    try:
        # 爬取各数据源
        for crawl_func, name in [(crawl_yicai, '第一财经'), (crawl_qq, '腾讯财经'), (crawl_stcn, '证券时报')]:
            news = crawl_func(ws)
            for item in news:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_news.append(item)
            time.sleep(2)
        
        print(f"\n📊 共 {len(all_news)} 条风险新闻（去重后）")
        
        if all_news:
            # 按数据源统计
            source_stats = {}
            for n in all_news:
                src = n['source']
                source_stats[src] = source_stats.get(src, 0) + 1
            
            print("\n数据源分布:")
            for src, cnt in sorted(source_stats.items(), key=lambda x: -x[1]):
                print(f"  {src}: {cnt} 条")
            
            # 按风险类型统计
            risk_stats = {}
            for n in all_news:
                for r in n['risks']:
                    cat = r['category']
                    risk_stats[cat] = risk_stats.get(cat, 0) + 1
            
            print("\n风险类型:")
            for cat, cnt in sorted(risk_stats.items(), key=lambda x: -x[1]):
                print(f"  {cat}: {cnt}")
            
            # 保存
            fpath = OUTPUT_DIR / f'multi_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump({
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total': len(all_news),
                    'sources': list(source_stats.keys()),
                    'news': all_news
                }, f, ensure_ascii=False, indent=2)
            print(f"\n💾 保存：{fpath}")
    
    finally:
        ws.close()
    
    print("\n" + "="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
