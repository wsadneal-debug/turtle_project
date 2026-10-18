# Earnings power value (EPV)

## Research order and economic scope

Estimate normal annual distributable earnings at current scale, sufficient to maintain competitive position without relying on growth. Use existing comparable history to judge normal margins and cycle position, then apply current scale. State years consulted/adopted, historical position, structural changes, and limitations. Two annual reports do not establish two cycles; ten years do not automatically normalize a cycle. Do not force a year count. TTM is only an arithmetic reference from comparable cumulative periods.

Adjust expenses both ways: retain a normal burden for recurring “one-off” costs. Add back only avoidable expansion portions of R&D, training, and marketing; necessary operating costs remain under zero growth. Retain share-based compensation costs or consistent dilution. Do not adjust expenses already normalized in the margin. Estimate maintenance from new functional cost and replacement cycles, not current economic net value × depreciation rate. Separate maintenance working capital from growth investment.

Prefer a consistent operating-rent lease basis: add back deducted ROU depreciation and other deducted rent to EBIT, then deduct full normal annual rent. Other D&A addbacks exclude the same ROU. Do not deduct same-scope lease debt already covered by core rent. Explicit `covered_by_core_rent=false` preserves noncore/divested obligations not covered by core rent. A financing basis needs consistent maintenance, tax, debt, and capital cost across bridges.

Operating tax excludes financing interest shields. Separate accounting depreciation, tax depreciation, and maintenance cash. Maintenance payment is not automatically fully deductible immediately; a D&A addback does not automatically increase the tax base. Include material tax differences such as nondeductible PPA amortization only if not already absorbed by the rate. Value finite legacy tax benefits as finite present values. Base capital cost on currency, risk, and structure without universal 8%/10% defaults.

Add matching nonoperating/excess resources to core EPV and deduct actual financing debt and external claims. Reconcile cash totals and required retention. If NCI is subsidiary earnings value for all owners × outside share, do not multiply the already owned share again. Asset-method NCI is not earnings-method NCI. Operating payables already reflected in operations are not all financing debt. Do not confuse finite tax benefits, remittance tax on old cash, and future annual taxes.

For material restricted/ring-fenced funds, assess purpose, release conditions, and timing. If ongoing operations require replacement capital, state net releasable funds and assumptions. Pair debt, guarantees, or performance obligations with the funds; do not deduct burdens already borne in operating cash flow or a net valuation. Restriction means neither zero value nor immediate distributability. Avoid mechanical full exclusion/full addition; estimates are allowed when breakdowns are missing.

For material cash, deposits, financial assets, and debt found in notes, explain where each is counted or excluded using existing `reason`, `adoptions`, or `review`. Removing income still requires deciding whether its principal enters the equity bridge; do not add resources already valued in earnings.

Removing derivative gains does not remove derivative liabilities. Omitting irrelevant deferred tax assets does not erase deferred tax liabilities. Explain matched settlement flows, tax, and stock obligations. Do not deduct burdens already in normal flows or other net amounts. Estimate/combine by materiality rather than mechanically completing every field or deducting all book balances.

Choose earnings, maintenance, tax, and capital cost independently and calculate EPV before reviewing the final selected asset calculation and detail. Check where major resources/obligations went and explain differences. Do not reverse-engineer EPV from asset totals or move every operating item into the equity bridge. Portable prepare provides cost/ownership context; it does not automatically bind asset totals or complete the comparison. Calculate a numeric difference only with aligned dates, currency, parent-common scope, leases, and completeness; otherwise compare qualitatively. A high EPV/asset ratio does not itself prove a moat. Do not average or add.

## Parameter contract

Runnable example: `assets/epv-synthetic.json`. Top level: `method="epv"`, currency, valuation_date, scope="parent_common", shares, premise, summary, earnings, maintenance, tax, capital_cost, equity_adjustments. Prefer explicit `financial_position_date` (equity bridge stock date) and `equity_basis` (dividends/subsequent adjustments). A research cutoff is not an updated financial position.

| Object | Supported fields and modes |
|---|---|
| earnings | revenue; decimal margin; signed pretax ebit_adjustments:[{id,value,reason,sources}]; da_addback; working_capital_addition; lease; reason |
| earnings.lease | mode=none/operating/financing; operating requires full-year rou_depreciation_in_ebit, rent_expense_in_ebit, normalized_rent |
| maintenance | mode=direct,value; or mode=components,items:[{id,name,gross_cost,residual,life_years,reason,sources,include}]. Explicit full-year value takes precedence; otherwise (new cost−residual)/cycle. No net_asset_value calculation |
| tax | mode=rate,rate; or mode=direct,value. Both accept signed adjustments:[{id,value,reason,sources}]; positive increases tax |
| capital_cost | mode=direct,currency,wacc; or mode=components,currency,equity_cost,debt_weight,debt_cost,tax_shield. No debt_cost requirement with zero debt. Explain as_of/reason/sources; do not mix modes |
| equity_adjustments | [{id,name,kind,value,include,reason,sources}]; nonnegative amount, direction from kind. parent_id denotes totals/components of the same right: select one level. reflected_in_earnings=true excludes already valued resources, never actual financing/preferred principal |

Add kinds: `excess_cash/nonoperating_asset/associate/tax_benefit/lease_advantage`. Deduct: `financing_debt/legacy_liability/transition_cost/nci/preferred/lease_debt`. `operating_asset/operating_payable/lease_right` are excluded references. Under operating rent, lease_debt is excluded by default as covered; explicit uncovered obligations use `covered_by_core_rent=false`. Do not deduct debt again when the asset was valued net of it.

When an equity row has null value, optional calculations are:

- `calculation=equity_epv, earnings, equity_cost, ownership`: investee's annual after-tax distributable earnings for all owners / equity cost × actual share. Do not tax again at the group rate.
- `calculation=present_value, rate, cashflows:[{amount,years}]`: individually discounted finite flows.
- `calculation=ownership, equity_value, ownership`: investee equity value × share.

EPV does not use the asset method's generic fact_ref. Keep normalized assumptions separate and link sources to facts. Use base currency amounts and decimal ratios. Optional `history_analysis`, `annual_comparison`, `materials_read`, `assumptions`, `adoptions`, and `competitive_advantage` preserve research without a mandatory evidence tree.

## Arithmetic and scenarios

Base EBIT = revenue × margin, plus pretax adjustments and the operating-lease adjustments above. Annual distributable operating E = normal EBIT + other D&A addbacks − annual maintenance − normal operating cash tax − necessary working-capital addition. Rate tax = max(normal EBIT,0) × rate + tax adjustments. Core EPV = E/WACC; apply the equity bridge for parent-common and per-share value. Output includes earnings_bridge/equity_bridge. Missing decisive amounts cannot yield a claimed complete EPV.

`scenarios=[{name,reason,earnings:{changes},maintenance:{changes},tax:{changes},capital_cost:{changes},shares:optional,equity_values:{existing_id:new_amount}}]`. Same-mode blocks shallow-merge; mode changes require a complete new block. Replace lease/adjustment lists completely. Pair material maintenance/tax/NCI changes. `sensitivity={margins:[...],waccs:[...]}` recalculates the actual grid with other assumptions fixed; it does not replace joint stress scenarios. Unknown fields are not successful changes.

Synthetic example: normal EBIT CNY200m + D&A CNY30m − maintenance CNY40m − tax CNY50m gives E=CNY140m. Teaching WACC 10% gives core CNY1.4bn; net equity adjustment −CNY150m gives parent-common CNY1.25bn and CNY12.5/share. Ten percent is not a market default.
