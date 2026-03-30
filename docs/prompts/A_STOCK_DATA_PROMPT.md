# A_stock_data 数据同步模块 Prompt

> 本文档用于指导 AI 助手理解和维护数据同步模块。


---

## 一、模块定位

`A_stock_data` 是项目的数据基础层，负责：

1. **原始数据同步**：从外部数据源同步 A 股和港股的行情、财务数据
2. **数据库管理**：维护 SQLite 数据库文件
3. **中间层重建**：从原始数据重建派生指标表

---

## 二、职责边界

### 2.1 核心职责

| 职责 | 说明 |
|------|------|
| raw 数据同步 | 同步日线行情、财务报表等原始数据 |
| middle 层重建 | 从 raw 层计算并写入派生指标表 |
| 数据库初始化 | 创建表结构、维护数据字典 |

### 2.2 禁止事项

- ❌ **不写最终榜单结果**：榜单由 C_daily_scan 产出
- ❌ **不直接参与评分**：评分由 B_scoring 负责
- ❌ **不在 raw 层做业务口径改写**：保持原始数据完整性

---

## 三、目录结构

```
A_stock_data/
├── databases/              # SQLite 数据库文件
│   ├── a_daily.db          # A股日线数据库
│   ├── a_financial.db      # A股财报数据库
│   ├── a_computed.db       # A股计算指标数据库
│   ├── hk_daily.db         # 港股日线数据库
│   ├── hk_financial.db     # 港股财报数据库
│   ├── hk_computed.db      # 港股计算指标数据库
│   ├── calc_history.db     # 统一计算结果库
│   └── ranking_history.db  # 统一榜单历史库
└── sync/                   # 数据同步脚本
    ├── fetch_data_v2.py    # A股数据同步
    ├── fetch_hk_data.py    # 港股数据同步
    ├── run_hk_connect_job.py # 港股通名单同步
    ├── rebuild_a_computed_from_raw.py # A股中间层重建
    ├── rebuild_hk_computed_from_raw.py # 港股中间层重建
    └── init_calc_history_schema.py # 统一结果库初始化
```

---

## 四、数据库分层

### 4.1 raw 层（原始数据）

| 数据库 | 核心表 | 说明 |
|--------|--------|------|
| `a_daily.db` | `a_daily_quotes`, `a_daily_basic` | A股日线行情、每日指标 |
| `a_financial.db` | `a_income`, `a_balancesheet`, `a_cashflow`, `a_fina_indicator` | A股财报数据 |
| `hk_daily.db` | `hk_daily_quotes` | 港股日线行情 |
| `hk_financial.db` | `hk_income`, `hk_balancesheet`, `hk_cashflow`, `hk_fina_indicator` | 港股财报数据 |

**raw 层原则**：
- 保持外部数据源的原始字段名
- 不做别名改写或业务口径转换
- 通过 `source` 字段记录数据来源

### 4.2 middle 层（派生指标）

| 数据库 | 核心表 | 说明 |
|--------|--------|------|
| `a_computed.db` | `a_anchor_metrics`, `a_spot_metrics`, `a_ttm_metrics`, `a_valuation_metrics` | A股派生指标 |
| `hk_computed.db` | `hk_anchor_metrics`, `hk_spot_metrics`, `hk_ttm_metrics`, `hk_valuation_metrics` | 港股派生指标 |

**middle 层原则**：
- 作为计算模块的中间输入层
- 不作为排名模块和回测模块的最终输入层
- 派生字段统一使用规范后缀（`_ttm`, `_latest`, `_3y_avg`, `_5y_median` 等）

### 4.3 final 层（统一结果）

| 数据库 | 核心表 | 说明 |
|--------|--------|------|
| `calc_history.db` | `calc_runs`, `calc_entries`, `calc_factor_snapshots` | 统一计算结果 |
| `ranking_history.db` | `ranking_runs`, `ranking_entries` | 统一榜单历史 |

---

## 五、同步脚本职责

### 5.1 A股数据同步

**fetch_data_v2.py**：
- 支持按模式拆分执行：`--mode daily`（日线）、`--mode financial`（财报）
- 同步完成后更新 `updated_at` 时间戳
- 记录数据来源到 `source` 字段

### 5.2 港股数据同步

**fetch_hk_data.py**：
- 同步港股日线行情和财务指标
- 支持按模式拆分执行
- 处理港股特有的字段映射

### 5.3 港股通名单同步

**run_hk_connect_job.py**：
- 同步港股通可交易证券名单
- 维护 `hk_connect_securities` 表
- 作为港股通市场筛选的唯一名单来源

### 5.4 中间层重建

**rebuild_a_computed_from_raw.py / rebuild_hk_computed_from_raw.py**：
- 从 raw 层数据重建 middle 层派生指标
- 支持按日期范围重建
- 不直接写 final 层结果

---

## 六、数据字典规范

项目维护统一的数据字典文件：`A_stock_data/databases/data_dictionary.txt`

**核心原则**：
1. 原始表保持外部数据源官方字段名
2. 市场通过表前缀区分：A 股使用 `a_`，港股使用 `hk_`
3. 非 Tushare 的外部补充数据进入独立标准补充表
4. 派生字段统一后缀：`_ttm`, `_latest`, `_3y_avg`, `_5y_list`, `_5y_median`, `_yoy`, `_ratio`
5. 同一含义只保留一个派生命名，不并存同义别名列

---

## 七、AI 助手行为准则

当基于此 Prompt 维护数据同步模块时，AI 助手应：

1. **保持 raw 层纯净**：不在原始表中添加业务口径字段
2. **遵循数据字典**：新增字段必须符合命名规范
3. **维护 AH 对称**：A 股和港股使用相同的派生逻辑抽象
4. **不越权计算**：派生指标只服务于中间层，不直接写最终榜单
5. **保护敏感信息**：不在代码中暴露数据源 API Token 或连接配置

---

**文档版本**: 1.0
**更新日期**: 2026-03-30
