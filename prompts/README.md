# Turtle Project Prompt 文档索引

> 本目录包含用于指导 AI 助手理解和维护 Turtle Project 的 Prompt 文档。


---

## 文档列表

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE_PROMPT.md](./ARCHITECTURE_PROMPT.md) | **总架构 Prompt** - 项目整体架构、核心原则、数据流设计 |
| [A_STOCK_DATA_PROMPT.md](./A_STOCK_DATA_PROMPT.md) | **数据同步模块** - 数据分层、同步脚本职责、命名规范 |
| [B_COMPUTE_PROMPT.md](./B_COMPUTE_PROMPT.md) | **统一计算模块** - 计算流程、数据结构、幂等规则（仅设计概念） |
| [B_SCORING_PROMPT.md](./B_SCORING_PROMPT.md) | **评分模块** - 评分流程、规则配置（仅设计概念） |
| [C_DAILY_SCAN_PROMPT.md](./C_DAILY_SCAN_PROMPT.md) | **每日扫描模块** - 扫描流程、排序切片、文件导出 |
| [D_SCAN_PUBLISH_PROMPT.md](./D_SCAN_PUBLISH_PROMPT.md) | **发布模块** - 渲染设计、发送抽象 |
| [E_DAILY_PIPELINE_PROMPT.md](./E_DAILY_PIPELINE_PROMPT.md) | **调度模块** - 流程编排、通知设计 |
| [F_BACKTEST_PROMPT.md](./F_BACKTEST_PROMPT.md) | **回测模块** - 区间遍历、历史可见口径 |
| [G_SIMULATED_PORTFOLIO_PROMPT.md](./G_SIMULATED_PORTFOLIO_PROMPT.md) | **模拟组合模块** - 交易规则、绩效计算（仅设计概念） |

---

## 使用说明

### 1. 总架构 Prompt

`ARCHITECTURE_PROMPT.md` 是核心文档，应首先阅读。它定义了：

- 项目整体定位和目标
- 核心架构原则（数据流唯一性、模块职责边界）
- 数据分层架构（raw/middle/final）
- 模块目录结构
- 策略与分支扩展规范
- 命名规范
- AI 助手行为准则

### 2. 模块 Prompt

各模块 Prompt 详细描述了：

- 模块定位和职责边界
- 目录结构
- 核心数据结构
- 流程设计
- 运行方式
- AI 助手行为准则

### 3. 敏感信息保护

所有文档遵循以下原则：

- ❌ 不包含 API Token、数据库密码、飞书连接配置
- ❌ 不包含数据源接口密钥
- ❌ 不包含私人仓库访问信息

---

## 模块关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                    E_daily_pipeline (调度)                       │
│                         ↓                                       │
├─────────────────────────────────────────────────────────────────┤
│  A_stock_data/sync (数据同步)                                    │
│         ↓                                                       │
│  raw 层 → middle 层                                             │
│         ↓                                                       │
├─────────────────────────────────────────────────────────────────┤
│  B_compute (统一计算)                                            │
│         ↓                                                       │
│  calc_history.db (统一结果库)                                    │
│         ↓                                                       │
├─────────────────────────────────────────────────────────────────┤
│  C_daily_scan (每日扫描)                                         │
│         ↓                                                       │
│  ranking_history.db (榜单历史库)                                 │
│         ↓                                                       │
├─────────────────────────────────────────────────────────────────┤
│  D_scan_publish (发布)                                          │
│         ↓                                                       │
│  图片渲染 → 发送                                                 │
├─────────────────────────────────────────────────────────────────┤
│  F_backtest (回测)                                              │
│         ↓                                                       │
│  ranking_history.db                                             │
│         ↓                                                       │
├─────────────────────────────────────────────────────────────────┤
│  G_simulated_portfolio (模拟组合)                                │
│         ↓                                                       │
│  portfolio.db (状态库)                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心原则摘要

### 数据流唯一性

```
raw 同步 → B_compute 计算并落库 → C_daily_scan / F_backtest / G_simulated_portfolio 只读统一结果
```

### 模块职责边界

| 模块 | 职责 | 禁止 |
|------|------|------|
| A_stock_data/sync | 只同步原始数据 | ❌ 不写最终榜单 |
| B_scoring | 纯公式，不读库不写库 | ❌ 不依赖数据库 |
| B_compute | 唯一合法计算与落库入口 | ❌ 不复用消费模块适配器 |
| C_daily_scan | 只排名、切片、导出 | ❌ 不运行时补算 |
| D_scan_publish | 只渲染图片并发送 | ❌ 不读取数据库 |
| F_backtest | 只读统一结果回测 | ❌ 不边回测边现算 |
| G_simulated_portfolio | 只读榜单做模拟交易 | ❌ 不混读 CSV 文件 |

---

**文档版本**: 1.0
**更新日期**: 2026-03-30
