# G_simulated_portfolio 模拟组合模块 Prompt

> 本文档用于指导 AI 助手理解和维护模拟组合模块。


---

## 一、模块定位

`G_simulated_portfolio` 是项目的**模拟组合模块**，负责基于榜单信号进行模拟交易与绩效追踪。

**核心职责**：
1. 从 `ranking_history.db` 读取榜单信号
2. 根据交易规则进行模拟买卖
3. 记录持仓状态和交易记录
4. 计算组合绩效并生成报表

---

## 二、职责边界

### 2.1 核心职责

| 职责 | 说明 |
|------|------|
| 信号读取 | 从 ranking_history.db 读取榜单 |
| 交易执行 | 根据规则进行模拟买卖 |
| 状态管理 | 维护持仓和账户状态 |
| 绩效计算 | 计算收益率并生成报表 |

### 2.2 禁止事项

- ❌ **不混读 CSV 文件**：只从数据库读取信号
- ❌ **不自行计算榜单**：榜单由 C_daily_scan / F_backtest 产出
- ❌ **不做真实交易**：仅模拟，不涉及真实资金

---

## 三、目录结构

```
G_simulated_portfolio/
├── __init__.py           # 模块入口
├── schema.py             # 数据结构定义
├── portfolio_config.py   # 组合配置
├── portfolio_db.py       # 状态数据库管理
├── repository.py         # 数据访问层
├── service.py            # 交易服务
├── runner.py             # 运行编排
├── improved.py           # 报表生成
├── history_benchmark_report.py # 历史对比报表
└── __main__.py           # CLI 入口
```

---

## 四、核心数据结构

### 4.1 BookConfig（组合配置）

定义一个模拟组合的配置：

| 字段 | 说明 |
|------|------|
| `key` | 组合标识 |
| `market` | 市场范围 |
| `strategy` | 策略类型 |
| `artifact_prefix` | 产物前缀 |
| `history_branch_key` | 榜单分支标识 |

### 4.2 PositionState（持仓状态）

记录单只股票的持仓状态：

| 字段 | 说明 |
|------|------|
| `book_key` | 组合标识 |
| `ts_code` | 股票代码 |
| `base_trade_date` | 首次建仓日期 |
| `base_price` | 首次建仓价格 |
| `base_shares` | 首次建仓股数 |
| `level1_active` | 一级仓位是否活跃 |
| `level2_active` | 二级仓位是否活跃 |
| `off_rank_days` | 跌出榜单天数 |

### 4.3 BookAccount（账户状态）

记录组合账户的资金状态：

| 字段 | 说明 |
|------|------|
| `book_key` | 组合标识 |
| `initial_capital` | 初始资金 |
| `cash` | 当前现金 |
| `realized_pnl` | 已实现盈亏 |
| `dividends_received` | 收到的分红 |

### 4.4 TradeAction（交易动作）

记录一次交易的动作：

| 字段 | 说明 |
|------|------|
| `side` | 买卖方向 |
| `lot_type` | 仓位类型 |
| `shares` | 交易股数 |
| `price` | 交易价格 |
| `reason` | 交易原因 |

---

## 五、交易规则设计

### 5.1 建仓规则

**设计概念**：
- 当日榜单前 N 名首次出现时建仓
- 单票单次建仓不超过指定金额
- 不设置总仓位上限

### 5.2 持仓规则

**设计概念**：
- 持仓满指定时间后，不在榜单前 N 名则卖出
- 记录跌出榜单的天数
- 若后续重新回到榜单，允许再次买入

### 5.3 分红处理

- A 股现金分红按除权日记入现金
- 同步降低持仓成本价

---

## 六、组合配置

### 6.1 默认组合

项目默认维护 4 个组合：

| 组合 | 市场 | 策略 | 分支标识 |
|------|------|------|----------|
| `a_share_classic` | A股 | classic | `sim_a_classic_v1` |
| `hk_connect_classic` | 港股通 | classic | `sim_hk_classic_v1` |


### 6.2 默认资金

- 每个组合初始资金：本地货币
- 不做汇率转换，A股/港股各用本地货币记账

---

## 七、运行方式

### 7.1 CLI 入口

```bash
python3 -m G_simulated_portfolio
```

### 7.2 指定日期或组合

```bash
python3 -m G_simulated_portfolio --date 2026-03-30
python3 -m G_simulated_portfolio --book a_share_classic
```

### 7.3 区间回放

```bash
python3 -m G_simulated_portfolio --start-date 2026-03-01 --end-date 2026-03-30 --reset
```

### 7.4 参数说明

| 参数 | 说明 |
|------|------|
| `--date` | 单日执行 |
| `--book` | 指定组合 |
| `--start-date` | 区间开始 |
| `--end-date` | 区间结束 |
| `--reset` | 重置状态 |

---

## 八、报表生成

### 8.1 每日报表

```bash
cd G_simulated_portfolio
python3 improved.py --date 20260330
```

生成内容：
- 各组合净值曲线图
- 持仓明细
- 交易记录

### 8.2 历史对比报表

```bash
python3 G_simulated_portfolio/history_benchmark_report.py --start-date 2026-03-01 --end-date 2026-03-30
```

生成内容：
- 组合收益率 vs 基准收益率
- 超额收益曲线

---

## 九、状态数据库

模拟组合状态落到：

```
cooke/simulated_portfolio/portfolio.db
```

核心表：
- `book_accounts`：账户状态
- `positions`：持仓状态
- `trades`：交易记录
- `daily_summaries`：每日摘要

---

## 十、AI 助手行为准则

当基于此 Prompt 维护模拟组合模块时，AI 助手应：

1. **保持只读信号边界**：不混读 CSV 文件
2. **维护状态一致性**：正确处理分红、成本调整
3. **遵循组合配置**：不随意修改默认组合设置
4. **保护敏感信息**：不在代码或文档中暴露任何 Token 或密码

---

**文档版本**: 1.0
**更新日期**: 2026-03-30
