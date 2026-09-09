# Conditional branches: read only for explicit reproduction or variants
Do not load by default, switch silently or claim pointwise equivalence with a legacy system. Missing source-system data, eligibility or tools remain missing, not invented.

## Annualized cumulative proxies
```text
Annualized_Q1 = Q1_YTD * 4
Annualized_H1 = H1_YTD * 2
Annualized_9M = 9M_YTD * 4 / 3
Annualized_FY = FY
```
Attribute current/prior same-window values separately and label annualized cumulative proxies: neither TTM, seasonal adjustment nor forecasts. Missing genuine TTM does not authorize a silent standard pass using proxies.

## Upstream heavy-asset smoothing variant
```text
adjusted_OCF = min(OCF_current, 1.5 * mean_OCF_5y)
adjusted_Capex = max(Capex_current, mean_Capex_5y)
heavy_FCF = adjusted_OCF - adjusted_Capex
```
Then apply actual attribution. Reproduce only when the original explicitly uses this basis; do not resmooth adjusted inputs or zero-fill missing five-year data.

## Consolidated capacity and native ordinary-dividend scaling
```text
O0_legacy_consolidated_proxy = max(0, OCF_annual - Capex_annual)
GG_native = g_ordinary * min(1, max(0, F_parent) / D_year), if D_year > 0
```
Use only for an explicit legacy-reproduction request. Consolidated capacity is not all attributable to listed shareholders. g_ordinary is ordinary net TTM event yield, D_year ordinary dividends in the latest financial row, and F_parent that row's attributable FCF. Periods may differ; this is not the default D_TTM shared-allocation formula. The old branch does not scale when D_year=0, but that does not prove TTM dividend funding; missing denominators are not zero.

An explicitly selected latest-cash-capacity method must state period/attribution rather than masquerade as the annual-capacity 60%/85% update rule. Cash/dividend assumptions remain consistent. Seasonality, event projection and business prerequisites are not waived by compatibility mode.

## Separate reproduction from current decisions
Faithful reproduction retains old inputs, formulas and results with current corrections/scenarios separately shown. Do not silently change old figures or equate reproduction with present strategy qualification. Attribute differences to data, currency, ownership, windows, scenarios or algorithms; return to default references when reproduction is not requested.
