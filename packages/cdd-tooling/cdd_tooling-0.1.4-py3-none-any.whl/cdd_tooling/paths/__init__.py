# src/cdd_tooling/paths/__init__.py
"""
CDD Path Verification

Pre-gate verification that all file paths in contracts resolve correctly.
Extracts paths from:
  - files: field (static executor)
  - shell command arrays (shell executor)

Usage:
    cdd paths contracts/feature.yaml
    cdd paths contracts/
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


def looks_like_path(s: Any) -> bool:
    """Check if string looks like a file path."""
    if not isinstance(s, str):
        return False
    # Must contain path separator
    if '/' not in s and '\\' not in s:
        return False
    # Skip URLs
    if s.startswith('http://') or s.startswith('https://'):
        return False
    # Skip common non-path patterns
    if s.startswith('-'):  # command flags
        return False
    # Has file extension or is relative path
    if re.search(r'\.\w+$', s) or s.startswith('../') or s.startswith('./'):
        return True
    return False


def extract_file_paths(contract_data: Dict[str, Any]) -> List[str]:
    """Extract all file paths from tests in a contract."""
    paths = []
    tests = contract_data.get('tests', [])
    
    for test in tests:
        # Extract from files: field (static executor)
        files = test.get('files')
        if files:
            if isinstance(files, list):
                paths.extend(files)
            else:
                paths.append(files)
        
        # Extract from steps (shell executor)
        steps = test.get('steps', [])
        for step in steps:
            # Shell command arrays: ["grep", "pattern", "../path/to/file"]
            command = step.get('command', [])
            if isinstance(command, list):
                for arg in command:
                    if looks_like_path(arg):
                        paths.append(arg)
    
    return paths


def suggest_fix(path: str, contract_dir: Path) -> Optional[str]:
    """Try to find the file and suggest a corrected path."""
    # Try adding ../
    parent_path = f"../{path}"
    if (contract_dir / parent_path).exists():
        return parent_path
    
    # Try removing ../
    if path.startswith("../"):
        child_path = path[3:]
        if (contract_dir / child_path).exists():
            return child_path
    
    # Try from repo root (two levels up)
    grandparent_path = f"../../{path}"
    if (contract_dir / grandparent_path).exists():
        return grandparent_path
    
    return None


def verify_contract(contract_path: Path) -> Dict[str, Any]:
    """
    Verify all file paths in a contract.
    
    Returns:
        {
            "contract": str,
            "contract_path": str,
            "ok": bool,
            "passed": [str, ...],
            "failed": [{"path": str, "suggestion": str|None}, ...],
            "total": int
        }
    """
    contract_dir = contract_path.parent
    
    with open(contract_path) as f:
        data = yaml.safe_load(f)
    
    contract_name = data.get('contract', contract_path.stem)
    file_paths = extract_file_paths(data)
    
    # Deduplicate while preserving order
    seen = set()
    unique_paths = []
    for p in file_paths:
        if p not in seen:
            seen.add(p)
            unique_paths.append(p)
    
    passed = []
    failed = []
    
    for path in unique_paths:
        resolved = contract_dir / path
        if resolved.exists():
            passed.append(path)
        else:
            suggestion = suggest_fix(path, contract_dir)
            failed.append({
                "path": path,
                "suggestion": suggestion
            })
    
    return {
        "contract": contract_name,
        "contract_path": str(contract_path),
        "ok": len(failed) == 0,
        "passed": passed,
        "failed": failed,
        "total": len(unique_paths)
    }


def verify_paths(contracts_path: Path) -> Dict[str, Any]:
    """
    Verify paths in one or more contracts.
    
    Args:
        contracts_path: Single contract file or directory of contracts
        
    Returns:
        {
            "ok": bool,
            "contracts_checked": int,
            "total_paths": int,
            "passed_paths": int,
            "failed_paths": int,
            "results": [verify_contract result, ...]
        }
    """
    if contracts_path.is_file():
        contract_files = [contracts_path]
    else:
        contract_files = sorted(contracts_path.glob("*.yaml"))
        # Exclude project.yaml from path checking
        contract_files = [f for f in contract_files if f.name != "project.yaml"]
    
    results = []
    total_passed = 0
    total_failed = 0
    
    for cf in contract_files:
        result = verify_contract(cf)
        results.append(result)
        total_passed += len(result["passed"])
        total_failed += len(result["failed"])
    
    return {
        "ok": total_failed == 0,
        "contracts_checked": len(contract_files),
        "total_paths": total_passed + total_failed,
        "passed_paths": total_passed,
        "failed_paths": total_failed,
        "results": results
    }
