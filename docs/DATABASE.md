# 📊 数据库字典 - 港股风险新闻监控系统

## 数据库概述

**数据库类型**: SQLite  
**数据库文件**: `/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db`  
**用途**: 存储和追踪港股风险股票的历史记录

---

## 数据表结构

### 表名：`risk_records` (风险股票记录表)

存储每条风险股票的详细信息。

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 | 1 |
| `record_date` | DATE | NOT NULL | 记录日期（发现风险的日期） | 2026-04-13 |
| `stock_code` | VARCHAR(20) | NOT NULL | 股票代码（港交所格式） | 02007 |
| `stock_name` | VARCHAR(100) | NOT NULL | 股票名称 | 碧桂园 |
| `stock_name_en` | VARCHAR(100) | | 英文名称（可选） | Country Garden |
| `risk_type` | VARCHAR(50) | NOT NULL | 风险类型 | 债务违约 |
| `risk_level` | VARCHAR(10) | NOT NULL | 风险等级：HIGH/MEDIUM | HIGH |
| `news_title` | VARCHAR(500) | NOT NULL | 新闻标题 | 未能按期偿还债券 |
| `news_url` | VARCHAR(500) | | 新闻链接 | https://... |
| `news_source` | VARCHAR(50) | | 新闻来源 | 东方财富网 |
| `publish_time` | DATETIME | | 新闻发布时间 | 2026-04-13 09:30:00 |
| `crawl_time` | DATETIME | NOT NULL | 爬取时间（系统记录时间） | 2026-04-13 15:52:33 |
| `is_verified` | BOOLEAN | DEFAULT 0 | 是否已人工核实 | 0 |
| `notes` | TEXT | | 备注信息 | |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 | 2026-04-13 15:52:33 |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录更新时间 | 2026-04-13 15:52:33 |

### 表名：`risk_statistics` (风险统计表)

按日期和风险类型聚合的统计数据。

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 | 1 |
| `stat_date` | DATE | NOT NULL UNIQUE | 统计日期 | 2026-04-13 |
| `total_news` | INTEGER | DEFAULT 0 | 监控新闻总数 | 52 |
| `risk_news_count` | INTEGER | DEFAULT 0 | 风险新闻数量 | 10 |
| `high_risk_count` | INTEGER | DEFAULT 0 | 高风险股票数量 | 3 |
| `medium_risk_count` | INTEGER | DEFAULT 0 | 中风险股票数量 | 7 |
| `regulatory_count` | INTEGER | DEFAULT 0 | 监管处罚类数量 | 2 |
| `audit_count` | INTEGER | DEFAULT 0 | 审计问题类数量 | 3 |
| `debt_count` | INTEGER | DEFAULT 0 | 债务违约类数量 | 1 |
| `business_count` | INTEGER | DEFAULT 0 | 经营风险类数量 | 1 |
| `executive_count` | INTEGER | DEFAULT 0 | 高管变动类数量 | 3 |
| `suspension_count` | INTEGER | DEFAULT 0 | 停牌风险类数量 | 2 |
| `market_count` | INTEGER | DEFAULT 0 | 市场风险类数量 | 4 |
| `crawl_pages` | INTEGER | DEFAULT 0 | 爬取页数 | 50 |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 | 2026-04-13 15:52:33 |

### 表名：`stock_pool` (股票池表)

记录监控股票的基本信息（可选扩展）。

| 字段名 | 类型 | 约束 | 说明 | 示例 |
|--------|------|------|------|------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 | 1 |
| `stock_code` | VARCHAR(20) | NOT NULL UNIQUE | 股票代码 | 02007 |
| `stock_name` | VARCHAR(100) | NOT NULL | 股票名称 | 碧桂园 |
| `industry` | VARCHAR(50) | | 所属行业 | 房地产 |
| `market_cap` | VARCHAR(20) | | 市值 | 大型 |
| `is_monitored` | BOOLEAN | DEFAULT 1 | 是否在监控列表 | 1 |
| `added_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 添加时间 | 2026-04-13 |

---

## 索引设计

```sql
-- 风险记录表索引
CREATE INDEX idx_record_date ON risk_records(record_date);
CREATE INDEX idx_stock_code ON risk_records(stock_code);
CREATE INDEX idx_risk_type ON risk_records(risk_type);
CREATE INDEX idx_risk_level ON risk_records(risk_level);
CREATE INDEX idx_crawl_time ON risk_records(crawl_time);

-- 统计表索引
CREATE INDEX idx_stat_date ON risk_statistics(stat_date);
```

---

## 风险类型枚举

| 值 | 说明 | 风险等级 |
|----|------|---------|
| `监管处罚` | 证监会、交易所等监管机构的处罚或问询 | HIGH |
| `债务违约` | 债券违约、无法兑付等 | HIGH |
| `停牌风险` | 停牌、暂停上市、终止上市 | HIGH |
| `审计问题` | 审计师辞任、财报问题等 | MEDIUM |
| `经营风险` | 破产清算、资产冻结、重大亏损 | MEDIUM |
| `高管变动` | 实控人被捕、董事长辞职等 | MEDIUM |
| `市场风险` | 关税战、封锁、制裁等宏观风险 | MEDIUM |

---

## 常用查询示例

### 1. 查询某日所有风险股票
```sql
SELECT stock_code, stock_name, risk_type, risk_level, news_title
FROM risk_records
WHERE record_date = '2026-04-13'
ORDER BY 
    CASE risk_level WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 END,
    risk_type;
```

### 2. 查询某股票的历史风险记录
```sql
SELECT record_date, risk_type, risk_level, news_title, news_url
FROM risk_records
WHERE stock_code = '02007'
ORDER BY record_date DESC;
```

### 3. 统计各风险类型数量
```sql
SELECT risk_type, COUNT(*) as count
FROM risk_records
WHERE record_date = '2026-04-13'
GROUP BY risk_type
ORDER BY count DESC;
```

### 4. 查询连续多日出现风险的股票
```sql
SELECT stock_code, stock_name, COUNT(DISTINCT record_date) as days
FROM risk_records
GROUP BY stock_code
HAVING days >= 3
ORDER BY days DESC;
```

### 5. 获取最新统计数据
```sql
SELECT * FROM risk_statistics
ORDER BY stat_date DESC
LIMIT 1;
```

---

## 数据库操作流程

### 初始化数据库
```bash
python3 database_manager.py --init
```

### 插入风险记录
```bash
python3 database_manager.py --insert --date 2026-04-13 --data risk_report.json
```

### 查询记录
```bash
python3 database_manager.py --query --date 2026-04-13
python3 database_manager.py --query --stock 02007
```

### 导出报表
```bash
python3 database_manager.py --export --format csv --output report.csv
```

---

## 数据备份策略

- **自动备份**: 每日爬取完成后自动备份数据库
- **备份位置**: `/home/yxy/.openclaw/workspace/hk_risk_news/backups/`
- **保留策略**: 保留最近 30 天的备份

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0 | 2026-04-14 | 初始版本，创建 3 张核心表 |

---

*最后更新：2026-04-14*
