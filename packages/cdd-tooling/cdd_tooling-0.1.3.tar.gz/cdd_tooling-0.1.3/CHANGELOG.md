# Changelog

Tooling implementation changes. For spec changes, see [CDD Spec CHANGELOG](https://github.com/thegdyne/cdd/blob/main/CHANGELOG.md).

## [0.1.3] - 2025-12-31

### Added
- `cdd isolate` command for single contract testing in isolated workspace
- Auto-detects project root (`.cdd/` + `contracts/`, `.git/` + `contracts/`, or `src/` + `contracts/`)
- Creates temporary workspace with only the target contract
- Symlinks required source directories automatically
- Safe cleanup with marker file verification

### Options
| Option | Short | Description |
|--------|-------|-------------|
| `--project` | `-p` | Explicit project root |
| `--keep` | `-k` | Keep work directory after run |
| `--keep-on-fail` | | Keep work directory only on failure |
| `--work-dir` | `-w` | Custom work directory |
| `--verbose` | `-v` | Show detailed operations |
| `--paths-only` | | Only run path verification |
| `--dry-run` | | Preview plan without execution |

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Paths and tests passed |
| 1 | Test failure |
| 2 | Path verification failed |
| 3 | Contract parse error |
| 4 | Project root not found |
| 5 | Invalid source path |

### Implements
- CDD Spec 1.1.5
- CDD_ISOLATE_SPEC.md v1.0

## [0.1.2] - 2025-12-30

### Added
- Source reference handler (`cdd analyze *.py`, `*.js`, `*.scd`, etc.)
- Captures frozen snapshot of source files for reference-based development
- Generates `PATTERNS.md` template for documenting patterns to preserve
- Source comparison via `cdd compare` (hash-based matching)

### Supported Source Types
| Extension | Type |
|-----------|------|
| `.py`, `.pyi` | Python |
| `.js`, `.jsx`, `.ts`, `.tsx` | JavaScript/TypeScript |
| `.scd`, `.sc` | SuperCollider |
| `.yaml`, `.yml`, `.json`, `.toml` | Config |
| `.sh`, `.bash`, `.zsh` | Shell |
| `.md`, `.txt`, `.css`, `.sql` | Text/Markup |
| `.rs`, `.go`, `.rb`, `.lua`, `.c`, `.cpp`, `.java`, `.swift`, `.kt` | Other languages |

### Output Structure
```
analysis/<name>/
├── source.<ext>       # Frozen snapshot
├── structure.json     # Metadata (hash, timestamp, line count)
├── PATTERNS.md        # Pattern template (fill in)
└── elements.md        # Summary
```

### Implements
- CDD Spec 1.1.5

## [0.1.1] - 2025-12-29

### Fixed
- `cdd compare` now correctly routes HTML analyses to `compare_html_analyses()`
- Previously all comparisons used PDF comparison logic regardless of file type

### Changed
- Compare command help text updated to reflect HTML support
- ROADMAP updated to reflect actual implementation status

### Implements
- CDD Spec 1.1.5

## [0.1.0] - 2025-12-29

### Added
- Initial release extracted from cdd repo
- PDF analyzer (`cdd analyze *.pdf`) — requires `[pdf]` extra
- HTML analyzer (`cdd analyze *.html`)
- Analysis comparison (`cdd compare`)
- Contract linting (`cdd lint`)
- Contract testing (`cdd test`)
- Coverage reporting (`cdd coverage`)
- Python executor with `call`, `call_n` actions
- Shell executor with `shell` action
- Static executor for file content assertions (`matches`, `not_matches`)
- SuperCollider executor (stub — `render_nrt` returns "not_implemented")

### Executors
| Executor | Status | Actions |
|----------|--------|---------|
| `python` | ✅ Full | `call`, `call_n` with timing |
| `shell` | ✅ Full | Command execution, stdout/stderr capture |
| `static` | ⚠️ Partial | File scanning works; AST parsing is stub |
| `sclang` | ⚠️ Stub | Returns "not_implemented" |

### Implements
- CDD Spec 1.1.x

---

## Version Numbering

Tooling versions are independent of spec versions:

| Tooling | Spec | Notes |
|---------|------|-------|
| 0.1.x | 1.1.x | Initial implementation |

Tooling uses semver:
- **Patch** (0.1.x): Bug fixes, no API changes
- **Minor** (0.x.0): New features, backwards compatible
- **Major** (x.0.0): Breaking changes to CLI or output format
