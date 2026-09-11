# Multi-year commitments: eligibility, current and full-term funding
Load only for potentially includable multi-year dividend/cancellation-buyback commitments. Require at least two years, formal verification, definite amounts/terms, continued validity and funding. Vague payout ratios, general authorizations or unspecified buyback purposes do not qualify. Preserve the ordinary scenario, then replace matching categories; never select the highest GG.

## Remaining schedule
Record category, annual a, total T, executed F, end date and remaining payment schedule; deduplicate corrections, superseded plans and fulfilled amounts. With both annual and total amounts:
```text
Remaining = min(max(0, T - F), a * n)
a_remaining = min(a, Remaining)
```
n is remaining years in a consistent observation horizon. A total alone cannot be evenly allocated without an explicit even schedule. An annualized benchmark differs from obligations unpaid after cutoff; current-year payments are not future demand again. Without a reliable schedule label an annualized scenario, not exact remaining coverage. Combined dividend-or-buyback commitments provide one envelope, with conservative classification/tax explanation.

## Recurring cash: fix years before flooring each
Select the latest up to 3 complete comparable years of raw attributable FCF, at least the latest 2. Retain negative years, never skip recent bad years or substitute older good years. State two-year coverage; missing data in selected years makes F_rec unknown.
```text
f_i_nonnegative = max(0, f_i)
F_rec = min(f_i_nonnegative for i = 1..m), m in {2, 3}
U = max(0, Available_net_cash - Capital_commitments_not_already_deducted)
O_current = max(0, FCF_parent_current, U)
TermCapacity = U + F_rec * n
```
40, -20, 50 yields F_rec=0, not 40. U must be usable, allocated to the same shareholders and net of previously undeducted capital commitments, not total group cash. U is used once; O_current is not FCF+U, and already deducted commitments are not deducted again.

## All demands and payment dates
Replace categories only: a buyback plan replaces buybacks while retaining ordinary dividends; a dividend plan retains independently verified buybacks. Never count one combined plan twice.
```text
CurrentDemand = D_current + B_current
RemainingDemand = sum(Commitment_remaining_j) + sum(Retained_distribution_t for t = 1..n)
CurrentSupported = O_current >= CurrentDemand
TermSupported = TermCapacity >= RemainingDemand
```
n extends to the latest component end date; each component follows its own schedule/term. Multiply retained annual amounts by n only for even schedules without already paid portions. Unknown retained components leave demand incomplete, not zero. Check intermediate payment dates: later cash cannot fund earlier maturities.

Only known inputs establish complete calculations. A known funding lower bound can support a conclusion if sufficient; only complete insufficient information establishes unsupported funding; otherwise unknown. When U alone covers all remaining demand, state that basis without inventing F_rec. Flooring recurring FCF does not remove actual future cash burn. With burn, known investment or financing pressure, model the funding schedule instead of claiming support from mechanical TermCapacity alone.

## Downside and the main result
Material stalling/decline requires updated current/full-term funding, not unchanged historical F_rec. Supported downside scenarios reduce projected future cash; unquantified effects require stating unconfirmed obligations. Do not mechanically cut a fixed commitment because revenue falls, but fixed amounts do not prove funding, and historical support does not establish support in a new scenario.

Only supported eligibility, current/full-term funding and necessary schedules permit replacement of main-result components using the [Look-through return](lookthrough-return.md) shared allocation within O_current. Unsupported/unknown plans stay separate without raising main GG. Disclose expiry: a time-limited plan is not proof of perpetual stable dividends. Show raw f_i, F_rec, U, n, current/remaining demand, both support states, cash-burn and payment-date constraints.
