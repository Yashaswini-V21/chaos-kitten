# Code Review – chaos-kitten (2026-02-05)

## Scope
Reviewed core runtime paths for scanning, configuration loading, and report generation:
- `chaos_kitten/cli.py`
- `chaos_kitten/brain/*`
- `chaos_kitten/paws/*`
- `chaos_kitten/utils/config.py`
- `chaos_kitten/litterbox/reporter.py`

## Findings

### 1) Critical: end-to-end scan path is not implemented
**Severity:** Critical  
**Why it matters:** The project advertises API security scanning, but the scan pipeline cannot execute. Key components raise `NotImplementedError`, so the core product promise is currently non-functional.

**Evidence:**
- `OpenAPIParser.parse/get_endpoints/get_security_schemes` are stubs.
- `AttackPlanner.load_attack_profiles/plan_attacks/reason_about_field` are stubs.
- `Orchestrator.run` is a stub.
- `Executor.execute_attack` is a stub.
- `BrowserAutomation.__aenter__/test_xss` are stubs.
- `scan` CLI command still prints “under construction” and does not wire the runtime stack.

**Recommended fix:**
- Implement the minimal happy-path scan first (OpenAPI parse → endpoint iteration → one executor request → report generation), then extend attack planning and browser validation.
- Gate incomplete modules with feature flags and clear CLI messaging until complete.

---

### 2) High: empty/invalid YAML causes non-user-friendly `TypeError`
**Severity:** High  
**Why it matters:** A malformed or empty config should fail with actionable validation output. Current behavior throws a Python `TypeError` (`NoneType` is not iterable), which is confusing and bypasses intended validation.

**Evidence:**
- `Config.load()` assigns `yaml.safe_load(f)` directly to `self._config`.
- For empty YAML, `safe_load` returns `None`.
- `_validate()` then performs membership checks assuming a dict.

**Reproduction:**
```bash
python - <<'PY'
from chaos_kitten.utils.config import Config
from pathlib import Path
p=Path('/tmp/empty-chaos.yaml')
p.write_text('')
Config(p).load()
PY
```

**Recommended fix:**
- Normalize `None` to `{}` immediately after parse.
- Add type guard:
  - if parsed root is not a dict, raise `ValueError("Configuration root must be a mapping/object")`.

---

### 3) Medium: `scan` command accepts config/target/spec but ignores most inputs
**Severity:** Medium  
**Why it matters:** Users can provide `--config`, `--target`, and `--spec`, but scan flow never loads/validates config nor launches orchestrator. This creates a mismatch between CLI contract and actual behavior.

**Evidence:**
- `scan()` defines options for config, target, spec, output, format.
- After API-key check, command prints placeholder messages and exits without scan orchestration.

**Recommended fix:**
- Load config (`Config(config).load()`), merge CLI overrides, initialize orchestrator/executor/reporter, and return meaningful exit codes.

---

### 4) Medium: auth types in docs/options are broader than implementation
**Severity:** Medium  
**Why it matters:** `Executor` advertises multiple auth modes including oauth, but header construction only supports bearer/basic. This can lead to silent auth misconfiguration.

**Evidence:**
- Executor docstring lists `oauth` support.
- `_build_headers()` only handles `bearer` and `basic`.

**Recommended fix:**
- Either implement oauth flow support or remove oauth from accepted auth type docs/config until implemented.

## Positive notes
- `Reporter` has robust template loading and explicit error wrapping, with data validation before rendering.
- Report output supports html/markdown/json and includes summary aggregation.

## Suggested next sprint plan
1. Implement minimal functional scan pipeline (single-pass endpoint probing + report).
2. Harden config validation (type-safe root object and clearer errors).
3. Align CLI/options and docs to shipped capabilities.
4. Add one integration test for `scan --demo` to prevent regression into “placeholder-only” behavior.
