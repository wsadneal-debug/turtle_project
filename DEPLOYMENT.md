# 📦 港股风险新闻监控 - 部署文档

**版本**: 1.0  
**部署时间**: 2026-04-14  
**下次执行**: 每天 15:30

---

## 🎯 系统概述

自动化港股风险新闻监控系统：
- ⏰ **定时执行**: 每天 15:30 自动爬取
- 🔒 **真实验证**: 只信任官方认证媒体
- 📊 **自动入库**: SQLite 数据库存储
- 📝 **日志记录**: 完整的执行日志

---

## 📁 项目结构

```
/home/yxy/.openclaw/workspace/hk_risk_news/
├── crawl_verified.py          # 增强验证版爬取脚本
├── scheduler.py               # 定时任务调度器
├── database_manager.py        # 数据库管理工具
├── install_cron.sh            # 定时任务安装脚本
├── risk_stocks.db             # SQLite 数据库
├── logs/                      # 日志目录
│   ├── scheduler.log         # 调度器日志
│   └── cron.log              # Cron 执行日志
├── verified_*.json           # 爬取结果
└── DEPLOYMENT.md             # 部署文档（本文件）
```

---

## ⏰ 定时任务配置

### 执行时间
- **每天**: 15:30（下午 3 点 30 分）
- **时区**: Asia/Shanghai (UTC+8)

### Crontab 配置
```bash
# 查看当前配置
crontab -l

# 配置内容
30 15 * * * cd /home/yxy/.openclaw/workspace/hk_risk_news && /usr/bin/python3 scheduler.py --cron >> logs/cron.log 2>&1
```

---

## 🔧 管理命令

### 立即执行
```bash
# 手动执行一次爬取任务
python3 /home/yxy/.openclaw/workspace/hk_risk_news/scheduler.py --run
```

### 查看日志
```bash
# 实时查看调度器日志
tail -f /home/yxy/.openclaw/workspace/hk_risk_news/logs/scheduler.log

# 实时查看 cron 日志
tail -f /home/yxy/.openclaw/workspace/hk_risk_news/logs/cron.log

# 查看最近 100 行日志
tail -n 100 /home/yxy/.openclaw/workspace/hk_risk_news/logs/scheduler.log
```

### 数据库查询
```bash
# 查看今日风险新闻
python3 database_manager.py --query --date 2026-04-14

# 查询某股票历史记录
python3 database_manager.py --query --stock 000638

# 导出 CSV 报表
python3 database_manager.py --export --output report.csv
```

### 管理定时任务
```bash
# 编辑 crontab
crontab -e

# 删除定时任务
crontab -r

# 重新安装定时任务
bash install_cron.sh
```

---

## 📊 数据库结构

### 表：risk_records（风险记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| record_date | DATE | 记录日期 |
| stock_code | VARCHAR(20) | 股票代码 |
| stock_name | VARCHAR(100) | 股票名称 |
| risk_type | VARCHAR(50) | 风险类型 |
| risk_level | VARCHAR(10) | 风险等级 (HIGH/MEDIUM) |
| news_title | VARCHAR(500) | 新闻标题 |
| news_url | VARCHAR(500) | 新闻链接（唯一） |
| news_source | VARCHAR(50) | 新闻来源 |
| quality_score | INTEGER | 质量评分 |
| crawl_time | DATETIME | 爬取时间 |
| is_processed | BOOLEAN | 是否已处理 |
| created_at | DATETIME | 创建时间 |

### 表：crawl_stats（爬取统计）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| crawl_date | DATE | 爬取日期 |
| crawl_time | DATETIME | 爬取时间 |
| total_crawled | INTEGER | 爬取总数 |
| total_verified | INTEGER | 验证通过数 |
| high_risk_count | INTEGER | 高风险数量 |
| medium_risk_count | INTEGER | 中风险数量 |
| avg_quality_score | REAL | 平均质量分 |
| sources | TEXT | 数据源列表 (JSON) |
| status | VARCHAR(20) | 状态 (success/error/timeout) |

---

## 📈 执行日志示例

### 成功执行
```
2026-04-14 15:30:00,000 - INFO - ============================================================
2026-04-14 15:30:00,000 - INFO - 🚀 开始执行风险新闻爬取任务
2026-04-14 15:30:00,000 - INFO - ============================================================
2026-04-14 15:30:00,000 - INFO - 📡 启动爬取脚本...
2026-04-14 15:30:30,000 - INFO - 📊 共 5 条验证通过的风险新闻
2026-04-14 15:30:30,000 - INFO - 💾 保存数据到数据库...
2026-04-14 15:30:30,000 - INFO - 📊 数据库操作：新增 5 条，跳过 0 条（重复）
2026-04-14 15:30:30,000 - INFO - ✅ 爬取完成：共 5 条，入库 5 条
2026-04-14 15:30:30,000 - INFO - ============================================================
2026-04-14 15:30:30,000 - INFO - ✅ 爬取任务执行完成
```

### 执行失败
```
2026-04-14 15:30:00,000 - ERROR - ❌ 爬取失败：网络连接超时
2026-04-14 15:30:00,000 - INFO - 📊 数据库操作：状态=error
```

---

## 🔍 故障排查

### 问题 1: 定时任务未执行
```bash
# 检查 cron 服务状态
systemctl status cron

# 查看 cron 日志
grep CRON /var/log/syslog | tail -20

# 检查 crontab 配置
crontab -l
```

### 问题 2: 爬取失败
```bash
# 查看错误日志
tail -100 logs/scheduler.log

# 手动执行测试
python3 scheduler.py --run

# 检查网络连接
curl -I https://finance.eastmoney.com/
```

### 问题 3: 数据库错误
```bash
# 重建数据库
python3 scheduler.py --init

# 检查数据库文件
ls -lh risk_stocks.db

# 查询数据库
sqlite3 risk_stocks.db "SELECT * FROM crawl_stats ORDER BY crawl_date DESC LIMIT 5;"
```

---

## 📝 数据备份

### 自动备份
数据库每次爬取后自动保存，JSON 文件带时间戳。

### 手动备份
```bash
# 备份数据库
cp risk_stocks.db risk_stocks_backup_$(date +%Y%m%d).db

# 备份所有数据
tar -czf hk_risk_news_backup_$(date +%Y%m%d).tar.gz \
    risk_stocks.db logs/ verified_*.json
```

---

## 🎯 监控指标

### 每日检查清单
- [ ] 定时任务是否正常执行
- [ ] 爬取新闻数量是否合理（3-10 条）
- [ ] 平均质量分是否 ≥70 分
- [ ] 是否有高风险新闻
- [ ] 日志是否有错误信息

### 周报指标
- 本周爬取天数
- 累计风险新闻数
- 高风险新闻占比
- 平均质量分趋势
- 数据源分布

---

## 📞 技术支持

### 日志文件位置
- 调度器日志：`/home/yxy/.openclaw/workspace/hk_risk_news/logs/scheduler.log`
- Cron 日志：`/home/yxy/.openclaw/workspace/hk_risk_news/logs/cron.log`

### 数据库位置
- SQLite 数据库：`/home/yxy/.openclaw/workspace/hk_risk_news/risk_stocks.db`

### 配置文件
- Crontab: 使用 `crontab -e` 编辑
- 执行时间：修改 `scheduler.py` 中的 `SCHEDULE_TIME` 变量

---

## ✅ 部署验证清单

- [x] 数据库初始化完成
- [x] Crontab 配置完成
- [x] 手动执行测试成功
- [x] 日志记录正常
- [x] 数据入库正常
- [ ] 等待第一次自动执行（今天 15:30）
- [ ] 验证自动执行结果

---

**部署时间**: 2026-04-14 12:10  
**下次执行**: 2026-04-14 15:30  
**系统状态**: ✅ 正常运行
