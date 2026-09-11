# Absolute valuation: six-year cash payback
Read before calculating; independent reconstruction is the default. Six years, trend caps and attribution proxies are method conventions, not accounting standards. This is not DCF, fair value, a target price or a return guarantee.

## Inputs and attribution
P and MV are same-date price and market value for the same share economic rights, finite and >0; use one currency/scale. Multiple share classes require a full-rights bridge or verifiable per-share allocation, not one class's market cap against all group cash.
C is unrestricted cash, A nonoverlapping financial assets realizable within a year, and B_debt interest-bearing debt. Identify leases/already deducted items; no additional mechanical cash haircut, receivables addition or operating-payables deduction. Unknown is not zero.
E is parent equity and N minority equity; E>0. Missing N can be zero only if same-period total equity verifiably equals E.
```text
alpha = E / (E + max(N, 0))
FCF_ordinary = (OCF - Capex) * alpha
FCF_conservative = (OCF - Capex - Lease_cash_not_already_deducted) * alpha
K = (C + A - B_debt) * alpha
```
0<alpha<=1 is an equity proxy, not legal ownership/upstream availability. Use period-matched alpha for annual FCF and cash. Do not reattribute parent FCF; directly attributable cash is a disclosed variant without duplicate reduction. K may be negative. Capex is positive cash spending; bridge ordinary/conservative FCF deductions. Read [Compatibility](compatibility.md) only when explicitly selecting special heavy-asset smoothing.

## Normalization and latest constraint
F1…F5 are the latest five complete comparable years of attributable FCF, newest first; retain negative years:
```text
M5 = median(F1, F2, F3, F4, F5)
A3 = (F1 + F2 + F3) / 3
F_norm = min(M5, A3)
```
Retain the existing exceptional convention: if exactly one of M5/A3 is zero use the other; if both are zero use zero. Missing years cannot be filled with zero to invoke it. Shorter history permits labeled simplified sensitivities, not a standard pass; quality research continues. Five years alone do not establish cycle coverage.

L and L_prev are the latest and prior-year same-type comparable attributable annualized FCF, preferring genuine TTM:
```text
TTM = FY_previous + YTD_current - YTD_previous_comparable
F0 = max(0, min(F_norm, max(0, L)))
raw_delta = L - L_prev
delta_base = max(-0.10 * F0, min(0.10 * F0, raw_delta))
```
Use the last expression only when F0, L and L_prev are positive. Missing L_prev or any nonpositive value sets delta_base=0 with explanation; missing L or F_norm cannot be repaired by this fallback. Never silently substitute annualized cumulative proxies; explicit reproduction uses Compatibility, and a proxy is neither TTM nor a forecast.

## Operating judgment changes the cash path
Ordinary deceleration/normal seasonality does not automatically reduce assumptions. For confirmed non-seasonal material stalling/decline, explain annual cash transmission and select a supported annual linear rate g, a fraction <=0, not quarterly deterioration multiplied by four. Without a reliable magnitude, g=0 produces only a no-growth reference upper bound, not a quantified decline case.
```text
delta_used = delta_base
delta_used_if_material_stalling_or_decline = min(delta_base, F0 * g)
F(t) = max(0, F0 + t * delta_used), t = 1..6
```
When activated, use the second expression as delta_used without raising an already worse path. Changes are fixed annual amounts, not compounding. Reassess whether the current base remains applicable; a traceable annual scenario base is a separately reconstructed variant, not a mechanical revenue haircut on FCF. Flooring negative FCF is a recovery convention only: separately expose actual cash burn, funding and financing pressure, not safety inferred from the cash floor.

## Coverage, payback and reference price
```text
R(n) = K + sum(F(t) for t = 1..n)
Coverage(n) = R(n) / MV
FlatCoverage(n) = (K + n * F0) / MV
SupportMV(n) = max(0, R(n))
SupportPrice(n) = P * SupportMV(n) / MV
Payback = k - 1 + (MV - R(k - 1)) / F(k)
```
Show five-/six-year flat/trend coverage and trend reference prices. Payback=0 when K>=MV; otherwise k is the first covering year. Report no coverage within six years rather than invent year seven. Floor reference market value only, retaining original K/R. Across dates do not add paid dividends to stale cash again.

With applicability and complete reliable inputs, Coverage(6)>=1 passes only the absolute price condition; <1 is not clearly cheap, not proof of expensive. Missing essentials are unknown; simplified variants are not standard passes, and banks/insurers/developers cannot be forced into an unsuitable method. Five-year/flat coverage and positive-FCF-year counts explain results without extra gates.
[Look-through return](lookthrough-return.md) and business/dividend prerequisites still must hold. Unquantified downside upper bounds are not verified buying evidence. Retain unadjusted inputs, selected scenario and before/after results; refresh from the originals rather than compound reductions.
