# Asset reproduction value

## Economic judgment

Ask what it would cost, using currently efficient means, to obtain equivalent existing operating capacity. Add nonoperating resources, subtract obligations and other claims, and determine the parent-common interest. Choose going concern, liquidation, or an explained segment mix. One loss-making year does not automatically require liquidation; idle capacity is not all necessary. Finance, resource reserves, and other special industries require explicit industry adaptation.

Compare two years and key notes before reviewing subsequent changes. Save actual comparison in `annual_comparison` (text, list, or object) and actual reports/sections read in `materials_read`. These record work done; they add no research rounds or gates. Do not infer completion from scattered comments or list unread sections. Reconcile cash totals/components, ownership, restrictions, and operating retention. Do not add finance-company deposits already included in cash. For receivables, deduct losses from gross or adjust only incremental losses from net. Separate normal inventory from excess recoverable inventory. Identify land, buildings, fit-out, equipment, and lease rights separately and pair rights with obligations. State whether construction in progress is valued as-is or at completion less remaining costs.

For material facilities inspect depreciation classes, lives, residuals, gross cost, accumulated depreciation, impairment, and renewal. Adjust current new equivalent cost for remaining service capacity. Do not deduct historical accumulated depreciation amounts from current replacement prices or treat one year's depreciation as accumulated wear. Estimate age by class when needed; undepreciated book proportions are only references. Fully depreciated equipment still in use is neither automatically zero nor as-new. Do not deduct wear twice from a net estimate. Fit-out life is bounded by enforceable tenure/reasonable renewal.

Independently estimate material reproducible technology, customer acquisition, training, organization, and systems, combining reasonable rough estimates where suitable. Replace goodwill with the underlying resources; count brands/channels/customers, development teams, and systems once. Do not invent a price for non-purchasable group identity or privileges. EPV exceeding incompletely measured resources does not prove barriers. Do not add both an associate's equity interest and its underlying assets.

Include all normal, financing, and off-balance-sheet economic obligations once. Estimate contract liabilities according to performance/refund assumptions; advances are not automatically zero. Pair obligations with available related resources. Apply disposal taxes only where actually relevant. Ordinary NCI uses the corresponding subsidiary's adjusted net reproduction resources and actual rights, not a perpetual earnings multiple within a supposedly pure asset method; explain redemption rights or mixed premises separately. Pair dividends, new shares, and exercise proceeds consistently.

## Valuation contract

See runnable `assets/asset-synthetic.json`. Minimal shape:

```json
{"method":"asset","currency":"CNY","valuation_date":"2026-06-30","shares":100000000,
 "premise":"Going concern; synthetic teaching only","summary":"Conclusion and decisive assumptions",
 "items":[{"id":"cash","name":"Cash","kind":"asset","operating":false,
   "book_value":100000000,"value":100000000,"basis":"fact","reason":"Synthetic parameter",
   "sources":["Synthetic teaching input"],"include":true}],"assumptions":[]}
```

Each item: unique `id`, `name`, `kind=asset|liability|nci|preferred`, boolean `operating`, numeric/null `book_value` and `value`, `basis=fact|estimate|book|omitted`, `reason`, string `sources`, and `include` (default true). Optional `low/high` are individual ranges, not joint scenarios. Preserve negatives. With `basis=book` and null value, use book_value; `omitted` does not contribute and needs an impact explanation. Optional currency/unit must match the valuation currency and base units.

Optional cross-method metadata: `scope=parent_common` only when established; `valuation_date` is the valuation reference date, while `financial_position_date` is the actual stock-data date. They need not coincide. Explain `lease_basis` (use `none` if none). Set `scope_status=full|partial` only when supported; otherwise keep `unknown`. Completion does not establish full scope. These are scope explanations, not certificates or gates; filling a missing label does not verify it.

Use `parent_id` for totals/components and value one level; set the other `include=false`. Estimate any unsplit remainder if using components. A direct `value` estimate suffices. Optional `formula` supports only:

| method | Fields and operation |
|---|---|
| quantity_cost | quantity × unit_cost |
| factor | base × factor |
| net | gross − deduction (default deduction 0 only for genuinely no deduction) |
| ownership | net_value × share |
| present_value | cashflows:[{amount,years}], each divided by (1+rate)^years |

An explicit value takes precedence over formula. `fact_ref={"period_end":"2026-06-30","canonical_key":"cash"}` adopts an unmodified full amount only from one unambiguous same-period, same-currency `unit=currency` fact. Do not use it for split, proportional, FX, or restricted-recovery estimates. Remove fact_ref and set basis=estimate when estimating; otherwise the source fact remains authoritative. Failed references preserve usable estimates and explanations without rewriting source facts.

Joint scenarios: `scenarios=[{"name":"Assumption","reason":"Explanation","item_values":{"existing_id":100000000},"shares":100000000}]`. Replace full amounts for existing selected items and optionally positive shares; keep currency unchanged. Pair changed resources with obligations. Text/ranges alone are discussion and do not prove a recalculated joint total.

## Result and review

Parent-common value = selected assets − liabilities − NCI − preferred; per share = parent-common value / equivalent outstanding shares. Explain measured scope, material unmeasured items, and sensitivity. Missing major obligations cannot support a verified lower bound. Optional `reproduction_context` explains business scope, replication cost/time, and access limits for later use without automatically proving advantage. Compare prices only after valuation; do not fit resources to price.
