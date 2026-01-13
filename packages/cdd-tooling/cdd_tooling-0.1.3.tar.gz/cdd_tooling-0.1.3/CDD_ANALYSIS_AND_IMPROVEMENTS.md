# CDD Analysis and Improvement Proposal

**Date:** 2025-12-31 (updated)  
**Based on:** CDD v1.1.5 codebase analysis  
**Problem Statement:** Contracts based on assumptions lead to iterative rework; gates without enforcement get skipped

---

## Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| `cdd analyze` (PDF) | ✅ Done | `src/cdd_tooling/analyze/pdf.py` |
| `cdd analyze` (HTML) | ✅ Done | `src/cdd_tooling/analyze/html.py` |
| `cdd analyze` (source) | ✅ Done | `src/cdd_tooling/analyze/source.py` |
| `cdd compare` | ✅ Done | Compare two analyses |
| `cdd paths` | ✅ Done | `src/cdd_tooling/paths/` |
| `cdd isolate` | ✅ Done | `src/cdd_tooling/isolate/` |
| `source_ref` field | 🔲 TODO | Links requirements to analysis |
| `visual_ref` field | 🔲 TODO | Links to reference images |
| `cdd validate` command | 🔲 TODO | Check source_refs exist |
| `sources` in project contract | 🔲 TODO | Declare source artifacts |
| Assumption language lint | 🔲 TODO | Detect vague wording |
| Mandatory gates | 🔲 TODO | G1/G2/G3 enforcement |
| `cdd gate` command | 🔲 TODO | Single command for all gates |

---

## Part 1: Current State Analysis

### What CDD Does Well

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT CDD PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   contracts/*.yaml  ──►  cdd lint  ──►  cdd test  ──►  report  │
│                              │              │                   │
│                              ▼              ▼                   │
│                      Schema valid?    Tests pass?               │
│                      Coverage OK?                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implemented Features:**
- ✅ YAML schema validation (lint)
- ✅ Requirement coverage checking (every req needs ≥1 test)
- ✅ Multiple executors (python, shell, static, sclang)
- ✅ Assertion DSL (12 operators)
- ✅ JSONPath resolution
- ✅ Variable injection (`--var`)
- ✅ Static file scanning with regex assertions
- ✅ Spec version compatibility checking
- ✅ PDF analysis (`cdd analyze *.pdf`)
- ✅ HTML analysis (`cdd analyze *.html`)
- ✅ Source analysis (`cdd analyze *.py`, `*.js`, etc.)
- ✅ Analysis comparison (`cdd compare`)
- ✅ Path verification (`cdd paths`)
- ✅ Isolated contract testing (`cdd isolate`)

**Code Quality:**
- Clean separation: cli.py → runner.py → executors → assertions
- Proper dataclasses (RunContext, StepResult, AssertionResult)
- Rich console output for human-readable reports
- JSON output for machine consumption

### The Gaps

#### Gap 1: No Source Validation

The linter checks:
```python
# From lint/__init__.py
def _lint_component(...):
    required = ["contract", "version", "status", "description", 
                "runner", "requirements", "tests"]
    # ✅ Checks fields exist
    # ✅ Checks requirement coverage
    # ❌ Does NOT check if requirements are grounded in evidence
```

**What's missing:** There's no validation that requirements describe reality.

#### Gap 2: No Gate Enforcement

Gates exist but nothing enforces them:
```python
# Current: gates are advisory
cdd lint contracts/   # Can ignore exit code
cdd test contracts/   # Can skip entirely
# Deploy anyway
```

**What's missing:** Hard stops that prevent proceeding without passing.

---

## Part 2: Failure Modes

### Failure Mode 1: Assumption-Based Contracts (Pyro-Logger PDF)

```
1. User: "Replicate this PDF form"
2. AI: *glances at PDF* → writes contract with "underlines for input fields"
3. Lint: ✅ PASS (schema valid, requirements covered)
4. Build: implements underlines
5. User: "Wrong! The original has boxes, not underlines"
6. Analysis: extract PDF images, discover actual layout
7. Fix contract, rebuild
```

**Root cause:** Contract written without analyzing source first.

### Failure Mode 2: Skipped Gates (Pyro-Logger Installer)

```
1. Phase 0: ✅ Reference + analysis tool + baseline created
2. Contract: ✅ Requirements + tests written
3. Lint: ⏭️ SKIPPED
4. Implement: ✅ Code written
5. Test: ⏭️ SKIPPED (tests weren't runnable anyway)
6. Freeze: ⏭️ SKIPPED
7. Deploy: ✅ Pushed to production
```

**Root cause:** No enforcement mechanism; human discipline failed.

---

## Part 3: Mandatory Gates

**[PROPOSED NORMATIVE ADDITION TO SPEC.md]**

### Gate Definitions

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

### Enforcement Mechanisms

```bash
# Option 1: Single gate command
cdd gate contracts/
# Runs: lint → test → frozen check
# Exits 0 only if all pass

# Option 2: CI workflow
- run: cdd lint contracts/
- run: cdd test contracts/
- run: |
    if grep -q "status: draft" contracts/*.yaml; then
      echo "ERROR: Cannot deploy draft contracts"
      exit 1
    fi

# Option 3: Pre-commit hook
# .git/hooks/pre-push
cdd gate contracts/ || exit 1
```

---

## Part 4: Anti-Patterns

**[PROPOSED GOVERNANCE ADDITION TO SPEC.md]**

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

## Part 5: Source-First Workflow

### The Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SOURCE-FIRST CDD WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. ACQUIRE                                                                 │
│     User provides source artifacts (PDFs, HTML, images, API specs)          │
│                                                                             │
│  2. ANALYZE (G0)                                                            │
│     $ cdd analyze sources/form.pdf --output analysis/                       │
│     → Produces: structure.json, page images, element catalog                │
│                                                                             │
│  3. WRITE CONTRACT                                                          │
│     Requirements MUST cite source_ref from analysis                         │
│     Visual requirements MUST include visual_ref                             │
│                                                                             │
│  4. VALIDATE                                                                │
│     $ cdd validate contracts/                                               │
│     → Checks all source_refs exist in analysis artifacts                    │
│     → Warns on requirements without source_refs                             │
│                                                                             │
│  5. LINT (G1)                                                               │
│     $ cdd lint contracts/                                                   │
│     → Schema validation + coverage + source_ref validation                  │
│                                                                             │
│  6. BUILD                                                                   │
│     Implementation guided by source_refs and analysis artifacts             │
│                                                                             │
│  7. TEST (G2)                                                               │
│     $ cdd isolate contracts/feature.yaml   # Single contract                │
│     $ cdd test contracts/                   # All contracts                 │
│     → Tests can reference same analysis for comparison                      │
│                                                                             │
│  8. FREEZE (G3)                                                             │
│     Set status: frozen in contract                                          │
│                                                                             │
│  9. DEPLOY                                                                  │
│     Only after G0-G3 all pass                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 6: Schema Changes Required

### New Top-Level Field: `sources`

```yaml
# contracts/project.yaml
project: pyro-logger
cdd_spec: 1.2.0
version: 1.0.0
status: draft

sources:  # NEW
  - id: SRC001
    type: pdf
    file: sources/WeeklyPyrotechnicLog_4.pdf
    analysis: analysis/form/
    description: Official form to replicate
    
  - id: SRC002
    type: html
    file: reference/wireframe.html
    analysis: analysis/wireframe/
    description: Installer landing page wireframe
```

### New Requirement Fields

```yaml
requirements:
  - id: R010b
    priority: must
    description: Input fields use rectangular boxes
    source_ref: SRC001#E1_5      # NEW: Required for grounded requirements
    visual_ref: analysis/form/page_1.png  # NEW: For visual requirements
    region: {x: 95, y: 85, w: 200, h: 20}  # NEW: Optional coordinates
    acceptance_criteria:
      - Bordered rectangle matching source element E1_5
```

### Lint Behavior

| Contract Status | source_ref Missing | visual_ref Missing (visual req) |
|-----------------|-------------------|--------------------------------|
| draft | Warning | Warning |
| frozen | Warning (strict=Error) | Error |

---

## Part 7: Process Checkpoints

| Checkpoint | Verified By | Must Be True |
|------------|-------------|--------------|
| Reference exists | Human | Artifact is available and accessible |
| Analysis complete | `cdd analyze` exits 0 | Tool produces baseline output |
| Baseline approved | Human | Analysis captures what matters |
| Contract valid | `cdd lint` exits 0 | Schema correct, requirements covered |
| Source refs valid | `cdd validate` exits 0 | All refs point to real elements |
| Tests runnable | `cdd test` executes | No missing tools or broken steps |
| Tests pass | `cdd test` exits 0 | All assertions satisfied |
| Contract frozen | `status: frozen` in YAML | Explicit human decision |
| Ready to deploy | G0 ∧ G1 ∧ G2 ∧ G3 | All gates passed |

---

## Part 8: Implementation Roadmap

### Phase A: Source Validation (Next Priority)

| Item | Effort | Impact | Status |
|------|--------|--------|--------|
| `cdd analyze` (PDF) | 2 days | High | ✅ Done |
| `cdd analyze` (HTML) | 1 day | High | ✅ Done |
| `cdd analyze` (source) | 1 day | High | ✅ Done |
| `cdd compare` | 0.5 day | Medium | ✅ Done |
| `cdd paths` | 0.5 day | High | ✅ Done |
| `cdd isolate` | 1 day | High | ✅ Done |
| `source_ref` field in schema | 1 day | High | 🔲 TODO |
| `sources` section in project | 0.5 day | High | 🔲 TODO |
| `cdd validate` command | 1 day | High | 🔲 TODO |
| Assumption language lint | 0.5 day | Medium | 🔲 TODO |

### Phase B: Gate Enforcement (After Phase A)

| Item | Effort | Impact | Status |
|------|--------|--------|--------|
| `cdd gate` command | 0.5 day | High | 🔲 TODO |
| Pre-commit hook generator | 0.5 day | Medium | 🔲 TODO |
| CI workflow templates | 0.5 day | Medium | 🔲 TODO |
| Gate violation reporting | 0.5 day | Medium | 🔲 TODO |

### Phase C: Extended Analysis (Future)

| Item | Effort | Impact | Status |
|------|--------|--------|--------|
| `cdd analyze` (images) | 2 days | Medium | 🔲 TODO |
| `cdd analyze` (API specs) | 2 days | Medium | 🔲 TODO |
| Visual diff testing | 3 days | Medium | 🔲 TODO |
| `$.file.content` in assertions | 1 day | High | 🔲 TODO |

---

## Part 9: Example - Complete Workflow

### Step 1: Analyze Source

```bash
$ cdd analyze sources/WeeklyPyrotechnicLog_4.pdf --output analysis/form/

Analyzing: sources/WeeklyPyrotechnicLog_4.pdf
  Page 1: 47 elements (23 rectangles, 24 text blocks)
  Page 2: 38 elements (15 rectangles, 23 text blocks)
Output: analysis/form/
  - page_1.png
  - page_2.png
  - structure.json
  - elements.md
```

### Step 2: Write Contract with Source Refs

```yaml
# contracts/project.yaml
project: pyro-logger
cdd_spec: 1.2.0
version: 1.0.0
status: draft

sources:
  - id: SRC001
    type: pdf
    file: sources/WeeklyPyrotechnicLog_4.pdf
    analysis: analysis/form/

# contracts/pdf_layout.yaml
contract: pdf_layout
version: 1.0.0
status: draft

requirements:
  - id: R001
    priority: must
    description: Input fields use rectangular boxes
    source_ref: SRC001#R1_5
    visual_ref: analysis/form/page_1.png
    acceptance_criteria:
      - Rectangular bordered box matching element R1_5
```

### Step 3: Validate

```bash
$ cdd validate contracts/
✅ R001: source_ref SRC001#R1_5 found in structure.json
✅ R001: visual_ref analysis/form/page_1.png exists
```

### Step 4: Lint

```bash
$ cdd lint contracts/
✅ PASS (schema valid, coverage OK, source_refs valid)
```

### Step 5: Implement and Test

```bash
# Test single contract in isolation
$ cdd isolate contracts/pdf_layout.yaml -v
✅ T001: field_dimensions_match PASS
✅ T002: box_borders_present PASS

# Or test all contracts
$ cdd test contracts/
```

### Step 6: Freeze and Deploy

```bash
# Set status: frozen in contracts
$ cdd gate contracts/
✅ G1 (lint): PASS
✅ G2 (test): PASS  
✅ G3 (frozen): PASS
Ready to deploy.
```

---

## Summary

| Problem | Solution | Status |
|---------|----------|--------|
| Contracts based on assumptions | `cdd analyze` extracts evidence first | ✅ PDF/HTML/source done |
| Testing single contracts tedious | `cdd isolate` automates isolation | ✅ Done |
| No source validation | `source_ref` field links requirements to artifacts | 🔲 TODO |
| Visual specs in prose | `visual_ref` + region coordinates | 🔲 TODO |
| Vague language passes lint | Assumption language detection | 🔲 TODO |
| Late discovery of errors | `cdd validate` catches missing refs early | 🔲 TODO |
| Gates get skipped | `cdd gate` + enforcement mechanisms | 🔲 TODO |
| No process documentation | Anti-patterns section in spec | 🔲 TODO |

**The core principle:** You can't write a requirement until you've analyzed the source. You can't deploy until all gates pass. The tooling enforces both.
