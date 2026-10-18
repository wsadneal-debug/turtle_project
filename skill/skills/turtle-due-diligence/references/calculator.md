# 可选零模型计算器
Python 3.10+标准库即可，在Skill目录执行，或使用脚本绝对路径；从任何工作目录可运行。无网络、无数据库、无模型调用，不写输入文件。没有Python用宿主计算器核对同一算式即可，不阻断研究。示例全部为合成数据，金额同币种/量级；百分数20表示20%，不是0.20。

```bash
python3 scripts/calculate.py --input /path/to/scenario.json
```
```json
{"operation":"cash_path","inputs":{"cash_base":180,"annual_fcf":[56,32,8,-16,-40,-64],"market_cap":660,"price":10}}
```
```json
{"operation":"returns","inputs":{"owner_cash":80,"ordinary_dividends":60,"qualified_buybacks":30,"dividend_tax_pct":20,"market_cap":660,"price":10,"required_return_pct":6}}
```
```json
{"operation":"routing","inputs":{"flat_coverage_6y":0.65,"conditional_return_pct":3.9,"required_return_pct":6}}
```

`cash_path`接收同币种/量级的现金底座、六个已归母年度估计 `annual_fcf`、市值和股价；年度值可正可负。按[现金回本](absolute-valuation.md)完成正常化与项目阶段分析后直接输入，不重复归属、截零、叠加斜率或限幅。平坦对照使用第一年现金。脚本只核算，不验证证据或买入资格。

仅复现旧路径或无法合理估计时明确调用 `legacy_cash_path`，输入旧字段 `starting_fcf`、`delta_base`、`projection`、`annual_change_pct` 以及现金底座/市值/股价。其结果标记 `calculation_basis=legacy_reference`，旧截零/10%规则保持；不能将其当作新的正常化预测或已核实现金安全。默认操作不静默接受旧字段。

`returns`只计算已核实的税前共享容量、普通股息优先、合格注销回购次之，税只扣股息。金额不得以负值冲抵；缺失买回记录不能填零，已核实没有合格回购才可0。核实来源、去重、可持续性、容量调整、有效期限与FX由研究者按[穿透回报](lookthrough-return.md)处理，脚本不自动分类或延长承诺。要求回报null时仍算GG，不算价格与门槛；港股加点区间分别运行端点，不默选有利端。

`routing`只做65%资源分流；缺必要值返回needs_input。调用前完成来源核查，不把未核金额送入后宣称研究获批。所有操作都回显输入并标记 `evidence_verified=false`、`strategy_eligibility=not_assessed`；输入错误退出2，不将错误改成通过。输入JSON可选用 `--input -` 从stdin读取。
