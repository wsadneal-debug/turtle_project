# Source discovery and read-only adaptation

## Check available capabilities first

Discover the financial-data, web, document, and cloud-file MCP tools available or searchable in the host. Try relevant queries and inspect actual responses. Use data tools for statements, shares, or history when suitable; prefer issuer investor-relations pages, exchanges, or statutory disclosure sites for full reports. If a tool is unavailable, unauthorized, quota-limited, or lacks a field, record that limitation and use uploaded material or official sources. Connectors are optional; do not activate paid services, install software, change permissions, or fill credentials automatically.

Ask once about local sources only if they are not already specified. Users need not create a database matching this package. Inspect only supplied paths: list the chosen folder or inspect its schema before querying a bounded company and period range. Do not traverse home directories, other projects, or unspecified private sources.

## Adapt raw sources

- Open SQLite with a read-only URI such as `file:/provided/path/db.sqlite?mode=ro` and `PRAGMA query_only=ON`. Use read-only accounts/transactions and bounded queries for other databases. Do not migrate, update, create tables, or repair source data.
- Inspect CSV/JSON/Excel column names, periods, scope, original units, currency, and source notes before reading needed rows. Map only fields whose accounting meaning matches. No fixed table, field, or vendor is required.
- Prefer PDF text layers. Available PDF tools or `pdftotext -layout` can create a new text copy. For scans, use available OCR and inspect critical pages. If unavailable, request readable material or an official text version; never claim successful extraction without it.
- Check the entity, consolidated/parent scope, annual/cumulative/single-quarter period, accounting standards, revisions, and restatements. Do not confuse income/cash-flow flows with asset stocks or double interim results mechanically.

Preserve raw names, values, units, and provenance in packet facts; put normalized amounts in `value`. Determine losses/reversals from the actual table headings rather than signs or account names alone. `unit=currency` already denotes base currency units: do not multiply again by thousands or millions. Null is not zero. Explain choices between conflicting sources; do not fill across vendors indiscriminately. The calculator's [internal packet](runtime.md) is AI-created middleware, **not a schema requirement for the user's database**.

Split material cash, deposits, financial assets, and debts using notes. Check cash equivalents, maturity, restrictions, and overlapping totals/subtotals. A summary line is not a complete breakdown. Smaller items may be combined or estimated based on materiality with a short explanation.

## Reports and history

Prepare full annual reports and notes for the latest two disclosed complete fiscal years, plus the latest subsequent quarterly report, or interim report where quarters are not disclosed. A prior-year comparative column does not replace a second full annual report. Respect non-calendar fiscal years. Save period ends, publication dates, URLs/user files, and readable local text paths.

Actually compare business, financials, and key notes across both years; use the latest period for changes. Tables of contents, searches, and continuous relevant sections are sufficient navigation; unrelated text need not be read word for word. Do not call truncated output or summaries full-report reading. Seek missing official originals; disclose unresolved gaps and use supported conditional estimates where useful without claiming complete materials. `materials_ready` only describes file preparation.

For material tax status, restrictions, contracts, or operations, use newer disclosure on the same entity and matter with comparable periods and explain what it supersedes. Do not replace all historical normalization data with the latest period mechanically. Separate disclosed facts from forecasts: future tax, renewal, or growth assumptions may differ, but acknowledge new facts and explain the difference rather than relying on expired status or dates.

For EPV, prefer existing comparable long-term series to judge normal margins and cycle position. Do not force 10/20 years or bulk-download to meet a year count. Estimate with limitations where history is short or structure changed. TTM requires comparable currency, scope, and cumulative periods: full year + current cumulative − prior comparable cumulative. It is an arithmetic reference, not normalized earnings.

Record price/FX dates, conversion direction, and sources. Value an A/H group once using all equivalent outstanding common shares; weighted-average EPS shares are not automatically the value denominator. One quote times all shares is a uniform-price assumption, not actual A/H group market capitalization. Missing FX affects price comparison, never makes a missing price zero. Research assets/EPV independently before comparison with the share price.
