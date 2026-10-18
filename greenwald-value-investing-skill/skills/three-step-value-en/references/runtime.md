# Portable runtime and internal packet

Requires local file reading/writing and Python 3.10+. Replace `<skill>` with the installed skill directory and `<work>` with the chosen output directory. Bundled scripts use only the standard library and included calculation code; no repository, private database, model CLI, API credentials, or system installation is needed. They do not perform online research, extract financial facts from PDFs, or complete AI research stages.

## Commands

```bash
python3 <skill>/scripts/run.py --help
python3 <skill>/scripts/run.py prepare --packet <work>/packet.json --method asset --run-dir <work>/asset
python3 <skill>/scripts/run.py recalculate --run-dir <work>/asset --valuation <work>/asset-valuation.json

python3 <skill>/scripts/run.py prepare --packet <work>/packet.json --method epv --run-dir <work>/epv --asset-run <work>/asset
python3 <skill>/scripts/run.py recalculate --run-dir <work>/epv --valuation <work>/epv-valuation.json

python3 <skill>/scripts/run.py growth --epv-run <work>/epv --run-dir <work>/growth --request <work>/growth-request.json
python3 <skill>/scripts/run.py recalculate --run-dir <work>/growth --valuation <work>/growth-valuation.json
```

`prepare` supports asset/epv; `growth` creates new input from the explicitly selected same-company EPV. Both accept optional `--asset-run`; omit it when absent without running assets solely to fill a gap. Growth also accepts `--as-of YYYY-MM-DD`, which changes only research cutoff, not source financial stocks. Use new preparation directories without overwriting research. `recalculate --method asset|epv|growth` optionally checks the method; omitting `--valuation` reuses this run's parameters. There is no analyze command: the host AI plans, extracts, researches, synthesizes, and reviews.

Prepare saves a packet copy and normalized `input.json`, copying named originals into materials. Resolve relative source paths against the packet directory; never change user originals. After relocating a run, check text/report references and use its copied files rather than original-machine absolute paths. Recalculate saves final `valuation.json` with actual calculation and `report.md`. Execution outcome and calculation contents determine what was actually calculated. Rerun after changing parameters; do not edit report totals manually.

The unchanged shared calculator's report headings, warnings, CLI help/diagnostics, and some generated JSON prose remain Chinese. JSON keys/enums and calculations are identical across editions. Use saved numerical results to write the final English explanation as described in [Delivery](delivery.md).

## Packet: host-generated, not a source-database schema

```json
{
  "simulation": true,
  "issuer": {"code": "DEMO.HK", "name": "Synthetic business", "market": "HK"},
  "as_of": "2026-10-17",
  "currency": "CNY",
  "shares": {"value": 100000000, "date": "2026-06-30", "source": "Synthetic teaching assumption"},
  "snapshots": [{
    "period_end": "2026-06-30", "report_type": "interim", "currency": "CNY", "scope": "consolidated",
    "canonical": {
      "cash": {"value": 100000000, "unit": "currency", "currency": "CNY", "raw_value": 100000, "raw_unit": "CNY thousands", "source": {"report": "Synthetic interim report", "page": 1, "origin": "synthetic"}},
      "operating_cashflow": {"value": null, "unit": "currency", "currency": "CNY", "source": {"origin": "not_available"}}
    },
    "statements": {"balance": [], "income": [], "cashflow": []},
    "report_facts": []
  }],
  "reports": [
    {"period_end": "2024-12-31", "report_type": "annual", "text_path": "materials/synthetic-2024.txt", "currency": "CNY"},
    {"period_end": "2025-12-31", "report_type": "annual", "text_path": "materials/synthetic-2025.txt", "currency": "CNY"},
    {"period_end": "2026-06-30", "report_type": "interim", "text_path": "materials/synthetic-2026H1.txt", "currency": "CNY"}
  ]
}
```

Minimum top-level content: issuer with code/name/market, as_of, currency, shares (number, fact object as above, or null), snapshots, and reports. Keep missing facts null; empty arrays with disclosed gaps are acceptable, invented statements are not. Not every source field must be mapped into canonical: map facts actually used whose meaning is established.

Snapshots: actual period_end; report_type=annual|interim|quarterly; canonical maps semantic keys to complete fact objects. Raw facts can be lists in statements.income/balance/cashflow with field, value/unit/currency, source. report_facts preserves note facts. Sources may include report, page, URL, table/field, and extraction basis, only when actually obtained. Recommended history semantics: revenue, reported_operating_profit, operating_cashflow, capital_expenditure. Do not automatically rename reported operating profit EBIT.

History may be omitted and derived from existing snapshots; missing years are not invented. Explicit history uses integer requested_years, integer annual_periods (**not a year list**), and periods as objects. Each period has period_end/report_type/currency/scope/metrics, where metrics maps semantic keys to complete fact objects, not bare numbers. Optional report_facts is retained. ttm_reference maps keys to TTM facts; use {} for unavailable/incomparable cases. Warnings is a list. One-year teaching example:

```json
{
  "requested_years": 1,
  "annual_periods": 1,
  "periods": [{
    "period_end": "2025-12-31", "report_type": "annual", "currency": "CNY", "scope": "consolidated",
    "metrics": {
      "revenue": {"value": 1000000000, "unit": "currency", "currency": "CNY", "source": {"origin": "synthetic"}},
      "reported_operating_profit": {"value": 200000000, "unit": "currency", "currency": "CNY", "source": {"origin": "synthetic"}}
    },
    "report_facts": []
  }],
  "ttm_reference": {},
  "warnings": ["One synthetic annual period; no comparable cumulative periods or TTM. This is not full-cycle history."]
}
```

Report entries need readable path and/or text_path, with optional url, publication_date, and period metadata. A URL alone does not let this offline helper download the report: the AI obtains local files first. Keep both PDF and text paths when useful and disclose OCR status accurately. The tiny synthetic texts demonstrate file wiring only; preparation success does not establish real full-report research.

## Parameters and price recalculation

See [Assets](asset.md), [EPV](epv.md), and [Growth](growth.md). Use base currency units, decimal ratios, and shares as a count. Unknowns stay null; only explicit estimates receive estimated numbers. Optional materials_read, sources, assumptions, adoptions, and review preserve actual research without a universal evidence tree.

For price-only comparisons, asset/EPV estimates do not change automatically with quotes; update only quotes/FX comparison. For growth, add complete price objects to price_grid and recalculate with operating parameters and frozen policy retained. An explicit new base price/policy calls for new growth input/request or a clearly new run with differences explained, never a silent edit to the old frozen request. Recalculation adds no research, reading, corrected judgment, or revival of skip/defer.

## Synthetic demonstration

Feed assets/packet-synthetic.json with its materials directory into prepare; asset-synthetic.json and epv-synthetic.json into their recalculate steps. growth-request-synthetic.json prepares new growth; growth-synthetic.json uses reuse_epv and matches that CNY EPV/request for the final recalculate step. Frozen E=CNY140m, S=CNY1bn, B=−CNY150m, WACC10%; synthetic Q=CNY1.5bn, M=CNY1.65bn; pre-decay base return ≈13.0364%, net return unquantified. These are synthetic teaching assumptions, never company defaults.
