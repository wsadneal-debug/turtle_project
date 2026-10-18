# Turtle Research and Optional Due Diligence 5.2.2

2026-10-18 correction: default cash payback uses six attributable annual estimates from normalized historical averages plus operating/capex-stage adjustments, retaining negative cash in coverage and headroom. `cash_path` accepts six `annual_fcf` values; old inputs require explicit `legacy_cash_path`. Reasonable estimates remain valid without extra research calls or evidence gates.

Base research now follows V5.2.2: choose an operating base case, then assess cash payback, look-through return and protection at the quote. Optional V2.3 investment due diligence is off by default and requires an explicit user choice. It preserves ten directions/60 questions, synthesis, challenges, scenarios and adjudication and can be installed alone.

## Install
Place each desired complete directory from `skills/` in a skill location supported by your host, or follow its import mechanism. Do not copy SKILL.md alone: retain `references/`, `scripts/` and optional `agents/`. Choose Chinese or English; both use the same invocation names. Follow the host's installation instructions; this package does not change global configuration.

- [Base research turtle-skill](skills/turtle-skill/SKILL.md) installs independently and works without the due-diligence directory.
- [Optional turtle-due-diligence](skills/turtle-due-diligence/SKILL.md) installs independently without the main system, base skill or an existing research report.

If installation is unsupported, read the selected entrypoint and necessary references as task materials without claiming installation. Hosts supporting `agents/openai.yaml` mark due diligence explicit-only; other hosts must still honor its activation instructions. Installing the bundle starts no research.

## Examples
“Use $turtle-skill to analyze this company under V5.2.2, showing the operating base case and both price results; ask whether I want additional due diligence.”

“Use $turtle-due-diligence for an investment review using only my attached annual reports and announcements.” This explicitly enables it; do not ask twice.

“Only analyze the earnings foundation; no pricing or due diligence.” Complete that scope without claiming full investment eligibility.

## Working without our data
Research runs through the user's existing AI host and authorized browsing/file tools. Start from official annual/latest interim reports, dividend announcements and public quotes, without a database, paid feed, fixed model or API configuration. Without browsing, use attachments and retain their as-of limits. Incomplete five-year history, industry series or quotes limits dependent conclusions, not all work; no data platform or invented numbers is needed.

One model may work sequentially, without claiming independent multi-model verification. Optional Python 3.10+ standard-library scripts calculate prepared cash paths, shared return capacity, separate headroom and 65% resource routing. They use no network/database/model calls. A host calculator can substitute. Scripts do not automatically download reports, extract all facts, compute full EPV/XIRR or run an entire review.

## Versions and delivery limits
Package/base research method: 5.2.2. Due-diligence method: 2.3. The prior 0.4.0 package was built in the 4.8.1 era; this update changes workflow, reasoning guidance and delivery rather than relabeling old reports. The 65% tests only allocate research; strict price conditions and business/dividend prerequisites remain. Label portable standard formulas, explicit compatibility variants and limited-data references separately; do not claim exact reproduction of private production data.

Distributions contain methods, optional arithmetic and synthetic examples only: no real-company working papers, databases, accounts, keys, logs or project absolute paths. Save research in separate task directories. Offline checks do not validate model research quality, all hosts or investment performance. Actual costs depend on the host/user allowance; due-diligence opt-in does not authorize added paid services. This is not a background service or trading program.

Packaging is not public publication; no automatic upload occurs. The owner determines license/attribution; no open-source/redistribution license is invented. Historical release records remain in the maintenance repository outside the new installer. See [CHANGELOG](CHANGELOG.md).

## Validation scope

Offline arithmetic and package-consistency checks passed. Synthetic cases exercised staged spending, attribution and negative cash paths. A full public-source trial still showed gaps in working-capital normalization and project-payment explanations. Review model outputs; technical completion does not validate a valuation conclusion. Packages contain methods, scripts and synthetic examples only, without company research artifacts, account information or runtime logs.
