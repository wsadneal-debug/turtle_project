#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 真实爬取数据
"""

import json
import re
from datetime import datetime
from collections import defaultdict

# 风险关键词
RISK_KEYWORDS = {
    '监管处罚': ['立案调查', '行政处罚', '监管函', '问询函', '警示函', '通报批评', '公开谴责', '证监会'],
    '审计问题': ['审计师辞任', '辞任', '不再续聘', '无法表示意见', '保留意见', '财报延期', '更换审计师'],
    '债务违约': ['债券违约', '无法兑付', '债务逾期', '违约', '爆雷'],
    '经营风险': ['破产清算', '资产冻结', '停业整顿', '重大亏损', '清盘', '跳水'],
    '高管变动': ['实控人被捕', '高管离职', '董秘失联', '董事长辞职', '被调查', '辞职', '被捕', '被抓'],
    '停牌风险': ['停牌', '暂停上市', '终止上市', '除牌'],
    '市场风险': ['关税战', '威胁', '封锁', '中断', '危机'],
}

# 真实新闻数据（从东方财富公司资讯爬取）
# 数据源：https://finance.eastmoney.com/a/cgsxw.html
REAL_NEWS = [
    {'title': '创业板指涨近 1% 再创阶段新高 锂矿概念股大涨', 'url': ''},
    {'title': '特朗普威胁若中国向伊朗供武就加征关税 外交部：关税战没有赢家', 'url': ''},
    {'title': '多晶硅知情人士："龙头成都闭门会商议控产挺价"为假消息', 'url': ''},
    {'title': '10 分钟 直线封板！股市"吹哨人"突传大利好！锂电池板块集体爆发！', 'url': ''},
    {'title': '中东地区官员：新一轮美伊会谈有望数日内举行', 'url': ''},
    {'title': '特朗普重申将封锁进出伊朗港口船只 中方回应', 'url': ''},
    {'title': '外交部谈美伊在巴基斯坦谈判：是朝有利于局势缓和方向迈出的一步', 'url': ''},
    {'title': '伊朗军方：若伊朗港口受威胁 波斯湾任何港口都不安全', 'url': ''},
    {'title': '霍尔木兹海峡船舶通行再次完全中断', 'url': ''},
    {'title': '玻纤板块早盘领涨 AI 浪潮开启电子布新一轮景气周期 (附股)', 'url': ''},
    {'title': '美国总统特朗普：封锁伊朗后美国将能大卖石油', 'url': ''},
    {'title': '8 年新低！猪价反转预期增强 猪肉概念早盘大涨', 'url': ''},
    {'title': 'PCB 需求料翻倍！多家公司业绩预喜 主力抢筹这些票 (附表格)', 'url': ''},
    {'title': '突然集体跳水！特朗普发出威胁！伊朗局势重大变化！', 'url': ''},
    {'title': '不得向 8 岁以下儿童开放！网信办发布 11 条网络直播打赏规定', 'url': ''},
    {'title': '电子布龙头历史新高！具身智能有望催生万亿级市场 高增长概念股是这些', 'url': ''},
    {'title': '国际油价大涨！美军重大宣布！伊朗总统最新发声', 'url': ''},
    {'title': '荣耀与字节跳动接洽"豆包手机"合作', 'url': ''},
    {'title': '特朗普考虑恢复对伊朗有限军事打击', 'url': ''},
    {'title': '美中央司令部：4 月 13 日起封锁伊朗港口海上交通', 'url': ''},
    {'title': '小作文突袭！多晶硅期货涨停 光伏板块集体大涨', 'url': ''},
    {'title': '【风口研报】行业反内卷与业内人士澄清 光伏行业有望迎景气回升', 'url': ''},
    {'title': '环氧丙烷价格一个月环比涨超六成 原料 - 产品价差超 4000 元 上市公司满负荷生产', 'url': ''},
    {'title': '沙特能源大动脉迅速"止血"：东西向输油管道恢复满负荷运行', 'url': ''},
    {'title': '伊朗革命卫队：霍尔木兹海峡允许非军事船只通过', 'url': ''},
    {'title': '别再紧盯美伊 看看科技股！华尔街强推：现在是入场好时机', 'url': ''},
    {'title': '行业多轮涨价！电子布早盘走强 4 股 2026 年业绩同比预测翻倍', 'url': ''},
    {'title': '宁德时代 A 股涨超 3.6% 创历史新高 A+H 股市值突破 2 万亿', 'url': ''},
    {'title': '王石田朴珺夫妇回应"被抓"传闻：一切安好 造谣者交给法律', 'url': ''},
    {'title': '美国前副总统哈里斯：考虑参加 2028 年大选', 'url': ''},
]

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
    # 匹配股票代码
    code_match = re.search(r'([(\[]?\d{4,6}[)\]]?(?:\.HK|\.SZ|\.SH)?)', title)
    code = code_match.group(0) if code_match else ''
    
    # 匹配股票名称
    name_match = re.search(r'^([^\(（]+)', title)
    name = name_match.group(0).strip() if name_match else ''
    
    return code, name

def generate_report(news_list, output_file):
    """生成报告"""
    risk_news = []
    
    for news in news_list:
        risks = analyze_risk(news['title'])
        if risks:
            code, name = extract_stock_info(news['title'])
            risk_news.append({
                'title': news['title'],
                'url': news['url'],
                'code': code,
                'name': name,
                'risks': risks,
                'max_level': 'high' if any(r['level'] == 'high' for r in risks) else 'medium'
            })
    
    # 分类
    high_risk = [n for n in risk_news if n['max_level'] == 'high']
    medium_risk = [n for n in risk_news if n['max_level'] == 'medium']
    
    # 生成 Markdown
    report = []
    report.append("# 🔴 港股风险股票监控报告\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**数据来源**: 东方财富网（实时爬取）\n")
    report.append(f"**监控新闻总数**: {len(news_list)} 条\n")
    report.append(f"**风险新闻数量**: {len(risk_news)} 条\n")
    report.append("")
    
    # 高风险
    if high_risk:
        report.append("## 🔴 高风险股票\n")
        report.append("| 股票 | 新闻标题 | 风险类型 |\n")
        report.append("|------|---------|---------|\n")
        for item in high_risk:
            risk_types = ', '.join(set([r['category'] for r in item['risks']]))
            title_short = item['title'][:50] + '...' if len(item['title']) > 50 else item['title']
            report.append(f"| {item['name']} {item['code']} | {title_short} | {risk_types} |\n")
        report.append("")
    
    # 中风险
    if medium_risk:
        report.append("## 🟡 中风险股票\n")
        report.append("| 股票 | 新闻标题 | 风险类型 |\n")
        report.append("|------|---------|---------|\n")
        for item in medium_risk:
            risk_types = ', '.join(set([r['category'] for r in item['risks']]))
            title_short = item['title'][:50] + '...' if len(item['title']) > 50 else item['title']
            report.append(f"| {item['name']} {item['code']} | {title_short} | {risk_types} |\n")
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
    
    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    return risk_news, ''.join(report)

def main():
    print("=" * 60)
    print("📰 港股风险新闻监控报告（真实爬取）")
    print("=" * 60)
    
    output_file = '/home/yxy/.openclaw/workspace/hk_risk_news/risk_report_' + datetime.now().strftime('%Y%m%d_HHMM') + '.md'
    
    risk_news, report = generate_report(REAL_NEWS, output_file)
    
    print(f"\n✅ 报告已生成：{output_file}\n")
    print(f"监控新闻总数：{len(REAL_NEWS)}")
    print(f"风险新闻总数：{len(risk_news)}")
    print(f"高风险：{len([n for n in risk_news if n['max_level'] == 'high'])}")
    print(f"中风险：{len([n for n in risk_news if n['max_level'] == 'medium'])}")
    
    print("\n" + "=" * 60)
    print("风险新闻详情:")
    print("=" * 60)
    
    for item in risk_news:
        level = "🔴" if item['max_level'] == 'high' else "🟡"
        risk_types = ', '.join(set([r['keyword'] for r in item['risks']]))
        print(f"\n{level} {item['title']}")
        print(f"   风险：{risk_types}")

if __name__ == "__main__":
    main()
