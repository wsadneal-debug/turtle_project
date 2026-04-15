# F_backtest 策略回测模块 Prompt

> 本文档用于指导 AI 助手理解和维护回测模块。


---

## 一、模块定位

`F_backtest` 是项目的**策略回测模块**，负责基于历史计算结果进行策略验证。

**核心职责**：
1. 按用户指定时间区间遍历交易日
2. 从 `calc_history.db` 读取区间内结果
3. 对每日结果排序并写入历史排名数据库

---

## 二、职责边界

### 2.1 核心职责

| 职责 | 说明 |
|------|------|
| 区间遍历 | 按日期区间遍历交易日 |
| 结果读取 | 从 calc_history.db 读取历史结果 |
| 排序入库 | 排序并写入 ranking_history.db |

### 2.2 禁止事项

- ❌ **不边回测边现算**：只读已落库结果
- ❌ **不修改评分逻辑**：复用 B_scoring
- ❌ **不做组合交易模拟**：由 G_simulated_portfolio 负责

---

## 三、目录结构

```
F_backtest/
├── __init__.py           # 模块入口与导出
├── backtest_schema.py    # 回测数据结构定义
├── backtest_adapter.py   # Legacy 历史数据适配器
├── calc_history_repository.py # calc_history 读取仓库
├── backtest_repository.py # 榜单入库仓库
├── backtest_service.py   # 回测服务编排
├── backtest_runner.py    # 运行编排
└── __main__.py           # CLI 入口
```

---

## 四、核心数据结构

### 4.1 BacktestRequest（回测请求）

表示一次回测任务的输入参数：

| 字段 | 说明 |
|------|------|
| `start_date` | 回测开始日期 |
| `end_date` | 回测结束日期 |
| `market` | 市场范围：`a_share` / `hk_connect` |
| `strategy` | 策略类型：`classic` |
| `branch_key` | 分支标识 |
| `source_type` | 来源类型：`backtest` |
| `top_n` | Top N 数量 |
| `read_from_calc_history` | 是否从 calc_history 读取 |

### 4.2 BacktestDaySummary（单日摘要）

记录单日回测的结果：

| 字段 | 说明 |
|------|------|
| `requested_trade_date` | 请求日期 |
| `resolved_trade_date` | 解析后的实际交易日 |
| `total_snapshots` | 快照总数 |
| `total_rankable` | 可排名总数 |
| `top_symbols` | Top N 股票代码列表 |

### 4.3 BacktestRunResult（回测结果）

记录整体回测执行结果：

| 字段 | 说明 |
|------|------|
| `request` | 原始请求 |
| `run_id` | 任务 ID |
| `status` | 执行状态 |
| `processed_days` | 处理天数 |
| `day_summaries` | 各日摘要列表 |

---

## 五、回测流程设计

### 5.1 流程概述

```
BacktestRequest -> 交易日遍历 -> calc_history 读取 -> 排序 -> 入库
```

### 5.2 交易日遍历

- 按日期区间生成交易日列表
- 处理非交易日跳过逻辑
- 记录请求日期与实际交易日的差异

### 5.3 calc_history 读取

**默认行为**：
- 从 `calc_history.db` 读取 `status=completed AND is_canonical=1` 的结果
- 按 `market + strategy + branch_key + trade_date` 定位

**读取优先级**：
- 默认读取 canonical 结果
- 可通过 `calc_run_id` 指定特定 run

### 5.4 排序入库

- 按 `total_score` 降序排列
- 写入 `ranking_history.db`
- 通过 `branch_key` 区分不同回测分支

---

## 六、历史可见口径

### 6.1 财报可见日期

**设计概念**（不透露具体公式）：
- 财报数据在公告日之后才对投资者可见
- 回测时需考虑财报公告日期
- 避免使用"未来数据"

### 6.2 Legacy 回滚

- 显式指定 `--legacy-read-path` 时使用旧适配器
- 仅用于故障回滚和结果对照
- 不作为默认行为

---

## 七、运行方式

### 7.1 CLI 入口

```bash
python3 -m F_backtest --start-date 2026-03-01 --end-date 2026-03-30 --market a_share --strategy classic
```

### 7.2 参数说明

| 参数 | 说明 |
|------|------|
| `--start-date` | 回测开始日期 |
| `--end-date` | 回测结束日期 |
| `--market` | 市场范围 |
| `--strategy` | 策略类型 |
| `--branch-key` | 分支标识 |
| `--history-db` | 榜单入库路径 |
| `--legacy-read-path` | Legacy 回滚模式 |

---

## 八、与模拟组合的关系

- F_backtest 产出历史榜单
- G_simulated_portfolio 可读取回测榜单进行模拟交易
- 两者通过 ranking_history.db 解耦

---

## 九、AI 助手行为准则

当基于此 Prompt 维护回测模块时，AI 助手应：

1. **保持只读边界**：不添加任何计算逻辑
2. **默认读 calc_history**：不使用 legacy 适配器作为默认
3. **遵循历史可见口径**：正确处理财报公告日期
4. **维护分支区分**：通过 branch_key 区分不同回测
5. **保护敏感信息**：不在代码或文档中暴露任何 Token 或密码

---

**文档版本**: 1.0
**更新日期**: 2026-03-30
