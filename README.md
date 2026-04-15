# 港股风险新闻监控 V2

## 🆕 改进内容

### 1. 结构化风险股票记录
从"新闻记录"变成"标准股票风险记录"：

```json
{
  "stock_code": "00700.HK",
  "stock_name": "腾讯控股",
  "risk_level": "HIGH",
  "risk_type": "监管处罚"
}
```

可直接导入龟龟项目使用。

### 2. 股票映射器
**支持港股 + A股**：
- 港股代码格式：`00700.HK`（5位数字）
- A股代码格式：`600519.SH`（沪市）、`000001.SZ`（深市）

**映射逻辑**：
1. 直接匹配股票代码（高置信度）
2. 模糊匹配公司名称（中等置信度）
3. 别名表：全名 → 简称 → 核心简称

### 3. 数据库表结构

**stock_pool**: 股票池
- stock_code: 股票代码
- stock_name: 股票名称
- industry: 行业
- market: 市场（HK/A）

**stock_aliases**: 股票名称别名
- stock_code: 股票代码
- alias_name: 别名
- alias_type: full/short/core
- market: 市场

**risk_records**: 风险记录
- stock_code: 股票代码
- stock_name: 股票名称
- risk_level: HIGH/MEDIUM
- risk_type: 风险类型

### 4. 核心文件

| 文件 | 功能 |
|------|------|
| `stock_mapper.py` | 股票映射器（港股+A股） |
| `daily_crawler_v2.py` | 结构化风险爬虫 |

## 🔜 待完成

1. **导入完整股票列表**：
   - 港股通：595只
   - A股：沪深300成分股

2. **定时任务**：
   - 每天15:00自动执行
   - 输出结构化风险股票名单

3. **与龟龟项目对接**：
   - JSON格式输出
   - 自动剔除风险股票