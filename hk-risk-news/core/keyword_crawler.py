#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
港股风险新闻监控 - 关键词搜索爬虫

功能：
1. 使用东方财富网搜索功能，通过关键词搜索风险新闻
2. 替代原来的遍历所有新闻的方式
3. 支持 20 个风险关键词
4. 自动去重并输出 JSON 结果

关键词列表：
- 监管处罚：立案调查、行政处罚、监管函、问询函
- 审计问题：审计师辞任、无法表示意见、财报延期
- 债务违约：债务违约、债券违约、无法兑付、债务逾期
- 经营风险：破产清算、资产冻结、重大亏损
- 高管变动：实控人被捕、董事长辞职、被调查
- 停牌风险：停牌、暂停上市、终止上市
"""

import json
import sqlite3
import logging
import re
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

WORKSPACE = Path('/home/yxy/.openclaw/workspace/hk_risk_news')
DB_PATH = WORKSPACE / 'risk_stocks.db'

# 20 个风险关键词
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

# 关键词到风险类型的映射
KEYWORD_TO_RISK_TYPE = {
    '立案调查': '监管处罚',
    '行政处罚': '监管处罚',
    '监管函': '监管处罚',
    '问询函': '监管处罚',
    '审计师辞任': '审计问题',
    '无法表示意见': '审计问题',
    '财报延期': '审计问题',
    '债务违约': '债务违约',
    '债券违约': '债务违约',
    '无法兑付': '债务违约',
    '债务逾期': '债务违约',
    '破产清算': '经营风险',
    '资产冻结': '经营风险',
    '重大亏损': '经营风险',
    '实控人被捕': '高管变动',
    '董事长辞职': '高管变动',
    '被调查': '高管变动',
    '停牌': '停牌风险',
    '暂停上市': '停牌风险',
    '终止上市': '停牌风险'
}

# 风险等级映射
RISK_LEVEL_MAP = {
    '监管处罚': 'HIGH',
    '债务违约': 'HIGH',
    '停牌风险': 'HIGH',
    '审计问题': 'MEDIUM',
    '经营风险': 'MEDIUM',
    '高管变动': 'MEDIUM'
}

# 搜索源配置
SEARCH_SOURCES = [
    {'name': '东方财富网', 'domain': 'eastmoney.com'},
    {'name': '第一财经', 'domain': 'yicai.com'}
]

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 数据库操作 ====================

def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 删除旧表（强制重建以更新 schema）
    cursor.execute('DROP TABLE IF EXISTS risk_records')
    cursor.execute('DROP TABLE IF EXISTS crawl_stats')
    cursor.execute('DROP TABLE IF EXISTS stock_pool')
    
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
            keyword VARCHAR(50),
            quality_score INTEGER,
            crawl_time DATETIME NOT NULL,
            is_processed BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建爬取统计表
    cursor.execute('''
        CREATE TABLE crawl_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crawl_date DATE NOT NULL UNIQUE,
            crawl_time DATETIME NOT NULL,
            keywords_searched INTEGER DEFAULT 0,
            total_crawled INTEGER DEFAULT 0,
            high_risk_count INTEGER DEFAULT 0,
            medium_risk_count INTEGER DEFAULT 0,
            deduplicated_count INTEGER DEFAULT 0,
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
            cursor.execute('''
                INSERT OR IGNORE INTO risk_records (
                    record_date, stock_code, stock_name, risk_type, risk_level,
                    news_title, news_url, news_source, keyword, quality_score, crawl_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                crawl_date,
                news.get('stock_code', ''),
                news.get('stock_name', ''),
                news['risk_type'],
                news['risk_level'],
                news['title'],
                news['url'],
                news['source'],
                news.get('keyword', ''),
                news.get('quality_score', 50),
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
            crawl_date, crawl_time, keywords_searched, total_crawled,
            high_risk_count, medium_risk_count, deduplicated_count,
            status, error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        crawl_date,
        crawl_time,
        stats.get('keywords_searched', 0),
        stats.get('total_crawled', 0),
        stats.get('high_risk_count', 0),
        stats.get('medium_risk_count', 0),
        stats.get('deduplicated_count', 0),
        stats.get('status', 'success'),
        stats.get('error_message', '')
    ))
    
    conn.commit()
    conn.close()


# ==================== 股票映射（集成 stock_mapper.py 逻辑） ====================

def load_stock_aliases():
    """加载股票别名表到内存"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT stock_code, alias_name, alias_type, market FROM stock_aliases')
        aliases = cursor.fetchall()
        conn.close()
        return aliases
    except sqlite3.OperationalError:
        # 表不存在，返回空列表
        conn.close()
        return []


def map_company_to_stock(company_name, aliases):
    """
    将公司名称映射到股票代码
    返回：(stock_code, stock_name, confidence)
    """
    if not company_name or not aliases:
        return '', '', 0
    
    # 清理公司名称
    company_name = company_name.strip()
    company_name = re.sub(r'[\s\-\_]', '', company_name)  # 去除空格、连字符等
    
    matches = []
    
    # 精确匹配（全名）
    for code, alias, alias_type, market in aliases:
        if alias_type == 'full' and company_name == alias:
            matches.append((code, alias, 100, market))
        elif alias_type == 'short' and company_name in alias:
            matches.append((code, alias, 80, market))
        elif alias_type == 'core' and company_name in alias:
            matches.append((code, alias, 60, market))
    
    if matches:
        # 返回置信度最高的匹配
        matches.sort(key=lambda x: x[2], reverse=True)
        best = matches[0]
        return best[0], best[1], best[2]
    
    return '', '', 0


def extract_stock_info(title, keyword, aliases=None):
    """
    从标题中提取股票信息（增强版）
    1. 先尝试从标题提取股票代码
    2. 再尝试从标题提取公司名称并映射
    """
    import re
    stock_code = ''
    stock_name = ''
    confidence = 0
    
    # 1. 尝试匹配股票代码 (港股格式：0XXXX.HK 或 A 股 6 位数字)
    hk_match = re.search(r'0(\d{4})\.HK|0(\d{4})|(\d{6})', title)
    if hk_match:
        code = hk_match.group(1) or hk_match.group(2) or hk_match.group(3)
        stock_code = f"0{code}" if len(code) == 4 else code
        stock_code = stock_code[:6]  # 确保不超过 6 位
        confidence = 90  # 代码匹配置信度高
    
    # 2. 尝试从标题中提取股票名称（通常在冒号前）
    name_match = re.search(r'^([^：:]+)[：:]', title)
    if name_match:
        extracted_name = name_match.group(1).strip()
        # 清理股票代码前缀
        extracted_name = re.sub(r'^\d{6}\s*', '', extracted_name)
        
        # 3. 使用别名表映射
        if aliases:
            mapped_code, mapped_name, map_confidence = map_company_to_stock(extracted_name, aliases)
            if mapped_code and map_confidence > confidence:
                stock_code = mapped_code
                stock_name = mapped_name
                confidence = map_confidence
            elif not stock_name:
                stock_name = extracted_name
        else:
            stock_name = extracted_name
    
    return stock_code, stock_name, confidence


def deduplicate_news(news_list):
    """去重：基于 URL 去重"""
    seen_urls = set()
    unique_news = []
    
    for news in news_list:
        if news['url'] not in seen_urls:
            seen_urls.add(news['url'])
            unique_news.append(news)
    
    return unique_news


def parse_search_results(search_data):
    """解析搜索结果数据（支持多搜索源 + 股票映射）"""
    news_list = []
    unmapped_news = []  # 记录无法映射的新闻
    
    # 跳过元数据字段，只处理关键词
    skip_keys = ['crawl_date', 'crawl_time', 'keywords', 'stats', 'news', 'sources']
    
    # 加载股票别名表
    aliases = load_stock_aliases()
    if aliases:
        logger.info(f"📊 加载股票别名表：{len(aliases)} 条记录")
    else:
        logger.warning("⚠️ 未找到股票别名表，将使用简单提取模式")
    
    for keyword, results in search_data.items():
        if keyword in skip_keys:
            continue
        
        if not isinstance(results, list):
            continue
        
        risk_type = KEYWORD_TO_RISK_TYPE.get(keyword, '未知')
        risk_level = RISK_LEVEL_MAP.get(risk_type, 'MEDIUM')
        
        for result in results:
            if not isinstance(result, dict):
                continue
            
            title = result.get('title', '')
            url = result.get('url', '')
            source = result.get('source', '第一财经')  # 支持多搜索源
            
            if not title or not url:
                continue
            
            stock_code, stock_name, confidence = extract_stock_info(title, keyword, aliases)
            
            news_item = {
                'title': title,
                'url': url,
                'stock_code': stock_code,
                'stock_name': stock_name,
                'risk_type': risk_type,
                'risk_level': risk_level,
                'keyword': keyword,
                'source': source,
                'quality_score': confidence,  # 使用映射置信度作为质量分数
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            news_list.append(news_item)
            
            # 记录无法映射的新闻
            if not stock_code:
                unmapped_news.append({
                    'title': title,
                    'url': url,
                    'keyword': keyword,
                    'source': source
                })
    
    # 保存未映射新闻
    if unmapped_news:
        crawl_date = datetime.now().strftime('%Y%m%d')
        unmapped_file = WORKSPACE / f'unmapped_news_{crawl_date}.json'
        with open(unmapped_file, 'w', encoding='utf-8') as f:
            json.dump(unmapped_news, f, ensure_ascii=False, indent=2)
        logger.info(f"📄 未映射新闻已保存到：{unmapped_file}")
    
    return news_list


# ==================== 主函数 ====================

def run_crawl(search_data=None):
    """执行爬取任务"""
    logger.info("="*60)
    logger.info("🚀 开始执行关键词搜索爬取任务")
    logger.info(f"📋 关键词数量：{len(RISK_KEYWORDS)}")
    logger.info("="*60)
    
    crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    crawl_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # 如果有外部传入的搜索数据（从浏览器工具获取），直接使用
        if search_data:
            logger.info("📄 使用外部提供的搜索数据")
            news_list = parse_search_results(search_data)
        else:
            # 否则从 JSON 文件读取（兼容旧模式）
            json_files = list(WORKSPACE.glob('keyword_search_*.json'))
            if json_files:
                latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
                logger.info(f"📄 读取搜索数据：{latest_file}")
                with open(latest_file, 'r', encoding='utf-8') as f:
                    search_data = json.load(f)
                news_list = parse_search_results(search_data)
            else:
                logger.warning("⚠️ 未找到搜索数据文件")
                news_list = []
        
        # 去重
        total_before = len(news_list)
        news_list = deduplicate_news(news_list)
        total_after = len(news_list)
        deduplicated = total_before - total_after
        
        logger.info(f"📊 去重：{total_before} → {total_after} (去除 {deduplicated} 条重复)")
        
        # 统计
        high_risk = sum(1 for n in news_list if n['risk_level'] == 'HIGH')
        medium_risk = sum(1 for n in news_list if n['risk_level'] == 'MEDIUM')
        mapped_count = sum(1 for n in news_list if n['stock_code'])
        unmapped_count = total_after - mapped_count
        
        stats = {
            'keywords_searched': len(RISK_KEYWORDS),
            'total_crawled': total_after,
            'high_risk_count': high_risk,
            'medium_risk_count': medium_risk,
            'deduplicated_count': deduplicated,
            'mapped_count': mapped_count,
            'unmapped_count': unmapped_count,
            'status': 'success'
        }
        
        # 保存 JSON 结果
        output_file = WORKSPACE / f'keyword_result_{crawl_date.replace("-", "")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'crawl_date': crawl_date,
                'crawl_time': crawl_time,
                'keywords': RISK_KEYWORDS,
                'stats': stats,
                'news': news_list
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 结果保存到：{output_file}")
        
        # 入库
        logger.info("💾 保存数据到数据库...")
        init_database()
        inserted, skipped = insert_risk_records(news_list, crawl_date)
        insert_crawl_stats(stats, crawl_date, crawl_time)
        
        logger.info("="*60)
        logger.info(f"✅ 爬取完成")
        logger.info(f"📊 统计：共 {total_after} 条，高风险 {high_risk} 条，中风险 {medium_risk} 条")
        logger.info(f"📊 股票映射：成功 {mapped_count} 条，失败 {unmapped_count} 条（{unmapped_count/total_after*100:.1f}%）")
        logger.info(f"📊 入库：新增 {inserted} 条，跳过 {skipped} 条")
        logger.info("="*60)
        
        if unmapped_count > 0:
            logger.warning(f"⚠️ 有 {unmapped_count} 条新闻未能映射到股票代码，请查看 unmapped_news_*.json")
        
        return True, news_list
        
    except Exception as e:
        error_msg = f"爬取失败：{str(e)}"
        logger.error(f"❌ {error_msg}")
        insert_crawl_stats({
            'keywords_searched': len(RISK_KEYWORDS),
            'status': 'error',
            'error_message': error_msg
        }, crawl_date, crawl_time)
        return False, []


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='港股风险新闻监控 - 关键词搜索爬虫')
    parser.add_argument('--input', type=str, help='输入 JSON 文件路径')
    parser.add_argument('--test', action='store_true', help='测试模式')
    
    args = parser.parse_args()
    
    if args.test:
        # 测试模式
        test_data = {
            '立案调查': [
                {'title': '广安爱众：董事李常兵被立案调查并实施留置', 'url': 'http://finance.eastmoney.com/a/202604113702012257.html'},
                {'title': '300152，相关股东被证监会立案调查！', 'url': 'http://finance.eastmoney.com/a/202604103701681937.html'}
            ],
            '债务违约': [
                {'title': '融创房地产集团：子公司新增一笔 1.23 亿元债务违约', 'url': 'http://finance.eastmoney.com/a/20260326386020384.html'}
            ]
        }
        run_crawl(test_data)
    else:
        run_crawl()


if __name__ == '__main__':
    main()
