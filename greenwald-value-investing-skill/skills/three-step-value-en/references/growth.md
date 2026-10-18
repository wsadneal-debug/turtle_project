# Growth returns at a specified price

## Assess applicability first

Read the explicitly selected EPV and existing resource cost/ownership explanations. Check changes and reuse normal earnings, maintenance, tax, and capital cost without repeating full-company EPV. Missing asset totals do not require another asset study; EPV exceeding assets is not evidence of advantage. Assess actual product/geographic/customer markets, cost/customer barriers a strong competitor cannot readily reproduce, durability and strongest counterevidence, and whether new investment remains protected and can exceed matching capital cost. Intense industry competition does not rule out local advantage; brands, margins, and management quality do not prove barriers.

Organic rates and supporting investment must match the protected business scope. When retaining the group EPV basis, sum revenue increments separately for protected and other businesses, then divide by matching group S. Sum earnings increments and divide by group E. Revenue and earnings weights differ; earnings must match E's tax, maintenance, and capital scope. Reasonable approximate weights are allowed with explanation. Use an incremental bridge for material losses/head-office costs rather than forcing positive weights. Sum I from those same businesses' revenue increments and capital requirements using direct, or an equivalent group intensity. Do not apply a core-business rate to group S. Explain through existing reason/assumptions; no new mandatory fields/tables.

Synthetic illustration: a protected business with 60% of comparable group earnings grows earnings 5%, and the rest is flat: group earnings g ≈60%×5%+40%×0%=3%, not 5%. Its revenue share need not be 60%; estimate group revenue growth and I separately. Retain group E, S, B, M and matching capital cost without inventing a subsidiary purchase price or dividing local E by whole-group M.

Remaining funds may enter other businesses. Estimate F by actual allocation, including destructive F<1 cases. Mixed group growth cannot automatically inherit local protection; new markets and other businesses do not automatically earn the same return. Use skip/defer when group mapping cannot reasonably be explained rather than forcing a complete number.

Light `growth_route={action,reason}`:

- `evaluate`: supported or reasoned conditional protected growth. Explain how partial applicability enters group growth/investment while retaining frozen group basis. Only use adjusted scope when genuinely needed, pairing earnings, investment, capital cost, resources, and purchase cost.
- `skip`: clearly inapplicable; finish with a short conclusion without requiring prices, factors, or numerical decay.
- `investigate`: investigate one decisive applicability question once, then converge to evaluate/skip/defer; no repeating assignment loop.
- `defer`: applicability cannot reasonably be bounded; do not adopt a growth premium this round. Unknown does not mean disproven advantage.

Skip/defer are normal research endings, not investment rejection or growth value zero. Preserve destructive expansion/cash erosion in `capital_allocation_risk/upstream_implications`. Explain needed upstream updates without overwriting EPV or calling it a guaranteed floor. A short result can be `{"method":"growth","growth_route":{"action":"skip","reason":"Economic reason"},"franchise":{"status":"unsupported","reason":"Basis"},"summary":"Conclusion","sources":[]}`. Avoid empty tables. If an initial calculation was withdrawn, say it was not finally adopted.

## Freeze EPV and user prices

`growth --epv-run <selected-directory>` creates an independent run after pure recalculation of the source EPV and freezes its basis, reports, dates, and limitations. `basis_mode=reuse_epv` binds that basis; the model cannot silently change it. Use `adjusted` only for supported scope/subsequent changes/corrections, with complete basis and `basis_change_reason`, showing original/new differences without writing to source. `explicit` is for manual/synthetic input without a source EPV, not a bypass of change explanations when a source exists.

Request fields are only `price`, `price_grid`, `policy`, `question`, `notes`. Supplied price/policy are frozen for the run. Explicit price={} or value=null preserves the gap; do not search around that freeze. If no price is supplied, verify one with time/currency/FX. If unavailable, still deliver operating/funding judgment without treating it as zero. A new research date does not update source equity stocks.

## Evaluate contract

Top level: method=growth, basis_mode, currency, summary, growth_route, franchise, distribution, organic, active, decay, price, policy. Optional sources/assumptions/adoptions/materials_read/unmeasured/review and risks above.

| Parameter | Fields and meaning |
|---|---|
| basis | currency,unit=currency,scope=enterprise or equity,revenue=S,earnings_power=E,equity_adjustment=B,capital_cost,capital_cost_basis=wacc or equity_cost,shares; optional valuation_date/financial_position_date/reason. E is after maintenance, before growth investment; B is the matching core-to-parent-common net bridge |
| franchise | status=supported/conditional/unsupported/not_assessed,reason; optional short market/protection/durability/growth_scope/incremental_returns/counterevidence, without mandatory research per field |
| distribution | mode=ratio,value decimal gives D=E×value; or mode=direct,value annual D; reason explains sustainability |
| organic | decimal revenue_growth and earnings_growth; investment; reason. Support rates separately without automatic operating-leverage gains |
| organic.investment | mode=direct,value annual incremental investment; or mode=intensity,working_capital,fixed_capital,expensed_growth: I=S×revenue growth×(working_capital+fixed_capital)+extra expensed investment. Fill 0 only when explicitly zero |
| active | mode=direct,factor=F; or mode=return_ratio,incremental_return,capital_cost,scope; or mode=allocations,items:[{share,factor,reason}], shares summing to 1 |
| active optional extreme | mode=repeat,initial_factor,payout_ratio; F=payout×initial_factor/[1−(1−payout)×initial_factor]. Nonpositive denominator is not infinity; not the default |
| decay | Four modes below; substantive consideration is required, numerical expression optional |
| price | mode=market_cap or per_share,value,currency,date,sources; foreign currency additionally fx_to_valuation (valuation units per quote-currency unit),fx_date |
| share-class price | mode=share_classes,quotes:[{label,shares,value,currency,date,fx_to_valuation,fx_date}], no overlap and full coverage of matching common shares |
| policy | optional additional_margin; for qualitative decay optional qualitative_decay_buffer. Decimal policy requirements, not company facts; no universal threshold or silent edits |

Enterprise scope uses operating E/WACC; equity scope uses after-tax shareholder E/equity_cost. Do not divide operating earnings by total equity price. Do not mechanically strip operating debt from financial businesses. Explain industry adaptation outside this initial nonfinancial scope rather than silently changing bases.

## Funding and returns

Total equity purchase cost Q; core cost M=Q−B. B is positive for resources, negative for financing/external claims; never apply twice. B is not asset-method total value. One share quote times all equivalent shares assumes uniform price, not actual A/H group capitalization. For M≤0, assess realization of net resources without infinite returns. Missing B is not 0. When large resource offsets produce small M/high returns, explain ownership, retention, and realization. Change B in a scenario only if material to the conclusion; no universal haircut.

D is sustainable net distribution for the matching capital scope, not necessarily personal cash dividends. D/M is a return component; D/Q is only scale context. Debt repayment counted in D cannot also receive a repayment factor in active investment. Deduct organic I first, without repeating maintenance or expenses already retained in E. Negative revenue growth does not mechanically release capital. Existing customer stickiness does not prove new-market protection; simply lowering growth does not resolve scope.

A=E−D−I. Disclose A<0 funding gaps without automatic borrowing, payout cuts, or truncation. A=0 needs no F; for A>0 with missing F retain known contributions and genuinely calculated scenarios without research loops. F is **total value created per investment**, not only excess value: 1 preserves, <1 destroys, >1 creates. Active contribution=A×F/M; net creation=A×(F−1) is explanation, never another added return. Consider eventual principal distribution/permanent retention for low-interest retained funds; interest/capital-cost ratios alone must not erase principal. Do not count the same efficiency in organic and active contributions.

Base return r=D/M+organic earnings growth+A×F/M assumes V≈M: a conditional reference, not actual IRR. Deduct quantified decay once. Net-return minus capital cost is a percentage-point gap, not loss probability. For 0<net return<capital cost with positive organic growth, the program may apply a single downward proxy adjustment. Do not iterate upward or reverse-solve a precise target price. Growth outputs no growth_value/equity_value/target_price; market cap−EPV is not growth value, and the three methods are not added.

## Consider decay; numerical half-life is optional

Focus by materiality on durability, gradual erosion/sudden loss, evidence/counterevidence, earnings or residual value after advantage loss, and constraints on price judgment. Reasoned analogies and independent estimates are allowed. If a numerical mapping is unhelpful or inappropriate, directly adopt an explained qualitative treatment without first trying a number or proving all estimation avenues exhausted. Half-life is not corporate life; loss of excess returns does not imply zero company value.

- `mode=deduct,rate,residual_fraction,reason`: annual deduction=rate×(1−residual fraction).
- `mode=half_life,half_life,convention,residual_fraction,reason`: positive T years; rule72 uses 0.72/T, constant_hazard uses 1−0.5^(1/T), then multiply by (1−residual fraction). Rate/T must be single numbers; put ranges in scenarios. Residual 0–1 is an estimate, not an assumed zero.
- `mode=embedded,reason`: name the net-growth parameter, erosion amount, and covered scope. Historical margin conservatism does not automatically cover future abrupt loss. Do not attach rate/half_life/residual_fraction.
- `mode=qualitative,reason`: explain choice, risks, post-advantage earnings/residuals, and conditional constraints, without numerical deduction fields. Retain pre-decay return and a reasoned conditional judgment. Missing half-life does not itself require skip/defer. Use existing stress scenarios when helpful; stress assumptions are not facts or a reason to research merely to fill fields.

With all else fixed, `gross_gap` is only a break-even annual deduction reference. It does not infer actual half-life or prove risks covered. A qualitative buffer is an extra policy requirement, not observed decay. Without a reasonable link between risk and compensation, passing it does not verify net returns or a margin of safety. No additional_margin means no conclusion that an explicit extra requirement was met.

## Scenarios and examples

`price_grid` lists complete price objects, varying purchase cost with operating assumptions fixed. `scenarios=[{name,reason,explicit changes to basis/distribution/organic/active/decay/policy/price/franchise}]`. Same blocks shallow-merge; price/decay/active or mode changes replace whole blocks, and nested investment must be complete. Independently recalculate each row from base. Mark textual scenarios discussion_only and missing-key cases not_calculated; do not display base numbers as executed scenarios. Frozen user values remain authoritative.

`assets/growth-synthetic.json` matches the CNY synthetic EPV with reuse_epv. E=140m, D=84m, I=5m, A=51m, F=1.6; Q=1.5bn, B=−150m, M=1.65bn. Components ≈5.0909%/3%/4.9455%, total ≈13.0364%. Qualitative decay leaves net return unknown; no verified risk-adjusted return is claimed. All inputs are teaching assumptions.

A separate method-check example from book table 8-1 uses USD S=3bn, E=240m, M=4bn, D=144m, I=4.5m, A=91.5m, F=1.6; components 3.6%/3.5%/3.66%, total 10.76%. Do not mix its USD price with this package's CNY EPV. Book inputs and capital costs are not company defaults.
