---
doc_status: frozen
doc_version: 1.1.5
date: 2025-12-29
reviewers: [AI1, AI2]
---

# Contract-Driven Development

## What

A software development methodology where:

1. **Analysis precedes contracts** — Understand the reference artifact before defining requirements
2. **The contract is the goal** — Before any code, define what success looks like
3. **Tests are embedded** — The contract carries its own verification
4. **Output is diagnostic** — Test results show actual vs expected with full context
5. **Iteration is fast** — Run tests, see failures, apply fixes, repeat

This applies to any software project.

---

## Glossary

| Term | Definition |
|------|------------|
| **Reference** | The artifact that defines success (PDF, mockup, audio file, API spec, sketch) |
| **Analysis** | Tool-generated micro-detail extraction from an artifact |
| **Baseline** | Analysis output from reference; the measurable target |
| **Contract** | YAML file containing spec + requirements + tests |
| **Run** | Single execution of a contract's tests (context + results + artifacts) |
| **Report** | JSON output from a run |
| **Executor** | Language-specific test runner (python, sclang, node, shell) |
| **Assertion** | Machine-evaluable check with explicit operator |

---

## Normative vs Illustrative

**Normative sections** (runner-enforced, must follow exactly):
- Contract Schema
- Contract Field Requirements
- Assertion DSL
- JSONPath Resolution
- Step/Action Vocabulary
- Step Result Envelope
- Report Format
- Contract Resolution (extends)
- Parameterisation

**Illustrative sections** (examples, may be adapted):
- Example contracts
- Noise Engine specific contracts

---

## The Model

```
    +---------------------------------------+
    |        REFERENCE ANALYSIS             |
    |                                       |
    |  What artifact defines success?       |
    |  What tool extracts micro-detail?     |
    |  Baseline = tool output on reference  |
    +---------------------------------------+
                      |
                      v
    +---------------------------------------+
    |           PROJECT CONTRACT            |
    |                                       |
    |  What are we building?                |
    |  What does success look like?         |
    |  How do we verify it works?           |
    +---------------------------------------+
                      |
                      v
    +---------------------------------------+
    |        COMPONENT CONTRACTS            |
    |                                       |
    |  Break down into parts                |
    |  Each part has requirements           |
    |  Each part has tests                  |
    +---------------------------------------+
                      |
                      v
    +---------------------------------------+
    |           IMPLEMENTATION              |
    |                                       |
    |  Build against contracts              |
    |  Run tests continuously               |
    |  Paste failures -> get fixes          |
    +---------------------------------------+
                      |
                      v
    +---------------------------------------+
    |       COMPARE OUTPUT TO BASELINE      |
    |                                       |
    |  Same tool on output vs reference     |
    |  Deviations = precise feedback        |
    |  Iterate until acceptable             |
    +---------------------------------------+
                      |
                      v
    +---------------------------------------+
    |            ALL GREEN                  |
    |                                       |
    |  Contract fulfilled                   |
    |  Project complete                     |
    +---------------------------------------+
```

---

## Mandatory Gates

**[NORMATIVE]**

CDD defines four mandatory gates. Implementation MUST NOT proceed past a gate until it passes.

| Gate | Command | Passes When | Blocks |
|------|---------|-------------|--------|
| G0: Analyze | `cdd analyze <ref>` | Baseline exists | Contract writing |
| G1: Lint | `cdd lint contracts/` | Exit 0 | Implementation start |
| G2: Test | `cdd test contracts/` | Exit 0 | Contract freeze |
| G3: Freeze | `status: frozen` | Manual verification | Deploy |

### Gate Sequence

```
Reference artifact exists
        │
        ▼
┌───────────────┐
│  G0: ANALYZE  │ ── no baseline ──▶ Run cdd analyze
└───────────────┘
        │ baseline exists
        ▼
Write contract (with source_refs)
        │
        ▼
┌───────────────┐
│   G1: LINT    │ ── fail ──▶ Fix contract
└───────────────┘
        │ pass
        ▼
Implement
        │
        ▼
┌───────────────┐
│   G2: TEST    │ ── fail ──▶ Fix implementation
└───────────────┘
        │ pass
        ▼
┌───────────────┐
│  G3: FREEZE   │ ── not frozen ──▶ Set status: frozen
└───────────────┘
        │ frozen
        ▼
Deploy
```

### Gate Violations

Deploying without passing all gates is a **process violation**. Document violations with:
- What gates were skipped
- Why they were skipped
- Remediation plan

**Gates are not suggestions. They are hard stops.**

### Enforcement

Gates are enforced by:

1. **Exit codes** — All CDD commands exit 1 on failure
2. **CI integration** — Gates run in CI pipeline, block merge on failure
3. **Pre-commit hooks** — Optional local enforcement
4. **`cdd gate` command** — Single command that runs all gates (planned)

---

## Process Checkpoints

**[NORMATIVE]**

| Checkpoint | Verified By | Must Be True |
|------------|-------------|--------------|
| Reference exists | Human | Artifact is available and accessible |
| Analysis complete | `cdd analyze` exits 0 | Tool produces baseline output |
| Baseline approved | Human | Analysis captures what matters |
| Contract valid | `cdd lint` exits 0 | Schema correct, requirements covered |
| Tests runnable | `cdd test` executes | No missing tools or broken steps |
| Tests pass | `cdd test` exits 0 | All assertions satisfied |
| Contract frozen | `status: frozen` in YAML | Explicit human decision |
| Ready to deploy | G0 ∧ G1 ∧ G2 ∧ G3 | All gates passed |

---

## Contract File Layout

```
contracts/
  project.yaml                    # Top-level project contract (exception to naming rule)
  api_client.yaml                 # Component contract
  api_client.cache.yaml           # Sub-component contract
  generator.yaml                  # Component contract
  generator.imaginarium.yaml      # Extended contract
```

**Naming convention:**
- Contract names are explicit string IDs (the `contract:` field)
- Dots imply hierarchy: `generator.audio` is a child of `generator`
- Filename matches contract name: `generator.audio.yaml`
- Contracts live in `contracts/` directory
- **Exception:** Project contract is always `contracts/project.yaml` (does not follow filename=id rule)

---

## Contract Field Requirements

**[NORMATIVE]**

### Project Contract Fields

| Field | Required | Type | Default |
|-------|----------|------|---------|
| `project` | Yes | string | - |
| `cdd_spec` | Conditional | semver | - |
| `version` | Yes | semver | - |
| `status` | Yes | enum(draft,frozen,deprecated) | - |
| `goal` | Yes | string | - |
| `success_criteria` | Yes | string[] | - |
| `components` | Yes | string[] | - |
| `change_log` | No | string[] | [] |

**`cdd_spec` requirement:** Required if `status: frozen`. Optional for `draft` or `deprecated`. Specifies the CDD spec version this contract targets. Tooling uses this for compatibility checking.

### Component Contract Fields

| Field | Required | Type | Default |
|-------|----------|------|---------|
| `contract` | Yes | string | - |
| `version` | Yes | semver | - |
| `status` | Yes | enum(draft,frozen,deprecated) | - |
| `description` | Yes | string | - |
| `runner` | Yes | object | - |
| `runner.executor` | Yes | enum(python,node,sclang,shell,static) | - |
| `requirements` | Yes | Requirement[] | - |
| `tests` | Yes | Test[] | - |
| `parent` | No | string | null |
| `extends` | No | string | null |
| `inputs` | No | Input[] | [] |
| `outputs` | No | Output[] | [] |
| `matrix` | No | object | null |
| `change_log` | No | string[] | [] |
| `runner.entry` | No | string | null |
| `runner.symbol` | No | string | null |
| `runner.command` | No | string[] | null |
| `runner.timeout_ms` | No | integer | 30000 |
| `runner.artifacts_dir` | No | string | "artifacts/{contract}/{run_id}/" |
| `runner.env` | No | object | {} |
| `runner.parser` | No | enum(sclang_ast,python_ast) | null |
| `runner.script_template` | No | string | null |

### Requirement Fields

| Field | Required | Type |
|-------|----------|------|
| `id` | Yes | string (R###) |
| `priority` | Yes | enum(must,should,nice) |
| `description` | Yes | string |
| `acceptance_criteria` | Yes | string[] |

### Test Fields

| Field | Required | Type | Default |
|-------|----------|------|---------|
| `id` | Yes | string (T###) | - |
| `name` | Yes | string | - |
| `type` | Yes | enum(unit,integration,e2e) | - |
| `assert` | Yes | Assertion[] | - |
| `requirement` | No | string (R###) | null |
| `steps` | No | Step[] | [] |
| `tags` | No | string[] | [] |
| `skip` | No | boolean | false |
| `skip_if` | No | string | null |
| `files` | No | string or string[] | null |

### Executor-Specific Constraints

| Executor | `steps` | `runner.parser` | `runner.symbol` |
|----------|---------|-----------------|-----------------|
| `python` | Optional | Not used | Required for `call` |
| `node` | Optional | Not used | Required for `call` |
| `sclang` | Optional | Not used | Not used |
| `shell` | Optional | Not used | Not used |
| `static` | **Absent or `[]`** | Required | Not used |

---

## Contract Schema

**[NORMATIVE]**

### Project-Level

```yaml
project: weather-dashboard
cdd_spec: 1.1.3
version: 1.0.0
status: draft | frozen | deprecated

goal: |
  A web dashboard that displays current weather and 5-day forecast
  for any city the user searches for.

success_criteria:
  - User can search for a city by name
  - Current conditions display within 2 seconds
  - 5-day forecast shows high/low temps and conditions
  - Works on mobile and desktop

components:
  - api_client
  - search_ui
  - weather_display

change_log:
  - 1.0.0: Initial contract
```

### Component-Level

```yaml
contract: api_client
version: 1.0.0
status: frozen
parent: weather-dashboard
extends: null  # or base contract name

description: |
  Fetches weather data from external API

runner:
  executor: python
  entry: src/api/client.py
  symbol: get_weather          # function/method to invoke for 'call' action
  timeout_ms: 30000
  artifacts_dir: artifacts/{contract}/{run_id}/

inputs:
  - name: city_name
    type: string
    required: true
    
outputs:
  - name: current_weather
    type: object
    properties:
      - name: temp
        type: number
      - name: conditions
        type: string
      - name: humidity
        type: number
      - name: wind
        type: number

requirements:
  - id: R001
    priority: must
    description: Returns data within 2 seconds
    acceptance_criteria:
      - Response time p95 < 2000ms (measured over 10 samples after warmup)
      
  - id: R002
    priority: must
    description: Handles invalid input gracefully
    acceptance_criteria:
      - Never throws uncaught exception to caller
      - Returns ok=false with error_code and message for invalid city
      - Retries at most 1 time on 5xx from upstream
      
  - id: R003
    priority: should
    description: Caches results for 10 minutes
    acceptance_criteria:
      - Second identical request within 10min returns cached
      - Cache key includes city name (case-insensitive)

tests:
  - id: T001
    name: valid_city_returns_data
    requirement: R001
    type: unit
    steps:
      - action: call
        with: { city: "London" }
        save_as: result
    assert:
      - op: eq
        actual: $.result.ok
        expected: true
      - op: has_keys
        actual: $.result.value
        expected: [temp, conditions, humidity, wind]
      
  - id: T002
    name: invalid_city_returns_error
    requirement: R002
    type: unit
    steps:
      - action: call
        with: { city: "NotARealCity12345" }
        save_as: result
    assert:
      - op: eq
        actual: $.result.ok
        expected: false
      - op: has_keys
        actual: $.result
        expected: [error_code, message]
      
  - id: T003
    name: response_time_p95_under_threshold
    requirement: R001
    type: integration
    tags: [performance]
    steps:
      - action: call
        with: { city: "Tokyo" }
        warmup: true
      - action: call_n
        with: { city: "Tokyo" }
        n: 10
        save_as: samples
    assert:
      - op: lt
        actual: $.samples.p95_ms
        expected: 2000
      
  - id: T004
    name: caching_works
    requirement: R003
    type: integration
    steps:
      - action: call
        with: { city: "Paris" }
        save_as: first
      - action: call
        with: { city: "Paris" }
        save_as: second
    assert:
      - op: eq
        actual: $.second.meta.cache_hit
        expected: true

change_log:
  - 1.0.0: Initial contract with R001-R003
```

---

## Call Target Resolution

**[NORMATIVE]**

The `call` action invokes a function/method. The target is resolved as follows:

1. **If step has `method:`** — Use that method name
2. **Else if `runner.symbol` is set** — Use that symbol
3. **Else** — Error: no call target defined

```yaml
# Option 1: runner-level default
runner:
  executor: python
  entry: src/api/client.py
  symbol: get_weather

# Option 2: per-step override
steps:
  - action: call
    method: get_weather_cached  # overrides runner.symbol
    with: { city: "London" }
    save_as: result
```

For `executor: shell`, `call` is not valid. Use `shell` action instead.

For `executor: static`, `call` is not valid. Static contracts only use assertions against `$.ast`.

---

## Step Result Envelope

**[NORMATIVE]**

Every step that uses `save_as` produces a standard envelope:

```yaml
result:
  ok: true | false        # did the operation succeed?
  value: <any>            # the payload (null if ok=false)
  error_code: <string>    # present if ok=false
  message: <string>       # present if ok=false
  meta:
    duration_ms: 45       # always present
    cache_hit: false      # optional, context-specific
  stdout: ""              # captured stdout (may be empty)
  stderr: ""              # captured stderr (may be empty)
```

JSONPath examples:
- `$.result.ok` — success boolean
- `$.result.value.temp` — nested payload access
- `$.result.meta.duration_ms` — timing
- `$.result.error_code` — error type when ok=false

### call_n Envelope (Special Case)

For `call_n`, the envelope aggregates multiple calls:

```yaml
samples:
  ok: true                # true if all calls succeeded
  n: 10                   # number of calls attempted
  durations_ms: [45, 47, 44, ...]
  p50_ms: 45
  p95_ms: 52
  p99_ms: 58
  mean_ms: 46
  min_ms: 44
  max_ms: 58
```

If any call fails (`ok: false`):
- `error_code`, `message`, `stdout`, `stderr` are included from first failure
- `durations_ms` contains only successful calls (may be empty)
- Percentile fields are omitted if insufficient data

---

## JSONPath Resolution

**[NORMATIVE]**

Rules for evaluating JSONPath expressions in assertions:

### Path Resolution
- Missing path resolves to `null` (not an error)
- Assertion against `null` follows normal operator semantics
- Report includes `error: path_not_found` in assertion detail when path missing

### Type Handling
- No implicit type coercion (numbers must be numbers, strings must be strings)
- Type mismatch causes assertion failure with `error: type_mismatch`
- `null` is a distinct type (not equal to `0`, `""`, `false`, or `[]`)
- `lt`, `lte`, `gt`, `gte`, `in_range` require numeric `actual` and `expected` (or `min`/`max`), else `type_mismatch`

### Operator-Specific Rules
- `matches`: Uses `re.search(pattern, string)` with default flags (no MULTILINE/DOTALL unless pattern includes inline flags like `(?m)`)
- `contains` on array: Checks if value is an element (exact equality, no substring matching on elements)
- `contains` on string: Checks if substring is present
- `contains` on object: **Not valid** — use `has_keys` instead
- `has_keys`: Passes if object contains at least the expected keys; extra keys are allowed. Only valid on objects.

### Report Output
When path resolution or type checking fails, assertion includes:

```json
{
  "op": "eq",
  "actual": null,
  "expected": 5,
  "pass": false,
  "error": "path_not_found",
  "path": "$.result.missing_field"
}
```

---

## Assertion DSL

**[NORMATIVE]**

Explicit operators, no magic parsing:

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `op: eq, actual: $.x, expected: 5` |
| `ne` | Not equals | `op: ne, actual: $.x, expected: null` |
| `lt` | Less than | `op: lt, actual: $.ms, expected: 2000` |
| `gt` | Greater than | `op: gt, actual: $.rms, expected: -60` |
| `lte` | Less than or equal | `op: lte, actual: $.peak, expected: 0.0` |
| `gte` | Greater than or equal | `op: gte, actual: $.count, expected: 1` |
| `has_keys` | Object has keys | `op: has_keys, actual: $.obj, expected: [a, b]` |
| `contains` | Array/string contains | `op: contains, actual: $.arr, expected: "x"` |
| `matches` | Regex match (Python re) | `op: matches, actual: $.str, expected: "^foo.*"` |
| `not_matches` | Regex must not match | `op: not_matches, actual: $.str, pattern: "forbidden.*"` |
| `file_exists` | File at path exists (implicit expected=true) | `op: file_exists, actual: $.path` |
| `in_range` | Value in [min, max] | `op: in_range, actual: $.x, min: 0, max: 100` |
| `approx` | Approximately equal (within tolerance) | `op: approx, actual: $.x, expected: 100, tolerance: 5` |
| `call_order` | Calls occur in sequence | `op: call_order, actual: $.ast.calls, expected: ["a", "b", "c"]` |

### JSONPath References

`$.` prefix references values from test context:
- `$.result` — saved output from a step
- `$.result.value.temp` — nested access
- `$.first.meta.cache_hit` — from named save
- `$.vars.target` — injected parameter (see Parameterisation)

**Both `actual` and `expected` may be JSONPath references** (strings starting with `$.`):

```yaml
# Compare two saved values
assert:
  - op: eq
    actual: $.first.hash
    expected: $.second.hash
```

### Implicit Expected Values

Some operators have implicit expected:
- `file_exists` — implicit `expected: true`

In report output, implicit values are made explicit for uniformity.

### YAML Value Typing

All `expected` scalar values are treated as strings/numbers/booleans per standard YAML typing. There is no symbol type. Unquoted `x` and quoted `"x"` both become the string `"x"`.

### call_order Semantics

`call_order` checks that the specified calls appear in order within the actual array. Non-matching elements are ignored (allows other calls between).

**Duplicate handling:** Matching is greedy left-to-right. Each expected element matches the first occurrence after the previous match.

```yaml
# Passes if $.ast.calls contains "a", then "b", then "c" (in that order)
# Other calls may appear before, between, or after
assert:
  - op: call_order
    actual: $.ast.calls
    expected: ["a", "b", "c"]
```

### approx Semantics

`approx` checks if `actual` is within `tolerance` of `expected`:

```yaml
assert:
  - op: approx
    actual: $.render.metrics.dc_offset
    expected: 0.0
    tolerance: 0.01
```

**Rules:**
- Passes iff `abs(actual - expected) <= tolerance`
- `actual`, `expected`, and `tolerance` MUST be numbers (else `type_mismatch`)
- Missing JSONPath -> ' `null` -> ' `type_mismatch`

---

## Step/Action Vocabulary

**[NORMATIVE]**

### Step Fields

| Field | Required | Type | Valid For | Notes |
|-------|----------|------|-----------|-------|
| `action` | Yes | enum | all | `call`, `call_n`, `render_nrt`, `shell`, `wait`, `setup`, `teardown` |
| `with` | No | object | call, call_n, render_nrt | Arguments passed to the action |
| `save_as` | No | string | all except warmup | Variable name for result envelope |
| `method` | No | string | call, call_n | Overrides `runner.symbol` |
| `n` | No | integer | call_n | Number of iterations (required for call_n) |
| `warmup` | No | boolean | call | If true, excluded from measurement; `save_as` must be absent |
| `command` | No | string[] | shell | Command and arguments |
| `seconds` | No | number | wait | Duration to wait |
| `fixture` | No | string | setup, teardown | Fixture identifier |

**Constraint:** `warmup: true` and `save_as` are mutually exclusive.

### Action Examples

```yaml
steps:
  # Call a function/method (single invocation)
  # Target: runner.symbol or step.method
  # Valid for: python, node
  - action: call
    with: { arg1: value1 }
    save_as: result

  # Call with explicit method override
  - action: call
    method: alternate_function
    with: { arg1: value1 }
    save_as: result

  # Call N times and aggregate metrics
  # Valid for: python, node
  - action: call_n
    with: { arg1: value1 }
    n: 10
    save_as: samples
    # Produces: durations_ms[], p50_ms, p95_ms, p99_ms, mean_ms, min_ms, max_ms

  # Warmup call (excluded from measurement, no save)
  - action: call
    with: { arg1: value1 }
    warmup: true

  # Wait (integration tests only)
  - action: wait
    seconds: 2

  # Set up fixture
  - action: setup
    fixture: clean_cache

  # Teardown
  - action: teardown
    fixture: clean_cache

  # Render audio via SuperCollider NRT
  # Valid ONLY for: executor: sclang
  - action: render_nrt
    with: { synthdef: "$.vars.target", dur_s: 3.0, sr: 48000, seed: 12345 }
    save_as: render
    # Produces: wav_path, hash, metrics {rms_db, peak_dbfs, dc_offset}

  # Run shell command
  # Valid for: all executors except static
  - action: shell
    command: ["sclang", "script.scd"]
    save_as: output
    # Produces: ok, stdout, stderr, exit_code
```

**Shell step environment:** Shell steps run with `cwd` set to the contract file's directory and inherit `runner.env` (plus `CONTRACT`, `RUN_ID`, `ARTIFACTS_DIR`). stdout/stderr are captured. Generated files should be placed in `$ARTIFACTS_DIR`.

### Action Validity by Executor

| Action | python | node | sclang | shell | static |
|--------|--------|------|--------|-------|--------|
| `call` | Y | Y | N | N | N |
| `call_n` | Y | Y | N | N | N |
| `render_nrt` | N | N | Y | N | N |
| `shell` | Y | Y | Y | Y | N |
| `wait` | Y | Y | Y | Y | N |
| `setup/teardown` | Y | Y | Y | Y | N |

**Static executor constraint:** For `executor: static`, `steps` MUST be absent or an empty array `[]`. Static contracts only use assertions against `$.ast`.

---

## Parameterisation

**[NORMATIVE]**

Contracts can be run against multiple targets using parameter injection.

### CLI Injection

```bash
# Single target
contract-test contracts/generator.audio.yaml --var target=ne_pack__gen

# Multiple targets (runs contract once per target)
contract-test contracts/generator.audio.yaml --var target=ne_pack__gen,ne_pack__pad,ne_pack__drone
```

### Matrix Definition

Contracts can define a matrix of targets:

```yaml
matrix:
  target:
    values: [ne_pack__gen, ne_pack__pad, ne_pack__drone]
```

Or discover targets:

```yaml
matrix:
  target:
    discover:
      pattern: "ne_*"
      source: synthdefs  # executor-specific discovery
```

### Discovery Timing

Discovery runs once before executing tests. Each discovered value spawns an independent Run with the same `run_id` prefix and a distinct suffix (e.g., `2025-12-27T15:30:00Z#A1B2-target-0`, `-target-1`, etc.).

### Accessing Parameters

Parameters are available under `$.vars`:

```yaml
steps:
  - action: render_nrt
    with:
      synthdef: "$.vars.target"
      dur_s: 3.0
    save_as: render
```

### Report Output

When running with matrix/multiple vars, report includes:

```json
{
  "contract": "generator.audio",
  "matrix_run": true,
  "vars": { "target": "ne_pack__gen" },
  "results": [...]
}
```

---

## Contract Resolution (extends)

**[NORMATIVE]**

When a contract uses `extends: base_contract`, resolution follows these rules:

### Merge Strategy

| Field | Strategy |
|-------|----------|
| `requirements` | Concatenate. Child overrides if same `id`. |
| `tests` | Concatenate. Child overrides if same `id`. |
| `runner` | Child overrides individual keys. |
| `inputs` | Concatenate. Child overrides if same `name`. |
| `outputs` | Concatenate. Child overrides if same `name`. |
| All other fields | Child overrides entirely. |

### Example

```yaml
# contracts/generator.yaml
contract: generator
version: 1.0.0
requirements:
  - id: R001
    description: Output is stereo
tests:
  - id: T001
    name: has_stereo_output

---
# contracts/generator.audio.yaml
contract: generator.audio
extends: generator
requirements:
  - id: R002
    description: No clipping
tests:
  - id: T002
    name: no_clipping
```

**Effective contract for generator.audio:**
- Requirements: R001, R002
- Tests: T001, T002

### Resolution in Reports

Reports include `effective_requirements` and `effective_tests` counts:

```json
{
  "contract": "generator.audio",
  "extends": "generator",
  "effective_requirements": 2,
  "effective_tests": 2
}
```

---

## Runner Configuration

Each contract specifies its executor:

```yaml
runner:
  executor: python | node | sclang | shell | static
  entry: src/api/client.py           # main file
  symbol: get_weather                # function to call (for call action)
  command: ["pytest", "-q"]          # optional custom command
  timeout_ms: 30000                  # per-test timeout
  artifacts_dir: artifacts/{contract}/{run_id}/
  script_template: tools/render.scd  # template for sclang executor
  parser: sclang_ast                 # required for static executor
  env:                               # environment variables
    API_KEY: test_key
```

**Timeout scope:** `runner.timeout_ms` applies **per-test** for all executors. It is the total time allowed for all steps within a single test. Individual step timeouts are not supported in v1.0.

### Executors

| Executor | Use Case | call action | static analysis |
|----------|----------|-------------|-----------------|
| `python` | Python code | Yes (via symbol/method) | No |
| `node` | JavaScript/TypeScript | Yes (via symbol/method) | No |
| `sclang` | SuperCollider | No (use render_nrt) | No |
| `shell` | Any CLI tool | No (use shell action) | No |
| `static` | Static analysis | No | Yes |

### Static Executor

For `executor: static`, the runner must specify a parser:

```yaml
runner:
  executor: static
  parser: sclang_ast | python_ast
```

**Constraints:**
- Regex-based parsing is explicitly excluded. AST parsing prevents false positives from comments/strings.
- For static executor, `steps` MUST be absent or an empty array `[]`.
- Static tests should use `type: unit` (they are deterministic and have no external dependencies).

The static executor populates `$.ast` with:
- `$.ast.calls` — Array of function/method calls found
- `$.ast.bus_reads` — Object of bus variable reads (domain-specific)
- `$.ast.source` — Original source (for reference, not assertion)

### Shell Executor

**[NORMATIVE]**

For `executor: shell`, the following runtime semantics apply:

**Working directory:**
- Shell steps run with `cwd` set to the **contract file's directory**
- This allows relative paths in shell commands to resolve predictably

**Artifacts directory:**
- `runner.artifacts_dir` is created before the first step executes
- Available as environment variable `$ARTIFACTS_DIR` in shell steps

**Environment:**
- `runner.env` variables are injected into each shell step's environment
- Standard variables also injected: `CONTRACT`, `RUN_ID`, `ARTIFACTS_DIR`

**Timeout:**
- `runner.timeout_ms` applies per-test (total time for all steps in a test)
- Individual step timeouts are not supported in v1.0

**Example:**
```yaml
runner:
  executor: shell
  timeout_ms: 60000
  artifacts_dir: artifacts/{contract}/{run_id}/
  env:
    API_KEY: test_key

tests:
  - id: T001
    name: check_installation
    type: unit
    steps:
      - action: shell
        command: ["python", "--version"]
        save_as: version
    assert:
      - op: eq
        actual: $.version.ok
        expected: true
```

### AST Output Schema

**[NORMATIVE]**

Static executors MUST produce `$.ast` conforming to this shape:

```yaml
ast:
  calls: string[]           # Function/method names in call order
  bus_reads: object         # { bus_name: true } for each bus read
  imports: string[]         # Imported modules/files (optional)
  definitions: string[]     # Defined functions/classes (optional)
  source: string            # Original source code (optional, included with --verbose)
  parse_errors: string[]    # Any non-fatal parse warnings (optional)
```

**Required fields:** `calls`, `bus_reads`

**Optional fields:** `source`, `imports`, `definitions`, `parse_errors`

**Stability note:** Only `calls` and `bus_reads` are stable/portable in v1.0. Other fields are optional and may vary by parser implementation.

The `source` field is omitted by default to reduce report size. Include with `--verbose` flag.

**Example output:**
```json
{
  "ast": {
    "calls": ["SinOsc.ar", "~ensure2ch", "~multiFilter", "~envVCA", "Out.ar"],
    "bus_reads": {
      "freqBus": true,
      "cutoffBus": true,
      "resBus": true
    },
    "parse_errors": []
  }
}
```

---

## Report Format

**[NORMATIVE]**

### Schema Version

Reports include `schema_version` to allow consumers to detect format compatibility:

| schema_version | Meaning |
|----------------|---------|
| `"1.0"` | Initial report format (this spec) |

**Versioning rules:**
- Minor version bump (1.0 -> ' 1.1): Additive changes only (new optional fields)
- Major version bump (1.x -> ' 2.0): Breaking changes to existing fields

Consumers should check `schema_version` before parsing. Unknown minor versions are safe to parse (ignore unknown fields). Unknown major versions should warn or fail.

### Report Structure

JSON output from a run:

```json
{
  "schema_version": "1.0",
  "contract": "api_client",
  "contract_version": "1.0.0",
  "runner_version": "{runner_version}",
  "run_id": "2025-12-27T15:30:00Z#A1B2",
  "git_sha": "d912033",
  "env": {
    "os": "fedora-41",
    "python": "3.12.2"
  },
  "timestamp": "2025-12-27T15:30:00Z",
  "duration_ms": 1234,
  "vars": {},
  "extends": null,
  "effective_requirements": 3,
  "effective_tests": 4,
  "summary": {
    "passed": 3,
    "failed": 1,
    "skipped": 0
  },
  "results": [
    {
      "test": "T001",
      "name": "valid_city_returns_data",
      "requirement": "R001",
      "type": "unit",
      "status": "pass",
      "duration_ms": 45,
      "assertions": [
        { "op": "eq", "actual": true, "expected": true, "pass": true }
      ]
    },
    {
      "test": "T002",
      "name": "invalid_city_returns_error",
      "requirement": "R002",
      "type": "unit",
      "status": "fail",
      "duration_ms": 32,
      "assertions": [
        { "op": "eq", "actual": true, "expected": false, "pass": false }
      ],
      "location": {
        "file": "src/api/client.py",
        "line": 45,
        "code": "return {'ok': True, 'value': None}"
      },
      "suggestion": "Return ok=false with error_code for invalid city",
      "stdout": "",
      "stderr": ""
    }
  ],
  "artifacts": [
    { "type": "log", "path": "artifacts/api_client/run.log" }
  ]
}
```

### Report Invariants

**[NORMATIVE]**

All reports MUST satisfy these invariants for cross-executor consistency:

**Status values:**
- `results[].status` ∈ `{"pass", "fail", "skipped", "error"}`
- No other status values are valid

**Assertions array:**
- `results[].assertions` is always present (even if empty `[]`)
- Each assertion record includes: `op`, `actual`, `expected`, `pass`
- Implicit expected values (e.g., `file_exists`) are rendered explicitly: `expected: true`

**Required top-level fields:**
- `schema_version`, `contract`, `contract_version`, `runner_version`
- `run_id`, `timestamp`, `duration_ms`
- `summary` with `passed`, `failed`, `skipped` counts
- `results` array (may be empty)

**Optional top-level fields:**
- `git_sha`, `env`, `vars`, `extends`, `artifacts`
- `effective_requirements`, `effective_tests` (when using extends)
- `report_type` (only for matrix summary reports)

---

## Test Filtering

**[NORMATIVE]**

Tests are filtered by `type` (primary) and `tags` (secondary):

```bash
# Filter by type
contract-test contracts/api_client.yaml --type unit
contract-test contracts/api_client.yaml --type integration

# Filter by tag
contract-test contracts/api_client.yaml --tag performance

# Combine
contract-test contracts/api_client.yaml --type integration --tag performance
```

- `--type` filters on the `type` field (required on all tests)
- `--tag` filters on the `tags` array (optional)
- Multiple `--tag` flags are OR'd

---

## Test Skipping

**[NORMATIVE]**

Tests can be conditionally skipped:

### Static Skip

```yaml
tests:
  - id: T001
    name: windows_only_test
    skip: true  # Always skipped
```

### Conditional Skip

```yaml
tests:
  - id: T002
    name: linux_specific
    skip_if: "$.env.os_family != 'linux'"  # JSONPath expression against run context
```

`skip_if` is evaluated before test execution. If the expression evaluates to truthy, the test is skipped.

### skip_if Context

**[NORMATIVE]**

The following fields are available in `skip_if` expressions:

| Path | Type | Description | Example |
|------|------|-------------|---------|
| `$.env.os` | string | Operating system (detailed) | `"fedora-41"`, `"ubuntu-24.04"`, `"darwin-23.1"`, `"windows-11"` |
| `$.env.os_family` | string | OS family (for skip logic) | `"linux"`, `"darwin"`, `"windows"` |
| `$.env.python` | string | Python version string | `"3.12.2"` |
| `$.env.python_major` | int | Python major version | `3` |
| `$.env.python_minor` | int | Python minor version | `12` |
| `$.env.node` | string | Node version string | `"20.10.0"` |
| `$.env.node_major` | int | Node major version | `20` |
| `$.env.sclang` | string | SuperCollider version string | `"3.14.0"` |
| `$.env.sclang_major` | int | SuperCollider major version | `3` |
| `$.env.sclang_minor` | int | SuperCollider minor version | `14` |
| `$.vars.*` | any | Injected parameters | `$.vars.target` |

This list is exhaustive. Additional context fields require a spec version bump.

**Version comparison note:** Use numeric fields (`_major`, `_minor`) for version comparisons. String comparison is lexicographic and will produce wrong results (e.g., `"3.9" > "3.10"` is true lexicographically).

### skip_if Expression Grammar

**[NORMATIVE]**

`skip_if` uses a restricted expression language. The following are the ONLY allowed constructs:

**Literals:**
- Numbers: `42`, `3.14`, `-1`
- Strings: `"windows"`, `'linux'`
- Booleans: `true`, `false`
- Null: `null`

**JSONPath references:**
- `$.env.*`, `$.vars.*` (as defined in context table above)

**Comparison operators:**
- `==`, `!=`, `<`, `<=`, `>`, `>=`

**Boolean operators:**
- `and`, `or`, `not`

**Grouping:**
- Parentheses: `(`, `)`

**NOT allowed:**
- Function calls
- Arithmetic operators (`+`, `-`, `*`, `/`)
- Property access beyond JSONPath resolution
- Regular expressions
- Array indexing

**Examples:**
```yaml
# Valid
skip_if: '$.env.os_family == "windows"'
skip_if: '$.env.os_family == "windows" or $.env.os_family == "darwin"'
skip_if: 'not ($.vars.target == null)'
skip_if: '$.env.python_minor >= 10 and $.env.os_family != "windows"'

# Invalid (will fail lint)
skip_if: '$.env.os.toLowerCase() == "windows"'  # function call
skip_if: '$.vars.count + 1 > 5'                  # arithmetic
skip_if: '$.vars.items[0] == "x"'                # array indexing
skip_if: '$.env.python >= "3.10"'                # string version compare (use _minor)
```

### skip_if Evaluation Rules

**JSONPath resolution:** Uses standard JSONPath rules (missing path -> ' `null`).

**Type coercion:** None. Comparing incompatible types (e.g., `"3" > 2`) results in `false`.

**Error handling by contract status:**

| Status | Eval Error Behavior |
|--------|---------------------|
| `frozen` | Lint fails. Expression must be valid before freeze. |
| `draft` | Test marked `status: "error"` with `skip_reason: "skip_if_eval_error: <details>"` |

### Skip Reporting

Skipped tests appear in report with `status: "skipped"` and count toward `summary.skipped`:

```json
{
  "test": "T002",
  "name": "linux_specific",
  "status": "skipped",
  "skip_reason": "$.env.os_family != 'linux' evaluated to true"
}
```

**Skipped tests do not fail the run.**

---

## Requirement Priority

**[NORMATIVE]**

Requirements have priority levels:

| Priority | Meaning |
|----------|---------|
| `must` | Critical requirement. Failure blocks release. |
| `should` | Important requirement. Failure is significant. |
| `nice` | Nice-to-have. Failure is noted but less critical. |

### Enforcement Behavior

**Priority is advisory, not enforcement.**

- All test failures are failures regardless of requirement priority
- `contract-test` exits 1 if any test fails (must, should, or nice)
- Priority is for human triage, not automated gating

**Rationale:** If you don't want a test to fail the build, use `skip: true` or don't write the test. Priority helps humans understand severity, not machines ignore failures.

### Future Extension

A future `--must-only` flag could run only tests linked to `must` requirements, but this is not in v1.0.

---

## Matrix Failure Modes

**[NORMATIVE]**

When running with matrix or multiple `--var` values:

### Default Behavior

All matrix values are tested. Failures are collected and reported at the end.

```bash
contract-test contracts/generator.yaml --var target=a,b,c
# Runs all 3, reports combined results
# Exit 1 if ANY failed
```

### Fail-Fast Mode

```bash
contract-test contracts/generator.yaml --var target=a,b,c --fail-fast
# Stops on first failure
# Exit 1 immediately
```

When `--fail-fast` triggers:
- Remaining targets are not executed
- `matrix_summary.total_targets` reflects how many **would have run** (from discovery/list)
- `matrix_summary.skipped_targets` shows how many were not attempted due to fail-fast
- `runs` array contains only completed runs

### Report Structure

Matrix runs produce **two report types**:

#### Per-Target Report

Standard report schema with `vars` populated for that target:

```json
{
  "schema_version": "1.0",
  "contract": "generator.audio",
  "vars": { "target": "ne_pack__gen" },
  "summary": { "passed": 5, "failed": 0, "skipped": 0 },
  "results": [...]
}
```

#### Matrix Summary Report

Aggregates results across all targets:

```json
{
  "schema_version": "1.0",
  "report_type": "matrix_summary",
  "contract": "generator.audio",
  "matrix_summary": {
    "total_targets": 50,
    "passed_targets": 48,
    "failed_targets": 2,
    "skipped_targets": 0,
    "failed_target_ids": ["ne_pack__broken1", "ne_pack__broken2"]
  },
  "runs": [
    { "vars": {"target": "ne_pack__gen"}, "summary": {"passed": 5, "failed": 0, "skipped": 0} },
    { "vars": {"target": "ne_pack__broken1"}, "summary": {"passed": 3, "failed": 2, "skipped": 0} }
  ]
}
```

**Invariant:** Matrix summary reports MUST set `report_type: "matrix_summary"`. Per-target reports MUST NOT include `report_type`.

The `runs` array contains **summaries only** (not full results). Full per-target reports are available separately.

With `--fail-fast` after first failure:
```json
{
  "schema_version": "1.0",
  "report_type": "matrix_summary",
  "contract": "generator.audio",
  "matrix_summary": {
    "total_targets": 50,
    "passed_targets": 0,
    "failed_targets": 1,
    "skipped_targets": 49,
    "failed_target_ids": ["ne_pack__broken1"]
  },
  "runs": [
    { "vars": {"target": "ne_pack__broken1"}, "summary": {"passed": 3, "failed": 2, "skipped": 0} }
  ]
}
```

### Report File Outputs

**[NORMATIVE]**

When `--keep` is specified, reports are written to disk:

**Single target (no matrix):**
```
artifacts/{contract}/{run_id}/report.json
```

**Matrix runs:**
```
artifacts/{contract}/{run_id}/
  matrix_summary.json              # Matrix summary report
  runs/
    {target_0}.json                # Per-target report (sanitized target name)
    {target_1}.json
    ...
```

**Target name sanitization:** Replace `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` with `_`.

**Matrix summary cross-reference:** The `runs[]` array includes `report_path` for each target:

```json
{
  "runs": [
    {
      "vars": {"target": "ne_pack__gen"},
      "summary": {"passed": 5, "failed": 0, "skipped": 0},
      "report_path": "runs/ne_pack__gen.json"
    }
  ]
}
```

---

## Determinism Rules

| Test Type | Rules |
|-----------|-------|
| `unit` | Must be deterministic. No network, no wall-clock, no random without seed. |
| `integration` | May touch network. Tag with relevant tags. Allow skip in CI. |
| `e2e` | Full system test. May be slow. Tag appropriately. |

For performance testing, always use `call_n` with percentile assertions.

---

## Contract Lifecycle

### Status Field

```yaml
status: draft | frozen | deprecated
```

| Status | Meaning |
|--------|---------|
| `draft` | Work in progress, may change |
| `frozen` | Locked, changes require version bump |
| `deprecated` | Superseded, do not use |

### Rules

1. **Only frozen contracts can ship** — Draft contracts are for development
2. **Changes to frozen require version bump** — No silent modifications
3. **Changelog required** — Document what changed and why

---

## Tooling

### Requirement Coverage Rules

**[NORMATIVE]**

Coverage is calculated based on `tests[].requirement` links:

- Only tests with `requirement: R###` count toward coverage
- Tests without `requirement` are excluded from coverage calculation
- For `status: frozen` contracts: every test SHOULD link a requirement
- Tests tagged `meta` are explicitly excluded from coverage (utility/setup tests)
- **Unlinked tests do not affect pass/fail; they only trigger warnings in frozen contracts**

```yaml
# Counts toward R001 coverage
- id: T001
  requirement: R001
  
# Excluded from coverage (no requirement link)
- id: T002
  tags: [meta]
  
# Warning in frozen contracts (unlinked test), but does not fail lint
- id: T003
  # no requirement field
```

`contract-lint` behavior:
- **Fails** if any requirement has zero linked tests
- **Warns** on unlinked tests in frozen contracts (does not fail)
- **Passes** if all requirements have ≥1 linked test, regardless of unlinked tests

### CLI Tools

```bash
# Validate contract schema + requirement coverage (gate)
contract-lint contracts/**/*.yaml
# Exit 0: schema valid, all requirements have ≥1 test
# Exit 1: schema error OR any requirement has 0 tests

# Run one contract
contract-test contracts/api_client.yaml
# Exit 0: all tests pass
# Exit 1: any test fails

# Run with parameters
contract-test contracts/generator.audio.yaml --var target=ne_pack__gen

# Run matrix with fail-fast (stop on first failure)
contract-test contracts/generator.audio.yaml --var target=a,b,c --fail-fast

# Run with artifacts preserved
contract-test contracts/api_client.yaml --keep --artifacts out/

# Run with verbose output (includes AST source in static tests)
contract-test contracts/api_client.yaml --verbose

# Run all contracts
contract-test contracts/ --all

# Filter by type/tag
contract-test contracts/api_client.yaml --type unit
contract-test contracts/api_client.yaml --tag performance

# Requirement coverage report (informational)
contract-coverage contracts/
# Always exits 0. Output: R001 (2 linked tests), R002 (1 linked test), R003 (0 linked tests) -> Â gap!

# Requirement coverage with strict mode (gate)
contract-coverage contracts/ --strict
# Exit 0: all requirements covered
# Exit 1: any requirement has 0 linked tests

# Generate implementation scaffold (Phase 2 - not yet implemented)
contract-scaffold contracts/api_client.yaml --output src/api/
```

### Tool Purposes

| Tool | Purpose |
|------|---------|
| `contract-lint` | **Gate.** Schema validation + requirement coverage. Fails on schema errors or uncovered requirements; warns on unlinked tests in frozen contracts. |
| `contract-test` | **Gate.** Run tests. Fails if any test fails. |
| `contract-coverage` | **Report.** Show coverage gaps. Only fails with `--strict`. |
| `contract-scaffold` | **Generator.** Create implementation stubs from contract. |

### Exit Codes

| Tool | Exit 0 | Exit 1 |
|------|--------|--------|
| `contract-lint` | Schema valid AND all requirements have tests | Schema error OR uncovered requirement |
| `contract-test` | All tests pass | Any test fails |
| `contract-coverage` | Always (default) | Uncovered requirements (with `--strict`) |

---

## Noise Engine: Audio Contracts

**[ILLUSTRATIVE]**

### Generator Contract (Base)

```yaml
contract: generator
version: 1.0.0
status: frozen

description: |
  Base requirements for all Noise Engine generators

runner:
  executor: static
  parser: sclang_ast

requirements:
  - id: R001
    priority: must
    description: Output wrapped in ~ensure2ch
    acceptance_criteria:
      - ~ensure2ch is called on output signal
      
  - id: R002
    priority: must
    description: Uses standard post-chain
    acceptance_criteria:
      - ~envVCA is called for amplitude envelope
      - ~multiFilter is called for filtering
      - Correct call order maintained
      
  - id: R003
    priority: must
    description: Reads all standard buses
    acceptance_criteria:
      - All required bus reads present in AST

tests:
  - id: T001
    name: has_ensure2ch
    requirement: R001
    type: unit
    assert:
      - op: contains
        actual: $.ast.calls
        expected: "~ensure2ch"
        
  - id: T002
    name: has_envVCA
    requirement: R002
    type: unit
    assert:
      - op: contains
        actual: $.ast.calls
        expected: "~envVCA"
        
  - id: T003
    name: has_multiFilter
    requirement: R002
    type: unit
    assert:
      - op: contains
        actual: $.ast.calls
        expected: "~multiFilter"
        
  - id: T004
    name: correct_call_order
    requirement: R002
    type: unit
    assert:
      - op: call_order
        actual: $.ast.calls
        expected: ["~ensure2ch", "~multiFilter", "~envVCA"]
        
  - id: T005
    name: reads_all_standard_buses
    requirement: R003
    type: unit
    assert:
      - op: has_keys
        actual: $.ast.bus_reads
        expected:
          - freqBus
          - cutoffBus
          - resBus
          - attackBus
          - decayBus
          - filterTypeBus
          - envEnabledBus
          - clockRateBus
          - clockTrigBus

matrix:
  target:
    discover:
      pattern: "ne_*"
      source: synthdefs
```

### Generator Audio Contract (Extends Base)

```yaml
contract: generator.audio
version: 1.0.0
status: frozen
extends: generator

description: |
  Audio rendering requirements for generators

runner:
  executor: sclang
  script_template: tools/render_contract_test.scd
  timeout_ms: 45000
  artifacts_dir: artifacts/{contract}/{run_id}/

requirements:
  - id: R004
    priority: must
    description: Renders without silence
    acceptance_criteria:
      - RMS > -60dB over 3 second render
      
  - id: R005
    priority: must
    description: No clipping
    acceptance_criteria:
      - Peak < -0.1dBFS
      
  - id: R006
    priority: must
    description: No DC offset
    acceptance_criteria:
      - DC offset within ±0.01
      
  - id: R007
    priority: must
    description: Deterministic output
    acceptance_criteria:
      - Same seed produces identical audio hash

tests:
  - id: T010
    name: renders_without_silence
    requirement: R004
    type: integration
    steps:
      - action: render_nrt
        with: 
          synthdef: "$.vars.target"
          dur_s: 3.0
          sr: 48000
          seed: 12345
        save_as: render
    assert:
      - op: file_exists
        actual: $.render.wav_path
      - op: gt
        actual: $.render.metrics.rms_db
        expected: -60
        
  - id: T011
    name: no_clipping
    requirement: R005
    type: integration
    steps:
      - action: render_nrt
        with:
          synthdef: "$.vars.target"
          dur_s: 3.0
          sr: 48000
          seed: 12345
        save_as: render
    assert:
      - op: lt
        actual: $.render.metrics.peak_dbfs
        expected: -0.1
        
  - id: T012
    name: no_dc_offset
    requirement: R006
    type: integration
    steps:
      - action: render_nrt
        with:
          synthdef: "$.vars.target"
          dur_s: 3.0
          sr: 48000
          seed: 12345
        save_as: render
    assert:
      - op: in_range
        actual: $.render.metrics.dc_offset
        min: -0.01
        max: 0.01
        
  - id: T013
    name: deterministic_output
    requirement: R007
    type: integration
    steps:
      - action: render_nrt
        with: { synthdef: "$.vars.target", dur_s: 1.0, seed: 99999 }
        save_as: first
      - action: render_nrt
        with: { synthdef: "$.vars.target", dur_s: 1.0, seed: 99999 }
        save_as: second
    assert:
      - op: eq
        actual: $.first.hash
        expected: $.second.hash

matrix:
  target:
    discover:
      pattern: "ne_*"
      source: synthdefs
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Lock contract schema (this spec -> ' v1.0 frozen)
- Implement `contract-lint` (schema validation + requirement coverage)
- Implement `contract-test` for Python executor
- Create example contract as proof of concept

### Phase 2: Parameterisation (Week 2)
- Implement `--var` CLI injection
- Implement matrix discovery
- Create `generator` contract with matrix

### Phase 3: Audio Executor (Week 3)
- Implement `sclang` executor with NRT render
- Audio metrics extraction (RMS, peak, DC offset)
- Create `generator.audio` contract
- Migrate `forge_audio_validate.py` to use contracts

### Phase 4: Full Migration (Week 4)
- All existing validation uses contracts
- `contract-coverage` shows requirement gaps
- New features start as contracts

---

## Success Criteria

- [ ] Contract schema is locked (v1.0 frozen)
- [ ] `contract-lint` validates schema and requirement coverage
- [ ] `contract-test` runs for Python executor with call/call_n
- [ ] Parameterisation works via --var and matrix
- [ ] Report format provides enough context for AI-assisted debugging
- [ ] Noise Engine generator contracts replace existing validation tools
- [ ] New features begin with frozen contract before implementation

---

## Changelog


- **1.1.5** (2025-12-29): Mandatory gates and anti-patterns — `No behavior change`
  - Added Mandatory Gates section (G0-G3) with sequence diagram
  - Added Process Checkpoints table
  - Added Anti-Patterns appendix (AP1-AP6)
  - Added HTML analyzer support (`cdd analyze *.html`)
  - Clarifies process enforcement without changing contract schema or tooling behavior

- **1.1.4** (2025-12-29): Analysis-first methodology — `No behavior change`
  - Added "Analysis precedes contracts" as first principle in What section
  - Added Reference, Analysis, Baseline to Glossary
  - Updated The Model diagram to include Reference Analysis and Compare phases
  - Clarifies process without changing contract schema or tooling behavior

- **1.1.3** (2025-12-28): Shell variable interpolation — `No behavior change`
  - Interpolate variables in shell command arguments (bug fix)

- **1.1.2** (2025-12-28): Path resolution fix — `No behavior change`
  - Fix repo_root detection when passing single contract file

- **1.1.1** (2025-12-27): Static scanning integration — `Additive, backwards compatible`
  - Native static file scanning wired into runner
  - Expanded README with full usage guide

- **1.1.0** (2025-12-27): Tooling integration "” `Additive, backwards compatible`
  - Added `cdd_spec` field to Project Contract Fields (required for frozen, optional for draft)
  - Tooling reads `cdd_spec` for version compatibility checking
  - Fallback to `.cdd-version` file if `cdd_spec` not present
  - Major version mismatch = error; minor/patch = warning
  - Added `--require-exact-spec` flag for strict enforcement

- **1.0.14** (2025-12-27): Schema completeness — `No behavior change`
  - Added normative Step Fields table (action, with, save_as, method, n, warmup, command, seconds, fixture)
  - Clarified `contains` on arrays uses exact element equality (no substring matching)
  - Updated coverage example to say "linked tests" for clarity
  - Renamed Process Evolution to "Appendix: Process Evolution"

- **1.0.13** (2025-12-27): Review fixes — `No behavior change`
  - Fixed `±` encoding issue
  - Added `$.env.os_family` for clean platform skip logic (os remains detailed string)
  - Fixed `contract-lint` Tool Purposes description to match warning behavior
  - Added explicit `report_type` invariant for matrix summary reports

- **1.0.12** (2025-12-27): Anti-mutation guardrails — `No behavior change`
  - Added Compatibility Promise with table format and behavioral test clause
  - Added Normative Core definition (explicit list of protected sections)
  - Added non-normative section guardrail (prevents accidental behavioral language)
  - Added "Reference runner is arbiter" rule with divergence clause
  - Added changelog compatibility notes requirement with format example
  - Renumbered rules for clarity

- **1.0.11** (2025-12-27): Process Evolution governance — `No behavior change`
  - Added Process Evolution section (governance, not normative)
  - Defined feedback loop for spec improvements
  - Added "spec before tooling" anti-drift rule
  - Defined dual-AI review requirements

- **1.0.10** (2025-12-27): Report invariants and AST stability — `No behavior change`
  - Added Report Invariants block (status values, assertions array, required/optional fields)
  - Added AST field stability note (only calls/bus_reads are stable in v1.0)

- **1.0.9** (2025-12-27): Report file outputs and timeout clarification
  - Added report file output convention for matrix runs (`matrix_summary.json`, `runs/*.json`)
  - Added `report_path` cross-reference in matrix summary `runs[]`
  - Clarified `timeout_ms` applies per-test for all executors

- **1.0.8** (2025-12-27): Shell executor and coverage clarifications
  - Added shell executor runner-level semantics (cwd, artifacts_dir, env, timeout)
  - Clarified requirement coverage pass/fail behavior (unlinked tests warn, don't fail)

- **1.0.7** (2025-12-27): Implementation footgun fixes
  - Added numeric version fields to skip_if context (`_major`, `_minor`) for safe version comparisons
  - Added requirement coverage mapping rules (only linked tests count)
  - Split matrix reporting into two explicit shapes (per-target report, matrix summary report)
  - Marked `contract-scaffold` as Phase 2 (not yet implemented)
  - Fixed skip_if example to use numeric version fields

- **1.0.6** (2025-12-27): Phase 1 critical additions
  - Added `approx` operator for float/timing comparisons with tolerance
  - Locked down `skip_if` expression grammar (restricted safe subset)
  - Differentiated `skip_if` error handling by contract status (frozen fails lint, draft marks error)

- **1.0.5** (2025-12-27): Report format versioning
  - Added `schema_version` field to report format
  - Documented schema versioning rules (minor = additive, major = breaking)

- **1.0.4** (2025-12-27): Edge case clarifications
  - Made AST `source` field optional (included with `--verbose`)
  - Added exhaustive `skip_if` context list
  - Defined `skip_if` error handling (skip with warning, not fail)
  - Clarified `--fail-fast` matrix_summary behavior (`skipped_targets` field)
  - Changed report example `runner_version` to placeholder

- **1.0.3** (2025-12-27): Gap closures
  - Added AST output schema (required shape for static executors)
  - Added test skipping (`skip`, `skip_if` fields)
  - Added requirement priority enforcement semantics (advisory, not gating)
  - Added matrix failure modes (`--fail-fast`, matrix_summary in report)

- **1.0.2** (2025-12-27): Semantic lock-downs
  - Added `has_keys` subset semantics (extra keys allowed)
  - Added numeric type requirement for comparison operators
  - Locked `matches` to `re.search()` with default flags
  - Added matrix discovery timing (once before tests, independent runs)
  - Added static tests `type: unit` recommendation

- **1.0.1** (2025-12-27): Clarifications
  - Added YAML value typing note (no symbol type)
  - Added call_order greedy left-to-right duplicate handling rule
  - Added shell step environment clarification (cwd, env, artifacts)

- **1.0.0** (2025-12-27): Initial frozen release
  - Complete schema with field tables
  - Assertion DSL with 12 operators
  - JSONPath resolution rules
  - Step/action vocabulary with executor validity matrix
  - Step result envelope including call_n special case
  - Parameterisation via CLI and matrix
  - Contract resolution (extends) semantics
  - Report format specification
  - Tooling with exit codes
  - Noise Engine illustrative contracts with requirements

---

## Appendix: Anti-Patterns

**[GOVERNANCE]** *(guidance for practitioners, not enforced by tooling)*

### AP1: Visual Verification

**Wrong:**
> "Can you look at the wireframe and confirm the icon is there?"

**Right:**
> Run `cdd analyze wireframe.html -o analysis/` and check `required_elements.app_icon: true`

Human visual verification is subjective and non-reproducible. Analysis tools provide objective, repeatable checks.

### AP2: Manual Grep Instead of Contract Tests

**Wrong:**
```bash
grep "display-mode.*standalone" output.html && echo "Pass"
```

**Right:**
```yaml
tests:
  - id: T001
    type: unit
    files: docs/index.html
    assert:
      - op: matches
        actual: $.file.content
        pattern: "display-mode:\\s*standalone"
```

Ad-hoc verification doesn't get recorded in the contract. Future runs won't repeat the check.

### AP3: Skipping Gates "Just This Once"

**Wrong:**
> "The tests aren't wired up yet, let's deploy and backfill later"

**Right:**
> Wire up tests before implementation. If tests can't run, the contract isn't ready.

"Later" becomes "never". Gates exist because skipping them causes the problems they prevent.

### AP4: Analysis Tool Outside Framework

**Wrong:**
> Create `analyze_html.py` as standalone script, reference in contract

**Right:**
> Add analyzer to CDD tooling, use `cdd analyze` command

Standalone scripts break the contract→test→report chain. Tests can't find the tool.

### AP5: Draft Contracts in Production

**Wrong:**
> Deploy with `status: draft`

**Right:**
> Set `status: frozen` after G2 passes, before deploy

Draft status means "this may change". Production code should not depend on things that may change.

### AP6: Requirements Without Source References

**Wrong:**
```yaml
- id: R001
  description: Input fields have underlines  # Says who?
```

**Right:**
```yaml
- id: R001
  description: Input fields use rectangular boxes
  source_ref: SRC001#E1_5  # Points to analyzed element
```

Ungrounded requirements are assumptions. Assumptions cause rework.

---

## Appendix: Process Evolution

**[GOVERNANCE]** *(normative for spec maintenance, not enforced by tooling)*

Projects using this spec may reveal gaps or ambiguities; changes follow the loop below.

### Feedback Loop

| Phase | Location | Action |
|-------|----------|--------|
| **Discover** | Project repo | Document issue and workaround in project notes |
| **Validate** | Project repo | Confirm the fix works in practice |
| **Generalize** | Spec repo | Strip project-specific details, propose change |
| **Review** | Spec repo | Dual-AI review required for normative changes |
| **Release** | Spec repo | Version bump + changelog entry |

### When to Checkpoint

- New operator needed that would benefit other projects
- Ambiguity caused implementation divergence
- Edge case not covered by current spec
- Tooling revealed spec gap
- Spec bug fix — A normative mistake that would cause incorrect runner behavior can be patched without project-first validation
  - Must include a regression test in the reference runner (once it exists) and a clear changelog note

### Version Semantics

| Bump | When | Example |
|------|------|---------|
| Patch (1.0.x) | Clarifications, examples, typos | 1.0.10 -> ' 1.0.11 |
| Minor (1.x.0) | New optional features, additive changes; backwards compatible defaults | 1.0.11 -> ' 1.1.0 |
| Major (x.0.0) | Breaking changes to normative sections | 1.1.0 -> ' 2.0.0 |

### Compatibility Promise

| Bump | MUST NOT | MAY |
|------|----------|-----|
| Patch | Change runner-observable behavior | Clarify wording, fix typos, add examples, update non-normative text |
| Minor | Break existing contracts or runners | Add new optional fields, operators, actions with backwards-compatible defaults |
| Major | *(no restrictions)* | Change any behavior |

**Test:** If an existing contract would produce different results (pass-> 'fail, fail-> 'pass, different report shape), it's not a patch. If an existing runner would reject a previously-valid contract or produce wrong output, it's not minor.

### Normative Core

The following sections constitute the Normative Core:

- Contract Schema
- Contract Field Requirements
- Assertion DSL
- JSONPath Resolution
- Step/Action Vocabulary
- Step Result Envelope
- Report Format and Invariants
- Contract Resolution (extends)
- Parameterisation
- Executor-specific semantics (shell, static, etc.)

**Rule:** Any change to Normative Core semantics requires at least a minor bump. Any change that alters behavior for existing contracts requires a major bump.

**Non-normative sections** (Illustrative examples, Implementation Phases, Success Criteria, this Appendix) may be updated without version bump, but MUST NOT introduce behavioral language ("runner SHOULD...", "contracts MUST...") that could be mistaken for normative requirements.

### Rules

1. **Spec before tooling** — If tooling implements behavior not described in the spec, the tooling is experimental until the spec is updated or the behavior removed
2. **Reference runner is arbiter** — Once a reference runner exists, any normative change MUST be accompanied by a reference-runner test demonstrating the intended behavior. If spec and runner diverge, the spec is authoritative and the runner is buggy.
3. **Project-first** — Test changes in a real project before proposing
4. **Generalize** — Spec changes must apply beyond the originating project
5. **Dual-AI review** — Normative changes require two independent AI passes (fresh context), each confirming: ambiguity removed, backwards compatibility preserved, examples consistent
6. **Changelog with compatibility** — Every changelog entry must include a compatibility note:
   ```
   - **X.Y.Z** (date): Summary — `No behavior change` | `Additive, backwards compatible` | `Breaking`
   ```
7. **Frozen means frozen** — Breaking changes to frozen sections require major version bump

---

*Version 1.1.5 — Frozen. Reviewed and approved by AI1 and AI2.*
