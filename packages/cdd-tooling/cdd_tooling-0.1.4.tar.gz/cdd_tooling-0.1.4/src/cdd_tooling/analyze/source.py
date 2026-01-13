# src/cdd_tooling/analyze/source.py
"""
Source Reference Handler for CDD Analyze.

For readable source files (Python, JS, SC, etc.), captures a frozen
reference snapshot with metadata and a patterns template for documentation.

Unlike PDF/HTML analyzers which extract measurements, source references
capture the file as-is since the file content is directly readable.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Recognized source extensions
SOURCE_EXTENSIONS: Dict[str, str] = {
    # Python
    ".py": "python",
    ".pyi": "python",
    # JavaScript/TypeScript
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    # SuperCollider
    ".scd": "supercollider",
    ".sc": "supercollider",
    # Config/Data
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "toml",
    # Shell
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    # Other
    ".md": "markdown",
    ".txt": "text",
    ".css": "css",
    ".sql": "sql",
    ".r": "r",
    ".rs": "rust",
    ".go": "go",
    ".rb": "ruby",
    ".lua": "lua",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".java": "java",
    ".swift": "swift",
    ".kt": "kotlin",
}


def is_source_file(path: Path) -> bool:
    """Check if file is a recognized source type."""
    return path.suffix.lower() in SOURCE_EXTENSIONS


def get_file_type(path: Path) -> Optional[str]:
    """Get the file type identifier for a source file."""
    return SOURCE_EXTENSIONS.get(path.suffix.lower())


def compute_hash(path: Path) -> str:
    """Compute SHA-256 hash of file contents."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def count_lines(path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def generate_patterns_template(file_type: str, source_path: Path, file_hash: str, timestamp: str) -> str:
    """Generate PATTERNS.md template based on file type."""
    
    base_template = f"""# Reference: {source_path.name}

> Captured: {timestamp}  
> Hash: {file_hash[:12]}...

## Purpose

<!-- What does this reference file do? Why is it the reference? -->


## Key Patterns to Preserve

<!-- What structural patterns should new code follow? -->

- 
- 
- 

## Required Elements

<!-- Classes, methods, functions that must exist in derived code -->

- 
- 
- 

## Allowed Deviations

<!-- What can/should differ in the new code? -->

- 
- 
- 

## Notes

<!-- Any additional context for implementation -->

"""

    # Add file-type specific prompts
    type_specific: Dict[str, str] = {
        "python": """
## Python-Specific

### Classes
<!-- List key classes and their responsibilities -->

### Public API
<!-- Functions/methods that form the interface -->

### Dependencies
<!-- Required imports/packages -->

""",
        "supercollider": """
## SuperCollider-Specific

### SynthDef Structure
<!-- Key UGen patterns, signal flow -->

### Bus Reads
<!-- Required control buses -->

### Post-Chain
<!-- ~ensure2ch, ~multiFilter, ~envVCA patterns -->

""",
        "javascript": """
## JavaScript-Specific

### Exports
<!-- Module exports that form the interface -->

### Component Structure
<!-- For React/Vue, component patterns -->

### Dependencies
<!-- Required imports/packages -->

""",
        "typescript": """
## TypeScript-Specific

### Exports
<!-- Module exports that form the interface -->

### Types/Interfaces
<!-- Key type definitions -->

### Dependencies
<!-- Required imports/packages -->

""",
    }
    
    return base_template + type_specific.get(file_type, "")


def analyze_source(source_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Analyze a source file by capturing reference snapshot.
    
    Args:
        source_path: Path to source file
        output_dir: Directory to write analysis output
        
    Returns:
        dict with analysis results
    """
    source_path = Path(source_path)
    output_dir = Path(output_dir)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")
    
    if not is_source_file(source_path):
        raise ValueError(f"Unsupported source type: {source_path.suffix}")
    
    file_type = get_file_type(source_path)
    file_hash = compute_hash(source_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    line_count = count_lines(source_path)
    size_bytes = source_path.stat().st_size
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Copy source file (frozen snapshot)
    snapshot_name = f"source{source_path.suffix}"
    snapshot_path = output_dir / snapshot_name
    shutil.copy2(source_path, snapshot_path)
    
    # 2. Generate manifest (structure.json for consistency with PDF/HTML)
    manifest = {
        "type": "source_reference",
        "original_path": str(source_path),
        "snapshot_path": snapshot_name,
        "hash": file_hash,
        "captured_at": timestamp,
        "file_type": file_type,
        "size_bytes": size_bytes,
        "line_count": line_count,
    }
    
    structure_path = output_dir / "structure.json"
    with open(structure_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    # 3. Generate patterns template
    patterns_template = generate_patterns_template(file_type, source_path, file_hash, timestamp)
    
    patterns_path = output_dir / "PATTERNS.md"
    with open(patterns_path, "w") as f:
        f.write(patterns_template)
    
    # 4. Generate summary (elements.md equivalent)
    summary = f"""# Source Reference: {source_path.name}

| Property | Value |
|----------|-------|
| Type | {file_type} |
| Original | `{source_path}` |
| Hash | `{file_hash[:12]}...` |
| Size | {size_bytes} bytes |
| Lines | {line_count} |
| Captured | {timestamp} |

## Files

- `{snapshot_name}` - Frozen snapshot of reference
- `structure.json` - Metadata
- `PATTERNS.md` - Pattern documentation (fill in)

## Next Steps

1. Review `{snapshot_name}` to understand the reference
2. Fill in `PATTERNS.md` with patterns to preserve
3. Write contract based on documented patterns
4. Implement against contract
"""
    
    summary_path = output_dir / "elements.md"
    with open(summary_path, "w") as f:
        f.write(summary)
    
    # Return result in format consistent with other analyzers
    return {
        "type": "source_reference",
        "source_name": source_path.name,
        "file_type": file_type,
        "hash": file_hash,
        "line_count": line_count,
        "size_bytes": size_bytes,
        "output_dir": str(output_dir),
        "files": [
            snapshot_name,
            "structure.json",
            "PATTERNS.md",
            "elements.md",
        ],
    }


def compare_source_analyses(original: Dict[str, Any], generated: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two source reference analyses.
    
    For source references, comparison checks:
    - Hash match (identical content)
    - File type match
    
    Detailed structural comparison requires contracts, not this tool.
    """
    results = {
        "type": "source_reference",
        "match": original.get("hash") == generated.get("hash"),
        "original_hash": original.get("hash"),
        "generated_hash": generated.get("hash"),
        "file_type_match": original.get("file_type") == generated.get("file_type"),
        "original_type": original.get("file_type"),
        "generated_type": generated.get("file_type"),
        "original_lines": original.get("line_count"),
        "generated_lines": generated.get("line_count"),
    }
    
    if results["match"]:
        results["summary"] = "✓ Files are identical"
    else:
        line_diff = (results.get("generated_lines") or 0) - (results.get("original_lines") or 0)
        if line_diff > 0:
            results["summary"] = f"✗ Files differ (+{line_diff} lines) - use contracts to verify structural requirements"
        elif line_diff < 0:
            results["summary"] = f"✗ Files differ ({line_diff} lines) - use contracts to verify structural requirements"
        else:
            results["summary"] = "✗ Files differ (same line count) - use contracts to verify structural requirements"
    
    return results
