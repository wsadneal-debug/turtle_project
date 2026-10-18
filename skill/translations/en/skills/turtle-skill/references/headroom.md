# Separate headroom and price-stage judgment
Invert the final recorded cash stock K, actual six-year cash total, same-price market cap MV and GG/II with unchanged tax, composition and expiry. Do not invent annual paths or risk forecasts.

```text
CashSurplus = K + SumSixYearFCF - MV
AnnualReductionToBoundary = max(0, CashSurplus) / 6
CashDeclineCapacity_pct = 100 * min(1, max(0, CashSurplus / SumSixYearFCF))
ReturnDeclineCapacity_pct = 100 * max(0, 1 - II / GG)
```
The cash percentage requires a positive six-year cash total; otherwise it is null. With GG<=0, return headroom is zero; missing/nonpositive II makes that measure unavailable. If the baseline fails, show failure and the shortfall, not negative loss tolerance. When cash alone covers the threshold, cap the percentage at 100% and explain reliance on usable cash and no extra cash burn, not a permanent floor.

Cash headroom is an equal annual reduction relative to the original average annual cash, not compound decline. Return headroom scales the original sustainable after-tax distribution, not necessarily ordinary dividends. Never add the two margins or call them revenue/stock-price declines. Term commitments do not renew forever; negative FCF in the default six-year path directly reduces cash without flooring; legacy floors exclude real consumption and must be labeled.

Give the final judge cash/financial-assets/debt and ownership components, the actual six-year path, return composition, corrections and both results. Explain risk effects on operations, dividends, funding and price protection, not merely pass/fail. Avoid double deductions and claims that stopping growth includes unmodeled losses. Unknown exact risk amounts need not prevent scoped conclusions; decisive cash-authenticity or operating counterevidence still matters. Recalculate changed assumptions. A quote-only refresh retains the counterevidence review date and cannot reuse old-price claims of current safety.
