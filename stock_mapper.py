#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票映射器 V2 - 支持港股 + A股
建立 公司名称 → 股票代码 的映射关系
用于将新闻标题中的公司名称映射到具体股票代码
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime

DB_PATH = Path('/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db')

def create_stock_aliases():
    """创建股票名称别名表（用于模糊匹配）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建别名表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code VARCHAR(20) NOT NULL,
            alias_name VARCHAR(100) NOT NULL,
            alias_type VARCHAR(20) DEFAULT 'short',
            market VARCHAR(10) DEFAULT 'HK',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 获取股票池
    cursor.execute('SELECT stock_code, stock_name, market FROM stock_pool')
    stocks = cursor.fetchall()
    
    for code, name, market in stocks:
        aliases = []
        
        # 1. 全名
        aliases.append((code, name, 'full', market))
        
        # 2. 简称（去掉常见后缀）
        short_name = name
        suffixes_hk = ['控股', '集团', '股份', '有限公司', '科技', '电子', '地产', '金融', '银行', '保险', '医药', '汽车', '教育', '娱乐', '零售', '实业', '投资']
        suffixes_a = ['股份有限公司', '有限公司', '股份', '集团', '控股', '科技', '电子', '电器', '机械', '设备', '材料', '能源', '电力', '通信', '信息', '软件', '网络', '传媒', '文化', '教育', '医疗', '医药', '生物', '制药', '化工', '建筑', '工程', '地产', '房地产', '置业', '商业', '贸易', '零售', '消费', '食品', '饮料', '白酒', '酒', '啤酒', '烟草', '服装', '纺织', '造纸', '印刷', '包装', '物流', '运输', '航空', '铁路', '港口', '公路', '交通', '汽车', '零部件', '轮胎', '橡胶', '塑料', '玻璃', '陶瓷', '水泥', '钢铁', '有色', '煤炭', '石油', '天然气', '环保', '水务', '燃气', '供热', '园林', '农业', '林业', '渔业', '牧业', '矿业', '资源', '金属', '合金', '复合材料']
        
        suffixes = suffixes_hk + suffixes_a
        for suffix in suffixes:
            if name.endswith(suffix):
                short_name = name[:-len(suffix)]
                break
        if short_name != name and short_name:
            aliases.append((code, short_name, 'short', market))
        
        # 3. 核心简称（去掉-W、-S等后缀）
        core_name = short_name
        for suffix in ['-W', '-S', '控股', '集团', '公司', '有限']:
            if short_name.endswith(suffix):
                core_name = short_name[:-len(suffix)]
                break
        if core_name != short_name and core_name:
            aliases.append((code, core_name, 'core', market))
        
        # 插入别名
        for alias_code, alias_name, alias_type, alias_market in aliases:
            cursor.execute('''
                INSERT OR IGNORE INTO stock_aliases (stock_code, alias_name, alias_type, market)
                VALUES (?, ?, ?, ?)
            ''', (alias_code, alias_name, alias_type, alias_market))
    
    conn.commit()
    conn.close()

def map_company_to_stock(company_name):
    """
    将公司名称映射到股票代码
    返回：(stock_code, stock_name, confidence)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 直接匹配别名表
    cursor.execute('''
        SELECT sa.stock_code, sp.stock_name, sa.alias_type
        FROM stock_aliases sa
        JOIN stock_pool sp ON sa.stock_code = sp.stock_code
        WHERE sa.alias_name = ?
        ORDER BY 
            CASE sa.alias_type 
                WHEN 'full' THEN 1 
                WHEN 'core' THEN 2 
                WHEN 'short' THEN 3 
                ELSE 4 
            END
        LIMIT 1
    ''', (company_name,))
    
    result = cursor.fetchone()
    if result:
        conn.close()
        return result[0], result[1], 'high'
    
    # 2. 模糊匹配（包含关系）
    cursor.execute('''
        SELECT sa.stock_code, sp.stock_name, sa.alias_name, sa.alias_type
        FROM stock_aliases sa
        JOIN stock_pool sp ON sa.stock_code = sp.stock_code
        WHERE ? LIKE '%' || sa.alias_name || '%' OR sa.alias_name LIKE '%' || ? || '%'
        ORDER BY LENGTH(sa.alias_name) DESC
        LIMIT 5
    ''', (company_name, company_name))
    
    results = cursor.fetchall()
    if results:
        best = results[0]
        conn.close()
        return best[0], best[1], 'medium'
    
    conn.close()
    return None, None, 'none'

def extract_and_map_stock_from_news(title):
    """
    从新闻标题中提取并映射股票信息
    支持：港股（.HK）、A股（.SZ/.SH）
    返回：(stock_code, stock_name, confidence)
    """
    # 1. 匹配港股代码：5位数字
    hk_match = re.search(r'([\\(\\[]?\\d{5}[\\)\\]]?(?:\\.HK)?)', title)
    if hk_match:
        raw_code = hk_match.group(0)
        code = re.sub(r'[()\\[\\]]', '', raw_code)
        if not code.endswith('.HK'):
            code = code + '.HK'
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT stock_name FROM stock_pool WHERE stock_code = ?', (code,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return code, result[0], 'high'
        else:
            return code, '未知', 'medium'
    
    # 2. 匹配A股代码：6位数字
    a_match = re.search(r'([\\(\\[]?\\d{6}[\\)\\]]?)', title)
    if a_match:
        raw_code = a_match.group(0)
        code_num = re.sub(r'[()\\[\\]]', '', raw_code)
        # 判断市场
        if code_num.startswith('00') or code_num.startswith('30') or code_num.startswith('002'):
            code = code_num + '.SZ'
        elif code_num.startswith('6'):
            code = code_num + '.SH'
        else:
            code = code_num
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT stock_name FROM stock_pool WHERE stock_code = ?', (code,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return code, result[0], 'high'
        else:
            return code, '未知', 'medium'
    
    # 3. 匹配公司名称
    patterns = [
        r'^([^\(（\[\]【]+)',  # 开头的公司名
        r'([^\s]+(?:控股|集团|股份|科技|电子|地产|金融|银行|保险|有限公司))',  # 带后缀的公司名
        r'《([^》]+)》',  # 书名号内的公司名
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            company_name = match.group(1).strip()
            # 过滤掉太短或太长的名称
            if len(company_name) < 2 or len(company_name) > 20:
                continue
            # 映射到股票代码
            stock_code, stock_name, confidence = map_company_to_stock(company_name)
            if confidence != 'none':
                return stock_code, stock_name, confidence
    
    return None, None, 'none'

def import_stock_list(stocks, market='HK'):
    """
    导入股票列表到数据库
    stocks: [{'code': '00700.HK', 'name': '腾讯控股', 'industry': '互联网'}, ...]
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for stock in stocks:
        code = stock.get('code', '')
        name = stock.get('name', '')
        industry = stock.get('industry', '')
        
        if code and name:
            cursor.execute('''
                INSERT OR IGNORE INTO stock_pool (stock_code, stock_name, industry, market)
                VALUES (?, ?, ?, ?)
            ''', (code, name, industry, market))
    
    conn.commit()
    conn.close()

def test_mapper():
    """测试映射器"""
    test_titles = [
        '腾讯控股遭证监会立案调查',
        '碧桂园未能按期偿还债券利息',
        '美团-W更换审计师',
        '小米集团股价暴跌20%',
        '中国恒大被申请清盘',
        '阿里巴巴高管离职',
        '贵州茅台股价创新高',
        '比亚迪股份涨停',
        '宁德时代被监管问询',
        '中国平安董事长辞职',
        '招商银行年报披露',
        '000001平安银行公告',
        '600519贵州茅台涨5%',
        '腾讯(00700)发布财报',
    ]
    
    print("=" * 60)
    print("测试股票映射器 (港股 + A股)")
    print("=" * 60)
    
    for title in test_titles:
        code, name, confidence = extract_and_map_stock_from_news(title)
        print(f"\n新闻: {title}")
        print(f"映射: {code} {name} (置信度: {confidence})")

if __name__ == "__main__":
    # 检查 stock_pool 是否有数据
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM stock_pool')
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        print("⚠️ stock_pool 表为空，正在导入示例数据...")
        
        # 示例港股
        hk_stocks = [
            {'code': '00700.HK', 'name': '腾讯控股', 'industry': '互联网'},
            {'code': '03690.HK', 'name': '美团-W', 'industry': '互联网'},
            {'code': '01810.HK', 'name': '小米集团-W', 'industry': '电子'},
            {'code': '02007.HK', 'name': '碧桂园', 'industry': '地产'},
            {'code': '03330.HK', 'name': '中国恒大', 'industry': '地产'},
            {'code': '09988.HK', 'name': '阿里巴巴-W', 'industry': '互联网'},
            {'code': '00005.HK', 'name': '汇丰控股', 'industry': '银行'},
            {'code': '01398.HK', 'name': '工商银行', 'industry': '银行'},
            {'code': '00388.HK', 'name': '港交所', 'industry': '金融'},
            {'code': '02318.HK', 'name': '平安好医生', 'industry': '医疗'},
        ]
        
        # 示例A股（热门股票）
        a_stocks = [
            {'code': '000001.SZ', 'name': '平安银行', 'industry': '银行'},
            {'code': '000002.SZ', 'name': '万科A', 'industry': '地产'},
            {'code': '000333.SZ', 'name': '美的集团', 'industry': '家电'},
            {'code': '000651.SZ', 'name': '格力电器', 'industry': '家电'},
            {'code': '000858.SZ', 'name': '五粮液', 'industry': '白酒'},
            {'code': '002415.SZ', 'name': '海康威视', 'industry': '安防'},
            {'code': '300750.SZ', 'name': '宁德时代', 'industry': '电池'},
            {'code': '600000.SH', 'name': '浦发银行', 'industry': '银行'},
            {'code': '600036.SH', 'name': '招商银行', 'industry': '银行'},
            {'code': '600519.SH', 'name': '贵州茅台', 'industry': '白酒'},
            {'code': '600887.SH', 'name': '伊利股份', 'industry': '乳业'},
            {'code': '601318.SH', 'name': '中国平安', 'industry': '保险'},
            {'code': '601398.SH', 'name': '工商银行', 'industry': '银行'},
            {'code': '601888.SH', 'name': '中国中免', 'industry': '零售'},
            {'code': '002594.SZ', 'name': '比亚迪', 'industry': '汽车'},
        ]
        
        import_stock_list(hk_stocks, 'HK')
        import_stock_list(a_stocks, 'A')
        print(f"✅ 已导入港股 {len(hk_stocks)} 只，A股 {len(a_stocks)} 只")
        
        # 创建别名
        create_stock_aliases()
        print("✅ 已创建股票名称别名表")
    
    # 运行测试
    test_mapper()

def simple_extract_company_from_title(title):
    """简单提取标题开头的公司名"""
    # 匹配开头，遇到常见分隔符停止
    match = re.match(r'^([^：:，,\s实发布报道]+)', title)
    if match:
        name = match.group(1)
        if len(name) >= 2 and len(name) <= 20:
            return name
    return None
