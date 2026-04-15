# 港股风险新闻监控系统

🔴 **自动监控 A/H 股市场风险新闻，智能识别风险股票，生成结构化风险名单**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)

---

## 📋 项目介绍

本系统通过**关键词搜索**方式，自动从多个财经网站抓取 A 股和港股市场的风险新闻，智能识别风险股票，生成可直接用于投资决策的结构化风险名单。

### 核心功能

- ✅ **20 个风险关键词**覆盖所有风险类型
- ✅ **多搜索源支持**：东方财富网、第一财经
- ✅ **A+H 股市场覆盖**：7876 条股票别名
- ✅ **智能股票映射**：自动映射到股票代码
- ✅ **自动去重入库**：基于 URL 去重
- ✅ **定时自动执行**：每天 18:00

---

## 📁 项目结构

```
turtle_project/
├── core/                      # 核心代码
│   ├── keyword_crawler.py     # 主爬虫程序
│   ├── browser_keyword_search.py  # 浏览器搜索工具
│   ├── scheduler.py           # 定时任务调度器
│   ├── stock_mapper.py        # 股票映射工具
│   └── database_manager.py    # 数据库管理
├── scripts/                   # 辅助脚本
│   ├── batch_fetch.sh         # 批量抓取脚本
│   ├── batch_process.py       # 批量处理脚本
│   └── install_cron.sh        # Cron 安装脚本
├── docs/                      # 项目文档
│   ├── README_GITHUB.md       # GitHub 详细说明
│   ├── DEPLOYMENT_CHECKLIST.md # 部署检查清单
│   ├── DATABASE.md            # 数据库字典
│   └── ...                    # 其他文档
├── legacy/                    # 历史代码（保留参考）
│   ├── daily_crawler.py       # 旧版爬虫
│   ├── cdp_crawler.py         # CDP 爬虫
│   └── ...                    # 其他历史文件
├── config/                    # 配置文件
├── examples/                  # 示例代码
├── tests/                     # 测试代码
├── logs/                      # 日志目录（.gitignore）
├── output/                    # 输出目录（.gitignore）
├── data/                      # 数据目录（.gitignore）
├── .gitignore                 # Git 忽略配置
├── .env.example               # 环境变量模板
├── requirements.txt           # Python 依赖
└── README.md                  # 本文件
```

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone git@github.com-myrepo:wsadneal-debug/turtle_project.git
cd turtle_project
```

### 2. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库路径等
```

### 4. 初始化数据库

```bash
cd core
python3 database_manager.py --init
```

### 5. 运行爬虫

```bash
# 手动运行一次
python3 keyword_crawler.py

# 或设置定时任务
../scripts/install_cron.sh
```

---

## 📖 详细文档

- **完整说明**: [docs/README_GITHUB.md](docs/README_GITHUB.md)
- **部署指南**: [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)
- **数据库字典**: [docs/DATABASE.md](docs/DATABASE.md)

---

## 🔧 核心模块

### keyword_crawler.py
主爬虫程序，负责：
- 加载搜索结果 JSON
- 股票名称映射（7876 条别名）
- 数据去重
- 写入数据库

### browser_keyword_search.py
浏览器搜索工具，负责：
- 控制浏览器访问搜索页面
- 提取搜索结果
- 支持多搜索源

### scheduler.py
定时任务调度器，负责：
- 每天 18:00 自动执行
- 错误处理和日志记录
- 发送通知

### stock_mapper.py
股票映射工具，负责：
- 加载股票别名表
- 模糊匹配公司名称
- 返回股票代码和置信度

---

## 📊 风险类型

| 类别 | 关键词 | 风险等级 |
|------|--------|---------|
| 监管处罚 | 立案调查、行政处罚、监管函、问询函 | 🔴 高 |
| 债务违约 | 债务违约、债券违约、无法兑付、债务逾期 | 🔴 高 |
| 停牌风险 | 停牌、暂停上市、终止上市 | 🔴 高 |
| 审计问题 | 审计师辞任、无法表示意见、财报延期 | 🟡 中 |
| 经营风险 | 破产清算、资产冻结、重大亏损 | 🟡 中 |
| 高管变动 | 实控人被捕、董事长辞职、被调查 | 🟡 中 |

---

## ⚠️ 免责声明

1. 本系统仅供学习和研究使用
2. 不构成任何投资建议
3. 数据来源于公开信息，不保证准确性
4. 请遵守相关网站的使用条款

---

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

*最后更新：2026-04-15*
