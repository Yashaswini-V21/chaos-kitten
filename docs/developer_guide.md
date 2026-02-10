# Developer Guide (Contributors and Extenders)

This guide is for developers who want to contribute to Chaos Kitten or extend it with new attack profiles, payload libraries, and runtime capabilities.

If you're new to the repo, skim the README first. For deeper dives, start with:

- [`README.md`](../README.md) (overview and quickstart)
- [`docs/getting_started.md`](./getting_started.md) (local install and first scan)
- [`docs/architecture.md`](./architecture.md) (how the runtime fits together)
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) and [`docs/contributing_guide.md`](./contributing_guide.md) (contribution workflow)

## Table of contents

- [System architecture overview](#system-architecture-overview)
- [Local development setup](#local-development-setup)
- [Project structure walkthrough](#project-structure-walkthrough)
- [CLI usage](#cli-usage)
- [API usage](#api-usage)
- [Adding new attack profiles (YAML)](#adding-new-attack-profiles-yaml)
- [Adding payloads to `naughty_strings.json`](#adding-payloads-to-naughty_stringsjson)
- [LLM debugging tips](#llm-debugging-tips)
- [Code style and testing expectations](#code-style-and-testing-expectations)
- [Common troubleshooting](#common-troubleshooting)

## System architecture overview

At a high level, a scan looks like this:

1. The CLI loads a config and builds a runtime configuration.
2. The Brain parses your OpenAPI/Swagger spec into a list of endpoints.
3. The Brain plans attacks for each endpoint (rule-based today; LLM-driven planning is an extension point).
4. The Paws execute HTTP requests against the target.
5. The Brain analyzes responses and turns them into findings.
6. The Litterbox generates a report (HTML/Markdown/JSON/SARIF).

ASCII view of the runtime modules:

```
chaos-kitten
  ├─ chaos_kitten/brain/      # parsing, planning, orchestration, analysis
  ├─ chaos_kitten/paws/       # HTTP + browser execution
  ├─ chaos_kitten/litterbox/  # report generation
  ├─ toys/                   # YAML/JSON attack content
  └─ tests/                  # pytest
```

For more detail (including a fuller diagram and data flow), see [`docs/architecture.md`](./architecture.md).

Note: Some extension areas (LLM-driven planning and browser-based validation) are under active development and may evolve quickly. If you're building a large feature in those areas, check the issue tracker first to avoid duplicating ongoing work.

## Local development setup

### Prerequisites

- Python 3.10+
- Git

Optional:

- Playwright (only needed for browser-based validation; current browser automation is still an extension point)

### Clone and install

```bash
git clone https://github.com/mdhaarishussain/chaos-kitten.git
cd chaos-kitten

python -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
# .\.venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install -e '.[dev]'
```

If you're working on browser automation:

```bash
python -m pip install -e '.[dev,browser]'
python -m playwright install
```

### Environment variables

Chaos Kitten reads provider credentials from environment variables.

- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`

The config loader also expands `${VARNAME}` syntax inside `chaos-kitten.yaml` (see `chaos_kitten/utils/config.py`).

Note: The CLI does not automatically load a `.env` file. If you prefer `.env`, load it into your shell (for example via `direnv`, your IDE, or your task runner).

The canonical list of dependencies and dev tooling is in `pyproject.toml`.

### Run tests

```bash
pytest
```

## Project structure walkthrough

### `chaos_kitten/` (library + CLI)

- `chaos_kitten/cli.py`
  - Typer CLI entrypoint (`chaos-kitten`).
  - Handles config merging between `chaos-kitten.yaml` and CLI flags.
- `chaos_kitten/utils/config.py`
  - Loads YAML config and expands `${ENV_VAR}` values.
- `chaos_kitten/brain/`
  - `openapi_parser.py`: parses OpenAPI 3.x and Swagger 2.0 into a normalized list of endpoints.
  - `orchestrator.py`: LangGraph-based scan loop (parse → plan → execute/analyze → report).
  - `attack_planner.py`: attack planning (currently rule-based; extension point for loading/selecting `toys/*.yaml`).
  - `response_analyzer.py`: heuristics/regex-based response analysis into typed findings.
- `chaos_kitten/paws/`
  - `executor.py`: async HTTP executor using `httpx`.
  - `browser.py`: browser automation placeholder (Playwright) for client-side validation.
- `chaos_kitten/litterbox/`
  - `reporter.py`: report generation (HTML/Markdown/JSON/SARIF) + templates.

### `toys/` (attack library)

The `toys/` directory contains attack profiles as YAML files and shared payload datasets.

- `toys/*.yaml`: attack profiles (SQLi, XSS, SSRF, etc.)
- `toys/data/naughty_strings.json`: categorized string payload library
- `toys/data/common_passwords.txt`: password list used by some profiles

### `examples/`

- `examples/demo_api/`: intentionally vulnerable Flask API used for local testing.
- `examples/sample_openapi.json`: OpenAPI spec for the demo API.

### `tests/`

Pytest test suite. Patterns to copy when adding new tests:

- unit tests with mocking for orchestrator flow: `tests/test_brain.py`
- CLI integration test using `typer.testing.CliRunner`: `tests/test_integration_scan.py`

## CLI usage

### Common commands

```bash
# Print version
chaos-kitten version

# Generate a starter config
chaos-kitten init

# Run against the demo API
chaos-kitten scan --demo
```

### Scan with explicit target/spec

This is the most reproducible way to run locally (especially for contributors):

```bash
chaos-kitten scan \
  --target http://localhost:5000 \
  --spec examples/sample_openapi.json \
  --output ./reports \
  --format html
```

Report formats currently supported by the reporter are:

- `html`
- `markdown`
- `json`
- `sarif`

For the full contributor workflow (formatting, linting, type-checking, tests), see [Code style and testing expectations](#code-style-and-testing-expectations).

## API usage

Chaos Kitten is importable as a Python library. The most direct entrypoint today is the Brain `Orchestrator`.

```python
import asyncio

from chaos_kitten.brain.orchestrator import Orchestrator

config = {
    "target": {
        "base_url": "http://localhost:5000",
        "openapi_spec": "examples/sample_openapi.json",
    },
    "reporting": {"format": "json", "output_path": "./reports"},
}

results = asyncio.run(Orchestrator(config).run())
print(results["summary"])
```

To reuse the same YAML config loading logic as the CLI:

```python
import asyncio

from chaos_kitten.brain.orchestrator import Orchestrator
from chaos_kitten.utils.config import Config

config = Config("chaos-kitten.yaml").load()
results = asyncio.run(Orchestrator(config).run())
print(results["summary"])
```

Notes for extenders:

- The library-level API is still evolving; treat imports like `Orchestrator` as internal building blocks rather than a stable public API.
- `Orchestrator` currently instantiates `Executor(base_url=...)` without wiring auth/settings from config. If you're implementing auth, start by threading `target.auth.*` (and executor settings like timeouts/rate limits) into `Executor` construction.
- Attack planning is currently rule-based in `AttackPlanner.plan_attacks`. YAML attack profiles in `toys/` are not auto-loaded during a scan yet.

## Adding new attack profiles (YAML)

Attack profiles live in `toys/*.yaml`. Each file describes:

- metadata (`name`, `category`, `severity`, `description`)
- which input fields to target (`target_fields`)
- payloads to try (`payloads`)
- what “success” looks like (`success_indicators`)
- remediation guidance (`remediation`)

### Minimal profile template

Create a new file like `toys/header_injection.yaml`:

```yaml
name: "Header Injection"
category: "injection"
severity: "high"
description: "Tests for CRLF/header injection patterns"

target_fields:
  - "url"
  - "redirect"
  - "callback"

payloads:
  - "\\r\\nX-Test: injected"
  - "%0d%0aX-Test: injected"

success_indicators:
  status_codes:
    - 200
    - 302
  response_contains:
    - "X-Test"

remediation: |
  Reject CR/LF characters in untrusted inputs and ensure headers are
  constructed using safe framework APIs.
```

### Conventions and best practices

1. Keep payloads safe by default.
   - Avoid destructive payloads (DELETE/DROP) unless explicitly gated by a “destructive mode”.
2. Prefer a clear `category` string over adding new ad-hoc keys.
   - Existing examples: `injection`, `authentication`, `request-forgery`, `file-access`.
3. Keep `success_indicators` conservative.
   - “Response contains X” is often enough to flag a likely finding, but avoid overly broad substrings that cause noise.
4. Include a `remediation` section.
   - This is often the most useful part of the report for end users.

### How profiles are used in code

Currently, profiles are not auto-loaded from `toys/` during a scan. Adding a YAML file is the first step, but wiring it into planning/analysis is still manual.

The long-term intention is for `chaos_kitten/brain/attack_planner.py` to:

1. load YAML profiles from `toys/`
2. match profiles to endpoints/fields
3. produce planned attacks (payload + target) for the executor

When you add a new YAML profile today, you will usually also want to:

- update `AttackPlanner` to load and select it
- update `ResponseAnalyzer` to recognize the vulnerability (or implement a new analyzer)

## Adding payloads to `naughty_strings.json`

The shared payload library lives at `toys/data/naughty_strings.json`.

File shape:

```json
{
  "name": "Naughty Strings",
  "description": "...",
  "version": "1.0.0",
  "categories": {
    "sql_injection": ["..."],
    "xss": ["..."],
    "path_traversal": ["..."],
    "...": ["..."]
  },
  "notes": ["..."]
}
```

### Adding a new payload

1. Choose the right category under `categories`.
   - If you create a new category, keep the name short and snake-cased.
2. Add your payload as a JSON string.
   - Remember to escape backslashes (`\\`) and double quotes (`\"`).
3. Keep entries focused.
   - A payload should test one idea; prefer multiple small payloads over one mega-string.

Example patch (adding a CRLF payload):

```diff
diff --git a/toys/data/naughty_strings.json b/toys/data/naughty_strings.json
@@
   "categories": {
@@
     "header_injection": [
+      "\\r\\nX-Test: injected"
     ]
   }
```

After editing, validate the JSON (this catches missing commas and escaping errors):

```bash
python -m json.tool toys/data/naughty_strings.json > /dev/null
```

## LLM debugging tips

LLM-driven planning is under active development. Today, the scan loop is primarily:

- spec parsing (OpenAPIParser)
- rule-based attack planning (AttackPlanner)
- HTTP execution (Executor)
- response heuristics (ResponseAnalyzer)

That said, contributors frequently work on LLM integration in `AttackPlanner` and/or the LangGraph workflow.

Practical debugging tips:

1. Make runs deterministic while debugging.
   - Set your model temperature to `0` (in config) once LLM planning is wired in.
   - The config template created by `chaos-kitten init` includes `agent.llm_provider`, `agent.model`, `agent.temperature`, and `agent.max_iterations`.
2. Reduce the blast radius.
   - Run against the demo API (`examples/demo_api`) and keep to a small spec.
3. Log prompts and decisions.
   - For local experiments, add `logging.basicConfig(level=logging.DEBUG)` in your entrypoint and emit the exact prompt + parsed response.
4. Add “golden” prompt tests.
   - If you’re changing prompts, add unit tests that validate structured outputs (rather than snapshotting full free-form text).
5. Watch for rate limits and retries.
   - LLM provider errors can look like network timeouts; capture the exception type and any provider request IDs.

## Code style and testing expectations

### Style

Tooling is configured in `pyproject.toml`:

- Black (`[tool.black]`) for formatting
- Ruff (`[tool.ruff]`) for linting
- Mypy (`[tool.mypy]`) for type checking

Recommended local commands:

```bash
black .
ruff check .
mypy chaos_kitten
```

Before opening a PR, run:

```bash
black .
ruff check .
mypy chaos_kitten
pytest
```

### Testing

Run the full test suite:

```bash
pytest
```

When you change behavior:

- add or update unit tests in `tests/`
- prefer small, focused tests
- use mocking for network calls (see `tests/test_brain.py`)
- keep integration tests hermetic (the demo API is used for this in `tests/test_integration_scan.py`)

## Common troubleshooting

### `chaos-kitten scan` exits because no API key is set

- Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in your environment.
- If you're running in demo mode (`--demo`), the CLI will proceed without a key, but you may still see a warning.

### Config values like `${API_TOKEN}` are empty

The config loader only expands values from the process environment; it does not read a `.env` file.

- Ensure the environment variable is exported before you run `chaos-kitten scan`.

### OpenAPI parsing failures

`OpenAPIParser` uses `prance` with an OpenAPI validator backend.

Common causes:

- invalid OpenAPI/Swagger JSON/YAML
- missing external `$ref` files
- relative paths in `$ref` that don’t resolve from your current working directory

Try:

```bash
python -c 'from chaos_kitten.brain.openapi_parser import OpenAPIParser; p=OpenAPIParser("examples/sample_openapi.json"); p.parse(); print(len(p.get_endpoints()))'
```

### Report generation errors

If you see template-related errors, confirm the templates exist at:

- `chaos_kitten/litterbox/templates/report.html`
- `chaos_kitten/litterbox/templates/report.md`

### Connection errors to your API

- Confirm the base URL is reachable from your machine.
- If you're using the demo API, start it from `examples/demo_api`.

```bash
cd examples/demo_api
python -m pip install -r requirements.txt
python app.py
```

### Playwright issues

If you installed `.[browser]`, ensure you also installed the browser binaries:

```bash
python -m playwright install
```

### Test failures / CI failures

- Re-run the failing test with more output: `pytest -vv`.
- If you changed CLI behavior, run the integration test: `pytest -vv tests/test_integration_scan.py`.
- If CI fails on formatting or linting, run the exact local commands in [Code style and testing expectations](#code-style-and-testing-expectations).
