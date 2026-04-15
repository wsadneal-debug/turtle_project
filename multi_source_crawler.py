#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 多数据源爬取模块

支持的数据源：
1. 东方财富网 - 个股新闻
2. 阿思达克财经网 - 港股资讯
3. 新浪财经 - 港股频道
4. 腾讯财经 - 港股新闻

使用已授权的 CDP 浏览器（端口 18800）
"""

import websocket
import json
import time
import re
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# CDP 浏览器配置
CDP_HOST = '127.0.0.1'
CDP_PORT = 18800

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责', '证监会', '交易所问询'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '更换审计师'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘', '跳水', '暴跌'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职', '被捕', '被抓'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌'],
    '市场风险': ['关税战', '威胁', '封锁', '中断', '危机', '制裁'],
}

OUTPUT_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news')


class CDPBrowser:
    """CDP 浏览器控制器"""
    
    def __init__(self):
        self.ws = None
        self.tab_id = None
        self.msg_id = 0
    
    def connect(self) -> bool:
        """连接到浏览器"""
        try:
            # 获取标签页列表
            response = requests.get(f'http://{CDP_HOST}:{CDP_PORT}/json/list', timeout=5)
            targets = response.json()
            
            if not targets:
                print("❌ 没有可用的标签页")
                return False
            
            self.tab_id = targets[0]['id']
            
            # 连接 WebSocket
            ws_url = f'ws://{CDP_HOST}:{CDP_PORT}/devtools/page/{self.tab_id}'
            self.ws = websocket.create_connection(ws_url, timeout=10)
            print(f"✅ 已连接到浏览器标签页：{self.tab_id}")
            return True
            
        except Exception as e:
            print(f"❌ 连接浏览器失败：{e}")
            return False
    
    def navigate(self, url: str) -> bool:
        """导航到指定 URL"""
        if not self.ws:
            return False
        
        cmd = {
            'id': 1,
            'method': 'Page.navigate',
            'params': {'url': url}
        }
        self.ws.send(json.dumps(cmd))
        result = json.loads(self.ws.recv())
        print(f"📍 导航到：{url}")
        return 'error' not in result
    
    def wait_for_load(self, timeout: int = 10):
        """等待页面加载完成"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                msg = json.loads(self.ws.recv())
                if msg.get('method') == 'Page.loadEventFired':
                    print("✅ 页面加载完成")
                    return True
            except:
                time.sleep(0.5)
        return False
    
    def evaluate(self, js_code: str) -> Optional[any]:
        """执行 JavaScript 代码"""
        if not self.ws:
            return None
        
        self.msg_id += 1
        cmd = {
            'id': self.msg_id,
            'method': 'Runtime.evaluate',
            'params': {
                'expression': js_code,
                'returnByValue': True
            }
        }
        self.ws.send(json.dumps(cmd))
        
        try:
            while True:
                result = json.loads(self.ws.recv())
                if result.get('id') == self.msg_id:
                    if 'result' in result and 'result' in result['result']:
                        return result['result']['result'].get('value')
                    break
        except Exception as e:
            print(f"⚠️ JS 执行错误：{e}")
        return None
    
    def get_html(self) -> Optional[str]:
        """获取页面 HTML"""
        html = self.evaluate('document.documentElement.outerHTML')
        return html
    
    def close(self):
        """关闭连接"""
        if self.ws:
            self.ws.close()
            print("🔌 已断开浏览器连接")


class NewsSource:
    """新闻源基类"""
    
    name = "未知数据源"
    base_url = ""
    
    def __init__(self, browser: CDPBrowser):
        self.browser = browser
        self.news_list = []
    
    def fetch(self) -> List[Dict]:
        """获取新闻列表"""
        raise NotImplementedError
    
    def analyze_risk(self, title: str) -> List[Dict]:
        """分析新闻风险"""
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
    
    def extract_stock_info(self, title: str) -> tuple:
        """提取股票信息"""
        # 匹配港股代码 (0xxxx.HK 或 0xxxx)
        code_match = re.search(r'([(\[]?0\d{4,5}[)\]]?(?:\.HK)?)', title)
        code = code_match.group(0).replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('.HK', '') if code_match else ''
        
        # 匹配公司名称（括号前的内容）
        name_match = re.search(r'^([^\(（]+)', title)
        name = name_match.group(0).strip() if name_match else ''
        
        return code, name


class EastMoneySource(NewsSource):
    """东方财富网 - 个股新闻"""
    
    name = "东方财富网"
    base_url = "https://finance.eastmoney.com/a/cgsxw_{}.html"
    
    def fetch(self, pages: int = 3) -> List[Dict]:
        """爬取指定页数的新闻"""
        all_news = []
        
        for page in range(1, pages + 1):
            url = self.base_url.format(page) if page > 1 else "https://finance.eastmoney.com/a/cgsxw.html"
            
            print(f"\n📰 爬取 {self.name} 第 {page} 页...")
            self.browser.navigate(url)
            time.sleep(5)
            
            # 提取新闻标题和链接 - 更精确的选择器
            js_code = '''
            (function() {
                const news = [];
                const links = Array.from(document.querySelectorAll('a'));
                links.forEach(a => {
                    const text = a.innerText.trim();
                    const href = a.href;
                    if (text.length > 15 && text.length < 100 && href) {
                        if (text.includes('涨停') || text.includes('跌停') || 
                            text.includes('公告') || text.includes('披露') ||
                            text.includes('调查') || text.includes('处罚') ||
                            text.includes('违约') || text.includes('诉讼') ||
                            text.includes('重组') || text.includes('亏损') ||
                            text.includes('业绩') || text.includes('财报') ||
                            text.includes('审计') || text.includes('辞任') ||
                            text.includes('辞职') || text.includes('被捕') ||
                            text.includes('冻结') || text.includes('质押') ||
                            text.includes('破产')) {
                            news.push({title: text, url: href});
                        }
                    }
                });
                return news.slice(0, 40);
            })()
            '''
            
            news = self.browser.evaluate(js_code)
            if news:
                for item in news:
                    risks = self.analyze_risk(item['title'])
                    if risks:
                        code, name = self.extract_stock_info(item['title'])
                        all_news.append({
                            'title': item['title'],
                            'url': item['url'],
                            'source': self.name,
                            'stock_code': code,
                            'stock_name': name,
                            'risks': risks,
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
            
            time.sleep(2)
        
        return all_news


class AastocksSource(NewsSource):
    """阿思达克财经网 - 港股资讯"""
    
    name = "阿思达克财经网"
    base_url = "https://www.aastocks.com/sc/stocks/news/lastest.aspx"
    
    def fetch(self, pages: int = 3) -> List[Dict]:
        """爬取新闻"""
        all_news = []
        
        print(f"\n📰 爬取 {self.name}...")
        self.browser.navigate(self.base_url)
        time.sleep(3)
        self.browser.wait_for_load(timeout=10)
        
        # 提取新闻
        js_code = '''
        () => {
            const links = Array.from(document.querySelectorAll('a'));
            return links
                .filter(a => a.href && (a.href.includes('news') || a.href.includes('stocks')))
                .map(a => ({
                    title: a.innerText.trim(),
                    url: a.href.startsWith('/') ? 'https://www.aastocks.com' + a.href : a.href
                }))
                .filter(item => item.title.length > 10 && item.title.length < 100);
        }
        '''
        
        news = self.browser.evaluate(js_code)
        if news:
            for item in news[:50]:
                risks = self.analyze_risk(item['title'])
                if risks:
                    code, name = self.extract_stock_info(item['title'])
                    all_news.append({
                        'title': item['title'],
                        'url': item['url'],
                        'source': self.name,
                        'stock_code': code,
                        'stock_name': name,
                        'risks': risks,
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return all_news


class SinaFinanceSource(NewsSource):
    """新浪财经 - 港股频道"""
    
    name = "新浪财经"
    base_url = "https://finance.sina.com.hk/"
    
    def fetch(self) -> List[Dict]:
        """爬取新闻"""
        all_news = []
        
        print(f"\n📰 爬取 {self.name}...")
        self.browser.navigate(self.base_url)
        time.sleep(3)
        self.browser.wait_for_load(timeout=10)
        
        js_code = '''
        () => {
            const links = Array.from(document.querySelectorAll('a'));
            return links
                .filter(a => a.href && a.href.includes('stock') || a.href.includes('hk'))
                .map(a => ({
                    title: a.innerText.trim(),
                    url: a.href
                }))
                .filter(item => item.title.length > 10 && item.title.length < 100);
        }
        '''
        
        news = self.browser.evaluate(js_code)
        if news:
            for item in news[:40]:
                risks = self.analyze_risk(item['title'])
                if risks:
                    code, name = self.extract_stock_info(item['title'])
                    all_news.append({
                        'title': item['title'],
                        'url': item['url'],
                        'source': self.name,
                        'stock_code': code,
                        'stock_name': name,
                        'risks': risks,
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return all_news


class TencentFinanceSource(NewsSource):
    """腾讯财经 - 港股新闻"""
    
    name = "腾讯财经"
    base_url = "https://finnce.qq.com/hkstock/"
    
    def fetch(self) -> List[Dict]:
        """爬取新闻"""
        all_news = []
        
        print(f"\n📰 爬取 {self.name}...")
        self.browser.navigate(self.base_url)
        time.sleep(3)
        self.browser.wait_for_load(timeout=10)
        
        js_code = '''
        () => {
            const links = Array.from(document.querySelectorAll('a'));
            return links
                .filter(a => a.href && (a.href.includes('stock') || a.href.includes('hk')))
                .map(a => ({
                    title: a.innerText.trim(),
                    url: a.href
                }))
                .filter(item => item.title.length > 10 && item.title.length < 100);
        }
        '''
        
        news = self.browser.evaluate(js_code)
        if news:
            for item in news[:40]:
                risks = self.analyze_risk(item['title'])
                if risks:
                    code, name = self.extract_stock_info(item['title'])
                    all_news.append({
                        'title': item['title'],
                        'url': item['url'],
                        'source': self.name,
                        'stock_code': code,
                        'stock_name': name,
                        'risks': risks,
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return all_news


def deduplicate_news(news_list: List[Dict]) -> List[Dict]:
    """去重：基于标题"""
    seen_titles = set()
    unique_news = []
    
    for news in news_list:
        if news['title'] not in seen_titles:
            seen_titles.add(news['title'])
            unique_news.append(news)
    
    print(f"\n📊 去重：{len(news_list)} → {len(unique_news)} 条")
    return unique_news


def save_to_json(news_list: List[Dict], filename: str = None):
    """保存为 JSON 文件"""
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'multi_source_news_{timestamp}.json'
    
    output_path = OUTPUT_DIR / filename
    
    data = {
        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sources': list(set(n['source'] for n in news_list)),
        'total_count': len(news_list),
        'news': news_list
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存到：{output_path}")
    return output_path


def main():
    print("=" * 60)
    print("🌐 多数据源港股风险新闻爬取")
    print("=" * 60)
    
    # 连接浏览器
    browser = CDPBrowser()
    if not browser.connect():
        print("❌ 无法连接浏览器，请确保 Chrome 已启动 CDP 模式（端口 18800）")
        return
    
    try:
        all_news = []
        
        # 东方财富网（爬取 5 页）
        east_money = EastMoneySource(browser)
        news = east_money.fetch(pages=5)
        print(f"  东方财富网：{len(news)} 条风险新闻")
        all_news.extend(news)
        
        # 阿思达克财经网
        aastocks = AastocksSource(browser)
        news = aastocks.fetch()
        print(f"  阿思达克：{len(news)} 条风险新闻")
        all_news.extend(news)
        
        # 新浪财经
        sina = SinaFinanceSource(browser)
        news = sina.fetch()
        print(f"  新浪财经：{len(news)} 条风险新闻")
        all_news.extend(news)
        
        # 腾讯财经
        tencent = TencentFinanceSource(browser)
        news = tencent.fetch()
        print(f"  腾讯财经：{len(news)} 条风险新闻")
        all_news.extend(news)
        
        # 去重
        all_news = deduplicate_news(all_news)
        
        # 保存
        if all_news:
            save_to_json(all_news)
            
            # 打印摘要
            print("\n" + "=" * 60)
            print("📊 风险新闻摘要")
            print("=" * 60)
            
            risk_types = {}
            for news in all_news:
                for risk in news['risks']:
                    cat = risk['category']
                    risk_types[cat] = risk_types.get(cat, 0) + 1
            
            for cat, count in sorted(risk_types.items(), key=lambda x: -x[1]):
                print(f"  {cat}: {count} 条")
            
            print(f"\n✅ 共发现 {len(all_news)} 条风险新闻")
        else:
            print("\n⚠️ 未发现风险新闻")
    
    finally:
        browser.close()
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
