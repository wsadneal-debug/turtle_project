# Optional prices: actually try an existing authorized MCP
Attempt in full research unless quality-only or excluded. With no suitable tools, permissions, reliable history or arithmetic, give a brief reason and continue. Unknown is not normal; missing history does not block other modules, while missing current price still affects valuation itself.

## Obtain and verify
Discover the connected, authorized local historical-daily-price MCP actually exposed in this session. Read its real schema and make the request: never invent interfaces/ports, install services or add model calls/subscriptions. Check market, share class, code, timezone, 365-calendar-day window, adjustments and fields; follow actual pagination cursors rather than treating page one as a full year. No actual result means no acquisition claim.

Retry only with a known correction or another authorized route, at most once more on the same failed route. No MCP does not automatically authorize web collection; qualified user-supplied prices or an explicitly selected alternative are usable with honest attribution. A local MCP can access the internet; offline requests permit only confirmed offline/cache actions. Queries contain no private material.

Deduplicate/sort dates, require positive finite prices and resolve same-day conflicts. Exclude post-cutoff records and check splits, distributions, currency, source completeness and freshness. Default to verifiably adjusted consistent prices normalized to the latest scale. Close-only data produces a closing range, not intraday extrema. Raw unadjusted prices may be limited separate observations; absence of a large jump does not prove adjustment. Unresolved material conflicts/jumps prevent reliable volatility conclusions.

Below60 valid trading days skip computation; 60–199 is partial; at least200 plus verifiable annual coverage/source completeness is complete. Counts alone do not prove completeness. Never zero-fill, fabricate suspended days or substitute monthly bars. Check freshness against actual trading sessions: closures are not automatic staleness, and unresolved freshness is unknown. Do not bridge invalid/unexplained gaps into normal one-day returns; reliable position can remain while volatility is omitted.

## Formulas and classification
C_i are N consistently scaled closes, P=C_N; H/L are matching window extrema (closing extrema with close-only data):
```text
RangePosition_pct = (P - L) / (H - L) * 100
ClosePercentile_pct = count(C_i <= P) / N * 100
r_i = ln(C_i / C_(i-1))
Vol_1y_pct = sample_stdev(r_i) * sqrt(252) * 100
Vol_20d_pct = sample_stdev(last_20_returns) * sqrt(252) * 100
VolRatio = Vol_20d_pct / Vol_1y_pct
Return_20d_pct = (C_N / C_(N-20) - 1) * 100
HighPosition = (ClosePercentile_pct >= 80) or (RangePosition_pct >= 85)
Warming = (VolRatio >= 1.25) and (Vol_20d_pct >= 30)
Violent = (Vol_20d_pct >= 60) or ((VolRatio >= 1.50) and (Vol_20d_pct >= 30))
```
Sample variance uses sample count-1. Twenty daily returns require21 consecutive valid closes; 252 is a method convention. Percentile includes the current observation and differs from range position. H=L leaves position undefined; a constant sequence's 100% percentile is nondiscriminating, not high position. Zero annual volatility leaves the ratio undefined. Never insert differently scaled live prices into historical closes.

Prioritize high-and-violent, high, violent, warming, then no trigger. A known true condition establishes a warning; unknown is not false. All relevant conditions must be assessable and false to claim no trigger. Report actual source/call, observation date, adjustments, samples/coverage, indicators and partial/skip reasons, never credentials. This module affects timing only, not quality, cash payback or look-through return, and never submits orders.
