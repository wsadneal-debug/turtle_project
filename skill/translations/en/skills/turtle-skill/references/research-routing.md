# Unified input review and research allocation
Use only for candidate batches/preflight. Explicit company research may proceed directly. Verify cash stocks, annual cash, ordinary dividends, buybacks and amount/term-specific return arrangements together before screening. Never reject on an unverified cash estimate first. Retain original/corrected values, official sources, actual review date and expiry; carry corrections into later calculations without changing original documents.

Compare original six-year flat coverage and conditional look-through return independently:
```text
cash_research_ok = FlatCoverage6 >= 0.65
return_research_ok = ConditionalReturn_pct >= 0.65 * RequiredReturn_pct
route = research if cash_research_ok and return_research_ok else defer
strict_cash_ok = FlatCoverage6 >= 1.0
strict_return_ok = ConditionalReturn_pct >= RequiredReturn_pct
```
Only uncomputable final numbers or failed input review require needs_input. Unquantified working capital, net cash not separately disclosed, irrelevant returns or rejected corrections remain warnings. Computable does not mean verified, stable, sustainable or price-qualified. Excess in one condition cannot offset the other.

Preflight may conditionally include official amount-and-term buyback/combined return plans unless explicitly for employee incentives, ownership plans or share awards. General authorizations without amount/term do not qualify; overlapping plans use the combined arrangement only. Conditional records with execution, cancellation or funding unresolved do not carry into final eligibility: apply the final return references. Never invent annual amounts or renew a historical plan. A return equal to 5% of market cap is a candidate lead, not a substitute for both calculations.

Invalid, excluded or unused records must not trigger a recomputation that erases an existing complete scenario. If a genuine correction lacks new cash fields, retain the same-price, fully classified ordinary-dividend baseline with its limits; do not invent new values. Quote refresh recalculates frozen inputs without claiming fresh announcement verification or automatically repeating completed research.
