#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龟龟项目股票池同步
从龟龟项目准入池读取股票列表，替代独立维护的stock_pool
"""

import sqlite3
import json
from pathlib import Path

TURTLE_A_DB = Path('/home/yxy/turtle_project/A_stock_data/databases/a_financial.db')
TURTLE_HK_DB = Path('/home/yxy/turtle_project/A_stock_data/databases/hk_financial.db')
RISK_DB = Path('/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db')

def sync_turtle_stock_pool():
    """从龟龟项目同步股票池"""
    conn_risk = sqlite3.connect(RISK_DB)
    cursor_risk = conn_risk.cursor()
    
    # 清空现有stock_pool
    cursor_risk.execute('DELETE FROM stock_pool')
    cursor_risk.execute('DELETE FROM stock_aliases')
    
    # 1. 同步A股准入池
    conn_a = sqlite3.connect(TURTLE_A_DB)
    cursor_a = conn_a.cursor()
    cursor_a.execute('SELECT ts_code, name FROM a_stock_basic WHERE is_active = 1')
    a_stocks = cursor_a.fetchall()
    
    for ts_code, name in a_stocks:
        # ts_code格式: 000001.SZ
        code = ts_code
        cursor_risk.execute('''
            INSERT INTO stock_pool (stock_code, stock_name, market)
            VALUES (?, ?, 'A')
        ''', (code, name))
        
        # 创建别名
        short_name = name
        for suffix in ['股份有限公司', '有限公司', '股份', '集团', '控股', '科技', '电子', '地产', '金融']:
            if name.endswith(suffix):
                short_name = name[:-len(suffix)]
                break
        
        cursor_risk.execute('INSERT INTO stock_aliases (stock_code, alias_name, alias_type, market) VALUES (?, ?, ?, ?)',
                           (code, name, 'full', 'A'))
        if short_name != name:
            cursor_risk.execute('INSERT INTO stock_aliases (stock_code, alias_name, alias_type, market) VALUES (?, ?, ?, ?)',
                               (code, short_name, 'short', 'A'))
    
    conn_a.close()
    print(f"✅ A股准入池: {len(a_stocks)} 只")
    
    # 2. 同步港股通准入池
    conn_hk = sqlite3.connect(TURTLE_HK_DB)
    cursor_hk = conn_hk.cursor()
    cursor_hk.execute('SELECT ts_code, name FROM hk_connect_securities')
    hk_stocks = cursor_hk.fetchall()
    
    for ts_code, name in hk_stocks:
        # ts_code格式: 00700.HK
        code = ts_code
        cursor_risk.execute('''
            INSERT INTO stock_pool (stock_code, stock_name, market)
            VALUES (?, ?, 'HK')
        ''', (code, name))
        
        # 创建别名
        short_name = name
        for suffix in ['控股', '集团', '股份', '有限公司', '-W', '-S']:
            if name.endswith(suffix):
                short_name = name[:-len(suffix)]
                break
        
        cursor_risk.execute('INSERT INTO stock_aliases (stock_code, alias_name, alias_type, market) VALUES (?, ?, ?, ?)',
                           (code, name, 'full', 'HK'))
        if short_name != name and short_name:
            cursor_risk.execute('INSERT INTO stock_aliases (stock_code, alias_name, alias_type, market) VALUES (?, ?, ?, ?)',
                               (code, short_name, 'short', 'HK'))
    
    conn_hk.close()
    print(f"✅ 港股通准入池: {len(hk_stocks)} 只")
    
    conn_risk.commit()
    conn_risk.close()
    
    print(f"\n✅ 股票池同步完成: A股 {len(a_stocks)} + 港股通 {len(hk_stocks)} = {len(a_stocks) + len(hk_stocks)} 只")
    
    return len(a_stocks) + len(hk_stocks)

if __name__ == "__main__":
    sync_turtle_stock_pool()