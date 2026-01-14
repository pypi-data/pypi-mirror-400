# Jasper Finance

CLI-first autonomous financial research agent. Deterministic workflow with validation-gating: Planning → Execution → Validation → Synthesis. If validation fails, no answer is produced (confidence = 0).

## What It Does

Jasper decomposes financial questions into research tasks, executes them using real data providers (Alpha Vantage, yfinance), validates the results, and synthesizes an answer only if validation passes. When data is missing or incomplete, synthesis is blocked—no hallucinated outputs.

## Key Features

- Deterministic workflow (Planning → Execution → Validation → Synthesis)
- Tool-grounded data fetching (Alpha Vantage, yfinance; no invention)
- Validation gating (blocks synthesis when data is insufficient)
- Confidence scoring (reports data coverage, data quality, inference strength)
- Interactive REPL mode (iterative queries with full validation on each)
- Professional CLI output (live progress board, structured final report)

## Installation

Install via pip:

```bash
pip install jasper-finance
```

## Quick Start

Single query:

```bash
jasper ask "What is Apple's revenue trend over the last 3 years?"
```

Interactive mode:

```bash
jasper interactive
```

## Setup (Required)

Set two environment variables before running Jasper:

```bash
export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxx"
export ALPHA_VANTAGE_API_KEY="your-key"
```

OPENROUTER_API_KEY is required. ALPHA_VANTAGE_API_KEY is optional but recommended.

Validate your configuration:

```bash
jasper doctor
```

## Failure Behavior (By Design)

Jasper fails safely:

- If a data provider returns incomplete or empty results, the validator detects this.
- If validation finds missing data, synthesis is blocked.
- When synthesis is blocked, Jasper returns "Research Failed" with confidence = 0.
- **No answer is produced if data is insufficient.** This is intentional.

Example:

```bash
$ jasper ask "What is the revenue of a private company?"

Research Failed

Validation Issues:
  - Missing data for task: Fetch financial statements
  - No provider returned data

Overall Confidence: 0.00
```

## What This Tool Does NOT Do

- Provide investment advice or trading signals
- Guarantee third-party data accuracy
- Make decisions on your behalf (human review is required)
- Hallucinate numbers or invent missing data

## Principles

- Answer synthesis only happens after validation passes
- Deterministic LLM usage (temperature = 0 for consistency)
- Tool-grounded data only (no free-form generation)
- Transparency: you see the workflow, tasks, and validation results
- Fail-safe design: missing data blocks synthesis, not the other way around

## Links

- GitHub: https://github.com/ApexYash11/jasper
- Issues: https://github.com/ApexYash11/jasper/issues

## License

MIT

