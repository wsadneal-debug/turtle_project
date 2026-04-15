#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 数据库管理模块

功能:
- 初始化数据库和表结构
- 插入风险记录
- 查询和统计
- 导出报表
"""

import sqlite3
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

DB_PATH = Path('/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db')
BACKUP_DIR = Path('/home/yxy/.openclaw/workspace/hk_risk_news/backups')


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库，创建表和索引"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 先删除旧表重建（用于升级）
    cursor.execute('DROP TABLE IF EXISTS risk_records')
    cursor.execute('DROP TABLE IF EXISTS risk_statistics')
    cursor.execute('DROP TABLE IF EXISTS stock_pool')
    cursor.execute('DROP TABLE IF EXISTS holdings')
    
    # 创建风险记录表
    cursor.execute('''
        CREATE TABLE risk_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date DATE NOT NULL,
            stock_code VARCHAR(20) NOT NULL,
            stock_name VARCHAR(100) NOT NULL,
            stock_name_en VARCHAR(100),
            risk_type VARCHAR(50) NOT NULL,
            risk_level VARCHAR(10) NOT NULL,
            news_title VARCHAR(500) NOT NULL,
            news_url VARCHAR(500),
            news_source VARCHAR(50),
            publish_time DATETIME,
            crawl_time DATETIME NOT NULL,
            is_verified BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建风险统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS risk_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date DATE NOT NULL UNIQUE,
            total_news INTEGER DEFAULT 0,
            risk_news_count INTEGER DEFAULT 0,
            high_risk_count INTEGER DEFAULT 0,
            medium_risk_count INTEGER DEFAULT 0,
            regulatory_count INTEGER DEFAULT 0,
            audit_count INTEGER DEFAULT 0,
            debt_count INTEGER DEFAULT 0,
            business_count INTEGER DEFAULT 0,
            executive_count INTEGER DEFAULT 0,
            suspension_count INTEGER DEFAULT 0,
            market_count INTEGER DEFAULT 0,
            crawl_pages INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建股票池表
    cursor.execute('''
        CREATE TABLE stock_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code VARCHAR(20) NOT NULL UNIQUE,
            stock_name VARCHAR(100) NOT NULL,
            industry VARCHAR(50),
            market_cap VARCHAR(20),
            is_monitored BOOLEAN DEFAULT 1,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建持仓记录表
    cursor.execute('''
        CREATE TABLE holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code VARCHAR(20) NOT NULL,
            stock_name VARCHAR(100) NOT NULL,
            action VARCHAR(10) NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            amount REAL NOT NULL,
            trade_time DATETIME NOT NULL,
            account_tail VARCHAR(10),
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建持仓表索引
    cursor.execute('CREATE INDEX idx_holdings_code ON holdings(stock_code)')
    cursor.execute('CREATE INDEX idx_holdings_time ON holdings(trade_time)')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_record_date ON risk_records(record_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON risk_records(stock_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk_type ON risk_records(risk_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk_level ON risk_records(risk_level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawl_time ON risk_records(crawl_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stat_date ON risk_statistics(stat_date)')
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成：{DB_PATH}")


def insert_risk_record(
    record_date: str,
    stock_code: str,
    stock_name: str,
    risk_type: str,
    risk_level: str,
    news_title: str,
    news_url: str = '',
    news_source: str = '',
    publish_time: Optional[str] = None,
    crawl_time: Optional[str] = None,
    stock_name_en: str = '',
    notes: str = ''
) -> int:
    """插入单条风险记录"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if crawl_time is None:
        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO risk_records (
            record_date, stock_code, stock_name, stock_name_en,
            risk_type, risk_level, news_title, news_url, news_source,
            publish_time, crawl_time, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        record_date, stock_code, stock_name, stock_name_en,
        risk_type, risk_level, news_title, news_url, news_source,
        publish_time, crawl_time, notes
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def insert_risk_records_from_json(json_file: str, record_date: str = None):
    """从 JSON 文件批量插入风险记录"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if record_date is None:
        record_date = data.get('record_date', datetime.now().strftime('%Y-%m-%d'))
    
    crawl_time = data.get('crawl_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    news_source = data.get('news_source', '东方财富网')
    
    inserted_count = 0
    
    # 插入高风险股票
    for stock in data.get('high_risk_stocks', []):
        record_id = insert_risk_record(
            record_date=record_date,
            stock_code=stock.get('stock_code', ''),
            stock_name=stock.get('stock_name', ''),
            risk_type=stock.get('risk_type', ''),
            risk_level='HIGH',
            news_title=stock.get('news_title', ''),
            news_url=stock.get('news_url', ''),
            news_source=news_source,
            crawl_time=crawl_time
        )
        inserted_count += 1
        print(f"  ✅ 插入高风险记录 ID={record_id}: {stock.get('stock_name')} ({stock.get('stock_code')})")
    
    # 插入中风险股票
    for stock in data.get('medium_risk_stocks', []):
        record_id = insert_risk_record(
            record_date=record_date,
            stock_code=stock.get('stock_code', ''),
            stock_name=stock.get('stock_name', ''),
            risk_type=stock.get('risk_type', ''),
            risk_level='MEDIUM',
            news_title=stock.get('news_title', ''),
            news_url=stock.get('news_url', ''),
            news_source=news_source,
            crawl_time=crawl_time
        )
        inserted_count += 1
        print(f"  ✅ 插入中风险记录 ID={record_id}: {stock.get('stock_name')} ({stock.get('stock_code')})")
    
    # 插入统计数据
    insert_statistics(data, record_date)
    
    print(f"\n✅ 共插入 {inserted_count} 条风险记录")
    return inserted_count


def insert_statistics(data: Dict, stat_date: str):
    """插入统计数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = data.get('statistics', {})
    
    cursor.execute('''
        INSERT OR REPLACE INTO risk_statistics (
            stat_date, total_news, risk_news_count, high_risk_count,
            medium_risk_count, regulatory_count, audit_count, debt_count,
            business_count, executive_count, suspension_count, market_count,
            crawl_pages
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        stat_date,
        stats.get('total_news', 0),
        stats.get('risk_news_count', 0),
        stats.get('high_risk_count', 0),
        stats.get('medium_risk_count', 0),
        stats.get('regulatory_count', 0),
        stats.get('audit_count', 0),
        stats.get('debt_count', 0),
        stats.get('business_count', 0),
        stats.get('executive_count', 0),
        stats.get('suspension_count', 0),
        stats.get('market_count', 0),
        stats.get('crawl_pages', 0)
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ 插入统计数据：{stat_date}")


def query_by_date(date: str) -> List[Dict]:
    """按日期查询风险记录"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT stock_code, stock_name, risk_type, risk_level, news_title, news_url
        FROM risk_records
        WHERE record_date = ?
        ORDER BY 
            CASE risk_level WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 END,
            risk_type
    ''', (date,))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def query_by_stock(stock_code: str) -> List[Dict]:
    """按股票代码查询历史风险记录"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT record_date, risk_type, risk_level, news_title, news_url
        FROM risk_records
        WHERE stock_code = ?
        ORDER BY record_date DESC
    ''', (stock_code,))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def get_latest_statistics() -> Optional[Dict]:
    """获取最新统计数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM risk_statistics
        ORDER BY stat_date DESC
        LIMIT 1
    ''')
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def export_to_csv(output_file: str, date: str = None):
    """导出数据为 CSV 格式"""
    import csv
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if date:
        cursor.execute('''
            SELECT record_date, stock_code, stock_name, risk_type, risk_level, news_title, news_url
            FROM risk_records
            WHERE record_date = ?
            ORDER BY risk_level, risk_type
        ''', (date,))
    else:
        cursor.execute('''
            SELECT record_date, stock_code, stock_name, risk_type, risk_level, news_title, news_url
            FROM risk_records
            ORDER BY record_date DESC, risk_level, risk_type
        ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['日期', '股票代码', '股票名称', '风险类型', '风险等级', '新闻标题', '新闻链接'])
        writer.writerows(rows)
    
    print(f"✅ 导出 {len(rows)} 条记录到 {output_file}")


def add_holding(stock_code, stock_name, action, price, quantity, trade_time, account_tail='', notes=''):
    """添加持仓记录"""
    conn = get_connection()
    cursor = conn.cursor()
    
    amount = price * quantity
    
    cursor.execute('''
        INSERT INTO holdings (
            stock_code, stock_name, action, price, quantity, amount,
            trade_time, account_tail, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (stock_code, stock_name, action, price, quantity, amount, trade_time, account_tail, notes))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ 持仓记录已添加 ID={record_id}")
    print(f"   股票：{stock_name} ({stock_code})")
    print(f"   方向：{action}")
    print(f"   价格：{price} 元 × {quantity} 股 = {amount:.2f} 元")
    print(f"   时间：{trade_time}")
    
    return record_id


def query_holdings(stock_code=None):
    """查询持仓记录"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if stock_code:
        cursor.execute('''
            SELECT * FROM holdings
            WHERE stock_code = ?
            ORDER BY trade_time DESC
        ''', (stock_code,))
    else:
        cursor.execute('SELECT * FROM holdings ORDER BY trade_time DESC')
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def backup_database():
    """备份数据库"""
    import shutil
    
    BACKUP_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = BACKUP_DIR / f'risk_stocks_backup_{timestamp}.db'
    
    shutil.copy(DB_PATH, backup_file)
    print(f"✅ 数据库已备份：{backup_file}")
    
    # 清理 30 天前的备份
    import time
    for f in BACKUP_DIR.glob('risk_stocks_backup_*.db'):
        if time.time() - f.stat().st_mtime > 30 * 24 * 3600:
            f.unlink()
            print(f"  🗑️ 清理旧备份：{f}")


def main():
    parser = argparse.ArgumentParser(description='港股风险新闻监控 - 数据库管理工具')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--insert', action='store_true', help='插入风险记录')
    parser.add_argument('--data', type=str, help='JSON 数据文件路径')
    parser.add_argument('--date', type=str, help='记录日期 (YYYY-MM-DD)')
    parser.add_argument('--query', action='store_true', help='查询记录')
    parser.add_argument('--stock', type=str, help='股票代码')
    parser.add_argument('--export', action='store_true', help='导出 CSV')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--backup', action='store_true', help='备份数据库')
    parser.add_argument('--add-holding', action='store_true', help='添加持仓记录')
    parser.add_argument('--action', type=str, help='买卖方向 (买入/卖出)')
    parser.add_argument('--price', type=float, help='成交价格')
    parser.add_argument('--quantity', type=int, help='成交数量')
    parser.add_argument('--time', type=str, help='成交时间')
    parser.add_argument('--account', type=str, help='账户尾号')
    parser.add_argument('--query-holdings', action='store_true', help='查询持仓记录')
    
    args = parser.parse_args()
    
    if args.init:
        init_database()
    
    elif args.insert and args.data:
        insert_risk_records_from_json(args.data, args.date)
    
    elif args.query:
        if args.stock:
            results = query_by_stock(args.stock)
            print(f"\n📊 股票 {args.stock} 的历史风险记录:")
            for r in results:
                print(f"  {r['record_date']} | {r['risk_level']} | {r['risk_type']} | {r['news_title']}")
        else:
            results = query_by_date(args.date or datetime.now().strftime('%Y-%m-%d'))
            print(f"\n📊 {args.date or '今日'} 的风险股票:")
            for r in results:
                print(f"  {r['stock_code']} {r['stock_name']} | {r['risk_level']} | {r['risk_type']}")
    
    elif args.add_holding:
        if all([args.stock, args.action, args.price, args.quantity, args.time]):
            # 获取股票名称
            stock_name = args.stock  # 简化处理，实际应该查询股票名称
            add_holding(args.stock, stock_name, args.action, args.price, args.quantity, args.time, args.account or '')
        else:
            print("❌ 缺少必要参数")
            print("需要：--stock, --action, --price, --quantity, --time")
    
    elif args.query_holdings:
        results = query_holdings(args.stock)
        if results:
            print(f"\n📊 持仓记录:")
            for r in results:
                print(f"  {r['trade_time']} | {r['action']} | {r['stock_name']} ({r['stock_code']}) | {r['price']}元 × {r['quantity']}股 = {r['amount']:.2f}元")
        else:
            print("\n⚠️ 无持仓记录")
    
    elif args.export:
        export_to_csv(args.output or 'risk_records.csv', args.date)
    
    elif args.backup:
        backup_database()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
