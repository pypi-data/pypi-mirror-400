# src/cdd/coverage.py
"""Requirement coverage computation."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


def compute_coverage(contracts_path: Path) -> Dict[str, Any]:
    """
    Compute requirement coverage across contracts.
    
    Returns:
        {
            "requirements": [{"id": "R001", "linked_tests": 2}, ...],
            "uncovered_count": int,
            "total_count": int,
        }
    """
    requirements: Dict[str, int] = {}  # req_id -> linked test count

    if contracts_path.is_file():
        files = [contracts_path]
    elif contracts_path.is_dir():
        files = sorted(contracts_path.rglob("*.yaml"))
    else:
        return {"requirements": [], "uncovered_count": 0, "total_count": 0}

    for f in files:
        try:
            with f.open("r", encoding="utf-8") as fp:
                doc = yaml.safe_load(fp)
            
            if not isinstance(doc, dict):
                continue

            # Skip project contracts
            if "project" in doc:
                continue

            # Collect requirement IDs
            for r in doc.get("requirements", []):
                if isinstance(r, dict) and "id" in r:
                    req_id = r["id"]
                    if req_id not in requirements:
                        requirements[req_id] = 0

            # Count linked tests
            for t in doc.get("tests", []):
                if isinstance(t, dict):
                    req = t.get("requirement")
                    if req and req in requirements:
                        requirements[req] += 1

        except Exception:
            continue

    result = [{"id": k, "linked_tests": v} for k, v in sorted(requirements.items())]
    uncovered = sum(1 for r in result if r["linked_tests"] == 0)

    return {
        "requirements": result,
        "uncovered_count": uncovered,
        "total_count": len(result),
    }
