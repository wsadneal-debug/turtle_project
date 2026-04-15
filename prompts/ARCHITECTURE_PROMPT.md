# Turtle Project 总架构 Prompt

> 本文档用于指导 AI 助手理解和维护 Turtle Project 股票投资分析框架。


---

## 一、项目定位

Turtle Project 是一个模块化的股票投资分析框架，核心目标是为 A 股和港股通市场提供：

1. **数据同步**：从外部数据源同步原始行情与财务数据
2. **统一计算**：基于原始数据计算投资因子并落库
3. **每日扫描**：从统一结果库读取并生成每日榜单
4. **策略回测**：基于历史计算结果进行策略验证
5. **模拟组合**：基于榜单信号进行模拟交易与绩效追踪

---

## 二、核心架构原则

### 2.1 数据流唯一性

项目遵循严格的数据流原则：

```
raw 同步 -> B_compute 计算并落库 -> C_daily_scan / F_backtest / G_simulated_portfolio 只读统一结果
```

**核心约束**：
- 计算模块（B_compute）是**唯一合法**的"读输入数据 -> 调公式 -> 落库"入口
- 其他模块只能**读取**统一结果库，严禁自行补算或混用数据源
- 历史结果一旦落库，后续 raw 数据变动不应隐式改写已落库结果

### 2.2 模块职责边界

| 模块 | 职责 | 禁止事项 |
|------|------|----------|
| `A_stock_data/sync` | 只负责同步原始数据 | ❌ 不写最终榜单结果 |
| `B_scoring` | 纯公式模块，不读库不写库 | ❌ 不依赖数据库连接 |
| `B_compute` | 唯一合法的计算与落库入口 | ❌ 不复用消费模块的适配器 |
| `C_daily_scan` | 只排名、切片、导出、发布 | ❌ 不运行时补算 |
| `D_scan_publish` | 只渲染图片并发送 | ❌ 不读取数据库 |
| `F_backtest` | 只读统一结果进行回测 | ❌ 不边回测边现算 |
| `G_simulated_portfolio` | 只读榜单做模拟交易 | ❌ 不混读 CSV 文件 |

### 2.3 AH 统一设计

A 股与港股通使用：
- 同一套计算流程抽象
- 同一套结果表结构
- 同一套运行维度字段（market, strategy, branch_key）
- 同一套命名规范

---

## 三、数据分层架构

### 3.1 三层数据职责

| 层级 | 数据库 | 职责 |
|------|--------|------|
| **raw 层** | `a_daily.db`, `a_financial.db`, `hk_daily.db`, `hk_financial.db` | 只同步原始数据，不直接作为排名/回测输入 |
| **middle 层** | `a_computed.db`, `hk_computed.db` | 计算模块的中间输入层，不作为最终消费层 |
| **final 层** | `calc_history.db`, `ranking_history.db` | 排名与回测的唯一共享输入层 |

### 3.2 统一结果库设计

**calc_history.db** 核心表：
- `calc_runs`：计算任务记录（含 source_type, run_mode, market, strategy, branch_key）
- `calc_day_summaries`：单日计算摘要
- `calc_entries`：单票最终计算结果（排名与回测主输入）
- `calc_factor_snapshots`：列式因子快照（回测与研究分析）

**ranking_history.db** 核心表：
- `ranking_runs`：榜单生成任务
- `ranking_day_summaries`：单日榜单摘要
- `ranking_entries`：榜单明细

### 3.3 Canonical 规则

- 同一维度 `(source_type, trade_date, market, strategy, branch_key)` 下只允许一条 `is_canonical=1`
- 消费者默认只读取 `status=completed AND is_canonical=1` 的结果
- 严禁使用"最新 created_at"作为默认选择规则

---

## 四、模块目录结构

```
turtle_project/
├── A_stock_data/           # 数据同步与数据库
│   ├── databases/          # SQLite 数据库文件
│   │   ├── a_daily.db      # A股日线
│   │   ├── a_financial.db  # A股财报
│   │   ├── a_computed.db   # A股计算指标
│   │   ├── hk_daily.db     # 港股日线
│   │   ├── hk_financial.db # 港股财报
│   │   ├── hk_computed.db  # 港股计算指标
│   │   ├── calc_history.db # 统一计算结果库
│   │   └── ranking_history.db # 统一榜单历史库
│   └── sync/               # 数据同步脚本
├── B_compute/              # 统一计算模块（核心）
├── B_scoring/              # 评分规则与评分模块
├── C_daily_scan/           # 每日扫描模块
├── D_scan_publish/         # 出图与发布模块
├── E_daily_pipeline/       # 早晚调度入口
├── F_backtest/             # 策略回测模块
├── G_simulated_portfolio/  # 模拟组合回测
├── config/                 # 项目配置
├── cooke/                  # 缓存与运行期辅助文件
├── output/                 # 历史扫描产物与发布图片
├── docs/                   # 文档目录
└── test/                   # 测试脚本
```

---

## 五、策略与分支扩展规范

### 5.1 维度设计

| 维度 | 说明 | 示例 |
|------|------|------|
| `strategy` | 策略大类 | `classic` |
| `branch_key` | 同一策略下的计算分支 | `live_main`, `classic_v1` |
| `branch_label` | 分支展示名 | "主线", "经典基线" |
| `source_type` | 来源类型 | `daily_scan`, `backtest` |

### 5.2 扩展规则

- 新增策略优先扩展 `strategy`
- 微调型分支优先扩展 `branch_key`
- 禁止为每个策略新建一套表
- 禁止因为新增策略复制一套排名流程

---

## 六、命名规范

### 6.1 表命名

- 原始/市场专属层：使用 `a_` / `hk_` 前缀
- 跨市场统一结果层：使用 `calc_` / `ranking_` 前缀

### 6.2 字段命名后缀

| 后缀 | 含义 |
|------|------|
| `_ttm` | 滚动十二个月 |
| `_latest` | 最近一期时点值 |
| `_3y_avg` | 3年均值 |
| `_5y_list` | 5年列表 |
| `_5y_median` | 5年中位数 |
| `_ratio` | 比率 |
| `_json` | JSON 扩展字段 |

### 6.3 禁止事项

- ❌ 禁止新增同义别名列
- ❌ 禁止 raw 层引入业务口径字段
- ❌ 禁止跨市场统一表使用 `a_` / `hk_` 前缀

---

## 七、运行方式

### 7.1 晚间调度流程

```bash
cd E_daily_pipeline
python3 run_daily.py
```

流程顺序：
1. 港股通名单同步
2. A/H 行情同步
3. 4 组 B_compute 计算
4. 4 组 C_daily_scan 扫描
5. 发布确认

### 7.2 早间财报同步

```bash
cd E_daily_pipeline
python3 run_morning_financial_sync.py
```

### 7.3 模拟组合回测

```bash
python3 -m G_simulated_portfolio
```

---

## 八、验收标准

### 8.1 架构验收

- `B_compute` 不再 `import C_daily_scan.*`
- `C_daily_scan` 默认只读 `calc_history`
- `F_backtest` 默认只读 `calc_history`
- `G_simulated_portfolio` 不再读取 CSV 结果文件

### 8.2 结果验收

- 同一 `run_id` 结果可重复读取
- 后续 raw 数据更新不会隐式改写已落库日榜
- 回测可精确指定 `market + strategy + branch_key + source_type`

---

## 九、AI 助手行为准则

当基于此 Prompt 进行代码维护或扩展时，AI 助手应：

1. **严格遵守模块边界**：不在消费模块中添加计算逻辑
2. **保持数据流唯一性**：不引入新的数据源混用
3. **遵循命名规范**：新增字段必须符合数据字典
4. **维护 AH 统一性**：A 股与港股通使用相同抽象
5. **保护敏感信息**：不在代码或文档中暴露任何 Token、密码、连接配置

---

**文档版本**: 1.0
**更新日期**: 2026-03-30
