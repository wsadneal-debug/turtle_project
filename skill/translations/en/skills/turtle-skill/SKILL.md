---
name: turtle-skill
description: "Research businesses and shareholder returns with V5.2.2: resolve six operating questions, choose a base case, calculate both price conditions and headroom, then judge protection at the quoted price. Public documents or offline attachments suffice; extra due diligence requires user opt-in. No trading."
metadata:
  version: "5.2.2"
  analysis_method: "5.2.2"
  language: en
---
# Turtle Business Research V5.2.2

Judge the business before its price. Stable fundamentals, no material deterioration and sustainable dividends are prerequisites. Cash payback and look-through return must each qualify; neither compensates for the other. A low price cannot offset major operating or integrity problems. This is a portable method package, not the production research system.


Cash payback defaults to normalized historical averages plus operating adjustments, directly using six attributable annual cash values including negatives. Identify major current capex projects and payment stages in the first analysis. See [cash payback](references/absolute-valuation.md); legacy formulas are explicitly labeled references only.


## Start and optional due diligence
Confirm the entity, share rights, cutoff and public/attachment/offline scope. Extra due diligence is off by default for ordinary analysis. Briefly ask at the start: “Enable additional investment due diligence for this task? Default: off. It adds material-risk, independent-valuation and transaction-condition research and uses more time and model allowance.” Continue base research while awaiting an answer. Silence, refusal or a request for ordinary analysis never starts due diligence or blocks the base report.
Do not ask again when this task already explicitly requests due diligence. After opt-in, use the separately installable `turtle-due-diligence` included in the bundle and read its entrypoint and needed references. If absent, state that limitation; do not claim completion. Installing both skills, passing prices, high risk or missing data does not enable it. Do not load its question catalog before opt-in.

## Six plus one research workflow
1. **Verify inputs and plan.** Verify cash, dividends and valid return arrangements before preliminary calculation; retain original/corrected values, official sources, expiry and actual verification date. Explicit single-company research bypasses resource screening. Only candidate batching uses the two independent 65% resource tests in [routing](references/research-routing.md); these are not investment eligibility.
2. **Earnings and protection; natural trajectory.** Identify profit pools, customers and charging mechanisms. Use five years and the latest-quarter/comparable half-year to separate seasonality, cycles and structural changes. A moat does not prove stable demand; lack of evidence of decline does not establish six flat years.
3. **Credible offsets; self-funding.** Project material events into future price/volume and realization timing, scale to group profit/cash and deduct necessary spending. Test operations, maintenance investment, maturities and dividends without net new external funding. Unproven transformation is not existing protection.
4. **Existing shareholders; strongest countercase.** Check cash authenticity, ownership/upstreaming, capital allocation, net dilution and delivery of dividends. Compare the strongest alternative explanation. Investigate only decisive gaps, retaining all returned evidence and group magnitudes. Six questions form one causal argument, not six mandatory agents or scoring chapters.
5. **Synthesize the business.** Before consulting the quote, select the most likely case: horizon (default six years), stable/improving/declining, whether decline is subjectively more likely, small/large extent, causal explanation, dividend implications and one primary reversal condition. Ordinary gaps do not replace a conclusion; absent evidence or tool failure remains incomplete. Read [analysis](references/analysis.md).
6. **Calculate.** Use consistent final cash assumptions for both original price conditions, the actual cash path and separate headroom measures. Keep the six-year path consistent with the operating base case; only the legacy fallback uses null magnitude and a no-growth reference upper bound, never a rate invented from a label. Read [cash payback](references/absolute-valuation.md), [returns](references/lookthrough-return.md) and [headroom](references/headroom.md). Use a host calculator or the optional [zero-model script](references/calculator.md).
7. **Judge protection at the quote.** Read cash components, actual path, return composition, expiry and headroom. Explain how material risks consume protection. Passing both conditions is not a safety explanation; stopping growth does not deduct unmodeled decline. Recalculate changed assumptions before delivering price and strategy eligibility separately.

## Conditional references
| When | Read |
|---|---|
| Official documents/attachments, short history or no database | [Evidence and limited-data paths](references/evidence.md) |
| Multi-year return arrangements may enter prices | [Commitment funding](references/return-commitments.md), including expiry/execution/funding |
| Explicit legacy reproduction or a special variant | [Compatibility](references/compatibility.md); not loaded by default |
| User wants market position | [Market context](references/market-position.md); optional |
| Delivery and actual review scope | [Review/output](references/review-output.md) |
| Private evidence or sharing | [Privacy](references/privacy.md) |
| Arithmetic boundaries | [Synthetic examples](references/calculation-examples.md) |

## Host capabilities and history
A single model can plan, gather evidence, synthesize and adjudicate sequentially in this conversation; label this single-model research, not independent multi-model verification. Delegate bounded decisive gaps only when the host supports it and the user authorizes it, with an agreed budget. Input review, lead research, delegated tasks and review within one run use the same provider; cross-provider comparisons remain separate runs. No recursive delegation, votes or spending to fill seats. Preserve partial work on stops/allowance exhaustion; do not switch providers, expand budgets, restart everything or poll progress with model calls.

Base analysis needs no private database, fixed model, API key, paid data or second skill. Optional Python performs arithmetic only; it does not browse or call models. Without browsing use attachments; without calculation show formulas and mark them unexecuted. Missing years, an industry database or precise fields limits dependent conclusions; do not fill zeros or claim standard price qualification. Use authorized tools only; no service installation, private uploads or trades.

Inherit only the latest concise model conclusion from the same provider, method 5.2.2 or later, dated within the preceding 365 days and no later than the cutoff. For unknown provenance, older methods, another provider or stale history, revisit original facts without inheriting the model interpretation. No history/industry memory is required. Public original facts can be shared. Quote-only refresh uses no new model research and preserves research date/method; it does not reverify events. Write into the user's task directory, preserving older reports; follow the requested language.
