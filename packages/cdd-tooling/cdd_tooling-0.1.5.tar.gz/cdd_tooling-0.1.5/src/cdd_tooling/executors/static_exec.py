# src/cdd/executors/static_exec.py
"""Static executor: file scanning and AST analysis."""
from __future__ import annotations

import re
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional

from cdd_tooling.executors.base import RunContext, StepResult, StepSpec
from cdd_tooling.assertions import AssertionResult
from cdd_tooling.jsonpath import interpolate_vars


class StaticExecutor:
    """
    Static analysis executor.
    
    Supports two modes:
    1. AST analysis: populates $.ast for assertions (requires parser)
    2. File scanning: runs regex assertions against file contents (type: static tests)
    """

    name = "static"

    def supports(self, action: str) -> bool:
        return False  # No runtime actions

    def setup(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        pass

    def execute_step(
        self,
        ctx: RunContext,
        runner_cfg: Dict[str, Any],
        test_id: str,
        step: StepSpec,
        timeout_ms: int,
    ) -> StepResult:
        return StepResult(
            ok=False,
            error_code="static_no_steps",
            message="Static executor does not execute steps; use assertions against $.ast or type: static tests",
        )

    def teardown(self, ctx: RunContext, runner_cfg: Dict[str, Any]) -> None:
        pass

    def analyze(self, ctx: RunContext, runner_cfg: Dict[str, Any], source_path: str) -> Dict[str, Any]:
        """
        Analyze source file and return AST blob.
        
        MVP: Returns empty structure. Full implementation requires parser
        specified by runner.parser (sclang_ast, python_ast).
        """
        parser = runner_cfg.get("parser")
        
        return {
            "schema_version": "1.0",
            "calls": [],
            "bus_reads": {},
            "imports": [],
            "definitions": [],
            "parse_errors": [],
            "parser": parser,
            "source_included": False,
        }


def expand_files(files_spec: Any, base_dir: Path, vars_dict: Optional[Dict[str, Any]] = None) -> List[Path]:
    """
    Expand files specification to list of paths.
    
    files_spec can be:
      - string glob: "packs/foo/generators/*.scd"
      - list of globs: ["*.scd", "*.sc"]
      - list of explicit files
      
    Supports {var} and $.vars.X interpolation from vars_dict.
    """
    if files_spec is None:
        return []
    
    vars_dict = vars_dict or {}
    
    if isinstance(files_spec, str):
        patterns = [files_spec]
    elif isinstance(files_spec, list):
        patterns = files_spec
    else:
        return []
    
    paths = []
    for pattern in patterns:
        # Interpolate variables
        pattern = interpolate_vars(pattern, vars_dict)
        # Expand glob relative to base_dir
        matches = glob(str(base_dir / pattern), recursive=True)
        paths.extend(Path(m) for m in matches)
    
    return sorted(set(paths))


def scan_file_assertions(
    file_path: Path,
    content: str,
    assertions: List[Dict[str, Any]],
) -> List[AssertionResult]:
    """
    Run assertions against file content.
    Returns list of failures (empty if all pass).
    
    Supported ops for file scanning:
      - not_matches: fail for each regex match found
      - matches: fail if no match found
    """
    results = []
    
    for a in assertions:
        op = a.get("op")
        pattern = a.get("pattern") or a.get("expected")
        message = a.get("message")
        
        if op == "not_matches":
            # Find all matches - each is a failure
            for m in re.finditer(pattern, content, re.MULTILINE):
                line_num = content.count('\n', 0, m.start()) + 1
                line_start = content.rfind('\n', 0, m.start()) + 1
                col = m.start() - line_start + 1
                lines = content.splitlines()
                snippet = lines[line_num - 1][:200] if line_num - 1 < len(lines) else ""
                
                results.append(AssertionResult(
                    op=op,
                    actual=m.group(0),
                    expected=f"no match for /{pattern}/",
                    pass_=False,
                    message=message,
                    details={
                        "file": str(file_path),
                        "line": line_num,
                        "col": col,
                        "match": m.group(0),
                        "snippet": snippet.strip(),
                    }
                ))
        
        elif op == "matches":
            # Must have at least one match
            if not re.search(pattern, content, re.MULTILINE):
                results.append(AssertionResult(
                    op=op,
                    actual=None,
                    expected=f"match for /{pattern}/",
                    pass_=False,
                    message=message,
                    details={"file": str(file_path)}
                ))
    
    return results


def run_static_test(
    test: Dict[str, Any],
    base_dir: Path,
    vars_dict: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run a static file scan test.
    
    This is called for tests with type: static and a files: field.
    
    Args:
        test: Test definition dict from YAML
        base_dir: Base directory for file glob resolution
        vars_dict: Variables for interpolation
    
    Returns dict with:
      - status: "pass" | "fail" | "error"
      - assertions: list of AssertionResult (failures only for brevity)
      - files_scanned: count of files processed
      - error: error message if status == "error"
    """
    vars_dict = vars_dict or {}
    files_spec = test.get("files")
    
    # Interpolate vars in files spec
    files_spec = interpolate_vars(files_spec, vars_dict)
    
    paths = expand_files(files_spec, base_dir, vars_dict)
    
    if not paths:
        return {
            "status": "error",
            "assertions": [],
            "files_scanned": 0,
            "error": f"No files matched: {files_spec}",
        }
    
    all_failures: List[AssertionResult] = []
    
    for path in paths:
        try:
            content = path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            all_failures.append(AssertionResult(
                op='read',
                actual=str(path),
                expected='readable file',
                pass_=False,
                error=str(e),
            ))
            continue
        
        failures = scan_file_assertions(path, content, test.get("assert", []))
        all_failures.extend(failures)
    
    return {
        "status": "pass" if not all_failures else "fail",
        "assertions": all_failures,
        "files_scanned": len(paths),
    }
