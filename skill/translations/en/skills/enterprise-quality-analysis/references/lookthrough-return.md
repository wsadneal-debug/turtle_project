# Look-through return: distributable cash, not FCF yield
Read for full price research; independent reconstruction is the default. Ordinary historical scenarios do not add total cash to every year's capacity. GG is not ROE, earnings yield or total investment return.

## Fix basis and demand
O, D, B_buyback and MV share economic rights, currency and scale. P, shares S and MV are same-date, normally MV=P*S. Bridge share classes separately and state FX as price-currency units per statement-currency unit. Retain original periods/sources; inputs are finite and tau in [0,1].
D uses actually paid, then-known ordinary cash-dividend events in (valuation date-365 days, valuation date]. Deduplicate/classify per-share d and adjust splits/consolidations:
```text
D = d * S
O0 = max(0, FCF_parent_annual)
```
D is an annual benchmark on current shares, not necessarily historical cash-flow-statement payouts; explain share/tax/timing differences. Special dividends are historical context and one-off declared-unpaid dividends forward context, not historical TTM additions. Single-period DPS, earnings payout ratios and multi-year averages cannot silently replace events. Incomplete classification/coverage is partial/unknown, not zero.

O0 first uses verifiable attributable distributable cash from the latest complete annual report, otherwise the FCF proxy above with leases/attribution explained, never automatically absolute-payback F0. L is newer reliable comparable attributable annualized FCF. When O0>0 and L/O0<60%, O=min(O0,max(0,L)); 60%<=ratio<85% warns only; >=85% does not reduce under this check. Do not divide by O0=0. Require an actually newer report, reliable Capex and attribution; newer profit or net-investing-cash proxies do not suffice. Growth never automatically raises annual capacity. Otherwise O=O0; unreliable updates require capacity-verification limitations.

B_buyback includes executed company purchases with cancellation verified, excluding treasury shares, incentives, unexecuted authorizations and personal purchases. For recurrence, require at least 3 execution dates in 3*365 days, a >=180-day span, >=2 calendar years, latest execution <=120 days ago, and reliable latest-complete-calendar-year coverage:
```text
B_buyback = min(B_actual_365d, B_latest_complete_calendar_year)
```
Buyback and recurrence windows include both endpoints, unlike the left-open dividend window. Verified failure of recurrence permits zero with actual executions shown separately; missing records are unknown. Issuance and stock splits are not buyback cancellations. For officially verified plans of at least two years with definite amounts/terms, read [Commitment funding](return-commitments.md) first; replace matching components only after eligibility and current/full-term support. Do not choose the highest scenario or overlap executed amounts.

## Shared capacity and tax
```text
D_alloc = min(max(D, 0), max(O, 0))
O_remaining = max(0, O - D_alloc)
B_alloc = min(max(B_buyback, 0), O_remaining)
ShareholderCash_net = D_alloc * (1 - tau) + B_alloc
GG = ShareholderCash_net / MV * 100
```
Ordinary dividends claim gross capacity first; buybacks use the remainder. Tax only dividends: do not free capacity after tax or add unconstrained buybacks/FCF yields. With known essentials and O=0, GG=0; unknown is not zero and no 0/0. Disclose method tax scenarios of 0% for A shares and 20% for Hong Kong, not a claim about the user's actual tax liability. Other markets do not inherit them; unknown tax identity requires explicit gross/net assumptions.

## Recalculate distributions after stalling/decline
Use an operating outlook consistent with absolute valuation, without mechanically translating revenue/FCF decline into dividend cuts. For confirmed non-seasonal material deterioration, independently estimate supported annual capacity and ordinary-dividend/qualified-buyback demand:
```text
O_forward = min(O, max(0, Supported_annual_owner_cash_scenario))
D_forward = Supported_annual_ordinary_dividend_scenario
B_forward = Supported_annual_qualified_buyback_scenario
GG_forward = Allocation(O_forward, D_forward, B_forward, tau) / MV * 100
```
Allocation is the preceding after-tax shared allocation; do not haircut an already capacity-adjusted GG again. Use only supported scenarios without rewriting historical events. Recheck fixed-amount plans still supported currently/over the remaining term under the commitment reference rather than mechanically cut them; their capacity is a separate time-limited O_current, not perpetual use of stock cash. When future distribution effects cannot be quantified, retain historical GG as context with unknown/upper-bound limitations, not verified forward return, and do not delete verified cancellations simply because a forecast is unknown.

## Required return and price levels
Obtain traceable benchmark yields as of valuation; the following are method parameters, with yields as percentage numbers and additions as percentage points:
```text
II_A = China_10Y_government_bond_yield + 2
II_HK = EFFR + s, s in [1, 2]
KK = GG - II
ObservePrice = P * GG / II
HeavyPrice = P * GG / max(10, II)
StandardPrice = (ObservePrice + HeavyPrice) / 2
```
No additional fixed A-share floor; other markets require stated benchmarks/spreads. With unspecified Hong Kong s, show an interval: GG>=upper passes all, GG<lower fails, and between depends on the spread. Do not silently choose midpoint/lower bound. An explicitly selected lower bound permits only a lower-bound claim, not full-interval passage.
Calculate levels only with positive P/GG/II and a defined requirement; evaluate both interval endpoints and sort. StandardPrice is a price midpoint, not a return midpoint; 10 means 10%. Zero GG stays zero without useful positive price levels; unknown inputs or II<=0 prevent division. Levels are method references, not positions/orders; freeze cash/shares/tax/FX and refresh from original scenarios.

Separate historical actual, ordinary TTM, one-off forward, qualified commitments and sustainable main results with terms. Disclose O/D/B and allocations, tax/FX, GG/II/KK, price and observation date. Both price tests and business/sustainable-dividend prerequisites are needed for a strategy opportunity; quality-only or incomplete work is not passed. Read [Compatibility](compatibility.md) only for explicit old-result reproduction; do not call it equivalent to the default.
