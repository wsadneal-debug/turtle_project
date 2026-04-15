#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单爬取器 - 使用 subprocess 调用 browser 工具
"""

import subprocess
import json
import re
from datetime import datetime
from pathlib import Path

# 风险关键词
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
    """获取风险等级"""
    if category in ['监管处罚', '债务违约', '停牌风险']:
        return 'HIGH'
    return 'MEDIUM'

def analyze_risk(title):
    """分析风险"""
    risks = []
    for category, keywords in RISK_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title:
                risks.append({
                    'category': category,
                    'keyword': keyword,
                    'level': get_risk_level(category)
                })
    return risks

def extract_stock_info(title):
    """提取股票信息"""
    # 匹配港股代码
    code_match = re.search(r'([(\[]?0\d{4,5}[)\]]?(?:\.HK)?)', title)
    code = code_match.group(0).replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('.HK', '') if code_match else ''
    
    # 匹配公司名称
    name_match = re.search(r'^([^\(（]+)', title)
    name = name_match.group(0).strip() if name_match else ''
    
    return code, name

def crawl_eastmoney(page=1):
    """爬取东方财富网"""
    url = f'https://finance.eastmoney.com/a/cgsxw_{page}.html' if page > 1 else 'https://finance.eastmoney.com/a/cgsxw.html'
    
    # 导航
    subprocess.run(['browser', 'action=navigate', f'url={url}'], capture_output=True)
    
    # 提取新闻
    js = '''() => {
        const links = Array.from(document.querySelectorAll('a'));
        return links
            .map(a => ({t: a.innerText.trim(), h: a.href}))
            .filter(x => x.t.length > 15 && x.t.length < 100 && 
                       (x.t.includes('公告') || x.t.includes('调查') || x.t.includes('诉讼') ||
                        x.t.includes('处罚') || x.t.includes('违约') || x.t.includes('审计') ||
                        x.t.includes('辞职') || x.t.includes('冻结') || x.t.includes('重组')));
    }'''
    
    result = subprocess.run(
        ['browser', f'action=act', 'kind=evaluate', f'fn={js}'],
        capture_output=True, text=True
    )
    
    # 解析结果
    try:
        output = result.stdout
        if '"result":' in output:
            json_str = output.split('"result":')[-1].strip()
            # 找到 JSON 数组
            start = json_str.find('[')
            if start >= 0:
                end = json_str.rfind(']') + 1
                if end > start:
                    news_list = json.loads(json_str[start:end])
                    return news_list
    except Exception as e:
        print(f"解析错误：{e}")
    
    return []

def main():
    print("=" * 60)
    print("📰 港股风险新闻爬取 - 测试版")
    print("=" * 60)
    
    all_news = []
    
    # 爬取 3 页
    for page in range(1, 4):
        print(f"\n爬取第 {page} 页...")
        news_list = crawl_eastmoney(page)
        
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
    
    print(f"\n共发现 {len(all_news)} 条风险新闻")
    
    # 保存
    if all_news:
        output_file = OUTPUT_DIR / f'test_news_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total': len(all_news),
                'news': all_news
            }, f, ensure_ascii=False, indent=2)
        print(f"已保存：{output_file}")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
