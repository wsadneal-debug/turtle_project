# 港股风险新闻监控系统

🔴 **自动监控 A/H 股市场风险新闻，智能识别风险股票，生成结构化风险名单**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Update](https://img.shields.io/badge/update-daily-orange.svg)](https://github.com)

---

## 📋 项目介绍

本系统通过**关键词搜索**方式，自动从多个财经网站抓取 A 股和港股市场的风险新闻，智能识别风险股票，生成可直接用于投资决策的结构化风险名单。

### 核心功能

- ✅ **20 个风险关键词**覆盖所有风险类型（监管处罚、债务违约、审计问题等）
- ✅ **多搜索源支持**：东方财富网、第一财经
- ✅ **A+H 股市场覆盖**：支持 7000+ 只 A 股和 700+ 只港股
- ✅ **智能股票映射**：自动将新闻映射到具体股票代码
- ✅ **自动去重入库**：基于 URL 去重，避免重复记录
- ✅ **定时自动执行**：每天自动抓取、分析、入库、通知
- ✅ **结构化输出**：可直接对接投资系统、风控系统

### 风险类型覆盖

| 风险类别 | 关键词示例 | 风险等级 |
|---------|-----------|---------|
| **监管处罚** | 立案调查、行政处罚、监管函、问询函 | 🔴 高 |
| **债务违约** | 债务违约、债券违约、无法兑付、债务逾期 | 🔴 高 |
| **停牌风险** | 停牌、暂停上市、终止上市 | 🔴 高 |
| **审计问题** | 审计师辞任、无法表示意见、财报延期 | 🟡 中 |
| **经营风险** | 破产清算、资产冻结、重大亏损 | 🟡 中 |
| **高管变动** | 实控人被捕、董事长辞职、被调查 | 🟡 中 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    定时任务 (每天 18:00)                  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   浏览器自动化工具                        │
│         (OpenClaw Browser Control - CDP 协议)            │
└─────────────────────────────────────────────────────────┘
                            ↓
    ┌───────────────────────┴───────────────────────┐
    ↓                                               ↓
┌───────────────┐                         ┌───────────────┐
│  东方财富网    │                         │   第一财经     │
│  关键词搜索    │                         │  关键词搜索    │
└───────────────┘                         └───────────────┘
    ↓                                               ↓
    └───────────────────────┬───────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   数据清洗与去重                          │
│         (基于 URL 去重、标题去重、相似去重)                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   股票名称映射                           │
│        (7876 条股票别名表 → 股票代码 + 置信度)            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   SQLite 数据库                          │
│    (risk_records: 风险记录 | stock_aliases: 股票别名)    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   输出与通知                             │
│    (JSON 文件 | 飞书通知 | 可直接对接投资系统)             │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 环境要求

### 系统要求

- **操作系统**: Linux / macOS / Windows
- **Python**: 3.8+
- **浏览器**: Google Chrome 90+ 或 Chromium
- **内存**: 至少 2GB 可用内存
- **存储**: 至少 500MB 可用空间

### Python 依赖

```bash
pip install sqlite3 logging pathlib
```

### 浏览器要求

系统使用 **CDP (Chrome DevTools Protocol)** 控制浏览器，需要：

1. Chrome/Chromium 浏览器
2. 浏览器以 CDP 模式启动（调试端口开放）
3. 或使用 OpenClaw 等支持 CDP 的自动化框架

---

## 🔌 需要的插件/工具

### 核心依赖

| 工具/插件 | 用途 | 必需 |
|----------|------|------|
| **OpenClaw** | 浏览器自动化控制、定时任务调度 | ✅ 是 |
| **Google Chrome** | 浏览器引擎，用于访问财经网站 | ✅ 是 |
| **SQLite3** | 数据库存储（Python 内置） | ✅ 是 |

### OpenClaw 配置

如果使用 OpenClaw 框架，需要以下配置：

```json
{
  "browser": {
    "profile": "openclaw",
    "cdpPort": 18800,
    "userDataDir": "/path/to/browser/data"
  },
  "cron": {
    "schedule": "0 18 * * *",
    "timezone": "Asia/Shanghai"
  }
}
```

### 可选工具

| 工具 | 用途 |
|------|------|
| **飞书 (Feishu)** | 接收风险股票通知 |
| **Git** | 版本控制和代码同步 |

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/hk-risk-news.git
cd hk-risk-news
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python3 keyword_crawler.py --init
```

### 4. 配置定时任务

#### 方式一：使用 OpenClaw Cron

```bash
# 导入 OpenClaw 配置
openclaw cron add --config config/openclaw_cron.json
```

#### 方式二：使用系统 Crontab

```bash
# 编辑 crontab
crontab -e

# 添加每日执行任务（每天 18:00）
0 18 * * * cd /path/to/hk-risk-news && python3 keyword_crawler.py >> logs/cron.log 2>&1
```

### 5. 手动测试

```bash
# 运行一次完整爬取
python3 keyword_crawler.py

# 查看结果
cat keyword_result_$(date +%Y%m%d).json
```

---

## 📁 项目结构

```
hk-risk-news/
├── README.md                 # 项目说明文档
├── DATABASE.md               # 数据库字典
├── DEPLOYMENT.md             # 部署指南
├── CHANGELOG.md              # 更新日志
├── requirements.txt          # Python 依赖
├── config/                   # 配置文件
│   └── openclaw_cron.json   # OpenClaw 定时任务配置
├── keyword_crawler.py        # 主爬虫程序（关键词搜索 + 股票映射）
├── browser_keyword_search.py # 浏览器搜索辅助工具
├── scheduler.py              # 定时任务调度器
├── stock_mapper.py           # 股票名称映射工具
├── database_manager.py       # 数据库管理工具
├── data/                     # 数据目录
│   └── raw_news/            # 原始新闻数据
├── output/                   # 输出目录
│   ├── keyword_result_*.json # 处理后的结果
│   └── unmapped_news_*.json  # 未映射新闻
├── logs/                     # 日志目录
│   └── crawler.log          # 爬虫日志
└── risk_stocks.db           # SQLite 数据库
```

---

## 📊 数据输出

### 数据库表结构

#### risk_records（风险记录表）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| id | INTEGER | 自增主键 | 1 |
| record_date | DATE | 记录日期 | 2026-04-15 |
| stock_code | VARCHAR(20) | 股票代码 | 600979.SH |
| stock_name | VARCHAR(100) | 股票名称 | 广安爱众 |
| risk_type | VARCHAR(50) | 风险类型 | 监管处罚 |
| risk_level | VARCHAR(10) | 风险等级 | HIGH |
| news_title | VARCHAR(500) | 新闻标题 | 广安爱众：董事被留置 |
| news_url | VARCHAR(500) | 新闻链接（唯一） | https://... |
| news_source | VARCHAR(50) | 搜索源 | 东方财富网 |
| quality_score | INTEGER | 映射置信度 | 95 |
| crawl_time | DATETIME | 爬取时间 | 2026-04-15 18:00:00 |

### 输出文件示例

#### keyword_result_YYYYMMDD.json

```json
{
  "crawl_date": "2026-04-15",
  "crawl_time": "2026-04-15 18:00:00",
  "stats": {
    "keywords_searched": 20,
    "total_crawled": 150,
    "high_risk_count": 80,
    "medium_risk_count": 70,
    "mapped_count": 95,
    "unmapped_count": 55
  },
  "news": [
    {
      "title": "广安爱众：董事被留置并辞职",
      "url": "https://...",
      "stock_code": "600979.SH",
      "stock_name": "广安爱众",
      "risk_type": "监管处罚",
      "risk_level": "HIGH",
      "keyword": "立案调查",
      "source": "东方财富网",
      "quality_score": 95
    }
  ]
}
```

---

## 🔧 配置说明

### 敏感信息处理

⚠️ **重要**: 上传到 GitHub 前，请确保删除或替换以下敏感信息：

1. **本地路径**: 使用环境变量或配置文件
2. **API Token**: 使用 `.env` 文件并加入 `.gitignore`
3. **数据库文件**: `risk_stocks.db` 加入 `.gitignore`
4. **日志文件**: `logs/*.log` 加入 `.gitignore`
5. **个人配置**: `config/*.local.json` 加入 `.gitignore`

### 推荐 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# 数据库
*.db
*.sqlite
*.sqlite3

# 日志
logs/
*.log

# 敏感配置
config/*.local.json
.env
*.env

# 输出数据
output/
data/
keyword_search_*.json
keyword_result_*.json
unmapped_news_*.json

# 系统
.DS_Store
Thumbs.db
```

### 环境变量配置

创建 `.env` 文件（不要上传到 Git）：

```bash
# 数据库路径
DB_PATH=/path/to/risk_stocks.db

# 日志路径
LOG_DIR=/path/to/logs

# 通知配置（如使用飞书）
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_TOKEN

# 浏览器配置
BROWSER_CDP_PORT=18800
BROWSER_PROFILE=openclaw
```

---

## 📈 使用场景

### 1. 投资决策支持

- 每日自动获取风险股票名单
- 排除风险股票，避免踩雷
- 跟踪持仓股票的风险动态

### 2. 风控系统对接

- 直接读取数据库或 JSON 文件
- 对接量化交易系统
- 自动触发风控规则

### 3. 研究分析

- 统计各行业风险分布
- 分析风险类型趋势
- 跟踪连续多日出现风险的股票

---

## 🎯 性能指标

| 指标 | 目标值 | 实际测试 |
|------|--------|---------|
| 搜索关键词数 | 20 个 | ✅ 20 个 |
| 搜索源 | 2 个 | ✅ 2 个 |
| 股票别名覆盖 | 7000+ | ✅ 7876 条 |
| 股票映射成功率 | >50% | ✅ 53.3% |
| 去重效率 | 100% | ✅ 基于 URL 去重 |
| 执行时间 | <10 分钟 | ✅ 5-7 分钟 |

---

## 🐛 常见问题

### Q1: 浏览器无法启动

**解决**:
1. 确保 Chrome/Chromium 已安装
2. 检查 CDP 端口是否被占用
3. 尝试以调试模式启动浏览器

### Q2: 股票映射失败率高

**解决**:
1. 检查 `stock_aliases` 表是否有数据
2. 手动添加缺失的股票别名
3. 运行 `stock_mapper.py` 更新别名表

### Q3: 定时任务不执行

**解决**:
1. 检查 crontab 配置：`crontab -l`
2. 查看日志：`cat logs/cron.log`
3. 确保 Python 路径正确

### Q4: 数据库锁定

**解决**:
1. 关闭所有正在访问数据库的进程
2. 删除 `risk_stocks.db-journal` 文件
3. 确保程序正常退出

---

## 📝 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)

### v2.0 (2026-04-15)
- ✅ 新增关键词搜索模式（替代遍历模式）
- ✅ 新增第一财经搜索源
- ✅ 集成股票映射功能（7876 条别名）
- ✅ 支持 A+H 股市场
- ✅ 自动去重入库
- ✅ 未映射新闻单独保存

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📧 联系方式

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/hk-risk-news/issues)
- **Email**: your.email@example.com

---

## ⚠️ 免责声明

1. 本系统仅供学习和研究使用
2. 不构成任何投资建议或推荐
3. 数据来源于公开信息，不保证准确性和完整性
4. 使用本系统产生的任何投资损失，作者不承担责任
5. 请遵守相关网站的使用条款和 robots.txt 协议

---

## 🙏 致谢

感谢以下开源项目：

- [OpenClaw](https://github.com/openclaw/openclaw) - 浏览器自动化框架
- [东方财富网](https://www.eastmoney.com/) - 财经数据源
- [第一财经](https://www.yicai.com/) - 财经数据源

---

*最后更新：2026-04-15*
