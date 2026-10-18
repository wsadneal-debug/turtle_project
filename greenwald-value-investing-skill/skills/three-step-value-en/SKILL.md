---
name: three-step-value-en
description: Research nonfinancial businesses using asset reproduction value, earnings power value (EPV), and growth returns at a specified price. Use for a few manually selected mainland China or Hong Kong companies, an individual method, or recalculation, using available data tools, user files, or official reports without a particular private database.
---

# Three-step value research

The host AI obtains data, reads reports, develops assumptions, synthesizes research, and reviews the result. Bundled Python performs arithmetic and produces a technical report. Default to assets → EPV → growth, while honoring requests for one method, a selected existing EPV, or a price-only recalculation. Keep the three results separate: never add or average them. Growth evaluates returns at a price; it is not another value total to add.

## Start with sources

1. Identify the company, method, valuation date, currency, and existing research. **Discover and try relevant MCP, financial-data, and report tools available in this environment first.** Choose suitable available tools without requiring a particular vendor, table name, or credentials. Verify the actual response's sources, periods, units, and scope; tool names alone are not data. Uploaded files and official public reports also work without connectors.
2. If local sources are not already specified, **ask once**: “Do you have a database, data files, or a financial-report folder I may use read-only? If so, provide the path or files; otherwise I will use available tools and official reports.” Continue tool discovery and official-source retrieval while awaiting the answer. Do not repeat a question already answered, scan home directories, or guess private paths.
3. Follow [Data sources](references/data-sources.md) for bounded access to explicitly supplied sources. Prepare full annual reports and notes for the latest two complete fiscal years, plus the latest subsequent quarterly or interim report. Retrieve missing documents from official sources. The AI writes the internal packet from documents it actually reads; Python does not automatically extract financial facts from PDFs. Keep missing facts null; place estimates in the valuation layer.

## Research and calculate

Read only the relevant method references:

- [Assets](references/asset.md): economic net reproduction cost of current equivalent operating resources, nonoperating resources, and all obligations.
- [EPV](references/epv.md): normal distributable earnings at current scale, maintenance, tax, capital cost, and the parent-common equity bridge. Estimate independently before explaining differences from a named asset study.
- [Growth](references/growth.md): assess sustainable competitive advantage and its growth boundary, then choose evaluate/skip/investigate/defer. Calculate price-dependent returns only for an applicable scope. Consider economic decay; a numerical half-life is optional.

Allow and encourage conventions, analogies, experience-based ratios, and reasonable independent estimates. Aim to deliver an asset/EPV base estimate. Small items may retain book values, be roughly estimated, combined, or explicitly omitted. Follow economic materiality without universal percentage, history-length, scoring, or completeness gates. Two reporting years do not establish two economic cycles.

Use a separate new directory per method. Keep a light record of actual preparation, planning, necessary focused research, synthesis, initial Python calculation, review, and final recalculation. Reuse available answers. When the host permits native subagents, delegate bounded independent questions according to complexity; see [Delivery](references/delivery.md). Otherwise work directly. No external model CLI, named model, paid API, fixed agent count, or fixed research rounds are required. Do not loop to fill fields. Mark unperformed stages skipped/pending and never invent calls, reading, or review.

Use bundled `scripts/run.py` following [Runtime and packet](references/runtime.md) and the method contracts. Confirm Python 3.10+ and local file access. No package installation, system configuration changes, or credentials are required. If execution is unavailable, deliver research and structured parameters while stating that arithmetic was not executed or verified. All examples are synthetic teaching inputs, never company facts.

## Deliver in English

Follow [Delivery](references/delivery.md). Write the host's final report in plain English, beginning with the conclusion, decisive reasons, and conditions that could change it, followed by calculation bridges, sources, and estimates. Use the saved program results for all numbers. The shared calculator's generated `report.md`, warnings, and some diagnostic/JSON text remain Chinese; treat these as technical working papers. Explain or translate them into English without changing values, JSON keys, enums, or the original working papers. This is an English instruction and final-delivery edition, not a fully localized calculator.

Distinguish materials prepared, research performed, actual program execution, method applicability, and conditional returns at the specified price. Completed research or arithmetic does not approve a purchase; assets/EPV do not guarantee a price floor. Do not add screening, scheduling, trading, or publishing unless requested.
