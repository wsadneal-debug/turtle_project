# Optional zero-model calculator
Python 3.10+ standard library suffices. Run from the skill directory or use the script's absolute path from any working directory. No network, database, model calls or input writes. Without Python, use a host calculator for the same formulas; research is not blocked. All examples are synthetic, with consistent currency/scale. Percentage 20 means 20%, not 0.20.

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

`cash_path` accepts same-currency/scale cash stock, six already-parent-attributed annual estimates in `annual_fcf`, market cap and price. Annual values may be positive or negative. Prepare normalization and project-stage analysis under [cash payback](absolute-valuation.md), then use the path directly without reattribution, flooring, slopes or caps. Flat comparison uses year-one cash. The script checks arithmetic, not evidence or investment eligibility.

Only for explicit legacy reproduction or when a forecast cannot reasonably be estimated, use `legacy_cash_path` with `starting_fcf`, `delta_base`, `projection`, `annual_change_pct` and cash stock/market cap/price. It labels results `calculation_basis=legacy_reference` and retains the old floor/10% rules; do not present it as a normalized forecast or verified cash safety. The default operation never silently accepts legacy fields.

`returns` applies verified pre-tax shared capacity, ordinary dividends first and qualifying cancellation buybacks second, taxing dividends only. Negative amounts are rejected. Missing buyback records are not zero; zero requires verified absence of qualifying buybacks. The researcher handles sources, deduplication, sustainability, capacity adjustments, expiry and FX under [returns](lookthrough-return.md); the script does not classify events or extend commitments. Null required return still permits GG, but no prices/threshold result. Run both endpoints of an HK spread interval rather than selecting the favorable end.

`routing` only performs the 65% resource tests; missing required numbers returns needs_input. Verify sources before using it, never treat unverified input arithmetic as research approval. Every operation echoes inputs and states `evidence_verified=false` and `strategy_eligibility=not_assessed`. Invalid input exits 2 without becoming a pass. Use `--input -` to read JSON from stdin.
