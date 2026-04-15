#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 定时任务调度器

功能：
1. 每天 15:30 自动启动爬取
2. 验证新闻真实性
3. 入库存储
4. 发送通知（可选）
5. 错误处理和日志记录

配置：
- 执行时间：每天 15:30
- 数据库：SQLite
- 日志：/home/yxy/.openclaw/workspace/hk_risk_news/logs/
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# ==================== 配置 ====================

WORKSPACE = Path('/home/yxy/.openclaw/workspace/hk_risk_news')
DB_PATH = WORKSPACE / 'risk_stocks.db'
LOG_DIR = WORKSPACE / 'logs'
CRAWL_SCRIPT = WORKSPACE / 'keyword_crawler.py'

# 定时配置
SCHEDULE_TIME = '18:00'  # 每天执行时间（18:00，搜索截至昨天 18:00 的信息）

# 20 个风险关键词（用于浏览器搜索）
RISK_KEYWORDS = [
    # 监管处罚类
    '立案调查', '行政处罚', '监管函', '问询函',
    # 审计问题类
    '审计师辞任', '无法表示意见', '财报延期',
    # 债务违约类
    '债务违约', '债券违约', '无法兑付', '债务逾期',
    # 经营风险类
    '破产清算', '资产冻结', '重大亏损',
    # 高管变动类
    '实控人被捕', '董事长辞职', '被调查',
    # 停牌风险类
    '停牌', '暂停上市', '终止上市'
]

# 搜索 URL 模板
SEARCH_URL_TEMPLATE = 'https://so.eastmoney.com/news/s?keyword={keyword}'

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== 数据库操作 ====================

def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 先删除旧表（如果有）- 用于升级
    cursor.execute('DROP TABLE IF EXISTS risk_records')
    cursor.execute('DROP TABLE IF EXISTS crawl_stats')
    
    # 创建风险记录表
    cursor.execute('''
        CREATE TABLE risk_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date DATE NOT NULL,
            stock_code VARCHAR(20),
            stock_name VARCHAR(100),
            risk_type VARCHAR(50) NOT NULL,
            risk_level VARCHAR(10) NOT NULL,
            news_title VARCHAR(500) NOT NULL,
            news_url VARCHAR(500) UNIQUE,
            news_source VARCHAR(50),
            quality_score INTEGER,
            crawl_time DATETIME NOT NULL,
            is_processed BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建爬取统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crawl_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crawl_date DATE NOT NULL UNIQUE,
            crawl_time DATETIME NOT NULL,
            total_crawled INTEGER DEFAULT 0,
            total_verified INTEGER DEFAULT 0,
            high_risk_count INTEGER DEFAULT 0,
            medium_risk_count INTEGER DEFAULT 0,
            avg_quality_score REAL,
            sources TEXT,
            status VARCHAR(20),
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_record_date ON risk_records(record_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_code ON risk_records(stock_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk_level ON risk_records(risk_level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawl_date ON crawl_stats(crawl_date)')
    
    conn.commit()
    conn.close()
    logger.info("✅ 数据库初始化完成")


def insert_risk_records(news_list, crawl_date):
    """插入风险记录到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    skipped = 0
    
    for news in news_list:
        try:
            # 提取主要风险类型
            risk_type = news['risks'][0]['category'] if news['risks'] else '未知'
            risk_level = news['risk_level']
            
            cursor.execute('''
                INSERT OR IGNORE INTO risk_records (
                    record_date, stock_code, stock_name, risk_type, risk_level,
                    news_title, news_url, news_source, quality_score, crawl_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                crawl_date,
                news.get('stock_code', ''),
                news.get('stock_name', ''),
                risk_type,
                risk_level,
                news['title'],
                news['url'],
                news['source'],
                news.get('quality_score', 0),
                news.get('crawl_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            ))
            
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
                
        except Exception as e:
            logger.error(f"❌ 插入记录失败：{news['title'][:50]} - {e}")
            skipped += 1
    
    conn.commit()
    conn.close()
    
    logger.info(f"📊 数据库操作：新增 {inserted} 条，跳过 {skipped} 条（重复）")
    return inserted, skipped


def insert_crawl_stats(stats, crawl_date, crawl_time):
    """插入爬取统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO crawl_stats (
            crawl_date, crawl_time, total_crawled, total_verified,
            high_risk_count, medium_risk_count, avg_quality_score,
            sources, status, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        crawl_date,
        crawl_time,
        stats.get('total_crawled', 0),
        stats.get('total_verified', 0),
        stats.get('high_risk_count', 0),
        stats.get('medium_risk_count', 0),
        stats.get('avg_quality_score', 0),
        json.dumps(stats.get('sources', []), ensure_ascii=False),
        stats.get('status', 'success'),
        stats.get('error_message', '')
    ))
    
    conn.commit()
    conn.close()


# ==================== 爬取任务 ====================

def run_crawl():
    """执行爬取任务 - 关键词搜索模式"""
    logger.info("="*60)
    logger.info("🚀 开始执行风险新闻关键词搜索爬取任务")
    logger.info(f"📋 关键词数量：{len(RISK_KEYWORDS)}")
    logger.info("="*60)
    
    crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    crawl_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # 确保日志目录存在
        LOG_DIR.mkdir(exist_ok=True)
        
        # 执行关键词搜索爬取脚本
        logger.info("📡 启动关键词搜索爬虫...")
        result = subprocess.run(
            ['python3', str(CRAWL_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=300  # 5 分钟超时
        )
        
        # 记录输出
        if result.stdout:
            logger.info("爬取输出:\n" + result.stdout)
        if result.stderr:
            logger.warning("爬取警告:\n" + result.stderr)
        
        # 查找生成的 JSON 文件
        json_files = list(WORKSPACE.glob('keyword_result_*.json'))
        if not json_files:
            raise Exception("未找到爬取结果文件")
        
        # 获取最新的 JSON 文件
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"📄 读取爬取结果：{latest_file}")
        
        # 解析 JSON
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        news_list = data.get('news', [])
        total_crawled = len(news_list)
        
        if total_crawled == 0:
            logger.warning("⚠️ 未爬取到任何风险新闻")
            stats = {
                'keywords_searched': len(RISK_KEYWORDS),
                'total_crawled': 0,
                'high_risk_count': 0,
                'medium_risk_count': 0,
                'deduplicated_count': 0,
                'status': 'no_data'
            }
        else:
            # 统计
            high_risk = sum(1 for n in news_list if n['risk_level'] == 'HIGH')
            medium_risk = sum(1 for n in news_list if n['risk_level'] == 'MEDIUM')
            deduplicated = data.get('stats', {}).get('deduplicated_count', 0)
            
            stats = {
                'keywords_searched': len(RISK_KEYWORDS),
                'total_crawled': total_crawled,
                'high_risk_count': high_risk,
                'medium_risk_count': medium_risk,
                'deduplicated_count': deduplicated,
                'status': 'success'
            }
            
            logger.info(f"✅ 爬取完成：共 {total_crawled} 条，高风险 {high_risk} 条，中风险 {medium_risk} 条")
        
        # 记录统计
        insert_crawl_stats(stats, crawl_date, crawl_time)
        
        logger.info("="*60)
        logger.info("✅ 爬取任务执行完成")
        logger.info("="*60)
        
        return True
        
    except subprocess.TimeoutExpired:
        error_msg = "爬取超时（>5 分钟）"
        logger.error(f"❌ {error_msg}")
        insert_crawl_stats({
            'status': 'timeout',
            'error_message': error_msg
        }, crawl_date, crawl_time)
        return False
        
    except Exception as e:
        error_msg = f"爬取失败：{str(e)}"
        logger.error(f"❌ {error_msg}")
        insert_crawl_stats({
            'status': 'error',
            'error_message': error_msg
        }, crawl_date, crawl_time)
        return False


# ==================== 定时调度 ====================

def should_run():
    """检查是否应该执行（到达设定时间）"""
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    
    # 检查是否到达执行时间
    if current_time == SCHEDULE_TIME:
        return True
    
    return False


def run_scheduler():
    """运行调度器（守护进程模式）"""
    logger.info("="*60)
    logger.info("⏰ 调度器启动")
    logger.info(f"📅 执行时间：每天 {SCHEDULE_TIME}")
    logger.info("="*60)
    
    # 初始化数据库
    init_database()
    
    last_run_date = None
    
    while True:
        try:
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            current_time = now.strftime('%H:%M')
            
            # 检查是否到达执行时间且今天未执行
            if current_time == SCHEDULE_TIME and last_run_date != current_date:
                logger.info(f"⏰ 到达执行时间：{SCHEDULE_TIME}")
                
                # 执行爬取
                success = run_crawl()
                
                if success:
                    last_run_date = current_date
                    logger.info(f"✅ 今日任务已完成，下次执行：明天 {SCHEDULE_TIME}")
                
                # 等待 1 分钟，避免重复执行
                import time
                time.sleep(60)
            
            # 每分钟检查一次
            import time
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("👋 调度器被用户中断")
            break
        except Exception as e:
            logger.error(f"❌ 调度器错误：{e}")
            import time
            time.sleep(60)


# ==================== Cron 模式 ====================

def run_cron_mode():
    """Cron 模式（由 crontab 调用）"""
    logger.info("="*60)
    logger.info("🕐 Cron 模式启动")
    logger.info("="*60)
    
    # 初始化数据库
    init_database()
    
    # 执行爬取
    success = run_crawl()
    
    sys.exit(0 if success else 1)


# ==================== 主函数 ====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='港股风险新闻监控 - 定时任务调度器')
    parser.add_argument('--daemon', action='store_true', help='守护进程模式')
    parser.add_argument('--cron', action='store_true', help='Cron 模式（由 crontab 调用）')
    parser.add_argument('--run', action='store_true', help='立即执行一次')
    parser.add_argument('--init', action='store_true', help='仅初始化数据库')
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    LOG_DIR.mkdir(exist_ok=True)
    
    if args.init:
        init_database()
    elif args.cron:
        run_cron_mode()
    elif args.daemon:
        run_scheduler()
    elif args.run:
        run_crawl()
    else:
        # 默认：Cron 模式
        run_cron_mode()


if __name__ == '__main__':
    main()
