# Three-step value research

[简体中文](README.zh-CN.md)

A portable AI skill for manually researching a few nonfinancial businesses using asset reproduction value, earnings power value (EPV), and growth returns at a specified price. The host AI obtains available data, reads official reports, develops estimates, and reviews the reasoning. Bundled Python performs the same deterministic calculations in both editions, using only the standard library.

The methods are independent. Do not add asset value and EPV, or convert growth returns into a third value total. Reasonable estimates are welcome when identified as estimates. Missing small items do not automatically block a useful base estimate. Completed calculations are not a purchase decision or a guaranteed price floor.

## Choose and install an edition

- `skills/three-step-value`: Chinese instructions, examples, and host delivery.
- `skills/three-step-value-en`: English instructions, UI metadata, reference guides, synthetic examples, and host delivery. The shared calculator's generated technical `report.md`, CLI help/diagnostics, warnings, and some generated JSON prose remain Chinese. The host uses saved numerical results to explain or translate them into English. The calculator is not fully localized.

Copy one complete skill directory into the skill location supported by your AI assistant. With the usual Codex location, for example:

```bash
mkdir -p ~/.codex/skills
cp -R skills/three-step-value-en ~/.codex/skills/
```

Use an unused destination; do not merge over an older installation. An edition ZIP, when supplied separately, extracts to that complete skill directory. The two editions have distinct names and may coexist; normally invoke the language you want. Other assistants must support local skill instructions, file access, and Python execution. A file-capable assistant can also follow the directory's `SKILL.md` directly.

Requires Python 3.10+ and local file read/write access. No pip installation, private database, model CLI, API credentials, or provider subscription is required by the bundled calculator. The host's own account/tools may have separate requirements. Web/document tools help obtain missing official reports; supplied complete documents allow offline work. A chat-only host may discuss the method but cannot claim it executed the calculator.

## Ask the host

> Use $three-step-value-en to research my chosen company with all three methods. First discover available financial-data/report tools and ask once whether I have local data or report files. Use the latest two full annual reports and latest subsequent interim or quarterly report. Keep the three results separate and explain the final conclusion in English.

> Use $three-step-value-en for EPV only, using these annual and interim reports. Clearly distinguish disclosures, estimates, and actual Python calculations.

> Reuse this selected EPV run for growth returns at my specified price. Assess sustainable competitive advantage first; a numerical half-life is optional. Keep the original EPV unchanged.

The host adapts sources into an internal JSON packet; users do not need a database with this package's schema. The helper does not automatically extract financial facts from PDFs or run an AI research model. Read `references/runtime.md` inside the chosen skill for contracts and six-step asset/EPV/growth commands. Save outputs outside the skill folder, in new directories per method.

## Offline synthetic demonstration

Run from this repository's root with a fresh output directory. These inputs are invented teaching data, and the tiny material files are not real full reports. This demonstrates execution only, with no model or network calls:

```bash
skill=skills/three-step-value-en
work=/tmp/three-step-value-demo-en
python3 "$skill/scripts/run.py" --help
python3 "$skill/scripts/run.py" prepare --packet "$skill/assets/packet-synthetic.json" --method asset --run-dir "$work/asset"
python3 "$skill/scripts/run.py" recalculate --run-dir "$work/asset" --valuation "$skill/assets/asset-synthetic.json"
python3 "$skill/scripts/run.py" prepare --packet "$skill/assets/packet-synthetic.json" --method epv --asset-run "$work/asset" --run-dir "$work/epv"
python3 "$skill/scripts/run.py" recalculate --run-dir "$work/epv" --valuation "$skill/assets/epv-synthetic.json"
python3 "$skill/scripts/run.py" growth --epv-run "$work/epv" --request "$skill/assets/growth-request-synthetic.json" --run-dir "$work/growth"
python3 "$skill/scripts/run.py" recalculate --run-dir "$work/growth" --valuation "$skill/assets/growth-synthetic.json"
```

Expected teaching results: asset parent-common CNY1.7bn (CNY17/share), EPV parent-common CNY1.25bn (CNY12.5/share), and growth pre-decay conditional return about 13.0364%. The qualitative base decay does not quantify net return. Chinese-edition examples have identical parameters and arithmetic; select `skills/three-step-value` and another fresh output directory.

## Publication status

This directory is prepared for a public release. No license has been selected or granted here; choose an appropriate license before describing the project as open source. No hosting repository URL or author identity is assumed. Only skill instructions, synthetic teaching assets, and necessary calculation code are included; private databases, real-company research, credentials, internal logs, and Git history are excluded.
