# C_daily_scan 每日扫描模块 Prompt

> 本文档用于指导 AI 助手理解和维护每日扫描模块。


---

## 一、模块定位

`C_daily_scan` 是项目的**每日扫描模块**，负责从统一结果库读取数据并生成每日榜单。

**核心职责**：
1. 从 `calc_history.db` 读取当日计算结果
2. 对结果进行排序、切片
3. 导出榜单文件（CSV、JSON）
4. 支持写入 `ranking_history.db`

---

## 二、职责边界

### 2.1 核心职责

| 职责 | 说明 |
|------|------|
| 结果读取 | 从 calc_history.db 读取当日计算结果 |
| 排序切片 | 按 total_score 排序，提取 Top N |
| 文件导出 | 导出 CSV、JSON、摘要文件 |
| 榜单入库 | 写入 ranking_history.db |

### 2.2 禁止事项

- ❌ **不运行时补算**：严禁在扫描过程中自行计算指标
- ❌ **不读取 raw/middle 层**：只读 calc_history.db
- ❌ **不修改评分逻辑**：评分由 B_scoring 负责

---

## 三、目录结构

```
C_daily_scan/
├── __init__.py           # 模块入口与导出
├── daily_scan_schema.py  # 扫描数据结构定义
├── calc_history_adapter.py # calc_history 读取适配器
├── daily_scan_adapter.py  # Legacy 数据库适配器（仅回滚用）
├── daily_scan_engine.py   # 扫描执行引擎
├── daily_scan_ranker.py   # 排序与切片逻辑
├── daily_scan_exporter.py # 文件导出逻辑
├── daily_scan_runner.py   # 运行编排
└── __main__.py           # CLI 入口
```

---

## 四、核心数据结构

### 4.1 DailyScanRequest（扫描请求）

表示一次扫描任务的输入参数：

| 字段 | 说明 |
|------|------|
| `trade_date` | 扫描日期 |
| `market` | 市场范围：`a_share` / `hk_connect` |
| `strategy` | 策略类型：`classic` |
| `top_n` | 核心榜单数量（默认 20） |
| `top_buffer_n` | 缓冲池数量（默认 50） |
| `output_dir` | 输出目录 |

### 4.2 DailyScanResultBundle（扫描结果包）

表示一次扫描任务完成后的结果集合：

| 字段 | 说明 |
|------|------|
| `request` | 原始请求 |
| `trade_date` | 实际扫描日期 |
| `total_snapshots` | 快照总数 |
| `total_scored` | 评分总数 |
| `total_rankable` | 可排名总数 |
| `all_results` | 全部评分结果（未排序） |
| `ranked_results` | 排序后的全部结果 |
| `top_buffer_results` | Top N + 缓冲池 |
| `top_results` | 最终 Top N |
| `export_paths` | 导出文件路径 |

### 4.3 DailyScanExportPaths（导出路径）

记录所有导出文件的路径：

| 字段 | 说明 |
|------|------|
| `all_csv_path` | 全量结果 CSV |
| `ranked_csv_path` | 可排名结果 CSV |
| `top_buffer_csv_path` | 缓冲池 CSV |
| `top_n_csv_path` | Top N CSV |
| `summary_json_path` | 摘要 JSON |
| `summary_txt_path` | 摄要文本 |

---

## 五、扫描流程设计

### 5.1 流程概述

```
DailyScanRequest -> calc_history 读取 -> 排序 -> 切片 -> 导出 -> 入库（可选）
```

### 5.2 calc_history 读取

**默认行为**：
- 从 `calc_history.db` 读取 `status=completed AND is_canonical=1` 的结果
- 按 `market + strategy + branch_key + trade_date` 定位

**Legacy 回滚**：
- 显式指定 `--legacy-read-path` 时使用旧适配器
- 仅用于故障回滚，不是并行正式链路

### 5.3 排序与切片

- 按 `total_score` 降序排列
- 过滤 `rankable=True` 的结果
- 提取 Top N 和缓冲池

### 5.4 文件导出

- 导出 CSV 文件（含全部字段）
- 导出 JSON 摘要（含统计信息）
- 导出文本摘要（人类可读）

### 5.5 榜单入库

可选写入 `ranking_history.db`：
- 通过 `--persist-ranking-db` 参数指定
- 通过 `--persist-branch-key` 指定分支标识

---

## 六、运行方式

### 6.1 CLI 入口

```bash
python3 -m C_daily_scan --date 2026-03-30 --market a_share --strategy classic
```

### 6.2 参数说明

| 参数 | 说明 |
|------|------|
| `--date` | 扫描日期 |
| `--market` | 市场范围 |
| `--strategy` | 策略类型 |
| `--top-n` | Top N 数量 |
| `--persist-ranking-db` | 榜单入库路径 |
| `--persist-branch-key` | 入库分支标识 |
| `--legacy-read-path` | Legacy 回滚模式 |

---

## 七、与发布模块的关系

- C_daily_scan 导出文件后，D_scan_publish 读取并渲染
- 两者通过文件产物解耦
- D_scan_publish 不读取数据库

---

## 八、AI 助手行为准则

当基于此 Prompt 维护扫描模块时，AI 助手应：

1. **保持只读边界**：不添加任何计算逻辑
2. **默认读 calc_history**：不使用 legacy 适配器作为默认
3. **遵循排序规则**：按 total_score 降序，过滤 rankable=True
4. **维护导出格式兼容**：不随意修改 CSV 字段顺序
5. **保护敏感信息**：不在代码或文档中暴露任何 Token 或密码

---

**文档版本**: 1.0
**更新日期**: 2026-03-30
