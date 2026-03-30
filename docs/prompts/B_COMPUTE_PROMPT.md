# B_compute 统一计算模块 Prompt

> 本文档用于指导 AI 助手理解和维护统一计算模块。


---

## 一、模块定位

`B_compute` 是项目的**核心计算模块**，是唯一合法的"读输入数据 -> 调公式 -> 落库"入口。

**核心职责**：
1. 交易日解析与验证
2. A/H 输入数据加载
3. 快照与因子构造
4. 调用评分引擎计算
5. 结果落库到 `calc_history.db`

---

## 二、职责边界

### 2.1 核心职责

| 职责 | 说明 |
|------|------|
| 输入加载 | 从 raw/middle 层加载 A 股和港股通数据 |
| 快照构造 | 构造评分引擎所需的 SecuritySnapshot |
| 因子计算 | 调用 B_scoring 进行评分计算 |
| 结果落库 | 写入 calc_history.db 的统一结果表 |

### 2.2 禁止事项

- ❌ **不复用消费模块适配器**：不依赖 C_daily_scan 的数据适配器
- ❌ **不做排名逻辑**：排名由 C_daily_scan 负责
- ❌ **不直接发布**：发布由 D_scan_publish 负责

---

## 三、目录结构

```
B_compute/
├── __init__.py           # 模块入口与导出
├── schema.py             # 核心数据类定义
├── compute_request.py    # 计算请求结构
├── compute_adapter.py    # A/H 输入适配器
├── compute_repository.py # 数据库访问层
├── compute_runner.py     # 计算流程编排
├── compute_service.py    # 高层服务接口
└── __main__.py           # CLI 入口
```

---

## 四、核心数据结构

### 4.1 ComputeRequest（计算请求）

表示一次统一计算请求的输入参数：

| 字段 | 说明 |
|------|------|
| `trade_date` | 实际要计算的交易日 |
| `requested_trade_date` | 用户请求的目标日期 |
| `market` | 市场范围：`a_share` / `hk_connect` |
| `strategy` | 策略大类：`classic` |
| `branch_key` | 同一策略下的计算分支 |
| `branch_label` | 分支展示名 |
| `source_type` | 来源类型：`daily_scan` / `backtest` |
| `run_mode` | 运行模式：`incremental` / `rebuild` |

### 4.2 ComputeRun（计算任务记录）

记录一次计算任务的运行信息：

| 字段 | 说明 |
|------|------|
| `id` | 任务唯一标识 |
| `status` | 任务状态：`pending` / `running` / `completed` / `failed` |
| `is_canonical` | 是否为该维度的正式结果 |
| `request_hash` | 请求参数哈希（用于幂等判断） |
| `rules_version` | 规则文件版本 |
| `calc_version` | 代码实现版本 |

### 4.3 ComputeEntry（单票计算结果）

记录单只股票的最终计算结果：

| 字段 | 说明 |
|------|------|
| `ts_code` | 股票代码 |
| `rankable` | 是否可参与排名 |
| `passed_tier1` | 是否通过第一层筛选 |
| `passed_tier15` | 是否通过预筛选 |
| `passed_tier2_hard` | 是否通过硬门槛 |
| `safety_score` | 安全维度分数 |
| `dividend_score` | 分红维度分数 |
| `valuation_score` | 估值维度分数 |
| `total_score` | 总分 |
| `fail_reasons_json` | 失败原因列表 |
| `raw_metrics_json` | 原始指标快照 |

### 4.4 ComputeFactorSnapshot（因子快照）

为回测和研究分析提供列式因子数据：

| 字段 | 说明 |
|------|------|
| `debt_to_assets_latest` | 最新资产负债率 |
| `roe_5y_median` | 5年ROE中位数 |
| `profit_dedt_positive_years_5y` | 5年扣非净利润为正年数 |
| `dividend_years_5y` | 5年有分红年数 |
| `fcf_positive_years_5y` | 5年自由现金流为正年数 |
| `cmr` | 现金回报率 |
| `ev_ebitda` | 企业价值/EBITDA |

---

## 五、计算流程设计

### 5.1 流程概述

```
ComputeRequest -> 交易日解析 -> 输入加载 -> 快照构造 -> 评分计算 -> 结果落库
```

### 5.2 交易日解析

- 根据请求日期解析实际交易日
- 处理非交易日顺延逻辑
- 记录 `requested_trade_date` 与实际 `trade_date` 的差异

### 5.3 输入加载

**设计概念**（不透露具体公式）：
- 从 raw/middle 层加载行情数据
- 从 raw/middle 层加载财务数据
- 处理数据缺失的 fallback 逻辑
- 处理港股通特有的字段映射

### 5.4 快照构造

**设计概念**（不透露具体公式）：
- 将加载的数据转换为评分引擎所需的 SecuritySnapshot
- 处理多年指标的聚合（如 5年中位数、3年均值）
- 处理估值指标的派生计算
- 记录数据来源日期信息

### 5.5 评分计算

- 调用 B_scoring 的评分引擎
- 支持 classic 规则
- 返回 ScoreResult 

### 5.6 结果落库

- 写入 `calc_runs`：任务记录
- 写入 `calc_day_summaries`：单日摘要
- 写入 `calc_entries`：单票结果
- 写入 `calc_factor_snapshots`：因子快照

---

## 六、幂等与 Canonical 规则

### 6.1 幂等判断

- 同一请求参数再次触发时，先按 `request_hash` 查重
- 如已存在 `status=completed AND is_canonical=1` 的同请求 run，默认复用
- 显式指定 `force_rerun=true` 时创建新 run

### 6.2 Canonical 维度

- `(source_type, trade_date, market, strategy, branch_key)` 下只允许一条 `is_canonical=1`
- `incremental` 模式默认可写 canonical
- `rebuild` 模式必须显式 `promote_to_canonical` 才能替换

---

## 七、运行方式

### 7.1 CLI 入口

```bash
python3 -m B_compute --date 2026-03-30 --market a_share --strategy classic
```

### 7.2 参数说明

| 参数 | 说明 |
|------|------|
| `--date` | 计算日期 |
| `--market` | 市场范围 |
| `--strategy` | 策略类型 |
| `--branch-key` | 分支标识 |
| `--force-rerun` | 强制重算 |
| `--dry-run` | 试运行模式 |

---

## 八、AI 助手行为准则

当基于此 Prompt 维护计算模块时，AI 助手应：

1. **保持模块独立性**：不依赖消费模块的适配器实现
2. **遵循数据流原则**：只从 raw/middle 层读取，只写 final 层
3. **维护幂等规则**：正确处理 request_hash 和 canonical 判断
4. **不透露计算公式**：只描述设计概念，不暴露具体计算细节
5. **保护敏感信息**：不在代码或文档中暴露任何 Token 或密码

---

**文档版本**: 1.0
**更新日期**: 2026-03-30
