# 便携运行与内部资料合同

需要本地文件读取/写入和Python 3.10+。把`<skill>`替换为当前技能安装目录，`<work>`替换为用户本轮输出目录。随包脚本使用标准库和包内计算代码，无需仓库、私库、模型CLI、API凭据或系统安装。它不会联网研究、自动提取PDF财务数或自动完成AI阶段。

## 命令

```bash
python3 <skill>/scripts/run.py --help
python3 <skill>/scripts/run.py prepare --packet <work>/packet.json --method asset --run-dir <work>/asset
python3 <skill>/scripts/run.py recalculate --run-dir <work>/asset --valuation <work>/asset-valuation.json

python3 <skill>/scripts/run.py prepare --packet <work>/packet.json --method epv --run-dir <work>/epv --asset-run <work>/asset
python3 <skill>/scripts/run.py recalculate --run-dir <work>/epv --valuation <work>/epv-valuation.json

python3 <skill>/scripts/run.py growth --epv-run <work>/epv --run-dir <work>/growth --request <work>/growth-request.json
python3 <skill>/scripts/run.py recalculate --run-dir <work>/growth --valuation <work>/growth-valuation.json
```

`prepare`只支持asset/epv；`growth`从明确选择的同企业EPV建立新输入，两者可选`--asset-run`。growth另可选`--as-of YYYY-MM-DD`，它只改研究截止日，不表示源财务存量已更新。没有资产研究时省略`--asset-run`，不为此补跑。准备目录必须为新目录，不覆盖旧研究。`recalculate`可选`--method asset|epv|growth`核对方法；省略`--valuation`则复用本轮已存参数。脚本无`analyze`命令，计划/提取/专项/综合/复核由宿主AI完成。

prepare保存原packet副本与规范化的`input.json`；具名原文复制到`materials`，相对源路径按packet所在目录解释。不要改写用户源文件。已有运行迁移后应检查文本和报告引用是否仍有效，使用本轮复制文件，勿靠原机器绝对目录。`recalculate`保存最终`valuation.json`（含实际calculation）和`report.md`；任何实际算过/未算过的结论以执行终态和calculation内容为准。更新参数后必须重新执行，不能手改报告总数。

## packet：宿主生成，用户来源不必长这样

```json
{
  "simulation": true,
  "issuer": {"code": "DEMO.HK", "name": "合成企业", "market": "HK"},
  "as_of": "2026-10-17",
  "currency": "CNY",
  "shares": {"value": 100000000, "date": "2026-06-30", "source": "合成教学假设"},
  "snapshots": [{
    "period_end": "2026-06-30", "report_type": "interim", "currency": "CNY", "scope": "consolidated",
    "canonical": {
      "cash": {"value": 100000000, "unit": "currency", "currency": "CNY", "raw_value": 100000, "raw_unit": "千元", "source": {"report": "合成中报", "page": 1, "origin": "synthetic"}},
      "operating_cashflow": {"value": null, "unit": "currency", "currency": "CNY", "source": {"origin": "not_available"}}
    },
    "statements": {"balance": [], "income": [], "cashflow": []},
    "report_facts": []
  }],
  "reports": [
    {"period_end": "2024-12-31", "report_type": "annual", "text_path": "materials/synthetic-2024.txt", "currency": "CNY"},
    {"period_end": "2025-12-31", "report_type": "annual", "text_path": "materials/synthetic-2025.txt", "currency": "CNY"},
    {"period_end": "2026-06-30", "report_type": "interim", "text_path": "materials/synthetic-2026H1.txt", "currency": "CNY"}
  ]
}
```

最少顶层用`issuer/code/name/market`、`as_of`、`currency`、`shares`（数值、上述事实对象或null）、`snapshots`和`reports`。事实缺失保留null；可使用空数组并披露缺口，不编造原始报表。示例不要求所有用户数据都映射到canonical；只把实际使用且明确语义的事实映射过来。

快照：`period_end`为实际期末，`report_type=annual|interim|quarterly`；`canonical`是语义键到事实对象的映射。原字段事实可放`statements.income/balance/cashflow`列表，每项另有`field`、`value/unit/currency`和`source`；`report_facts`可保留附注原事实。来源可附报告、页码、URL、表/字段及原提取依据；不要写未实际取得的引用。用于历史复用的推荐语义键为`revenue`、`reported_operating_profit`、`operating_cashflow`、`capital_expenditure`；只映射已核对口径的事实，原报表营业利润不自动改名EBIT。

历史可省略，由packet现有快照整理，不能凭空产生缺失年份。显式提供`history`时：`requested_years`为请求年数整数，`annual_periods`为实际取得的完整年度期数整数（**不是年份列表**），`periods`才是期间对象列表；每期包含`period_end/report_type/currency/scope/metrics`，其中`metrics`与快照canonical一样，是语义键到完整事实对象的映射，不是直接数字。可另保留`report_facts`；`ttm_reference`为语义键到TTM事实的对象，缺失/不可比时用空对象{}，`warnings`为说明列表。例如仅取得一个合成年期的有效形状：

```json
{
  "requested_years": 1,
  "annual_periods": 1,
  "periods": [{
    "period_end": "2025-12-31", "report_type": "annual", "currency": "CNY", "scope": "consolidated",
    "metrics": {
      "revenue": {"value": 1000000000, "unit": "currency", "currency": "CNY", "source": {"origin": "synthetic"}},
      "reported_operating_profit": {"value": 200000000, "unit": "currency", "currency": "CNY", "source": {"origin": "synthetic"}}
    },
    "report_facts": []
  }],
  "ttm_reference": {},
  "warnings": ["仅合成一个年度，无可比累计期，不生成TTM；不代表充分周期历史。"]
}
```

报告项至少给实际可读`path`和/或`text_path`，可附`url`、`publication_date`及上述期间信息。只有URL不足以让这个离线辅助器取得报告；AI先用可用工具取得本轮文件。PDF路径与文本路径可同时保留，扫描件需如实披露OCR状态。合成样本的短文本仅作文件接线演示，即使文件准备检查通过，也不证明真实报告全文研究。

## 估值参数与价格重算

三个估值对象分别看[asset](asset.md)、[epv](epv.md)、[growth](growth.md)。金额全部为计价币种基本单位，比例小数，股数用股；未知留null，明确估计才填数。可选`materials_read`、`sources`、`assumptions`、`adoptions`、`review`保留实际研究，无统一证据树。

仅价格对照：资产/EPV的价值不随股票报价自动改变，只更新报价/换汇比较；成长把完整价格对象放已有`price_grid`后重算，保持经营参数及本轮冻结policy。若用户明确改了基准价格/政策，应建立新growth输入（新request）或明确的新运行，说明旧新差别，不能在旧冻结请求上悄悄改值。单纯重算零新增研究；不会补做阅读、修正旧判断或复活skip/defer。

## 合成演示

`assets/packet-synthetic.json`与同目录`materials`可直接喂prepare；`asset-synthetic.json`和`epv-synthetic.json`可用于各自recalculate。`growth-request-synthetic.json`用于新growth准备；`growth-synthetic.json`使用reuse_epv，匹配上述CNY合成EPV及request，可直接用于最后一条recalculate。冻结EPV的E=1.4亿、S=10亿、B=−1.5亿、WACC10%，合成Q=15亿，M=16.5亿；基准衰减前回报约13.0364%，未量化净回报。示例均明确为合成，不能成为真实公司的默认参数。
