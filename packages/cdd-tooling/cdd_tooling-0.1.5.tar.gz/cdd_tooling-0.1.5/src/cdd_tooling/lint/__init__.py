# src/cdd/lint/__init__.py
"""Contract linting: schema validation + requirement coverage."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


def lint_contracts(contracts_path: Path, strict: bool = False) -> Dict[str, Any]:
    """
    Lint contract files.
    
    Returns:
        {
            "ok": bool,
            "errors": [...],
            "warnings": [...],
            "contracts_checked": int,
        }
    """
    errors: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    contracts_checked = 0

    if contracts_path.is_file():
        files = [contracts_path]
    elif contracts_path.is_dir():
        files = sorted(contracts_path.rglob("*.yaml"))
    else:
        return {
            "ok": False,
            "errors": [{"code": "path_not_found", "message": f"Path not found: {contracts_path}"}],
            "warnings": [],
            "contracts_checked": 0,
        }

    for f in files:
        contracts_checked += 1
        try:
            with f.open("r", encoding="utf-8") as fp:
                doc = yaml.safe_load(fp)
            
            if not isinstance(doc, dict):
                errors.append({"code": "invalid_yaml", "message": f"{f}: must be a mapping"})
                continue

            # Determine contract type
            is_project = "project" in doc
            is_component = "contract" in doc

            if not is_project and not is_component:
                errors.append({"code": "unknown_contract_type", "message": f"{f}: must have 'project' or 'contract' field"})
                continue

            if is_project:
                _lint_project(f, doc, errors, warnings, strict)
            else:
                _lint_component(f, doc, errors, warnings, strict)

        except yaml.YAMLError as e:
            errors.append({"code": "yaml_parse_error", "message": f"{f}: {e}"})
        except Exception as e:
            errors.append({"code": "unexpected_error", "message": f"{f}: {e}"})

    ok = len(errors) == 0
    if strict and len(warnings) > 0:
        ok = False

    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "contracts_checked": contracts_checked,
    }


def _lint_project(path: Path, doc: Dict[str, Any], errors: List, warnings: List, strict: bool) -> None:
    """Lint a project contract."""
    required = ["project", "version", "status", "goal", "success_criteria", "components"]
    
    for field in required:
        if field not in doc:
            errors.append({"code": "missing_field", "message": f"{path}: missing required field '{field}'"})

    status = doc.get("status")
    if status not in ("draft", "frozen", "deprecated"):
        errors.append({"code": "invalid_status", "message": f"{path}: status must be draft|frozen|deprecated"})

    # cdd_spec required for frozen
    if status == "frozen" and "cdd_spec" not in doc:
        errors.append({"code": "missing_cdd_spec", "message": f"{path}: frozen project requires 'cdd_spec' field"})


def _lint_component(path: Path, doc: Dict[str, Any], errors: List, warnings: List, strict: bool) -> None:
    """Lint a component contract."""
    required = ["contract", "version", "status", "description", "runner", "requirements", "tests"]
    
    for field in required:
        if field not in doc:
            errors.append({"code": "missing_field", "message": f"{path}: missing required field '{field}'"})

    status = doc.get("status")
    if status not in ("draft", "frozen", "deprecated"):
        errors.append({"code": "invalid_status", "message": f"{path}: status must be draft|frozen|deprecated"})

    # Check runner
    runner = doc.get("runner", {})
    if not isinstance(runner, dict):
        errors.append({"code": "invalid_runner", "message": f"{path}: runner must be an object"})
    elif "executor" not in runner:
        errors.append({"code": "missing_executor", "message": f"{path}: runner.executor is required"})

    # Check requirements have required fields
    requirements = doc.get("requirements", [])
    if not isinstance(requirements, list):
        errors.append({"code": "invalid_requirements", "message": f"{path}: requirements must be an array"})
    else:
        req_ids = set()
        for r in requirements:
            if not isinstance(r, dict):
                errors.append({"code": "invalid_requirement", "message": f"{path}: requirement must be an object"})
                continue
            for field in ["id", "priority", "description", "acceptance_criteria"]:
                if field not in r:
                    errors.append({"code": "missing_field", "message": f"{path}: requirement missing '{field}'"})
            if "id" in r:
                req_ids.add(r["id"])

    # Check tests and coverage
    tests = doc.get("tests", [])
    if not isinstance(tests, list):
        errors.append({"code": "invalid_tests", "message": f"{path}: tests must be an array"})
    else:
        linked_reqs = set()
        for t in tests:
            if not isinstance(t, dict):
                errors.append({"code": "invalid_test", "message": f"{path}: test must be an object"})
                continue
            for field in ["id", "name", "type", "assert"]:
                if field not in t:
                    errors.append({"code": "missing_field", "message": f"{path}: test missing '{field}'"})
            
            req = t.get("requirement")
            if req:
                linked_reqs.add(req)
            elif status == "frozen":
                warnings.append({"code": "unlinked_test", "message": f"{path}: test {t.get('id', '?')} has no requirement link"})

        # Check coverage: every requirement needs at least one test
        for req_id in req_ids:
            if req_id not in linked_reqs:
                errors.append({"code": "uncovered_requirement", "message": f"{path}: requirement {req_id} has no linked tests"})
